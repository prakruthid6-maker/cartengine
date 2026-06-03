import aiosqlite
from typing import List, Optional
from models.data_models import Product, Seller, Order, Payment, OrderTracking, Wishlist, Review, Coupon, CartItem, Cart
import os
import json
import uuid
from datetime import datetime

# Optional Firebase SDK Imports
try:
    from google.oauth2 import service_account
    from google.cloud import firestore
    HAS_FIRESTORE = True
except ImportError:
    HAS_FIRESTORE = False

# Optional PostgreSQL SDK Imports
try:
    import asyncpg
    HAS_ASYNCPG = True
except ImportError:
    HAS_ASYNCPG = False


# =====================================================================
# Database Helpers for PostgreSQL DateTime Conversions
# =====================================================================

def format_row(row) -> Optional[dict]:
    if row is None:
        return None
    d = dict(row)
    for k, v in d.items():
        if isinstance(v, datetime):
            d[k] = v.isoformat()
    return d

def format_rows(rows) -> List[dict]:
    return [format_row(row) for row in rows]


# =====================================================================
# PostgreSQL / Supabase Implementation
# =====================================================================

class PostgresProductRepo:
    def __init__(self, db_url: str):
        # asyncpg requires postgresql:// format
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        self.db_url = db_url
        self._pool = None

    async def _get_pool(self):
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self.db_url)
        return self._pool

    async def init_db(self):
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            # Enforce case sensitivity by using double quotes around categoryId
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    "categoryId" TEXT,
                    description TEXT,
                    price DOUBLE PRECISION,
                    ratings DOUBLE PRECISION,
                    reviews DOUBLE PRECISION,
                    image TEXT,
                    badge TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    seller_id TEXT,
                    stock_quantity INTEGER DEFAULT 100,
                    discount_percent DOUBLE PRECISION DEFAULT 0,
                    original_price DOUBLE PRECISION,
                    sku TEXT,
                    specifications TEXT
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS sellers (
                    seller_id TEXT PRIMARY KEY,
                    name TEXT,
                    location TEXT,
                    rating DOUBLE PRECISION
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    product_id TEXT,
                    user_id TEXT,
                    quantity INTEGER,
                    total_price DOUBLE PRECISION,
                    status TEXT,
                    delivery_address TEXT,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id TEXT PRIMARY KEY,
                    order_id TEXT,
                    amount DOUBLE PRECISION,
                    method TEXT,
                    status TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS order_tracking (
                    tracking_id TEXT PRIMARY KEY,
                    order_id TEXT,
                    status TEXT,
                    location TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS wishlist (
                    wishlist_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    product_id TEXT,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    review_id TEXT PRIMARY KEY,
                    product_id TEXT,
                    user_id TEXT,
                    rating DOUBLE PRECISION,
                    comment TEXT,
                    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS coupons (
                    coupon_code TEXT PRIMARY KEY,
                    discount_percent DOUBLE PRECISION,
                    expiry_date TEXT,
                    status TEXT
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS cart (
                    cart_item_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    product_id TEXT,
                    quantity INTEGER DEFAULT 1,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, product_id)
                )
            """)

    # -------------------- PRODUCTS --------------------
    async def insert_product(self, product: Product) -> None:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO products (id, name, "categoryId", description, price, ratings, reviews, image, badge, seller_id, stock_quantity, discount_percent, original_price, sku, specifications)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                ON CONFLICT (id) DO NOTHING
            """, product.id, product.name, product.categoryId, product.description, product.price, product.ratings, product.reviews, product.image, product.badge, product.seller_id, product.stock_quantity, product.discount_percent, product.original_price, product.sku, product.specifications)

    async def update_product(self, product: Product) -> int:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE products
                SET name = $1, description = $2, price = $3, ratings = $4, reviews = $5, image = $6, badge = $7, seller_id = $8, stock_quantity = $9, discount_percent = $10, original_price = $11, sku = $12, specifications = $13
                WHERE id = $14 AND "categoryId" = $15
            """, product.name, product.description, product.price, product.ratings, product.reviews, product.image, product.badge, product.seller_id, product.stock_quantity, product.discount_percent, product.original_price, product.sku, product.specifications, product.id, product.categoryId)
            if result.startswith("UPDATE "):
                return int(result.split(" ")[1])
            return 0

    async def get_product(self, product_id: str, category_id: str) -> Optional[Product]:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT id, name, "categoryId", description, price, ratings, reviews, image, badge, created_at, seller_id, stock_quantity, discount_percent, original_price, sku, specifications
                FROM products
                WHERE id = $1 AND "categoryId" = $2
            """, product_id, category_id)
            if row:
                return Product(**format_row(row))
            return None

    async def delete_product(self, product_id: str, category_id: str) -> int:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute("""
                DELETE FROM products WHERE id = $1 AND "categoryId" = $2
            """, product_id, category_id)
            if result.startswith("DELETE "):
                return int(result.split(" ")[1])
            return 0

    async def get_all_products(self) -> List[Product]:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, name, "categoryId", description, price, ratings, reviews, image, badge, created_at, seller_id, stock_quantity, discount_percent, original_price, sku, specifications
                FROM products
            """)
            return [Product(**format_row(row)) for row in rows]

    # -------------------- SELLERS --------------------
    async def insert_seller(self, seller: Seller) -> None:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO sellers (seller_id, name, location, rating)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (seller_id) DO NOTHING
            """, seller.seller_id, seller.name, seller.location, seller.rating)

    async def get_all_sellers(self) -> List[Seller]:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT seller_id, name, location, rating FROM sellers")
            return [Seller(**format_row(row)) for row in rows]

    # -------------------- ORDERS --------------------
    async def insert_order(self, order: Order) -> None:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO orders (order_id, product_id, user_id, quantity, total_price, status, delivery_address)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (order_id) DO NOTHING
            """, order.order_id, order.product_id, order.user_id, order.quantity, order.total_price, order.status, order.delivery_address)

    async def get_order(self, order_id: str) -> Optional[Order]:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT order_id, product_id, user_id, quantity, total_price, status, delivery_address, order_date
                FROM orders WHERE order_id = $1
            """, order_id)
            if row:
                return Order(**format_row(row))
            return None

    async def get_user_orders(self, user_id: str) -> List[Order]:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT order_id, product_id, user_id, quantity, total_price, status, delivery_address, order_date
                FROM orders WHERE user_id = $1 ORDER BY order_date DESC
            """, user_id)
            return [Order(**format_row(row)) for row in rows]

    async def update_order_status(self, order_id: str, status: str) -> int:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE orders SET status = $1 WHERE order_id = $2
            """, status, order_id)
            if result.startswith("UPDATE "):
                return int(result.split(" ")[1])
            return 0

    # -------------------- PAYMENTS --------------------
    async def insert_payment(self, payment: Payment) -> None:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO payments (payment_id, order_id, amount, method, status)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (payment_id) DO NOTHING
            """, payment.payment_id, payment.order_id, payment.amount, payment.method, payment.status)

    async def get_payment(self, order_id: str) -> Optional[Payment]:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT payment_id, order_id, amount, method, status, timestamp
                FROM payments WHERE order_id = $1
            """, order_id)
            if row:
                return Payment(**format_row(row))
            return None

    # -------------------- ORDER TRACKING --------------------
    async def insert_tracking(self, tracking: OrderTracking) -> None:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO order_tracking (tracking_id, order_id, status, location)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (tracking_id) DO NOTHING
            """, tracking.tracking_id, tracking.order_id, tracking.status, tracking.location)

    async def get_tracking_history(self, order_id: str) -> List[OrderTracking]:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT tracking_id, order_id, status, location, timestamp
                FROM order_tracking WHERE order_id = $1 ORDER BY timestamp DESC
            """, order_id)
            return [OrderTracking(**format_row(row)) for row in rows]

    # -------------------- WISHLIST --------------------
    async def add_to_wishlist(self, wishlist: Wishlist) -> None:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO wishlist (wishlist_id, user_id, product_id)
                VALUES ($1, $2, $3)
                ON CONFLICT (wishlist_id) DO NOTHING
            """, wishlist.wishlist_id, wishlist.user_id, wishlist.product_id)

    async def get_wishlist(self, user_id: str) -> List[Wishlist]:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT wishlist_id, user_id, product_id, added_date
                FROM wishlist WHERE user_id = $1
            """, user_id)
            return [Wishlist(**format_row(row)) for row in rows]

    async def remove_from_wishlist(self, user_id: str, product_id: str) -> int:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute("""
                DELETE FROM wishlist WHERE user_id = $1 AND product_id = $2
            """, user_id, product_id)
            if result.startswith("DELETE "):
                return int(result.split(" ")[1])
            return 0

    # -------------------- REVIEWS --------------------
    async def add_review(self, review: Review) -> None:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO reviews (review_id, product_id, user_id, rating, comment)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (review_id) DO NOTHING
            """, review.review_id, review.product_id, review.user_id, review.rating, review.comment)

    async def get_product_reviews(self, product_id: str) -> List[Review]:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT review_id, product_id, user_id, rating, comment, review_date
                FROM reviews WHERE product_id = $1 ORDER BY review_date DESC
            """, product_id)
            return [Review(**format_row(row)) for row in rows]

    # -------------------- COUPONS --------------------
    async def insert_coupon(self, coupon: Coupon) -> None:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO coupons (coupon_code, discount_percent, expiry_date, status)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (coupon_code) DO NOTHING
            """, coupon.coupon_code, coupon.discount_percent, coupon.expiry_date, coupon.status)

    async def get_coupon(self, coupon_code: str) -> Optional[Coupon]:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT coupon_code, discount_percent, expiry_date, status
                FROM coupons WHERE coupon_code = $1
            """, coupon_code)
            if row:
                return Coupon(**format_row(row))
            return None

    # -------------------- CART --------------------
    async def add_to_cart(self, cart_item: CartItem) -> None:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO cart (cart_item_id, user_id, product_id, quantity)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (user_id, product_id)
                DO UPDATE SET quantity = cart.quantity + EXCLUDED.quantity
            """, cart_item.cart_item_id, cart_item.user_id, cart_item.product_id, cart_item.quantity)

    async def get_cart(self, user_id: str) -> List[CartItem]:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT c.cart_item_id, c.user_id, c.product_id, c.quantity, c.added_at,
                       p.name, p.price, p.image, p.stock_quantity, p.discount_percent
                FROM cart c
                LEFT JOIN products p ON c.product_id = p.id
                WHERE c.user_id = $1
                ORDER BY c.added_at DESC
            """, user_id)
            items = []
            for row in rows:
                p_dict = format_row(row)
                price = p_dict.get("price") or 0.0
                discount = p_dict.get("discount_percent") or 0.0
                final_price = price * (1 - discount / 100)
                items.append(CartItem(
                    cart_item_id=p_dict["cart_item_id"],
                    user_id=p_dict["user_id"],
                    product_id=p_dict["product_id"],
                    quantity=p_dict["quantity"],
                    added_at=p_dict["added_at"],
                    product_name=p_dict["name"],
                    product_price=round(final_price, 2),
                    product_image=p_dict["image"]
                ))
            return items

    async def update_cart_quantity(self, user_id: str, product_id: str, quantity: int) -> int:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            if quantity <= 0:
                result = await conn.execute("""
                    DELETE FROM cart WHERE user_id = $1 AND product_id = $2
                """, user_id, product_id)
                if result.startswith("DELETE "):
                    return int(result.split(" ")[1])
            else:
                result = await conn.execute("""
                    UPDATE cart SET quantity = $1 WHERE user_id = $2 AND product_id = $3
                """, quantity, user_id, product_id)
                if result.startswith("UPDATE "):
                    return int(result.split(" ")[1])
            return 0

    async def remove_from_cart(self, user_id: str, product_id: str) -> int:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute("""
                DELETE FROM cart WHERE user_id = $1 AND product_id = $2
            """, user_id, product_id)
            if result.startswith("DELETE "):
                return int(result.split(" ")[1])
            return 0

    async def clear_cart(self, user_id: str) -> int:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute("""
                DELETE FROM cart WHERE user_id = $1
            """, user_id)
            if result.startswith("DELETE "):
                return int(result.split(" ")[1])
            return 0

    # -------------------- INVENTORY / STOCK / DISCOUNT --------------------
    async def update_stock(self, product_id: str, quantity_change: int) -> bool:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE products 
                SET stock_quantity = stock_quantity + $1 
                WHERE id = $2 AND stock_quantity + $1 >= 0
            """, quantity_change, product_id)
            if result.startswith("UPDATE "):
                return int(result.split(" ")[1]) > 0
            return False

    async def check_stock(self, product_id: str) -> dict:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT stock_quantity, name FROM products WHERE id = $1", product_id)
            if not row:
                return {"available": False, "quantity": 0, "message": "Product not found"}
            data = format_row(row)
            stock = data.get("stock_quantity") or 0
            return {
                "available": stock > 0,
                "quantity": stock,
                "product_name": data.get("name", "Unknown Product"),
                "message": "In stock" if stock > 0 else "Out of stock"
            }

    async def set_discount(self, product_id: str, discount_percent: float) -> bool:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT price, original_price FROM products WHERE id = $1", product_id)
            if not row:
                return False
            data = format_row(row)
            current_price = data.get("price") or 0.0
            original_price = data.get("original_price") or current_price
            new_price = original_price * (1 - discount_percent / 100)
            
            result = await conn.execute("""
                UPDATE products 
                SET price = $1, discount_percent = $2, original_price = $3 
                WHERE id = $4
            """, round(new_price, 2), discount_percent, original_price, product_id)
            if result.startswith("UPDATE "):
                return int(result.split(" ")[1]) > 0
            return False

    async def get_discounted_products(self) -> List[Product]:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, name, "categoryId", description, price, ratings, reviews, image, badge, created_at, seller_id, stock_quantity, discount_percent, original_price, sku, specifications
                FROM products 
                WHERE discount_percent > 0
                ORDER BY discount_percent DESC
            """)
            return [Product(**format_row(row)) for row in rows]


