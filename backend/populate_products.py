import sqlite3
import json

def populate_products():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    
    # Clear existing products
    cursor.execute("DELETE FROM products")
    
    products = [
        # Electronics
        {
            "id": "elec-001",
            "name": "iPhone 15 Pro Max",
            "categoryId": "Electronics",
            "description": "Latest iPhone with titanium design and A17 Pro chip",
            "price": 1199.99,
            "ratings": 4.8,
            "reviews": 2847,
            "image": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab",
            "badge": "Best Seller"
        },
        {
            "id": "elec-002", 
            "name": "Samsung 65\" QLED 4K TV",
            "categoryId": "Electronics",
            "description": "Quantum Dot technology with HDR10+ support",
            "price": 899.99,
            "ratings": 4.6,
            "reviews": 1523,
            "image": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1",
            "badge": "Deal"
        },
        {
            "id": "elec-003",
            "name": "MacBook Air M3",
            "categoryId": "Electronics", 
            "description": "13-inch laptop with M3 chip and 18-hour battery",
            "price": 1299.99,
            "ratings": 4.9,
            "reviews": 892,
            "image": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8",
            "badge": "New"
        },
        {
            "id": "elec-004",
            "name": "Sony WH-1000XM5 Headphones",
            "categoryId": "Electronics",
            "description": "Wireless noise-canceling headphones",
            "price": 349.99,
            "ratings": 4.7,
            "reviews": 3421,
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e",
            "badge": "Top Rated"
        },
        
        # Fashion
        {
            "id": "fash-001",
            "name": "Nike Air Max 270",
            "categoryId": "Fashion",
            "description": "Men's running shoes with Max Air cushioning",
            "price": 149.99,
            "ratings": 4.5,
            "reviews": 2156,
            "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
            "badge": "Popular"
        },
        {
            "id": "fash-002",
            "name": "Levi's 501 Original Jeans",
            "categoryId": "Fashion",
            "description": "Classic straight-leg denim jeans",
            "price": 89.99,
            "ratings": 4.4,
            "reviews": 5847,
            "image": "https://images.unsplash.com/photo-1542272604-787c3835535d",
            "badge": "Classic"
        },
        {
            "id": "fash-003",
            "name": "Adidas Ultraboost 22",
            "categoryId": "Fashion",
            "description": "Women's running shoes with Boost midsole",
            "price": 179.99,
            "ratings": 4.6,
            "reviews": 1834,
            "image": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a",
            "badge": "Trending"
        },
        {
            "id": "fash-004",
            "name": "Ray-Ban Aviator Sunglasses",
            "categoryId": "Fashion",
            "description": "Classic aviator sunglasses with UV protection",
            "price": 154.99,
            "ratings": 4.8,
            "reviews": 3267,
            "image": "https://images.unsplash.com/photo-1572635196237-14b3f281503f",
            "badge": "Iconic"
        },
        
        # Home
        {
            "id": "home-001",
            "name": "Dyson V15 Detect Vacuum",
            "categoryId": "Home",
            "description": "Cordless vacuum with laser dust detection",
            "price": 749.99,
            "ratings": 4.7,
            "reviews": 1456,
            "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64",
            "badge": "Premium"
        },
        {
            "id": "home-002",
            "name": "Instant Pot Duo 7-in-1",
            "categoryId": "Home",
            "description": "Electric pressure cooker with 7 functions",
            "price": 99.99,
            "ratings": 4.6,
            "reviews": 8934,
            "image": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136",
            "badge": "Best Value"
        },
        {
            "id": "home-003",
            "name": "Philips Hue Smart Bulbs 4-Pack",
            "categoryId": "Home",
            "description": "Color-changing LED smart bulbs",
            "price": 199.99,
            "ratings": 4.5,
            "reviews": 2743,
            "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d",
            "badge": "Smart Home"
        },
        {
            "id": "home-004",
            "name": "KitchenAid Stand Mixer",
            "categoryId": "Home",
            "description": "5-quart tilt-head stand mixer",
            "price": 379.99,
            "ratings": 4.8,
            "reviews": 4521,
            "image": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136",
            "badge": "Chef's Choice"
        },
        
        # Sports
        {
            "id": "sport-001",
            "name": "Peloton Bike+",
            "categoryId": "Sports",
            "description": "Indoor exercise bike with rotating screen",
            "price": 2495.00,
            "ratings": 4.4,
            "reviews": 1876,
            "image": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b",
            "badge": "Fitness"
        },
        {
            "id": "sport-002",
            "name": "Yeti Rambler 30oz Tumbler",
            "categoryId": "Sports",
            "description": "Insulated stainless steel tumbler",
            "price": 39.99,
            "ratings": 4.9,
            "reviews": 6234,
            "image": "https://images.unsplash.com/photo-1523362628745-0c100150b504",
            "badge": "Outdoor"
        },
        {
            "id": "sport-003",
            "name": "Wilson Pro Staff Tennis Racket",
            "categoryId": "Sports",
            "description": "Professional tennis racket 97 sq in",
            "price": 249.99,
            "ratings": 4.6,
            "reviews": 892,
            "image": "https://images.unsplash.com/photo-1551698618-1dfe5d97d256",
            "badge": "Pro"
        },
        {
            "id": "sport-004",
            "name": "Hydro Flask Water Bottle 32oz",
            "categoryId": "Sports",
            "description": "Insulated water bottle keeps drinks cold 24hrs",
            "price": 44.99,
            "ratings": 4.7,
            "reviews": 3456,
            "image": "https://images.unsplash.com/photo-1602143407151-7111542de6e8",
            "badge": "Eco-Friendly"
        }
    ]
    
    for product in products:
        cursor.execute("""
            INSERT INTO products (id, name, categoryId, description, price, ratings, reviews, image, badge)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product["id"],
            product["name"], 
            product["categoryId"],
            product["description"],
            product["price"],
            product["ratings"],
            product["reviews"],
            product["image"],
            product["badge"]
        ))
    
    conn.commit()
    conn.close()
    print(f"Added {len(products)} products to database")

if __name__ == "__main__":
    populate_products()