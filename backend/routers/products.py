"""
Product routes with role-based access control.

- GET endpoints: Public access
- POST/PUT/DELETE: Admin only
"""

from fastapi import APIRouter, status, Depends, HTTPException
from typing import List
from models.data_models import Product
from services.product_service import ProductService
from core.security import TokenData, get_current_user, require_admin

router = APIRouter()
product_service = ProductService("products.db")


# ============ Public Endpoints ============

@router.get("/", response_model=List[Product])
async def get_all_products(query: str = "SELECT * FROM c"):
    """
    Get all products or search with a query.
    Public access - no authentication required.
    """
    return await product_service.get_products_by_query(query)


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str, category_id: str):
    """
    Get a specific product by ID.
    Public access - no authentication required.
    """
    product = await product_service.get_product(product_id, category_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )
    return product


# ============ Protected Endpoints (Admin Only) ============

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: Product,
    current_user: TokenData = Depends(require_admin)
):
    """
    Create a new product.
    Admin access only.
    """
    await product_service.create_product(product)
    return product


@router.put("/", response_model=Product)
async def update_product(
    product: Product,
    current_user: TokenData = Depends(require_admin)
):
    """
    Update an existing product.
    Admin access only.
    """
    updated = await product_service.update_product(product)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or not updated"
        )
    return updated


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(
    product_id: str,
    category_id: str,
    current_user: TokenData = Depends(require_admin)
):
    """
    Delete a product.
    Admin access only.
    """
    await product_service.delete_product(product_id, category_id)
    return {"message": "Product deleted successfully", "product_id": product_id}
