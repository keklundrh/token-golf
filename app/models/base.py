"""
Token Golf - SQLAlchemy Base Classes

Base configuration for all database models.
Using SQLAlchemy 2.0+ async style with declarative base.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


# Naming convention for constraints (helps with Alembic migrations)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    Provides common functionality and metadata configuration.
    """

    metadata = metadata

    def __repr__(self) -> str:
        """
        Default representation for models.

        Returns a string showing the model class and its primary key.
        """
        # Try to get an id attribute for representation
        id_str = ""
        if hasattr(self, "id"):
            id_str = f"id={self.id}"
        elif hasattr(self, "__table__"):
            # Get the first primary key column
            pk_cols = [col.name for col in self.__table__.primary_key.columns]
            if pk_cols:
                pk_values = [f"{col}={getattr(self, col)}" for col in pk_cols]
                id_str = ", ".join(pk_values)

        return f"<{self.__class__.__name__}({id_str})>"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert model instance to dictionary.

        Returns:
            Dictionary with column names as keys and values as values.
            Excludes SQLAlchemy internal attributes.
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


class TimestampMixin:
    """
    Mixin to add created_at and updated_at timestamps to models.

    Usage:
        class MyModel(Base, TimestampMixin):
            ...
    """

    created_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        nullable=False,
        comment="Timestamp when record was created",
    )

    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when record was last updated",
    )