# =====================================================================
# Firebase / Firestore Implementation
# =====================================================================

class FirestoreProductRepo:
    def __init__(self):
        creds_json = os.getenv("FIREBASE_CREDENTIALS")
        if creds_json:
            try:
                creds_dict = json.loads(creds_json)
                creds = service_account.Credentials.from_service_account_info(creds_dict)
                self.db = firestore.AsyncClient(project=creds_dict.get("project_id"), credentials=creds)
            except Exception as e:
                print(f"Warning: Failed to load Firebase credentials JSON: {e}")
                self.db = firestore.AsyncClient()
        else:
            self.db = firestore.AsyncClient()

    async def init_db(self):
        # Firestore does not require tables creation
        pass

    # -------------------- PRODUCTS --------------------
    async def insert_product(self, product: Product) -> None:
        doc_ref = self.db.collection("products").document(product.id)
        if not product.created_at:
            product.created_at = datetime.utcnow().isoformat() + "Z"
        await doc_ref.set(product.model_dump())

    async def update_product(self, product: Product) -> int:
        doc_ref = self.db.collection("products").document(product.id)
        doc = await doc_ref.get()
        if doc.exists:
            await doc_ref.set(product.model_dump())
            return 1
        return 0

    async def get_product(self, product_id: str, category_id: str) -> Optional[Product]:
        doc = await self.db.collection("products").document(product_id).get()
        if doc.exists:
            data = doc.to_dict()
            if data.get("categoryId") == category_id:
                return Product(**data)
        return None

    async def delete_product(self, product_id: str, category_id: str) -> int:
        doc_ref = self.db.collection("products").document(product_id)
        doc = await doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            if data.get("categoryId") == category_id:
                await doc_ref.delete()
                return 1
        return 0

    async def get_all_products(self) -> List[Product]:
        docs = self.db.collection("products").stream()
        products = []
        async for doc in docs:
            products.append(Product(**doc.to_dict()))
        return products

    # -------------------- SELLERS --------------------
    async def insert_seller(self, seller: Seller) -> None:
        await self.db.collection("sellers").document(seller.seller_id).set(seller.model_dump())

    async def get_all_sellers(self) -> List[Seller]:
        docs = self.db.collection("sellers").stream()
        sellers = []
        async for doc in docs:
            sellers.append(Seller(**doc.to_dict()))
        return sellers

    # -------------------- ORDERS --------------------
    async def insert_order(self, order: Order) -> None:
        if not order.order_date:
            order.order_date = datetime.utcnow().isoformat() + "Z"
        await self.db.collection("orders").document(order.order_id).set(order.model_dump())

    async def get_order(self, order_id: str) -> Optional[Order]:
        doc = await self.db.collection("orders").document(order_id).get()
        if doc.exists:
            return Order(**doc.to_dict())
        return None

    async def get_user_orders(self, user_id: str) -> List[Order]:
        query = self.db.collection("orders").where(filter=firestore.FieldFilter("user_id", "==", user_id))
        docs = query.stream()
        orders = []
        async for doc in docs:
            orders.append(Order(**doc.to_dict()))
        orders.sort(key=lambda o: o.order_date or "", reverse=True)
        return orders

    async def update_order_status(self, order_id: str, status: str) -> int:
        doc_ref = self.db.collection("orders").document(order_id)
        doc = await doc_ref.get()
        if doc.exists:
            await doc_ref.update({"status": status})
            return 1
        return 0

    # -------------------- PAYMENTS --------------------
    async def insert_payment(self, payment: Payment) -> None:
        if not payment.timestamp:
            payment.timestamp = datetime.utcnow().isoformat() + "Z"
        await self.db.collection("payments").document(payment.payment_id).set(payment.model_dump())

    async def get_payment(self, order_id: str) -> Optional[Payment]:
        query = self.db.collection("payments").where(filter=firestore.FieldFilter("order_id", "==", order_id)).limit(1)
        docs = query.stream()
        async for doc in docs:
            return Payment(**doc.to_dict())
        return None

    # -------------------- ORDER TRACKING --------------------
    async def insert_tracking(self, tracking: OrderTracking) -> None:
        if not tracking.timestamp:
            tracking.timestamp = datetime.utcnow().isoformat() + "Z"
        await self.db.collection("order_tracking").document(tracking.tracking_id).set(tracking.model_dump())

    async def get_tracking_history(self, order_id: str) -> List[OrderTracking]:
        query = self.db.collection("order_tracking").where(filter=firestore.FieldFilter("order_id", "==", order_id))
        docs = query.stream()
        history = []
        async for doc in docs:
            history.append(OrderTracking(**doc.to_dict()))
        history.sort(key=lambda t: t.timestamp or "", reverse=True)
        return history

    # -------------------- WISHLIST --------------------
    async def add_to_wishlist(self, wishlist: Wishlist) -> None:
        if not wishlist.added_date:
            wishlist.added_date = datetime.utcnow().isoformat() + "Z"
        await self.db.collection("wishlist").document(wishlist.wishlist_id).set(wishlist.model_dump())

    async def get_wishlist(self, user_id: str) -> List[Wishlist]:
        query = self.db.collection("wishlist").where(filter=firestore.FieldFilter("user_id", "==", user_id))
        docs = query.stream()
        wishlist = []
        async for doc in docs:
            wishlist.append(Wishlist(**doc.to_dict()))
        return wishlist

    async def remove_from_wishlist(self, user_id: str, product_id: str) -> int:
        query = self.db.collection("wishlist")\
            .where(filter=firestore.FieldFilter("user_id", "==", user_id))\
            .where(filter=firestore.FieldFilter("product_id", "==", product_id))
        docs = query.stream()
        count = 0
        async for doc in docs:
            await doc.reference.delete()
            count += 1
        return count

    # -------------------- REVIEWS --------------------
    async def add_review(self, review: Review) -> None:
        if not review.review_date:
            review.review_date = datetime.utcnow().isoformat() + "Z"
        await self.db.collection("reviews").document(review.review_id).set(review.model_dump())

    async def get_product_reviews(self, product_id: str) -> List[Review]:
        query = self.db.collection("reviews").where(filter=firestore.FieldFilter("product_id", "==", product_id))
        docs = query.stream()
        reviews = []
        async for doc in docs:
            reviews.append(Review(**doc.to_dict()))
        reviews.sort(key=lambda r: r.review_date or "", reverse=True)
        return reviews

    # -------------------- COUPONS --------------------
    async def insert_coupon(self, coupon: Coupon) -> None:
        await self.db.collection("coupons").document(coupon.coupon_code).set(coupon.model_dump())

    async def get_coupon(self, coupon_code: str) -> Optional[Coupon]:
        doc = await self.db.collection("coupons").document(coupon_code).get()
        if doc.exists:
            return Coupon(**doc.to_dict())
        return None

    # -------------------- CART --------------------
    async def add_to_cart(self, cart_item: CartItem) -> None:
        query = self.db.collection("cart")\
            .where(filter=firestore.FieldFilter("user_id", "==", cart_item.user_id))\
            .where(filter=firestore.FieldFilter("product_id", "==", cart_item.product_id))\
            .limit(1)
        docs = query.stream()
        existing = None
        async for doc in docs:
            existing = doc
            break

        if existing:
            new_quantity = existing.to_dict().get("quantity", 0) + cart_item.quantity
            await existing.reference.update({"quantity": new_quantity})
        else:
            if not cart_item.added_at:
                cart_item.added_at = datetime.utcnow().isoformat() + "Z"
            await self.db.collection("cart").document(cart_item.cart_item_id).set(cart_item.model_dump())

    async def get_cart(self, user_id: str) -> List[CartItem]:
        query = self.db.collection("cart").where(filter=firestore.FieldFilter("user_id", "==", user_id))
        docs = query.stream()
        items = []
        async for doc in docs:
            items.append(CartItem(**doc.to_dict()))

        for item in items:
            p_doc = await self.db.collection("products").document(item.product_id).get()
            if p_doc.exists:
                p_data = p_doc.to_dict()
                item.product_name = p_data.get("name")
                price = p_data.get("price") or 0.0
                discount = p_data.get("discount_percent") or 0.0
                item.product_price = round(price * (1 - discount / 100), 2)
                item.product_image = p_data.get("image")
        
        items.sort(key=lambda c: c.added_at or "", reverse=True)
        return items

    async def update_cart_quantity(self, user_id: str, product_id: str, quantity: int) -> int:
        query = self.db.collection("cart")\
            .where(filter=firestore.FieldFilter("user_id", "==", user_id))\
            .where(filter=firestore.FieldFilter("product_id", "==", product_id))\
            .limit(1)
        docs = query.stream()
        existing = None
        async for doc in docs:
            existing = doc
            break

        if existing:
            if quantity <= 0:
                await existing.reference.delete()
            else:
                await existing.reference.update({"quantity": quantity})
            return 1
        return 0

    async def remove_from_cart(self, user_id: str, product_id: str) -> int:
        query = self.db.collection("cart")\
            .where(filter=firestore.FieldFilter("user_id", "==", user_id))\
            .where(filter=firestore.FieldFilter("product_id", "==", product_id))
        docs = query.stream()
        count = 0
        async for doc in docs:
            await doc.reference.delete()
            count += 1
        return count

    async def clear_cart(self, user_id: str) -> int:
        query = self.db.collection("cart").where(filter=firestore.FieldFilter("user_id", "==", user_id))
        docs = query.stream()
        count = 0
        async for doc in docs:
            await doc.reference.delete()
            count += 1
        return count

    # -------------------- INVENTORY OPERATIONS --------------------
    async def update_stock(self, product_id: str, quantity_change: int) -> bool:
        doc_ref = self.db.collection("products").document(product_id)
        doc = await doc_ref.get()
        if not doc.exists:
            return False
        data = doc.to_dict()
        current = data.get("stock_quantity") or 0
        new_val = current + quantity_change
        if new_val < 0:
            return False
        await doc_ref.update({"stock_quantity": new_val})
        return True

    async def check_stock(self, product_id: str) -> dict:
        doc = await self.db.collection("products").document(product_id).get()
        if not doc.exists:
            return {"available": False, "quantity": 0, "message": "Product not found"}
        data = doc.to_dict()
        stock = data.get("stock_quantity") or 0
        return {
            "available": stock > 0,
            "quantity": stock,
            "product_name": data.get("name", "Unknown Product"),
            "message": "In stock" if stock > 0 else "Out of stock"
        }

    async def set_discount(self, product_id: str, discount_percent: float) -> bool:
        doc_ref = self.db.collection("products").document(product_id)
        doc = await doc_ref.get()
        if not doc.exists:
            return False
        data = doc.to_dict()
        current_price = data.get("price") or 0.0
        original_price = data.get("original_price") or current_price
        new_price = original_price * (1 - discount_percent / 100)
        await doc_ref.update({
            "price": round(new_price, 2),
            "discount_percent": discount_percent,
            "original_price": original_price
        })
        return True

    async def get_discounted_products(self) -> List[Product]:
        query = self.db.collection("products").where(filter=firestore.FieldFilter("discount_percent", ">", 0))
        docs = query.stream()
        products = []
        async for doc in docs:
            products.append(Product(**doc.to_dict()))
        products.sort(key=lambda p: p.discount_percent or 0.0, reverse=True)
        return products


