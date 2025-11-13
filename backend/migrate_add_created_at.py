import sqlite3
from datetime import datetime

db = sqlite3.connect("products.db")
cursor = db.cursor()

try:
    cursor.execute("ALTER TABLE products ADD COLUMN created_at TEXT")
    cursor.execute("UPDATE products SET created_at = ? WHERE created_at IS NULL", (datetime.now().isoformat(),))
    db.commit()
    print("✓ Added created_at column and set default timestamps")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("✓ Column already exists")
    else:
        raise

db.close()
