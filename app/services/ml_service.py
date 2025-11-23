"""Machine Learning service with multiple model types and evaluation."""
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.svm import SVR, SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)
from typing import List, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.model_metadata import ModelMetadata
from app.config import settings


class MLService:
    """Service for ML model training with multiple algorithms and evaluation."""

    # Supported model types
    REGRESSION_MODELS = {
        "linear_regression": LinearRegression,
        "random_forest_regressor": RandomForestRegressor,
        "svr": SVR,
    }

    CLASSIFICATION_MODELS = {
        "logistic_regression": LogisticRegression,
        "random_forest_classifier": RandomForestClassifier,
        "svc": SVC,
    }

    ALL_MODELS = {**REGRESSION_MODELS, **CLASSIFICATION_MODELS}

    def __init__(self):
        """Initialize ML service and ensure models directory exists."""
        os.makedirs(settings.MODELS_DIR, exist_ok=True)

    def _get_model_instance(self, model_type: str, model_params: Dict[str, Any] = None):
        """
        Create model instance based on type and parameters.

        Args:
            model_type: Type of model to create
            model_params: Optional parameters for the model

        Returns:
            Model instance
        """
        if model_type not in self.ALL_MODELS:
            raise ValueError(
                f"Unsupported model type: {model_type}. "
                f"Supported types: {list(self.ALL_MODELS.keys())}"
            )

        model_class = self.ALL_MODELS[model_type]

        # Default parameters for each model type
        default_params = {
            "random_forest_regressor": {"n_estimators": 100, "random_state": 42},
            "random_forest_classifier": {"n_estimators": 100, "random_state": 42},
            "svr": {"kernel": "rbf"},
            "svc": {"kernel": "rbf"},
            "logistic_regression": {"random_state": 42, "max_iter": 1000},
        }

        # Merge with user-provided parameters
        params = default_params.get(model_type, {})
        if model_params:
            params.update(model_params)

        return model_class(**params)

    def _is_classification(self, model_type: str) -> bool:
        """Check if model type is for classification."""
        return model_type in self.CLASSIFICATION_MODELS

    def _calculate_regression_metrics(
        self, y_true: np.ndarray, y_pred: np.ndarray
    ) -> Dict[str, float]:
        """Calculate regression evaluation metrics."""
        return {
            "mae": float(mean_absolute_error(y_true, y_pred)),
            "mse": float(mean_squared_error(y_true, y_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
            "r2": float(r2_score(y_true, y_pred)),
        }

    def _calculate_classification_metrics(
        self, y_true: np.ndarray, y_pred: np.ndarray
    ) -> Dict[str, float]:
        """Calculate classification evaluation metrics."""
        # Determine if binary or multiclass
        n_classes = len(np.unique(y_true))
        average = 'binary' if n_classes == 2 else 'weighted'

        return {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, average=average, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, average=average, zero_division=0)),
            "f1_score": float(f1_score(y_true, y_pred, average=average, zero_division=0)),
        }

    def train_model(
        self,
        db: Session,
        csv_file_path: str,
        model_name: str,
        model_type: str,
        features: List[str],
        label: str,
        model_params: Dict[str, Any] = None,
        test_size: float = 0.2,
    ) -> Dict[str, Any]:
        """
        Train a model with specified type and evaluate it.

        Args:
            db: Database session
            csv_file_path: Path to the CSV file
            model_name: Name to save the model as
            model_type: Type of model (e.g., 'linear_regression', 'random_forest_regressor')
            features: List of feature column names
            label: Target column name
            model_params: Optional model parameters
            test_size: Fraction of data to use for testing (default: 0.2)

        Returns:
            Dictionary with training status, metadata, and evaluation metrics
        """
        # Load CSV
        df = pd.read_csv(csv_file_path)

        # Validate columns
        missing_features = [f for f in features if f not in df.columns]
        if missing_features:
            raise ValueError(f"Features not found in CSV: {missing_features}")

        if label not in df.columns:
            raise ValueError(f"Label column '{label}' not found in CSV")

        # Prepare data
        X = df[features]
        y = df[label]

        # Split data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        # Create and train model
        model = self._get_model_instance(model_type, model_params)
        model.fit(X_train, y_train)

        # Make predictions on test set
        y_pred = model.predict(X_test)

        # Calculate evaluation metrics
        is_classification = self._is_classification(model_type)
        if is_classification:
            metrics = self._calculate_classification_metrics(y_test, y_pred)
        else:
            metrics = self._calculate_regression_metrics(y_test, y_pred)

        # Save model to file
        model_file_path = os.path.join(settings.MODELS_DIR, f"{model_name}.pkl")
        joblib.dump(model, model_file_path)

        # Save or update metadata in database
        existing_model = db.query(ModelMetadata).filter(
            ModelMetadata.model_name == model_name
        ).first()

        if existing_model:
            # Update existing model
            existing_model.model_type = model_type
            existing_model.features = features
            existing_model.label = label
            existing_model.trained_at = datetime.utcnow()
            existing_model.file_path = model_file_path
            existing_model.metrics = metrics
        else:
            # Create new model metadata
            model_metadata = ModelMetadata(
                model_name=model_name,
                model_type=model_type,
                features=features,
                label=label,
                file_path=model_file_path,
                metrics=metrics,
            )
            db.add(model_metadata)

        db.commit()

        return {
            "status": "model trained",
            "model_type": model_type,
            "features": features,
            "label": label,
            "metrics": metrics,
            "test_size": test_size,
        }

    def predict(
        self,
        db: Session,
        model_name: str,
        input_data: Dict[str, Any],
    ) -> float:
        """
        Make a prediction using a trained model.

        Args:
            db: Database session
            model_name: Name of the model to use
            input_data: Dictionary of feature values

        Returns:
            Prediction value
        """
        # Get model metadata from database
        model_metadata = db.query(ModelMetadata).filter(
            ModelMetadata.model_name == model_name
        ).first()

        if not model_metadata:
            raise ValueError(f"Model '{model_name}' not found")

        # Load model from file
        if not os.path.exists(model_metadata.file_path):
            raise FileNotFoundError(f"Model file not found: {model_metadata.file_path}")

        model = joblib.load(model_metadata.file_path)

        # Prepare input data in the correct order
        features = model_metadata.features
        missing_features = [f for f in features if f not in input_data]
        if missing_features:
            raise ValueError(f"Missing features in input: {missing_features}")

        # Create DataFrame with features in correct order
        input_df = pd.DataFrame([input_data])[features]

        # Make prediction
        prediction = model.predict(input_df)[0]

        return float(prediction)

    def get_all_models(self, db: Session) -> List[ModelMetadata]:
        """
        Get all trained models metadata.

        Args:
            db: Database session

        Returns:
            List of model metadata
        """
        return db.query(ModelMetadata).all()

    def get_model_metrics(self, db: Session, model_name: str) -> Dict[str, Any]:
        """
        Get evaluation metrics for a specific model.

        Args:
            db: Database session
            model_name: Name of the model

        Returns:
            Dictionary with model metrics
        """
        model_metadata = db.query(ModelMetadata).filter(
            ModelMetadata.model_name == model_name
        ).first()

        if not model_metadata:
            raise ValueError(f"Model '{model_name}' not found")

        return {
            "model_name": model_name,
            "model_type": model_metadata.model_type,
            "metrics": model_metadata.metrics or {},
            "trained_at": model_metadata.trained_at,
        }


# Singleton instance
ml_service = MLService()
