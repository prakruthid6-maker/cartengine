import sqlite3

def fix_iphone_image():
    """Fix the broken iPhone 15 Pro Max image"""
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    
    # Use a working generic smartphone image
    cursor.execute(
        "UPDATE products SET image = ? WHERE id = ?",
        ("https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800", "elec-001")
    )
    
    conn.commit()
    conn.close()
    
    print("✅ Fixed iPhone 15 Pro Max image")

if __name__ == "__main__":
    fix_iphone_image()