# =====================================================================
# SQLite Implementation
# =====================================================================

class SQLiteProductRepo:
    def __init__(self, db_path: str = "products.db"):
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
                    badge TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    seller_id TEXT,
                    stock_quantity INTEGER DEFAULT 100,
                    discount_percent REAL DEFAULT 0,
                    original_price REAL,
                    sku TEXT,
                    specifications TEXT
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sellers (
                    seller_id TEXT PRIMARY KEY,
                    name TEXT,
                    location TEXT,
                    rating REAL
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    product_id TEXT,
                    user_id TEXT,
                    quantity INTEGER,
                    total_price REAL,
                    status TEXT,
                    delivery_address TEXT,
                    order_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id TEXT PRIMARY KEY,
                    order_id TEXT,
                    amount REAL,
                    method TEXT,
                    status TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS order_tracking (
                    tracking_id TEXT PRIMARY KEY,
                    order_id TEXT,
                    status TEXT,
                    location TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS wishlist (
                    wishlist_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    product_id TEXT,
                    added_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    review_id TEXT PRIMARY KEY,
                    product_id TEXT,
                    user_id TEXT,
                    rating REAL,
                    comment TEXT,
                    review_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS coupons (
                    coupon_code TEXT PRIMARY KEY,
                    discount_percent REAL,
                    expiry_date TEXT,
                    status TEXT
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS cart (
                    cart_item_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    product_id TEXT,
                    quantity INTEGER DEFAULT 1,
                    added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, product_id)
                )
            """)
            try:
                await db.execute("ALTER TABLE products ADD COLUMN stock_quantity INTEGER DEFAULT 100")
            except:
                pass
            try:
                await db.execute("ALTER TABLE products ADD COLUMN discount_percent REAL DEFAULT 0")
            except:
                pass
            try:
                await db.execute("ALTER TABLE products ADD COLUMN original_price REAL")
            except:
                pass
            await db.commit()

    # -------------------- POST (Create) --------------------
    async def insert_product(self, product: Product) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO products (id, name, categoryId, description, price, ratings, reviews, image, badge, created_at, seller_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
            """, (
                product.id,
                product.name,
                product.categoryId,
                product.description,
                product.price,
                product.ratings,
                product.reviews,
                product.image,
                product.badge,
                product.seller_id
            ))
            await db.commit()

    # -------------------- PUT (Update) --------------------
    async def update_product(self, product: Product) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                UPDATE products
                SET name = ?, description = ?, price = ?, ratings = ?, reviews = ?, image = ?, badge = ?, seller_id = ?
                WHERE id = ? AND categoryId = ?
            """, (
                product.name,
                product.description,
                product.price,
                product.ratings,
                product.reviews,
                product.image,
                product.badge,
                product.seller_id,
                product.id,
                product.categoryId
            ))
            await db.commit()
            return cursor.rowcount

    # -------------------- GET --------------------
    async def get_product(self, product_id: str, category_id: str) -> Optional[Product]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT id, name, categoryId, description, price, ratings, reviews, image, badge, created_at, seller_id
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
                SELECT id, name, categoryId, description, price, ratings, reviews, image, badge, created_at, seller_id
                FROM products
            """)
            rows = await cursor.fetchall()
            return [
                Product(
                    id=row[0], name=row[1], categoryId=row[2], description=row[3],
                    price=row[4], ratings=row[5], reviews=row[6], image=row[7],
                    badge=row[8], created_at=row[9], seller_id=row[10]
                )
                for row in rows
            ]

    # -------------------- SELLERS --------------------
    async def insert_seller(self, seller: Seller) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO sellers (seller_id, name, location, rating)
                VALUES (?, ?, ?, ?)
            """, (seller.seller_id, seller.name, seller.location, seller.rating))
            await db.commit()

    async def get_all_sellers(self) -> List[Seller]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT seller_id, name, location, rating FROM sellers")
            rows = await cursor.fetchall()
            return [Seller(seller_id=row[0], name=row[1], location=row[2], rating=row[3]) for row in rows]

    # -------------------- ORDERS --------------------
    async def insert_order(self, order: Order) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO orders (order_id, product_id, user_id, quantity, total_price, status, delivery_address, order_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (order.order_id, order.product_id, order.user_id, order.quantity, order.total_price, order.status, order.delivery_address))
            await db.commit()

    async def get_order(self, order_id: str) -> Optional[Order]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT order_id, product_id, user_id, quantity, total_price, status, delivery_address, order_date FROM orders WHERE order_id = ?", (order_id,))
            row = await cursor.fetchone()
            if not row:
                return None
            return Order(order_id=row[0], product_id=row[1], user_id=row[2], quantity=row[3], total_price=row[4], status=row[5], delivery_address=row[6], order_date=row[7])

    async def get_user_orders(self, user_id: str) -> List[Order]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT order_id, product_id, user_id, quantity, total_price, status, delivery_address, order_date FROM orders WHERE user_id = ? ORDER BY order_date DESC", (user_id,))
            rows = await cursor.fetchall()
            return [Order(order_id=row[0], product_id=row[1], user_id=row[2], quantity=row[3], total_price=row[4], status=row[5], delivery_address=row[6], order_date=row[7]) for row in rows]

    async def update_order_status(self, order_id: str, status: str) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))
            await db.commit()
            return cursor.rowcount

    # -------------------- PAYMENTS --------------------
    async def insert_payment(self, payment: Payment) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO payments (payment_id, order_id, amount, method, status, timestamp)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (payment.payment_id, payment.order_id, payment.amount, payment.method, payment.status))
            await db.commit()

    async def get_payment(self, order_id: str) -> Optional[Payment]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT payment_id, order_id, amount, method, status, timestamp FROM payments WHERE order_id = ?", (order_id,))
            row = await cursor.fetchone()
            if not row:
                return None
            return Payment(payment_id=row[0], order_id=row[1], amount=row[2], method=row[3], status=row[4], timestamp=row[5])

    # -------------------- TRACKING --------------------
    async def insert_tracking(self, tracking: OrderTracking) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO order_tracking (tracking_id, order_id, status, location, timestamp)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (tracking.tracking_id, tracking.order_id, tracking.status, tracking.location))
            await db.commit()

    async def get_tracking_history(self, order_id: str) -> List[OrderTracking]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT tracking_id, order_id, status, location, timestamp FROM order_tracking WHERE order_id = ? ORDER BY timestamp DESC", (order_id,))
            rows = await cursor.fetchall()
            return [OrderTracking(tracking_id=row[0], order_id=row[1], status=row[2], location=row[3], timestamp=row[4]) for row in rows]

    # -------------------- WISHLIST --------------------
    async def add_to_wishlist(self, wishlist: Wishlist) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO wishlist (wishlist_id, user_id, product_id, added_date) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", (wishlist.wishlist_id, wishlist.user_id, wishlist.product_id))
            await db.commit()

    async def get_wishlist(self, user_id: str) -> List[Wishlist]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT wishlist_id, user_id, product_id, added_date FROM wishlist WHERE user_id = ?", (user_id,))
            rows = await cursor.fetchall()
            return [Wishlist(wishlist_id=row[0], user_id=row[1], product_id=row[2], added_date=row[3]) for row in rows]

    async def remove_from_wishlist(self, user_id: str, product_id: str) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM wishlist WHERE user_id = ? AND product_id = ?", (user_id, product_id))
            await db.commit()
            return cursor.rowcount

    # -------------------- REVIEWS --------------------
    async def add_review(self, review: Review) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO reviews (review_id, product_id, user_id, rating, comment, review_date) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", (review.review_id, review.product_id, review.user_id, review.rating, review.comment))
            await db.commit()

    async def get_product_reviews(self, product_id: str) -> List[Review]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT review_id, product_id, user_id, rating, comment, review_date FROM reviews WHERE product_id = ? ORDER BY review_date DESC", (product_id,))
            rows = await cursor.fetchall()
            return [Review(review_id=row[0], product_id=row[1], user_id=row[2], rating=row[3], comment=row[4], review_date=row[5]) for row in rows]

    # -------------------- COUPONS --------------------
    async def insert_coupon(self, coupon: Coupon) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO coupons (coupon_code, discount_percent, expiry_date, status) VALUES (?, ?, ?, ?)", (coupon.coupon_code, coupon.discount_percent, coupon.expiry_date, coupon.status))
            await db.commit()

    async def get_coupon(self, coupon_code: str) -> Optional[Coupon]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT coupon_code, discount_percent, expiry_date, status FROM coupons WHERE coupon_code = ?", (coupon_code,))
            row = await cursor.fetchone()
            if not row:
                return None
            return Coupon(coupon_code=row[0], discount_percent=row[1], expiry_date=row[2], status=row[3])

    # -------------------- CART --------------------
    async def add_to_cart(self, cart_item: CartItem) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT cart_item_id, quantity FROM cart WHERE user_id = ? AND product_id = ?",
                (cart_item.user_id, cart_item.product_id)
            )
            existing = await cursor.fetchone()
            if existing:
                new_quantity = existing[1] + cart_item.quantity
                await db.execute("UPDATE cart SET quantity = ? WHERE cart_item_id = ?", (new_quantity, existing[0]))
            else:
                await db.execute("INSERT INTO cart (cart_item_id, user_id, product_id, quantity, added_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)", (cart_item.cart_item_id, cart_item.user_id, cart_item.product_id, cart_item.quantity))
            await db.commit()

    async def get_cart(self, user_id: str) -> List[CartItem]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT c.cart_item_id, c.user_id, c.product_id, c.quantity, c.added_at,
                       p.name, p.price, p.image, p.stock_quantity, p.discount_percent
                FROM cart c
                LEFT JOIN products p ON c.product_id = p.id
                WHERE c.user_id = ?
                ORDER BY c.added_at DESC
            """, (user_id,))
            rows = await cursor.fetchall()
            items = []
            for row in rows:
                price = row[6] or 0
                discount = row[9] or 0
                final_price = price * (1 - discount / 100)
                items.append(CartItem(
                    cart_item_id=row[0], user_id=row[1], product_id=row[2], quantity=row[3], added_at=row[4],
                    product_name=row[5], product_price=round(final_price, 2), product_image=row[7]
                ))
            return items

    async def update_cart_quantity(self, user_id: str, product_id: str, quantity: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            if quantity <= 0:
                cursor = await db.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
            else:
                cursor = await db.execute("UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?", (quantity, user_id, product_id))
            await db.commit()
            return cursor.rowcount

    async def remove_from_cart(self, user_id: str, product_id: str) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
            await db.commit()
            return cursor.rowcount

    async def clear_cart(self, user_id: str) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
            await db.commit()
            return cursor.rowcount

    # -------------------- STOCK & DISCOUNTS --------------------
    async def update_stock(self, product_id: str, quantity_change: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT stock_quantity FROM products WHERE id = ?", (product_id,))
            row = await cursor.fetchone()
            if not row:
                return False
            current = row[0] or 0
            new_stock = current + quantity_change
            if new_stock < 0:
                return False
            await db.execute("UPDATE products SET stock_quantity = ? WHERE id = ?", (new_stock, product_id))
            await db.commit()
            return True

    async def check_stock(self, product_id: str) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT stock_quantity, name FROM products WHERE id = ?", (product_id,))
            row = await cursor.fetchone()
            if not row:
                return {"available": False, "quantity": 0, "message": "Product not found"}
            stock = row[0] or 0
            return {"available": stock > 0, "quantity": stock, "product_name": row[1], "message": "In stock" if stock > 0 else "Out of stock"}

    async def set_discount(self, product_id: str, discount_percent: float) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT price, original_price FROM products WHERE id = ?", (product_id,))
            row = await cursor.fetchone()
            if not row:
                return False
            curr = row[0]
            orig = row[1] or curr
            new_p = orig * (1 - discount_percent / 100)
            await db.execute("UPDATE products SET price = ?, discount_percent = ?, original_price = ? WHERE id = ?", (round(new_p, 2), discount_percent, orig, product_id))
            await db.commit()
            return True

    async def get_discounted_products(self) -> List[Product]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT id, name, categoryId, description, price, ratings, reviews, image, badge, created_at, seller_id, stock_quantity, discount_percent, original_price FROM products WHERE discount_percent > 0 ORDER BY discount_percent DESC")
            rows = await cursor.fetchall()
            return [Product(id=row[0], name=row[1], categoryId=row[2], description=row[3], price=row[4], ratings=row[5], reviews=row[6], image=row[7], badge=row[8], created_at=row[9], seller_id=row[10], stock_quantity=row[11], discount_percent=row[12], original_price=row[13]) for row in rows]


# =====================================================================
# Database Repository Router / Switch Proxy
# =====================================================================

class ProductRepo:
    def __init__(self, db_path: str = "products.db"):
        self.db_url = os.getenv("DATABASE_URL")
        # Check if database URL points to PostgreSQL (Supabase)
        self.use_postgres = self.db_url and (self.db_url.startswith("postgres://") or self.db_url.startswith("postgresql://"))
        self.use_firebase = os.getenv("USE_FIREBASE") == "true"

        if self.use_postgres:
            if not HAS_ASYNCPG:
                raise ImportError(
                    "asyncpg is required to use PostgreSQL/Supabase. "
                    "Please install it using: pip install asyncpg"
                )
            self.repo = PostgresProductRepo(self.db_url)
        elif self.use_firebase:
            if not HAS_FIRESTORE:
                raise ImportError(
                    "google-cloud-firestore and google-auth are required to use Firebase. "
                    "Please install them using: pip install google-cloud-firestore google-auth"
                )
            self.repo = FirestoreProductRepo()
        else:
            self.repo = SQLiteProductRepo(db_path)

    async def init_db(self):
        await self.repo.init_db()

    async def insert_product(self, product: Product) -> None:
        await self.repo.insert_product(product)

    async def update_product(self, product: Product) -> int:
        return await self.repo.update_product(product)

    async def get_product(self, product_id: str, category_id: str) -> Optional[Product]:
        return await self.repo.get_product(product_id, category_id)

    async def delete_product(self, product_id: str, category_id: str) -> int:
        return await self.repo.delete_product(product_id, category_id)

    async def get_all_products(self) -> List[Product]:
        return await self.repo.get_all_products()

    async def insert_seller(self, seller: Seller) -> None:
        await self.repo.insert_seller(seller)

    async def get_all_sellers(self) -> List[Seller]:
        return await self.repo.get_all_sellers()

    async def insert_order(self, order: Order) -> None:
        await self.repo.insert_order(order)

    async def get_order(self, order_id: str) -> Optional[Order]:
        return await self.repo.get_order(order_id)

    async def get_user_orders(self, user_id: str) -> List[Order]:
        return await self.repo.get_user_orders(user_id)

    async def update_order_status(self, order_id: str, status: str) -> int:
        return await self.repo.update_order_status(order_id, status)

    async def insert_payment(self, payment: Payment) -> None:
        await self.repo.insert_payment(payment)

    async def get_payment(self, order_id: str) -> Optional[Payment]:
        return await self.repo.get_payment(order_id)

    async def insert_tracking(self, tracking: OrderTracking) -> None:
        await self.repo.insert_tracking(tracking)

    async def get_tracking_history(self, order_id: str) -> List[OrderTracking]:
        return await self.repo.get_tracking_history(order_id)

    async def add_to_wishlist(self, wishlist: Wishlist) -> None:
        await self.repo.add_to_wishlist(wishlist)

    async def get_wishlist(self, user_id: str) -> List[Wishlist]:
        return await self.repo.get_wishlist(user_id)

    async def remove_from_wishlist(self, user_id: str, product_id: str) -> int:
        return await self.repo.remove_from_wishlist(user_id, product_id)

    async def add_review(self, review: Review) -> None:
        await self.repo.add_review(review)

    async def get_product_reviews(self, product_id: str) -> List[Review]:
        return await self.repo.get_product_reviews(product_id)

    async def insert_coupon(self, coupon: Coupon) -> None:
        await self.repo.insert_coupon(coupon)

    async def get_coupon(self, coupon_code: str) -> Optional[Coupon]:
        return await self.repo.get_coupon(coupon_code)

    async def add_to_cart(self, cart_item: CartItem) -> None:
        await self.repo.add_to_cart(cart_item)

    async def get_cart(self, user_id: str) -> List[CartItem]:
        return await self.repo.get_cart(user_id)

    async def update_cart_quantity(self, user_id: str, product_id: str, quantity: int) -> int:
        return await self.repo.update_cart_quantity(user_id, product_id, quantity)

    async def remove_from_cart(self, user_id: str, product_id: str) -> int:
        return await self.repo.remove_from_cart(user_id, product_id)

    async def clear_cart(self, user_id: str) -> int:
        return await self.repo.clear_cart(user_id)

    async def update_stock(self, product_id: str, quantity_change: int) -> bool:
        return await self.repo.update_stock(product_id, quantity_change)

    async def check_stock(self, product_id: str) -> dict:
        return await self.repo.check_stock(product_id)

    async def set_discount(self, product_id: str, discount_percent: float) -> bool:
        return await self.repo.set_discount(product_id, discount_percent)

    async def get_discounted_products(self) -> List[Product]:
        return await self.repo.get_discounted_products()
