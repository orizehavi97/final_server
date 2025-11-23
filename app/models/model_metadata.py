"""Model metadata for tracking trained ML models."""
from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from app.database import Base


class ModelMetadata(Base):
    """Table for storing metadata about trained models."""

    __tablename__ = "model_metadata"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, unique=True, index=True, nullable=False)
    model_type = Column(String, nullable=False)
    features = Column(JSON, nullable=False)
    label = Column(String, nullable=False)
    trained_at = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String, nullable=False)  # Path to .pkl file
    metrics = Column(JSON, nullable=True)
