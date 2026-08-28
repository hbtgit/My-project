from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.modules.catalog.models import Category, Product


class CategoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, category_id: int) -> Category | None:
        return self.db.get(Category, category_id)

    def get_by_name(self, name: str) -> Category | None:
        return self.db.scalar(select(Category).where(func.lower(Category.name) == name.lower()))

    def list(
        self, *, is_active: bool | None, limit: int, offset: int
    ) -> tuple[list[Category], int]:
        stmt = select(Category)
        if is_active is not None:
            stmt = stmt.where(Category.is_active == is_active)
        return _paginate(self.db, stmt.order_by(Category.name), limit, offset)

    def add(self, category: Category) -> Category:
        self.db.add(category)
        self.db.flush()
        return category


class ProductRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, product_id: int) -> Product | None:
        return self.db.get(Product, product_id)

    def get_by_sku(self, sku: str) -> Product | None:
        return self.db.scalar(select(Product).where(Product.sku == sku))

    def get_by_barcode(self, barcode: str) -> Product | None:
        return self.db.scalar(select(Product).where(Product.barcode == barcode))

    def search(
        self,
        *,
        q: str | None,
        category_id: int | None,
        is_active: bool | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Product], int]:
        stmt = select(Product)
        if q:
            pattern = f"%{q.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Product.name).like(pattern),
                    func.lower(Product.sku).like(pattern),
                    func.lower(Product.barcode).like(pattern),
                )
            )
        if category_id is not None:
            stmt = stmt.where(Product.category_id == category_id)
        if is_active is not None:
            stmt = stmt.where(Product.is_active == is_active)
        return _paginate(self.db, stmt.order_by(Product.name, Product.id), limit, offset)

    def add(self, product: Product) -> Product:
        self.db.add(product)
        self.db.flush()
        return product


def _paginate(db: Session, stmt: Select, limit: int, offset: int) -> tuple[list, int]:
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery()))
    items = list(db.scalars(stmt.limit(limit).offset(offset)))
    return items, total or 0
