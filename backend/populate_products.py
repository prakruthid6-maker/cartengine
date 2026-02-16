import sqlite3
import json

def populate_products():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    
    # Clear existing products
    cursor.execute("DELETE FROM products")
    
    products = [
        # ================== Electronics (6 products) ==================
        {
            "id": "elec-001",
            "name": "iPhone 15 Pro Max",
            "categoryId": "Electronics",
            "description": "Latest iPhone with titanium design and A17 Pro chip. Features a 6.7-inch Super Retina XDR display with ProMotion, Dynamic Island, and 48MP camera system with 5x optical zoom.",
            "price": 1199.99,
            "ratings": 4.8,
            "reviews": 2847,
            "image": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab",
            "badge": "Best Seller",
            "sku": "APL-IP15PM-256",
            "specifications": {
                "Display": "6.7-inch OLED, 2796x1290, 120Hz ProMotion",
                "Processor": "A17 Pro chip (3nm)",
                "Storage": "256GB / 512GB / 1TB",
                "Camera": "48MP + 12MP + 12MP, 5x optical zoom",
                "Battery": "4422mAh, up to 29h video playback",
                "Material": "Titanium frame, Ceramic Shield",
                "Weight": "221g",
                "Connectivity": "5G, Wi-Fi 6E, Bluetooth 5.3, USB-C"
            }
        },
        {
            "id": "elec-002", 
            "name": "Samsung 65\" QLED 4K TV",
            "categoryId": "Electronics",
            "description": "Quantum Dot technology with HDR10+ support. Features vivid colors, smart TV capabilities with Tizen OS, and Object Tracking Sound for immersive audio.",
            "price": 949.99,
            "ratings": 4.6,
            "reviews": 1523,
            "image": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1",
            "badge": "Deal",
            "sku": "SAM-QN65Q80C",
            "specifications": {
                "Screen Size": "65 inches (163.9 cm)",
                "Resolution": "4K Ultra HD (3840 x 2160)",
                "Panel Type": "QLED Quantum Dot",
                "Refresh Rate": "120Hz native",
                "HDR": "HDR10+, HLG",
                "Audio": "60W 2.2.2 channel, Dolby Atmos",
                "Smart OS": "Tizen 7.0",
                "Ports": "4x HDMI 2.1, 2x USB"
            }
        },
        {
            "id": "elec-003",
            "name": "MacBook Air M3",
            "categoryId": "Electronics", 
            "description": "13-inch laptop with M3 chip and 18-hour battery. Ultra-thin design with Liquid Retina display, MagSafe charging, and fanless silent operation.",
            "price": 1299.99,
            "ratings": 4.9,
            "reviews": 892,
            "image": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8",
            "badge": "New",
            "sku": "APL-MBA-M3-256",
            "specifications": {
                "Display": "13.6-inch Liquid Retina, 2560x1664",
                "Processor": "Apple M3 (8-core CPU, 10-core GPU)",
                "Memory": "8GB / 16GB / 24GB Unified",
                "Storage": "256GB / 512GB / 1TB / 2TB SSD",
                "Battery": "Up to 18 hours",
                "Weight": "1.24 kg (2.7 lb)",
                "Ports": "2x Thunderbolt 4, MagSafe 3",
                "Keyboard": "Magic Keyboard with Touch ID"
            }
        },
        {
            "id": "elec-004",
            "name": "Sony WH-1000XM5 Headphones",
            "categoryId": "Electronics",
            "description": "Wireless noise-canceling headphones with industry-leading ANC, 30-hour battery, and exceptional comfort with premium materials.",
            "price": 349.99,
            "ratings": 4.7,
            "reviews": 3421,
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e",
            "badge": "Top Rated",
            "sku": "SNY-WH1000XM5-B",
            "specifications": {
                "Driver Units": "30mm Dynamic",
                "Frequency Response": "4Hz - 40,000Hz",
                "Battery Life": "30 hours (ANC on)",
                "Charging": "USB-C, 3min charge = 3hrs playback",
                "Noise Cancellation": "Dual processor V1, 8 microphones",
                "Bluetooth": "5.2 with LDAC, AAC, SBC",
                "Weight": "250g",
                "Connectivity": "Multipoint (2 devices)"
            }
        },
        {
            "id": "elec-005",
            "name": "iPad Pro 12.9\" M2",
            "categoryId": "Electronics",
            "description": "The ultimate iPad experience with M2 chip, Liquid Retina XDR display, and Apple Pencil hover support for creative professionals.",
            "price": 1099.99,
            "ratings": 4.8,
            "reviews": 1234,
            "image": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0",
            "badge": "Premium",
            "sku": "APL-IPADPRO-12-M2",
            "specifications": {
                "Display": "12.9-inch Liquid Retina XDR, 2732x2048",
                "Processor": "Apple M2 chip",
                "Storage": "128GB to 2TB",
                "Camera": "12MP Wide + 10MP Ultra Wide",
                "Face ID": "TrueDepth camera system",
                "Connectivity": "Wi-Fi 6E, 5G optional",
                "Weight": "682g (Wi-Fi)",
                "Accessories": "Apple Pencil 2, Magic Keyboard"
            }
        },
        {
            "id": "elec-006",
            "name": "Samsung Galaxy Watch 6",
            "categoryId": "Electronics",
            "description": "Advanced health tracking with BioActive Sensor, sleep coaching, and Wear OS for seamless smartphone integration.",
            "price": 329.99,
            "ratings": 4.5,
            "reviews": 987,
            "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30",
            "badge": "Smart Home",
            "sku": "SAM-GW6-44-BK",
            "specifications": {
                "Display": "1.5-inch Super AMOLED, 480x480",
                "Processor": "Exynos W930 Dual Core 1.4GHz",
                "Memory": "2GB RAM + 16GB Storage",
                "Battery": "425mAh, up to 40 hours",
                "Sensors": "BioActive, Temperature, GPS",
                "Water Resistance": "5ATM + IP68",
                "OS": "Wear OS 4, One UI Watch 5",
                "Connectivity": "Bluetooth 5.3, Wi-Fi, NFC"
            }
        },
        
        # ================== Fashion (5 products) ==================
        {
            "id": "fash-001",
            "name": "Nike Air Max 270",
            "categoryId": "Fashion",
            "description": "Men's running shoes with Max Air cushioning. Breathable mesh upper with bold colors for standout street style.",
            "price": 149.99,
            "ratings": 4.5,
            "reviews": 2156,
            "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
            "badge": "Popular",
            "sku": "NKE-AM270-BLK-10",
            "specifications": {
                "Upper": "Engineered mesh with synthetic overlays",
                "Midsole": "Foam with visible Max Air 270 unit",
                "Outsole": "Rubber waffle pattern",
                "Heel Drop": "13mm",
                "Weight": "340g (size 10)",
                "Closure": "Lace-up",
                "Available Sizes": "6-14 US (Men's)",
                "Colors": "Black/White, Red, Blue, Volt"
            }
        },
        {
            "id": "fash-002",
            "name": "Levi's 501 Original Jeans",
            "categoryId": "Fashion",
            "description": "Classic straight-leg denim jeans with iconic button fly. Timeless American style since 1873.",
            "price": 89.99,
            "ratings": 4.4,
            "reviews": 5847,
            "image": "https://images.unsplash.com/photo-1542272604-787c3835535d",
            "badge": "Classic",
            "sku": "LVS-501-IND-32",
            "specifications": {
                "Fit": "Original fit, straight leg",
                "Rise": "Regular mid-rise",
                "Material": "100% Cotton denim, 12.5oz",
                "Closure": "Button fly",
                "Waist Sizes": "28-42",
                "Length Options": "30, 32, 34",
                "Wash": "Medium indigo stonewash",
                "Care": "Machine wash cold"
            }
        },
        {
            "id": "fash-003",
            "name": "Ray-Ban Aviator Sunglasses",
            "categoryId": "Fashion",
            "description": "Classic aviator sunglasses with UV protection. Iconic pilot-style frames worn by celebrities worldwide.",
            "price": 154.99,
            "ratings": 4.8,
            "reviews": 3267,
            "image": "https://images.unsplash.com/photo-1572635196237-14b3f281503f",
            "badge": "Iconic",
            "sku": "RB-AVI-G15-58",
            "specifications": {
                "Frame Material": "Metal (nickel alloy)",
                "Lens Material": "Crystal glass",
                "Lens Width": "58mm (also 55mm, 62mm)",
                "Bridge": "14mm",
                "Temple Length": "135mm",
                "UV Protection": "100% UVA/UVB",
                "Lens Color": "G-15 green, grey, brown",
                "Includes": "Case, cleaning cloth"
            }
        },
        {
            "id": "fash-004",
            "name": "Adidas Ultraboost 23",
            "categoryId": "Fashion",
            "description": "Women's running shoes with Light BOOST midsole for incredible energy return. Primeknit+ upper for sock-like fit.",
            "price": 189.99,
            "ratings": 4.7,
            "reviews": 1834,
            "image": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a",
            "badge": "Trending",
            "sku": "ADI-UB23-WHT-8W",
            "specifications": {
                "Upper": "Primeknit+ with Fitcounter heel",
                "Midsole": "Light BOOST (20% lighter)",
                "Outsole": "Continental Rubber",
                "Heel Drop": "10mm",
                "Weight": "292g (size 8 women's)",
                "Stack Height": "31mm heel / 21mm forefoot",
                "Available Sizes": "5-12 US (Women's)",
                "Sustainability": "50% recycled content"
            }
        },
        {
            "id": "fash-005",
            "name": "Canada Goose Expedition Parka",
            "categoryId": "Fashion",
            "description": "Extreme cold weather protection rated to -30°C. Arctic-ready outerwear with genuine coyote fur trim.",
            "price": 1295.00,
            "ratings": 4.9,
            "reviews": 876,
            "image": "https://images.unsplash.com/photo-1544022613-e87ca75a784a",
            "badge": "Premium",
            "sku": "CG-EXPD-BLK-L",
            "specifications": {
                "Temperature Rating": "-30°C (-22°F)",
                "Fill": "625 fill power white duck down",
                "Shell": "Arctic Tech (85% polyester, 15% cotton)",
                "Hood": "Removable, with coyote fur ruff",
                "Pockets": "8 exterior, 4 interior",
                "Weight": "2.04kg",
                "Origin": "Made in Canada",
                "Warranty": "Lifetime"
            }
        },
        
        # ================== Home (4 products) ==================
        {
            "id": "home-001",
            "name": "Dyson V15 Detect Vacuum",
            "categoryId": "Home",
            "description": "Cordless vacuum with laser dust detection. Automatically adjusts suction and shows particle count in real-time.",
            "price": 749.99,
            "ratings": 4.7,
            "reviews": 1456,
            "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64",
            "badge": "Premium",
            "sku": "DYS-V15-DET",
            "specifications": {
                "Motor": "Dyson Hyperdymium, 125,000rpm",
                "Suction Power": "230 AW (boost mode)",
                "Battery": "Up to 60 minutes",
                "Bin Capacity": "0.76L",
                "Weight": "3.1kg (with battery)",
                "Display": "LCD shows particles & runtime",
                "Filtration": "Whole-machine HEPA",
                "Accessories": "6 tools included"
            }
        },
        {
            "id": "home-002",
            "name": "KitchenAid Artisan Stand Mixer",
            "categoryId": "Home",
            "description": "5-quart tilt-head stand mixer with 10 speeds. The iconic workhorse for serious home bakers.",
            "price": 379.99,
            "ratings": 4.8,
            "reviews": 4521,
            "image": "https://images.unsplash.com/photo-1578662996442-48f60103fc96",
            "badge": "Chef's Choice",
            "sku": "KA-KSM150-RED",
            "specifications": {
                "Motor": "325 watts",
                "Bowl Capacity": "5 quarts (4.7L)",
                "Speed Settings": "10 speeds + soft start",
                "Head Type": "Tilt-head",
                "Attachments": "Flat beater, dough hook, wire whip",
                "Power Hub": "For 10+ optional attachments",
                "Dimensions": "14.1\" H x 8.7\" W x 14.6\" D",
                "Weight": "11.8 kg (26 lbs)"
            }
        },
        {
            "id": "home-003",
            "name": "Philips Hue Smart Bulbs 4-Pack",
            "categoryId": "Home",
            "description": "Color-changing LED smart bulbs with 16 million colors. Voice control with Alexa, Google, and Apple HomeKit.",
            "price": 199.99,
            "ratings": 4.5,
            "reviews": 2743,
            "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d",
            "badge": "Smart Home",
            "sku": "PHI-HUE-4PK-CLR",
            "specifications": {
                "Bulb Type": "A19/E26 LED",
                "Wattage": "9W (60W equivalent)",
                "Lumens": "800lm per bulb",
                "Color Range": "16 million colors + 50,000 white shades",
                "Lifespan": "25,000 hours",
                "Connectivity": "Zigbee 3.0 (requires Hue Bridge)",
                "Voice Control": "Alexa, Google, Siri",
                "Energy Class": "A+"
            }
        },
        {
            "id": "home-004",
            "name": "Breville Barista Express",
            "categoryId": "Home",
            "description": "All-in-one espresso machine with built-in grinder. Café-quality espresso at home with precise temperature control.",
            "price": 699.99,
            "ratings": 4.6,
            "reviews": 3234,
            "image": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085",
            "badge": "Best Value",
            "sku": "BRV-BES870-SS",
            "specifications": {
                "Pump Pressure": "15 bar Italian pump",
                "Grinder": "Conical burr, 18 settings",
                "Boiler": "Stainless steel ThermoJet",
                "Heat-up Time": "3 seconds",
                "Water Tank": "2L removable",
                "Portafilter": "54mm with single/double baskets",
                "Steam Wand": "Manual micro-foam milk",
                "Dimensions": "13.2\" H x 12.6\" W x 15.8\" D"
            }
        },
        
        # ================== Sports (4 products) ==================
        {
            "id": "sport-001",
            "name": "Peloton Bike+",
            "categoryId": "Sports",
            "description": "Indoor exercise bike with 23.8\" rotating HD touchscreen. Live and on-demand classes with world-class instructors.",
            "price": 2495.00,
            "ratings": 4.4,
            "reviews": 1876,
            "image": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b",
            "badge": "Fitness",
            "sku": "PLT-BIKE-PLUS",
            "specifications": {
                "Screen": "23.8-inch HD touchscreen, rotates 180°",
                "Resistance": "Magnetic, 100 levels",
                "Metrics": "Cadence, output, heart rate, Strive Score",
                "Content": "10,000+ cycling, strength, yoga classes",
                "Audio": "2x 10W front speakers + 3W rear woofers",
                "Connectivity": "Wi-Fi, Bluetooth, ANT+",
                "Dimensions": "4' L x 2' W",
                "Weight Limit": "297 lbs (135 kg)"
            }
        },
        {
            "id": "sport-002",
            "name": "Yeti Rambler 30oz Tumbler",
            "categoryId": "Sports",
            "description": "Insulated stainless steel tumbler that keeps drinks cold for 24hrs or hot for 12hrs. Durable double-wall vacuum construction.",
            "price": 39.99,
            "ratings": 4.9,
            "reviews": 6234,
            "image": "https://images.unsplash.com/photo-1523362628745-0c100150b504",
            "badge": "Outdoor",
            "sku": "YETI-RAM-30-BLK",
            "specifications": {
                "Capacity": "30 fl oz (887ml)",
                "Insulation": "Double-wall vacuum",
                "Material": "18/8 stainless steel",
                "Lid": "MagSlider magnetic lid (BPA-free)",
                "Dishwasher Safe": "Yes",
                "Hot Retention": "12+ hours",
                "Cold Retention": "24+ hours",
                "Colors": "25+ options"
            }
        },
        {
            "id": "sport-003",
            "name": "TRX All-in-One Suspension Trainer",
            "categoryId": "Sports",
            "description": "Professional-grade suspension training system for total body workouts. Used by military, athletes, and trainers worldwide.",
            "price": 179.99,
            "ratings": 4.7,
            "reviews": 2156,
            "image": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b",
            "badge": "Pro",
            "sku": "TRX-AIO-HOME",
            "specifications": {
                "Straps": "Commercial-grade nylon",
                "Weight Capacity": "350 lbs (159 kg)",
                "Anchor Options": "Door, mount, or outdoor",
                "Adjustability": "5.5' - 9' strap length",
                "Handles": "Rubber grip with foot cradles",
                "Included": "Suspension anchor, door anchor, 6 workouts",
                "Portability": "Weighs under 2 lbs",
                "Warranty": "1 year"
            }
        },
        {
            "id": "sport-004",
            "name": "Garmin Fenix 7X Solar",
            "categoryId": "Sports",
            "description": "Premium multisport GPS watch with solar charging. Built for endurance athletes with advanced training metrics.",
            "price": 899.99,
            "ratings": 4.8,
            "reviews": 1543,
            "image": "https://images.unsplash.com/photo-1510017803434-a899398421b3",
            "badge": "Iconic",
            "sku": "GAR-FNX7X-SOL",
            "specifications": {
                "Display": "1.4-inch solar-charging, 280x280",
                "Battery": "Up to 37 days (28 days + solar)",
                "GPS": "Multi-band GNSS, SatIQ",
                "Sports Modes": "30+ built-in sports apps",
                "Training Features": "Training Status, Recovery, Load",
                "Health Metrics": "HRV, Pulse Ox, Body Battery",
                "Maps": "TopoActive maps, ski resort maps",
                "Water Rating": "10 ATM"
            }
        }
    ]
    
    # Check if specifications column exists, add if not
    cursor.execute("PRAGMA table_info(products)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'sku' not in columns:
        cursor.execute("ALTER TABLE products ADD COLUMN sku TEXT")
    if 'specifications' not in columns:
        cursor.execute("ALTER TABLE products ADD COLUMN specifications TEXT")
    
    for product in products:
        specs_json = json.dumps(product.get("specifications", {}))
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
            product["badge"],
            product.get("sku", ""),
            specs_json
        ))
    
    conn.commit()
    conn.close()
    print(f"Added {len(products)} products to database with rich specifications!")

if __name__ == "__main__":
    populate_products()