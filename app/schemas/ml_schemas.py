"""Pydantic schemas for ML endpoints."""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class TrainResponse(BaseModel):
    """Response schema for training endpoint."""

    status: str
    model_type: str
    features: List[str]
    label: str
    metrics: Dict[str, float]
    test_size: float


class PredictionRequest(BaseModel):
    """Request schema for prediction endpoint (JWT authenticated)."""

    # Accept dynamic feature values as a dictionary
    class Config:
        extra = "allow"


class PredictionResponse(BaseModel):
    """Response schema for prediction endpoint."""

    prediction: float


class ModelInfo(BaseModel):
    """Schema for model information."""

    model_name: str
    model_type: str
    features: List[str]
    label: str
    trained_at: datetime
    metrics: Optional[Dict[str, float]] = None

    class Config:
        from_attributes = True


class ModelsListResponse(BaseModel):
    """Response schema for listing all models."""

    models: List[ModelInfo]


class ModelMetricsResponse(BaseModel):
    """Response schema for model metrics endpoint."""

    model_name: str
    model_type: str
    metrics: Dict[str, float]
    trained_at: datetime
