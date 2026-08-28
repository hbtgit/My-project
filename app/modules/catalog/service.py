"""Business rules for the catalog. Routers stay thin; everything enforceable lives here."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError, ValidationFailedError
from app.modules.catalog.models import Category, Product
from app.modules.catalog.repository import CategoryRepository, ProductRepository
from app.modules.catalog.schemas import (
    CategoryCreate,
    CategoryUpdate,
    ProductCreate,
    ProductUpdate,
)


class CategoryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = CategoryRepository(db)

    def get(self, category_id: int) -> Category:
        category = self.repo.get(category_id)
        if category is None:
            raise NotFoundError("Category not found", category_id=category_id)
        return category

    def list(self, *, is_active: bool | None, limit: int, offset: int):
        return self.repo.list(is_active=is_active, limit=limit, offset=offset)

    def create(self, data: CategoryCreate) -> Category:
        self._ensure_name_free(data.name)
        category = self.repo.add(Category(name=data.name, description=data.description))
        _commit(self.db, "Category name already exists")
        return category

    def update(self, category_id: int, data: CategoryUpdate) -> Category:
        category = self.get(category_id)
        changes = data.model_dump(exclude_unset=True)
        if "name" in changes and changes["name"] is None:
            raise ValidationFailedError("Category name cannot be empty")
        if changes.get("name") and changes["name"].lower() != category.name.lower():
            self._ensure_name_free(changes["name"])
        for field, value in changes.items():
            setattr(category, field, value)
        _commit(self.db, "Category name already exists")
        return category

    def _ensure_name_free(self, name: str) -> None:
        if self.repo.get_by_name(name) is not None:
            raise ConflictError("Category name already exists", name=name)


class ProductService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ProductRepository(db)
        self.categories = CategoryRepository(db)

    def get(self, product_id: int) -> Product:
        product = self.repo.get(product_id)
        if product is None:
            raise NotFoundError("Product not found", product_id=product_id)
        return product

    def get_by_sku(self, sku: str) -> Product:
        product = self.repo.get_by_sku(sku.strip().upper())
        if product is None:
            raise NotFoundError("Product not found", sku=sku)
        return product

    def search(self, **filters):
        return self.repo.search(**filters)

    def create(self, data: ProductCreate) -> Product:
        # Business rule 1 / AT-01: every product must have a unique SKU.
        if self.repo.get_by_sku(data.sku) is not None:
            raise ConflictError("A product with this SKU already exists", sku=data.sku)
        if data.barcode:
            self._ensure_barcode_free(data.barcode)
        if data.category_id is not None:
            self._ensure_category_usable(data.category_id)

        product = self.repo.add(Product(**data.model_dump()))
        # The unique constraint is the final guard against concurrent duplicates.
        _commit(self.db, "A product with this SKU or barcode already exists")
        return product

    def update(self, product_id: int, data: ProductUpdate) -> Product:
        product = self.get(product_id)
        changes = data.model_dump(exclude_unset=True)
        for required in ("name", "unit_of_measure", "cost_price", "selling_price", "reorder_level"):
            if required in changes and changes[required] is None:
                raise ValidationFailedError(f"{required} cannot be null")
        if changes.get("barcode") and changes["barcode"] != product.barcode:
            self._ensure_barcode_free(changes["barcode"])
        if changes.get("category_id") is not None and changes["category_id"] != product.category_id:
            self._ensure_category_usable(changes["category_id"])
        for field, value in changes.items():
            setattr(product, field, value)
        _commit(self.db, "A product with this barcode already exists")
        return product

    def set_active(self, product_id: int, active: bool) -> Product:
        product = self.get(product_id)
        product.is_active = active
        _commit(self.db, "Could not update product status")
        return product

    def _ensure_barcode_free(self, barcode: str) -> None:
        if self.repo.get_by_barcode(barcode) is not None:
            raise ConflictError("A product with this barcode already exists", barcode=barcode)

    def _ensure_category_usable(self, category_id: int) -> None:
        category = self.categories.get(category_id)
        if category is None:
            raise ValidationFailedError("Category does not exist", category_id=category_id)
        if not category.is_active:
            raise ValidationFailedError("Category is inactive", category_id=category_id)


def _commit(db: Session, conflict_message: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(conflict_message) from exc
