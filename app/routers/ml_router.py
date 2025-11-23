"""ML endpoints for training, prediction, and model listing."""
import json
import os
import tempfile
from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.ml_schemas import (
    TrainResponse,
    PredictionRequest,
    PredictionResponse,
    ModelsListResponse,
    ModelInfo,
    ModelMetricsResponse,
)
from app.services.ml_service import ml_service
from app.services.user_service import user_service
from app.utils.dependencies import get_current_user, get_current_user_with_rate_limit
from app.models.user import User
from app.utils.logger import log_info, log_warning, log_error

router = APIRouter(prefix="", tags=["Machine Learning"])


@router.post("/train", response_model=TrainResponse)
async def train_model(
    file: UploadFile = File(...),
    model_name: str = Form(...),
    model_type: str = Form("linear_regression"),
    features: str = Form(...),
    label: str = Form(...),
    model_params: Optional[str] = Form(None),
    test_size: float = Form(0.2),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Train an ML model with evaluation. Requires 1 token and JWT authentication.

    Supported model types:
    - Regression: linear_regression, random_forest_regressor, svr
    - Classification: logistic_regression, random_forest_classifier, svc

    Args:
        file: CSV file with training data
        model_name: Name for the model (e.g., "my_model")
        model_type: Type of model to train (default: "linear_regression")
        features: JSON array of feature column names (e.g., '["age", "salary", "rooms"]')
        label: Name of the target column (e.g., "price")
        model_params: Optional JSON object with model hyperparameters
        test_size: Fraction of data for testing (default: 0.2)
        current_user: Authenticated user from JWT token
        db: Database session

    Returns:
        Training status, model metadata, and evaluation metrics
    """
    try:
        # Check and deduct tokens (1 token for training)
        try:
            user_service.deduct_tokens(db, current_user.username, 1)
            log_info(f"Token deducted for training", username=current_user.username, amount=1, operation="train")
        except ValueError as e:
            log_warning(f"Insufficient tokens for training", username=current_user.username, operation="train")
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=str(e)
            )
        # Parse features JSON
        features_list = json.loads(features)
        if not isinstance(features_list, list):
            raise ValueError("Features must be a JSON array")

        # Parse model_params if provided
        params_dict = None
        if model_params:
            params_dict = json.loads(model_params)

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".csv") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            # Train model with ml_service
            result = ml_service.train_model(
                db=db,
                csv_file_path=tmp_file_path,
                model_name=model_name,
                model_type=model_type,
                features=features_list,
                label=label,
                model_params=params_dict,
                test_size=test_size,
            )
            log_info(f"Model trained successfully", username=current_user.username, model_name=model_name, model_type=model_type, metrics=result.get('metrics'))
            return result
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

    except json.JSONDecodeError as e:
        log_error(f"Training failed - invalid JSON", username=current_user.username, error=str(e))
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
    except ValueError as e:
        log_error(f"Training failed - validation error", username=current_user.username, error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log_error(f"Training failed - unexpected error", username=current_user.username, error=str(e))
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.post("/predict/{model_name}", response_model=PredictionResponse)
async def predict(
    model_name: str,
    input_data: dict,
    current_user: User = Depends(get_current_user_with_rate_limit),
    db: Session = Depends(get_db),
):
    """
    Make a prediction using a trained model. Requires 5 tokens and JWT authentication.

    Args:
        model_name: Name of the trained model
        input_data: Dictionary with feature values
        current_user: Authenticated user from JWT token
        db: Database session

    Returns:
        Prediction value
    """
    try:
        # Check and deduct tokens (5 tokens for prediction)
        try:
            user_service.deduct_tokens(db, current_user.username, 5)
            log_info(f"Token deducted for prediction", username=current_user.username, amount=5, operation="predict", model=model_name)
        except ValueError as e:
            log_warning(f"Insufficient tokens for prediction", username=current_user.username, operation="predict", model=model_name)
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=str(e)
            )
        prediction = ml_service.predict(
            db=db,
            model_name=model_name,
            input_data=input_data,
        )
        log_info(f"Prediction made successfully", username=current_user.username, model=model_name, prediction=prediction)
        return {"prediction": prediction}
    except ValueError as e:
        log_error(f"Prediction failed - model not found", username=current_user.username, model=model_name, error=str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError as e:
        log_error(f"Prediction failed - file not found", username=current_user.username, model=model_name, error=str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log_error(f"Prediction failed - unexpected error", username=current_user.username, model=model_name, error=str(e))
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/models", response_model=ModelsListResponse)
async def get_models(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a list of all trained models. Requires 1 token and JWT authentication.

    Args:
        current_user: Authenticated user from JWT token
        db: Database session

    Returns:
        List of all models with their metadata
    """
    try:
        # Check and deduct tokens (1 token for metadata)
        try:
            user_service.deduct_tokens(db, current_user.username, 1)
            log_info(f"Token deducted for models list", username=current_user.username, amount=1, operation="get_models")
        except ValueError as e:
            log_warning(f"Insufficient tokens for models list", username=current_user.username, operation="get_models")
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=str(e)
            )
        models = ml_service.get_all_models(db)
        model_infos = [
            ModelInfo(
                model_name=m.model_name,
                model_type=m.model_type,
                features=m.features,
                label=m.label,
                trained_at=m.trained_at,
                metrics=m.metrics,
            )
            for m in models
        ]
        log_info(f"Models list retrieved", username=current_user.username, count=len(model_infos))
        return {"models": model_infos}
    except Exception as e:
        log_error(f"Failed to retrieve models", username=current_user.username, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve models: {str(e)}")


@router.get("/models/{model_name}/metrics", response_model=ModelMetricsResponse)
async def get_model_metrics(
    model_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get evaluation metrics for a specific model. Requires 1 token and JWT authentication.

    Args:
        model_name: Name of the model
        current_user: Authenticated user from JWT token
        db: Database session

    Returns:
        Model metrics (MAE, R2, RMSE for regression; Accuracy, Precision, Recall for classification)
    """
    try:
        # Check and deduct tokens (1 token for metrics)
        try:
            user_service.deduct_tokens(db, current_user.username, 1)
            log_info(f"Token deducted for model metrics", username=current_user.username, amount=1, operation="get_metrics", model=model_name)
        except ValueError as e:
            log_warning(f"Insufficient tokens for model metrics", username=current_user.username, operation="get_metrics", model=model_name)
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=str(e)
            )

        metrics_data = ml_service.get_model_metrics(db, model_name)
        log_info(f"Model metrics retrieved", username=current_user.username, model=model_name)
        return ModelMetricsResponse(**metrics_data)
    except ValueError as e:
        log_error(f"Failed to retrieve metrics - model not found", username=current_user.username, model=model_name, error=str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log_error(f"Failed to retrieve model metrics", username=current_user.username, model=model_name, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve model metrics: {str(e)}")
