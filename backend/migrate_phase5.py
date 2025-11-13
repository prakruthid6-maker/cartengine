import sqlite3

db = sqlite3.connect("products.db")
cursor = db.cursor()

tables = [
    ("wishlist", """
        CREATE TABLE IF NOT EXISTS wishlist (
            wishlist_id TEXT PRIMARY KEY,
            user_id TEXT,
            product_id TEXT,
            added_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """),
    ("reviews", """
        CREATE TABLE IF NOT EXISTS reviews (
            review_id TEXT PRIMARY KEY,
            product_id TEXT,
            user_id TEXT,
            rating REAL,
            comment TEXT,
            review_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """),
    ("coupons", """
        CREATE TABLE IF NOT EXISTS coupons (
            coupon_code TEXT PRIMARY KEY,
            discount_percent REAL,
            expiry_date TEXT,
            status TEXT
        )
    """)
]

for table_name, create_sql in tables:
    try:
        cursor.execute(create_sql)
        print(f"✓ Created {table_name} table")
    except Exception as e:
        print(f"Error creating {table_name}: {e}")

db.commit()
db.close()
print("✓ Phase 5 migration completed")
