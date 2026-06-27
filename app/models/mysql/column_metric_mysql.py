"""column_metric MySQL ORM model."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ColumnMetricMySQL(Base):
    __tablename__ = "column_metric"

    column_id: Mapped[str] = mapped_column(String(64), primary_key=True, comment="列编号")
    metric_id: Mapped[str] = mapped_column(String(64), primary_key=True, comment="指标编号")