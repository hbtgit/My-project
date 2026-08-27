from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, Numeric, String, Text, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.models import TimestampMixin

MONEY = Numeric(12, 2)


class Category(TimestampMixin, Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())

    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Product(TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("cost_price >= 0", name="cost_price_non_negative"),
        CheckConstraint("selling_price >= 0", name="selling_price_non_negative"),
        CheckConstraint("reorder_level >= 0", name="reorder_level_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # Stored upper-cased so uniqueness is effectively case-insensitive (business rule 1).
    sku: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    barcode: Mapped[str | None] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), index=True
    )
    unit_of_measure: Mapped[str] = mapped_column(String(20), nullable=False, default="unit")
    cost_price: Mapped[Decimal] = mapped_column(MONEY, nullable=False, default=Decimal("0"))
    selling_price: Mapped[Decimal] = mapped_column(MONEY, nullable=False, default=Decimal("0"))
    reorder_level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Products are deactivated, never deleted, so history stays intact (FR-02).
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())

    category: Mapped[Category | None] = relationship(back_populates="products")
