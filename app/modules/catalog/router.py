from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.pagination import Page, PageParams, page_params
from app.modules.catalog.schemas import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    ProductCreate,
    ProductRead,
    ProductUpdate,
)
from app.modules.catalog.service import CategoryService, ProductService

router = APIRouter()

DB = Annotated[Session, Depends(get_db)]
Paging = Annotated[PageParams, Depends(page_params)]


# Categories


@router.get("/categories", response_model=Page[CategoryRead], tags=["categories"])
def list_categories(db: DB, paging: Paging, is_active: bool | None = None):
    items, total = CategoryService(db).list(
        is_active=is_active, limit=paging.limit, offset=paging.offset
    )
    return Page(items=items, total=total, limit=paging.limit, offset=paging.offset)


@router.post(
    "/categories",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    tags=["categories"],
)
def create_category(data: CategoryCreate, db: DB):
    return CategoryService(db).create(data)


@router.get("/categories/{category_id}", response_model=CategoryRead, tags=["categories"])
def get_category(category_id: int, db: DB):
    return CategoryService(db).get(category_id)


@router.patch("/categories/{category_id}", response_model=CategoryRead, tags=["categories"])
def update_category(category_id: int, data: CategoryUpdate, db: DB):
    return CategoryService(db).update(category_id, data)


# Products


@router.get("/products", response_model=Page[ProductRead], tags=["products"])
def list_products(
    db: DB,
    paging: Paging,
    q: Annotated[
        str | None, Query(max_length=100, description="Search name, SKU or barcode")
    ] = None,
    category_id: int | None = None,
    is_active: bool | None = None,
):
    items, total = ProductService(db).search(
        q=q,
        category_id=category_id,
        is_active=is_active,
        limit=paging.limit,
        offset=paging.offset,
    )
    return Page(items=items, total=total, limit=paging.limit, offset=paging.offset)


@router.post(
    "/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED, tags=["products"]
)
def create_product(data: ProductCreate, db: DB):
    return ProductService(db).create(data)


@router.get("/products/by-sku/{sku}", response_model=ProductRead, tags=["products"])
def get_product_by_sku(sku: str, db: DB):
    return ProductService(db).get_by_sku(sku)


@router.get("/products/{product_id}", response_model=ProductRead, tags=["products"])
def get_product(product_id: int, db: DB):
    return ProductService(db).get(product_id)


@router.patch("/products/{product_id}", response_model=ProductRead, tags=["products"])
def update_product(product_id: int, data: ProductUpdate, db: DB):
    return ProductService(db).update(product_id, data)


@router.post("/products/{product_id}/deactivate", response_model=ProductRead, tags=["products"])
def deactivate_product(product_id: int, db: DB):
    return ProductService(db).set_active(product_id, False)


@router.post("/products/{product_id}/activate", response_model=ProductRead, tags=["products"])
def activate_product(product_id: int, db: DB):
    return ProductService(db).set_active(product_id, True)
