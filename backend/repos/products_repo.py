import aiosqlite
from typing import List, Optional
from models.data_models import Product, Seller, Order, Payment, OrderTracking, Wishlist, Review, Coupon, CartItem, Cart


class ProductRepo:
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
            # New: Cart table for persistent shopping cart
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
            # Add inventory columns to products if they don't exist
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
        """Returns number of rows updated"""
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
                    badge=row[8],
                    created_at=row[9],
                    seller_id=row[10]
                )
                for row in rows
            ]
            return products

    # -------------------- SELLER OPERATIONS --------------------
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

    # -------------------- ORDER OPERATIONS --------------------
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

    # -------------------- PAYMENT OPERATIONS --------------------
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

    # -------------------- ORDER TRACKING OPERATIONS --------------------
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

    # -------------------- WISHLIST OPERATIONS --------------------
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

    # -------------------- REVIEW OPERATIONS --------------------
    async def add_review(self, review: Review) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO reviews (review_id, product_id, user_id, rating, comment, review_date) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", (review.review_id, review.product_id, review.user_id, review.rating, review.comment))
            await db.commit()

    async def get_product_reviews(self, product_id: str) -> List[Review]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT review_id, product_id, user_id, rating, comment, review_date FROM reviews WHERE product_id = ? ORDER BY review_date DESC", (product_id,))
            rows = await cursor.fetchall()
            return [Review(review_id=row[0], product_id=row[1], user_id=row[2], rating=row[3], comment=row[4], review_date=row[5]) for row in rows]

    # -------------------- COUPON OPERATIONS --------------------
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

    # -------------------- CART OPERATIONS --------------------
    async def add_to_cart(self, cart_item: CartItem) -> None:
        """Add item to cart or update quantity if already exists"""
        async with aiosqlite.connect(self.db_path) as db:
            # Check if item already in cart
            cursor = await db.execute(
                "SELECT cart_item_id, quantity FROM cart WHERE user_id = ? AND product_id = ?",
                (cart_item.user_id, cart_item.product_id)
            )
            existing = await cursor.fetchone()
            
            if existing:
                # Update quantity
                new_quantity = existing[1] + cart_item.quantity
                await db.execute(
                    "UPDATE cart SET quantity = ? WHERE cart_item_id = ?",
                    (new_quantity, existing[0])
                )
            else:
                # Insert new item
                await db.execute(
                    "INSERT INTO cart (cart_item_id, user_id, product_id, quantity, added_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
                    (cart_item.cart_item_id, cart_item.user_id, cart_item.product_id, cart_item.quantity)
                )
            await db.commit()

    async def get_cart(self, user_id: str) -> List[CartItem]:
        """Get all items in user's cart with product details"""
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
                # Apply discount to price
                price = row[6] or 0
                discount = row[9] or 0
                final_price = price * (1 - discount / 100)
                items.append(CartItem(
                    cart_item_id=row[0],
                    user_id=row[1],
                    product_id=row[2],
                    quantity=row[3],
                    added_at=row[4],
                    product_name=row[5],
                    product_price=round(final_price, 2),
                    product_image=row[7]
                ))
            return items

    async def update_cart_quantity(self, user_id: str, product_id: str, quantity: int) -> int:
        """Update quantity of item in cart. Returns rows affected."""
        async with aiosqlite.connect(self.db_path) as db:
            if quantity <= 0:
                # Remove item if quantity is 0 or negative
                cursor = await db.execute(
                    "DELETE FROM cart WHERE user_id = ? AND product_id = ?",
                    (user_id, product_id)
                )
            else:
                cursor = await db.execute(
                    "UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?",
                    (quantity, user_id, product_id)
                )
            await db.commit()
            return cursor.rowcount

    async def remove_from_cart(self, user_id: str, product_id: str) -> int:
        """Remove item from cart. Returns rows affected."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM cart WHERE user_id = ? AND product_id = ?",
                (user_id, product_id)
            )
            await db.commit()
            return cursor.rowcount

    async def clear_cart(self, user_id: str) -> int:
        """Clear all items from user's cart. Returns rows affected."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
            await db.commit()
            return cursor.rowcount

    # -------------------- INVENTORY OPERATIONS --------------------
    async def update_stock(self, product_id: str, quantity_change: int) -> bool:
        """Update product stock. Negative for decrease, positive for increase."""
        async with aiosqlite.connect(self.db_path) as db:
            # Check current stock
            cursor = await db.execute(
                "SELECT stock_quantity FROM products WHERE id = ?", (product_id,)
            )
            row = await cursor.fetchone()
            if not row:
                return False
            
            current_stock = row[0] or 0
            new_stock = current_stock + quantity_change
            
            if new_stock < 0:
                return False  # Cannot have negative stock
            
            await db.execute(
                "UPDATE products SET stock_quantity = ? WHERE id = ?",
                (new_stock, product_id)
            )
            await db.commit()
            return True

    async def check_stock(self, product_id: str) -> dict:
        """Check product stock availability"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT stock_quantity, name FROM products WHERE id = ?", (product_id,)
            )
            row = await cursor.fetchone()
            if not row:
                return {"available": False, "quantity": 0, "message": "Product not found"}
            
            stock = row[0] or 0
            return {
                "available": stock > 0,
                "quantity": stock,
                "product_name": row[1],
                "message": "In stock" if stock > 0 else "Out of stock"
            }

    async def set_discount(self, product_id: str, discount_percent: float) -> bool:
        """Set discount percentage for a product"""
        async with aiosqlite.connect(self.db_path) as db:
            # Get current price to save as original if not already set
            cursor = await db.execute(
                "SELECT price, original_price FROM products WHERE id = ?", (product_id,)
            )
            row = await cursor.fetchone()
            if not row:
                return False
            
            current_price = row[0]
            original_price = row[1] or current_price
            
            # Calculate new discounted price
            new_price = original_price * (1 - discount_percent / 100)
            
            await db.execute(
                "UPDATE products SET price = ?, discount_percent = ?, original_price = ? WHERE id = ?",
                (round(new_price, 2), discount_percent, original_price, product_id)
            )
            await db.commit()
            return True

    async def get_discounted_products(self) -> List[Product]:
        """Get all products with active discounts"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT id, name, categoryId, description, price, ratings, reviews, image, badge, 
                       created_at, seller_id, stock_quantity, discount_percent, original_price
                FROM products 
                WHERE discount_percent > 0
                ORDER BY discount_percent DESC
            """)
            rows = await cursor.fetchall()
            products = []
            for row in rows:
                products.append(Product(
                    id=row[0], name=row[1], categoryId=row[2], description=row[3],
                    price=row[4], ratings=row[5], reviews=row[6], image=row[7],
                    badge=row[8], created_at=row[9], seller_id=row[10],
                    stock_quantity=row[11], discount_percent=row[12], original_price=row[13]
                ))
            return products

