import sqlite3

db = sqlite3.connect("products.db")
cursor = db.cursor()

sellers = [
    ("seller-001", "TechWorld", "New York", 4.8),
    ("seller-002", "FashionHub", "Los Angeles", 4.5),
    ("seller-003", "HomeEssentials", "Chicago", 4.7),
    ("seller-004", "SportsPro", "Miami", 4.9),
]

for seller in sellers:
    cursor.execute("INSERT OR IGNORE INTO sellers (seller_id, name, location, rating) VALUES (?, ?, ?, ?)", seller)

cursor.execute("UPDATE products SET seller_id = 'seller-001' WHERE categoryId = 'Electronics'")
cursor.execute("UPDATE products SET seller_id = 'seller-002' WHERE categoryId = 'Fashion'")
cursor.execute("UPDATE products SET seller_id = 'seller-003' WHERE categoryId = 'Home'")
cursor.execute("UPDATE products SET seller_id = 'seller-004' WHERE categoryId = 'Sports'")

db.commit()
db.close()

print("✓ Populated sellers and linked to products")
