import sqlite3

db = sqlite3.connect("products.db")
cursor = db.cursor()

try:
    cursor.execute("""
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
    print("✓ Created orders table")
except Exception as e:
    print(f"Error creating orders table: {e}")

try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            payment_id TEXT PRIMARY KEY,
            order_id TEXT,
            amount REAL,
            method TEXT,
            status TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Created payments table")
except Exception as e:
    print(f"Error creating payments table: {e}")

db.commit()
db.close()
print("✓ Migration completed")
