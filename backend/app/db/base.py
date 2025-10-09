"""SQLAlchemy base configuration."""

from sqlalchemy.ext.declarative import declarative_base

# Create the declarative base
Base = declarative_base()

# Import all models here to ensure they are registered with Base
# This is important for Alembic migrations
from app.db.models import AnalysisHistory  # noqa: F401, E402
