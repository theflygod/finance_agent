"""ValueInfo ES document model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ValueInfoEs:
    id: str = ""
    value: str = ""
    type: str = ""
    column_id: str = ""
    column_name: str = ""
    table_id: str = ""
    table_name: str = ""