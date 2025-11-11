from fastapi import APIRouter, status
from typing import List
from models.data_models import Product
from services.product_service import ProductService

router = APIRouter()
product_service = ProductService("products.db")

# -------------------- POST (Create) --------------------
@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product_endpoint(product: Product):
    await product_service.create_product(product)
    return product  # Return the created product

# -------------------- PUT (Update) --------------------
@router.put("/", response_model=Product, status_code=status.HTTP_200_OK)
async def update_product_endpoint(product: Product):
    updated_product = await product_service.update_product(product)
    if not updated_product:
        return {"message": "Product not found or not updated"}
    return updated_product

# -------------------- GET (Single Product) --------------------
@router.get("/{product_id}", response_model=Product)
async def get_product_endpoint(product_id: str, category_id: str):
    return await product_service.get_product(product_id, category_id)

# -------------------- DELETE --------------------
@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product_endpoint(product_id: str, category_id: str):
    await product_service.delete_product(product_id, category_id)
    return {"message": "Product deleted successfully"}

# -------------------- GET ALL / Search --------------------
@router.get("/", response_model=List[Product])
async def search_products_endpoint(query: str = "SELECT * FROM c"):
    return await product_service.get_products_by_query(query)
