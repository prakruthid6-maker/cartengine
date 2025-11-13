import sqlite3

db = sqlite3.connect("products.db")
cursor = db.cursor()

try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_tracking (
            tracking_id TEXT PRIMARY KEY,
            order_id TEXT,
            status TEXT,
            location TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Created order_tracking table")
except Exception as e:
    print(f"Error: {e}")

db.commit()
db.close()
