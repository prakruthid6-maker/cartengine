import aiosqlite
from typing import List, Optional
from models.data_models import Product


class ProductRepo:
    def __init__(self, db_path: str = "backend/products.db"):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    categoryId TEXT,
                    description TEXT,
                    price REAL,
                    ratings REAL,
                    reviews REAL,
                    image TEXT,
                    badge TEXT
                )
            """)
            await db.commit()

    # -------------------- POST (Create) --------------------
    async def insert_product(self, product: Product) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO products (id, name, categoryId, description, price, ratings, reviews, image, badge)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product.id,
                product.name,
                product.categoryId,
                product.description,
                product.price,
                product.ratings,
                product.reviews,
                product.image,
                product.badge
            ))
            await db.commit()

    # -------------------- PUT (Update) --------------------
    async def update_product(self, product: Product) -> int:
        """Returns number of rows updated"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                UPDATE products
                SET name = ?, description = ?, price = ?, ratings = ?, reviews = ?, image = ?, badge = ?
                WHERE id = ? AND categoryId = ?
            """, (
                product.name,
                product.description,
                product.price,
                product.ratings,
                product.reviews,
                product.image,
                product.badge,
                product.id,
                product.categoryId
            ))
            await db.commit()
            return cursor.rowcount

    # -------------------- GET --------------------
    async def get_product(self, product_id: str, category_id: str) -> Optional[Product]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT id, name, categoryId, description, price, ratings, reviews, image, badge
                FROM products
                WHERE id = ? AND categoryId = ?
            """, (product_id, category_id))
            
            row = await cursor.fetchone()
            if not row:
                return None

            columns = [column[0] for column in cursor.description]
            data = dict(zip(columns, row))
            return Product(**data)

    # -------------------- DELETE --------------------
    async def delete_product(self, product_id: str, category_id: str) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                DELETE FROM products WHERE id = ? AND categoryId = ?
            """, (product_id, category_id))
            await db.commit()
            return cursor.rowcount

    # -------------------- GET ALL --------------------
    async def get_all_products(self) -> List[Product]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT id, name, categoryId, description, price, ratings, reviews, image, badge
                FROM products
            """)
            rows = await cursor.fetchall()
            products = [
                Product(
                    id=row[0],
                    name=row[1],
                    categoryId=row[2],
                    description=row[3],
                    price=row[4],
                    ratings=row[5],
                    reviews=row[6],
                    image=row[7],
                    badge=row[8]
                )
                for row in rows
            ]
            return products
