from typing import List
from fastapi import HTTPException
from models.data_models import Product
from repos.products_repo import ProductRepo


class ProductService:
    def __init__(self, repo: ProductRepo):
        if isinstance(repo, str):
            repo = ProductRepo(repo)
        self.repo = repo

    # -------------------- CREATE (POST) --------------------
    async def create_product(self, product: Product) -> Product:
        await self.repo.init_db()
        if isinstance(product, dict):
            product = Product(**product)
        existing = await self.repo.get_product(product.id, product.categoryId)
        if existing:
            raise HTTPException(status_code=409, detail="Product already exists")

        await self.repo.insert_product(product)
        return product

    # -------------------- UPDATE (PUT) --------------------
    async def update_product(self, product: Product) -> Product:
        await self.repo.init_db()
        if isinstance(product, dict):
            product = Product(**product)
        updated_rows = await self.repo.update_product(product)
        if updated_rows == 0:
            raise HTTPException(status_code=404, detail="Product not found or not updated")
        return product

    # -------------------- GET --------------------
    async def get_product(self, product_id: str, category_id: str) -> Product:
        await self.repo.init_db()
        product = await self.repo.get_product(product_id, category_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    # -------------------- DELETE --------------------
    async def delete_product(self, product_id: str, category_id: str) -> bool:
        await self.repo.init_db()
        deleted = await self.repo.delete_product(product_id, category_id)
        if deleted == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        return True

    # -------------------- GET ALL / SEARCH --------------------
    async def get_products_by_query(self, query: str) -> List[Product]:
        await self.repo.init_db()
        # Currently ignoring query filtering
        return await self.repo.get_all_products()
