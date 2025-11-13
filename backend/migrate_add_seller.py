import sqlite3

db = sqlite3.connect("products.db")
cursor = db.cursor()

try:
    cursor.execute("ALTER TABLE products ADD COLUMN seller_id TEXT")
    print("✓ Added seller_id column to products")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("✓ seller_id column already exists")
    else:
        raise

try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sellers (
            seller_id TEXT PRIMARY KEY,
            name TEXT,
            location TEXT,
            rating REAL
        )
    """)
    db.commit()
    print("✓ Created sellers table")
except Exception as e:
    print(f"Error creating sellers table: {e}")

db.close()
