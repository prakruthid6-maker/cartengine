import sqlite3

def fix_first_four_products():
    """Fix images for the first 4 products (elec-001 to elec-004)"""
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    
    # Fix only the first 4 products with proper, product-specific images
    fixes = {
        "elec-001": "https://images.unsplash.com/photo-1678652197257-d0a47cd8dcd0?w=800",  # iPhone 15 Pro Max
        "elec-002": "https://images.unsplash.com/photo-1593784991095-a205069470b6?w=800",  # Samsung QLED TV
        "elec-003": "https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=800",  # MacBook Air
        "elec-004": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800",   # Sony Headphones
    }
    
    for product_id, new_image_url in fixes.items():
        cursor.execute(
            "UPDATE products SET image = ? WHERE id = ?",
            (new_image_url, product_id)
        )
        print(f"  ✓ Fixed: {product_id}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Fixed images for first 4 products")
    print(f"📸 Images now show actual products instead of landscapes")

if __name__ == "__main__":
    fix_first_four_products()
