from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Sku = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        to_upper=True,
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9._-]+$",
    ),
]
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Barcode = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]
Unit = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]
Money = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]


# Categories


class CategoryCreate(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
    description: str | None = None


class CategoryUpdate(BaseModel):
    name: (
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
        | None
    ) = None
    description: str | None = None
    is_active: bool | None = None


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


# Products


class ProductCreate(BaseModel):
    sku: Sku
    barcode: Barcode | None = None
    name: Name
    description: str | None = None
    category_id: int | None = None
    unit_of_measure: Unit = "unit"
    cost_price: Money = Decimal("0")
    selling_price: Money = Decimal("0")
    reorder_level: int = Field(0, ge=0)


class ProductUpdate(BaseModel):
    """Partial update. SKU is intentionally immutable once created."""

    barcode: Barcode | None = None
    name: Name | None = None
    description: str | None = None
    category_id: int | None = None
    unit_of_measure: Unit | None = None
    cost_price: Money | None = None
    selling_price: Money | None = None
    reorder_level: int | None = Field(None, ge=0)


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    barcode: str | None
    name: str
    description: str | None
    category_id: int | None
    unit_of_measure: str
    cost_price: Decimal
    selling_price: Decimal
    reorder_level: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
