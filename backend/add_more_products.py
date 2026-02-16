import sqlite3
import json

def add_more_products():
    """Add 30+ additional products with similar items for better AI recommendations"""
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    
    # Check if columns exist
    cursor.execute("PRAGMA table_info(products)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'sku' not in columns:
        cursor.execute("ALTER TABLE products ADD COLUMN sku TEXT")
    if 'specifications' not in columns:
        cursor.execute("ALTER TABLE products ADD COLUMN specifications TEXT")
    
    new_products = [
        # ========== MORE SMARTPHONES ==========
        {
            "id": "phone-001",
            "name": "Samsung Galaxy S24 Ultra",
            "categoryId": "Electronics",
            "description": "Flagship Samsung phone with S Pen, 200MP camera, and AI features. Premium titanium build with 6.8-inch Dynamic AMOLED display.",
            "price": 1299.99,
            "ratings": 4.7,
            "reviews": 1842,
            "image": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c",
            "badge": "Popular",
            "sku": "SAM-S24U-256"
        },
        {
            "id": "phone-002",
            "name": "Google Pixel 8 Pro",
            "categoryId": "Electronics",
            "description": "Google's flagship with Tensor G3 chip, best-in-class camera AI, and 7 years of updates. Pure Android experience.",
            "price": 999.99,
            "ratings": 4.6,
            "reviews": 956,
            "image": "https://images.unsplash.com/photo-1598327105666-5b89351aff97",
            "badge": "Top Rated",
            "sku": "GOO-PX8P-256"
        },
        {
            "id": "phone-003",
            "name": "iPhone 14 Pro",
            "categoryId": "Electronics",
            "description": "Previous gen iPhone Pro with Dynamic Island, 48MP camera, and A16 Bionic. Great value for premium features.",
            "price": 899.99,
            "ratings": 4.8,
            "reviews": 3284,
            "image": "https://images.unsplash.com/photo-1678652197257-d0a47cd8dcd0",
            "badge": "Deal",
            "sku": "APL-IP14P-256"
        },
        
        # ========== MORE LAPTOPS ==========
        {
            "id": "laptop-001",
            "name": "Dell XPS 15",
            "categoryId": "Electronics",
            "description": "Professional Windows laptop with Intel i7-13700H, NVIDIA RTX 4050, stunning 15.6-inch OLED display.",
            "price": 1899.99,
            "ratings": 4.5,
            "reviews": 728,
            "image": "https://images.unsplash.com/photo-1593642532400-2682810df593",
            "badge": "Professional",
            "sku": "DELL-XPS15-1TB"
        },
        {
            "id": "laptop-002",
            "name": "ASUS ROG Zephyrus G14",
            "categoryId": "Electronics",
            "description": "Gaming laptop with AMD Ryzen 9, RTX 4060, 14-inch QHD display. Portable yet powerful for gaming.",
            "price": 1599.99,
            "ratings": 4.7,
            "reviews": 1245,
            "image": "https://images.unsplash.com/photo-1603302576837-37561b2e2302",
            "badge": "Gaming",
            "sku": "ASUS-G14-512"
        },
        {
            "id": "laptop-003",
            "name": "HP Spectre x360",
            "categoryId": "Electronics",
            "description": "2-in-1 convertible laptop with Intel i7, touchscreen, and premium build. Perfect for professionals.",
            "price": 1399.99,
            "ratings": 4.4,
            "reviews": 634,
            "image": "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2",
            "badge": "Convertible",
            "sku": "HP-SPEC-512"
        },
        
        # ========== MORE HEADPHONES/EARBUDS ==========
        {
            "id": "audio-001",
            "name": "Bose QuietComfort 45",
            "categoryId": "Electronics",
            "description": "Premium noise-canceling headphones with legendary Bose sound quality and 24-hour battery life.",
            "price": 329.99,
            "ratings": 4.6,
            "reviews": 2156,
            "image": "https://images.unsplash.com/photo-1546435770-a3e426bf472b",
            "badge": "Popular",
            "sku": "BOSE-QC45-BLK"
        },
        {
            "id": "audio-002",
            "name": "AirPods Pro 2",
            "categoryId": "Electronics",
            "description": "Apple's premium earbuds with adaptive transparency, spatial audio, and H2 chip for superior ANC.",
            "price": 249.99,
            "ratings": 4.7,
            "reviews": 4523,
            "image": "https://images.unsplash.com/photo-1606841837239-c5a1a4a07af7",
            "badge": "Best Seller",
            "sku": "APL-APP2-USB"
        },
        {
            "id": "audio-003",
            "name": "Jabra Elite 85t",
            "categoryId": "Electronics",
            "description": "Premium earbuds with adjustable ANC, great call quality, and customizable sound with app.",
            "price": 229.99,
            "ratings": 4.5,
            "reviews": 1876,
            "image": "https://images.unsplash.com/photo-1590658165737-15a047b0ef01",
            "badge": "Top Rated",
            "sku": "JAB-E85T-BLK"
        },
        
        # ========== SMARTWATCHES ==========
        {
            "id": "watch-001",
            "name": "Apple Watch Series 9",
            "categoryId": "Electronics",
            "description": "Latest Apple Watch with S9 chip, always-on Retina display, and advanced health tracking.",
            "price": 429.99,
            "ratings": 4.8,
            "reviews": 2947,
            "image": "https://images.unsplash.com/photo-1579586337278-3befd40fd17a",
            "badge": "New",
            "sku": "APL-AWS9-45"
        },
        {
            "id": "watch-002",
            "name": "Samsung Galaxy Watch 6",
            "categoryId": "Electronics",
            "description": "Android smartwatch with Wear OS, comprehensive health tracking, and beautiful AMOLED display.",
            "price": 329.99,
            "ratings": 4.5,
            "reviews": 1523,
            "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30",
            "badge": "Popular",
            "sku": "SAM-GW6-44"
        },
        {
            "id": "watch-003",
            "name": "Garmin Fenix 7",
            "categoryId": "Electronics",
            "description": "Rugged outdoor smartwatch with GPS, 18-day battery, and advanced training metrics.",
            "price": 699.99,
            "ratings": 4.7,
            "reviews": 892,
            "image": "https://images.unsplash.com/photo-1617625802912-cde586faf331",
            "badge": "Premium",
            "sku": "GAR-FEN7-BLK"
        },
        
        # ========== TABLETS ==========
        {
            "id": "tablet-001",
            "name": "iPad Pro 12.9",
            "categoryId": "Electronics",
            "description": "Professional tablet with M2 chip, Liquid Retina XDR display, and Magic Keyboard support.",
            "price": 1099.99,
            "ratings": 4.8,
            "reviews": 1745,
            "image": "https://images.unsplash.com/photo-1585790050230-5dd28404ccb9",
            "badge": "Professional",
            "sku": "APL-IPP12-256"
        },
        {
            "id": "tablet-002",
            "name": "Samsung Galaxy Tab S9+",
            "categoryId": "Electronics",
            "description": "Android tablet with S Pen, 12.4-inch AMOLED display, and DeX mode for desktop experience.",
            "price": 899.99,
            "ratings": 4.6,
            "reviews": 967,
            "image": "https://images.unsplash.com/photo-1561154464-82e9adf32764",
            "badge": "Popular",
            "sku": "SAM-GTS9P-256"
        },
        
        # ========== CAMERAS ==========
        {
            "id": "camera-001",
            "name": "Sony Alpha A7 IV",
            "categoryId": "Electronics",
            "description": "Professional mirrorless camera with 33MP sensor, 4K 60p video, and advanced autofocus.",
            "price": 2499.99,
            "ratings": 4.9,
            "reviews": 645,
            "image": "https://images.unsplash.com/photo-1606980622109-6c5c96b32708",
            "badge": "Professional",
            "sku": "SNY-A7IV-BODY"
        },
        {
            "id": "camera-002",
            "name": "Canon EOS R6 Mark II",
            "categoryId": "Electronics",
            "description": "Hybrid camera for photos and video with 24MP sensor, in-body stabilization, and dual card slots.",
            "price": 2399.99,
            "ratings": 4.8,
            "reviews": 523,
            "image": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd",
            "badge": "Top Rated",
            "sku": "CAN-R6II-BODY"
        },
        
        # ========== GAMING CONSOLES ==========
        {
            "id": "console-001",
            "name": "PlayStation 5",
            "categoryId": "Electronics",
            "description": "Next-gen gaming console with ultra-fast SSD, ray tracing, and exclusive titles.",
            "price": 499.99,
            "ratings": 4.7,
            "reviews": 5234,
            "image": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db",
            "badge": "Gaming",
            "sku": "SNY-PS5-DISC"
        },
        {
            "id": "console-002",
            "name": "Xbox Series X",
            "categoryId": "Electronics",
            "description": "Microsoft's most powerful console with 4K 120fps gaming and Game Pass access.",
            "price": 499.99,
            "ratings": 4.6,
            "reviews": 4156,
            "image": "https://images.unsplash.com/photo-1621259182978-fbf93132d53d",
            "badge": "Gaming",
            "sku": "MS-XBSX-1TB"
        },
        {
            "id": "console-003",
            "name": "Nintendo Switch OLED",
            "categoryId": "Electronics",
            "description": "Hybrid console with 7-inch OLED screen, portable and docked modes, perfect for Nintendo games.",
            "price": 349.99,
            "ratings": 4.8,
            "reviews": 6782,
            "image": "https://images.unsplash.com/photo-1578303512597-81e6cc155b3e",
            "badge": "Family Friendly",
            "sku": "NIN-SW-OLED"
        },
        
        # ========== HOME & KITCHEN ==========
        {
            "id": "home-001",
            "name": "Dyson V15 Detect",
            "categoryId": "Home & Kitchen",
            "description": "Cordless vacuum with laser dust detection, powerful suction, and up to 60 min runtime.",
            "price": 649.99,
            "ratings": 4.6,
            "reviews": 2341,
            "image": "https://images.unsplash.com/photo-1558317374-067fb5f30001",
            "badge": "Top Rated",
            "sku": "DYS-V15-DET"
        },
        {
            "id": "home-002",
            "name": "Ninja Foodi Air Fryer",
            "categoryId": "Home & Kitchen",
            "description": "8-in-1 air fryer with pressure cooker function. 6.5 quart capacity for family meals.",
            "price": 229.99,
            "ratings": 4.7,
            "reviews": 8945,
            "image": "https://images.unsplash.com/photo-1585629876994-cc9e1c8ae63e",
            "badge": "Best Seller",
            "sku": "NIN-FOODI-65"
        },
        {
            "id": "home-003",
            "name": "iRobot Roomba j7+",
            "categoryId": "Home & Kitchen",
            "description": "Smart robot vacuum with obstacle avoidance, self-emptying base, and mapping technology.",
            "price": 799.99,
            "ratings": 4.5,
            "reviews": 3456,
            "image": "https://images.unsplash.com/photo-1558317374-067fb5f30001",
            "badge": "Smart Home",
            "sku": "IRO-J7PLUS"
        },
        {
            "id": "home-004",
            "name": "Keurig K-Elite Coffee Maker",
            "categoryId": "Home & Kitchen",
            "description": "Single-serve coffee maker with iced coffee setting, strong brew option, and large water reservoir.",
            "price": 169.99,
            "ratings": 4.4,
            "reviews": 12456,
            "image": "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6",
            "badge": "Popular",
            "sku": "KEU-ELITE-BRU"
        },
        
        # ========== FASHION ==========
        {
            "id": "fashion-001",
            "name": "Nike Air Max 270",
            "categoryId": "Fashion",
            "description": "Iconic sneakers with large Air unit, comfortable mesh upper, and modern design.",
            "price": 150.00,
            "ratings": 4.6,
            "reviews": 5678,
            "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
            "badge": "Popular",
            "sku": "NIKE-AM270-10"
        },
        {
            "id": "fashion-002",
            "name": "Adidas Ultraboost 23",
            "categoryId": "Fashion",
            "description": "Premium running shoes with Boost cushioning, Primeknit upper, and Continental rubber outsole.",
            "price": 190.00,
            "ratings": 4.7,
            "reviews": 3452,
            "image": "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa",
            "badge": "Top Rated",
            "sku": "ADI-UB23-105"
        },
        {
            "id": "fashion-003",
            "name": "Levi's 501 Original Jeans",
            "categoryId": "Fashion",
            "description": "Classic straight-leg jeans with button fly. Timeless style since 1873.",
            "price": 69.99,
            "ratings": 4.5,
            "reviews": 8923,
            "image": "https://images.unsplash.com/photo-1542272604-787c3835535d",
            "badge": "Classic",
            "sku": "LEVI-501-32x32"
        },
        {
            "id": "fashion-004",
            "name": "Ray-Ban Aviator Sunglasses",
            "categoryId": "Fashion",
            "description": "Iconic aviator sunglasses with UV protection and metal frame. Timeless design.",
            "price": 154.00,
            "ratings": 4.8,
            "reviews": 6734,
            "image": "https://images.unsplash.com/photo-1511499767150-a48a237f0083",
            "badge": "Iconic",
            "sku": "RAY-AVI-58"
        },
        {
            "id": "fashion-005",
            "name": "The North Face Down Jacket",
            "categoryId": "Fashion",
            "description": "Warm insulated jacket with 700-fill down, water-resistant,perfect for winter.",
            "price": 249.99,
            "ratings": 4.7,
            "reviews": 2134,
            "image": "https://images.unsplash.com/photo-1544923246-77583df18f5e",
            "badge": "Winter Essential",
            "sku": "TNF-DOWN-L"
        },
        
        # ========== SPORTS & FITNESS ==========
        {
            "id": "sports-001",
            "name": "Peloton Bike+",
            "categoryId": "Sports",
            "description": "Premium indoor cycling bike with rotating screen, auto-resistance, and live classes.",
            "price": 2495.00,
            "ratings": 4.6,
            "reviews": 4523,
            "image": "https://images.unsplash.com/photo-1617704548623-340376564e68",
            "badge": "Premium",
            "sku": "PEL-BIKE-PLUS"
        },
        {
            "id": "sports-002",
            "name": "Bowflex SelectTech Dumbbells",
            "categoryId": "Sports",
            "description": "Adjustable dumbbells 5-52.5 lbs per dumbbell. Space-saving home gym solution.",
            "price": 449.00,
            "ratings": 4.8,
            "reviews": 7892,
            "image": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438",
            "badge": "Best Seller",
            "sku": "BOW-ST552"
        },
        {
            "id": "sports-003",
            "name": "Hydro Flask Water Bottle 32oz",
            "categoryId": "Sports",
            "description": "Insulated stainless steel bottle keeps drinks cold 24hrs or hot 12hrs. BPA-free.",
            "price": 44.95,
            "ratings": 4.7,
            "reviews": 15234,
            "image": "https://images.unsplash.com/photo-1602143407151-7111542de6e8",
            "badge": "Popular",
            "sku": "HYD-32OZ-BLK"
        }
    ]
    
    for product in new_products:
        try:
            cursor.execute("""
                INSERT INTO products (id, name, categoryId, description, price, ratings, reviews, image, badge, sku, specifications)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product["id"],
                product["name"],
                product["categoryId"],
                product["description"],
                product["price"],
                product["ratings"],
                product["reviews"],
                product["image"],
                product.get("badge", ""),
                product.get("sku", ""),
                json.dumps(product.get("specifications", {}))
            ))
        except sqlite3.IntegrityError:
            # Product ID already exists, skip
            continue
    
    conn.commit()
    conn.close()
    print(f"✅ Added {len(new_products)} more products to the database!")
    print(f"📊 Product categories expanded:")
    print(f"   - Smartphones: Multiple brands (Apple, Samsung, Google)")
    print(f"   - Laptops: Various types (Professional, Gaming, Convertible)")
    print(f"   - Audio: Headphones & Earbuds (Sony, Bose, Apple, Jabra)")
    print(f"   - Wearables: Smartwatches (Apple, Samsung, Garmin)")
    print(f"   - Tablets: iPad & Android options")
    print(f"   - Cameras: Professional mirrorless cameras")
    print(f"   - Gaming: All major consoles (PS5, Xbox, Switch)")
    print(f"   - Home & Kitchen: Smart appliances")
    print(f"   - Fashion: Shoes, clothing, accessories")
    print(f"   - Sports & Fitness: Equipment & accessories")

if __name__ == "__main__":
    add_more_products()
