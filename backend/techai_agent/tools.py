import requests, os, random, json
from typing import Dict, List, Optional
from models.data_models import Product, Seller, Order, Payment, OrderTracking, Wishlist, Review, Coupon, CartItem, Cart
from services.product_service import ProductService
from repos.products_repo import ProductRepo
import uuid
from datetime import datetime, timedelta


product_service = ProductService("products.db")
product_repo = ProductRepo("products.db")

async def fetch_products(query: str) ->  dict:
    return await product_service.get_products_by_query(query= "SELECT * from c")

async def search_products_by_category(category: str) -> dict:
    """Search products by category (Electronics, Fashion, Home, Sports, Clothing, Books, etc)."""
    products = await product_service.get_products_by_query("SELECT * FROM c")
    filtered = [p for p in products if p.categoryId == category]
    return {
        "category": category, 
        "result_count": len(filtered), 
        "products": [
            {
                "id": p.id, 
                "name": p.name, 
                "price": p.price, 
                "rating": p.ratings,
                "image": p.image or "",
                "description": p.description or ""
            } for p in filtered
        ]
    }

async def filter_products_by_price(min_price: float, max_price: float) -> dict:
    """Filter products within a price range."""
    return await product_service.get_products_by_query(f"SELECT * FROM c WHERE price BETWEEN {min_price} AND {max_price}")

async def get_product_details(product_id: str) -> dict:
    """Get detailed information about a specific product."""
    return await product_service.get_products_by_query(f"SELECT * FROM c WHERE id = '{product_id}'")

async def get_top_rated_products(min_rating: float = 4.0) -> dict:
    """Get products with high customer ratings."""
    return await product_service.get_products_by_query(f"SELECT * FROM c WHERE rating >= {min_rating} ORDER BY rating DESC")

async def get_products_on_sale() -> dict:
    """Get products currently on sale or with active discounts."""
    await product_repo.init_db()
    products = await product_repo.get_discounted_products()
    return {
        "sale_count": len(products),
        "products": [{"id": p.id, "name": p.name, "price": p.price, "original_price": p.original_price, "discount_percent": p.discount_percent, "savings": round((p.original_price or p.price) - p.price, 2)} for p in products]
    }

# ============ PERSISTENT CART FUNCTIONS (FIXED) ============

async def add_to_cart(product_id: str, user_id: str = "guest", quantity: int = 1) -> dict:
    """Add a product to the shopping cart. Cart persists in database."""
    await product_repo.init_db()
    
    # Check if product exists and has stock
    stock_info = await product_repo.check_stock(product_id)
    if not stock_info["available"]:
        return {"status": "error", "message": f"Product is out of stock"}
    
    if stock_info["quantity"] < quantity:
        return {"status": "error", "message": f"Only {stock_info['quantity']} items available"}
    
    # Create cart item
    cart_item = CartItem(
        cart_item_id=f"CART-{uuid.uuid4().hex[:8].upper()}",
        user_id=user_id,
        product_id=product_id,
        quantity=quantity
    )
    await product_repo.add_to_cart(cart_item)
    
    return {"status": "success", "message": f"Added {quantity} x {stock_info['product_name']} to cart", "product_id": product_id, "user_id": user_id}

async def get_cart_summary(user_id: str = "guest") -> dict:
    """Get current shopping cart summary with all items and totals."""
    await product_repo.init_db()
    items = await product_repo.get_cart(user_id)
    
    if not items:
        return {"user_id": user_id, "items": [], "total_items": 0, "subtotal": 0.0, "total_price": 0.0, "message": "Cart is empty"}
    
    total_items = sum(item.quantity for item in items)
    subtotal = sum((item.product_price or 0) * item.quantity for item in items)
    
    return {
        "user_id": user_id,
        "items": [{"product_id": item.product_id, "name": item.product_name, "quantity": item.quantity, "unit_price": item.product_price, "line_total": round((item.product_price or 0) * item.quantity, 2)} for item in items],
        "total_items": total_items,
        "subtotal": round(subtotal, 2),
        "total_price": round(subtotal, 2),
        "message": f"Cart has {total_items} item(s)"
    }

async def update_cart_item(product_id: str, quantity: int, user_id: str = "guest") -> dict:
    """Update quantity of an item in cart. Set quantity to 0 to remove."""
    await product_repo.init_db()
    result = await product_repo.update_cart_quantity(user_id, product_id, quantity)
    if result > 0:
        if quantity <= 0:
            return {"status": "success", "message": "Item removed from cart"}
        return {"status": "success", "message": f"Quantity updated to {quantity}"}
    return {"status": "error", "message": "Item not found in cart"}

async def remove_from_cart_tool(product_id: str, user_id: str = "guest") -> dict:
    """Remove an item from the shopping cart."""
    await product_repo.init_db()
    result = await product_repo.remove_from_cart(user_id, product_id)
    if result > 0:
        return {"status": "success", "message": "Item removed from cart"}
    return {"status": "error", "message": "Item not found in cart"}

async def clear_cart_tool(user_id: str = "guest") -> dict:
    """Clear all items from the shopping cart."""
    await product_repo.init_db()
    count = await product_repo.clear_cart(user_id)
    return {"status": "success", "message": f"Removed {count} item(s) from cart", "items_removed": count}

# ============ INVENTORY FUNCTIONS (FIXED) ============

async def check_product_availability(product_id: str) -> dict:
    """Check if a product is in stock with real inventory data."""
    await product_repo.init_db()
    return await product_repo.check_stock(product_id)

async def update_inventory_tool(product_id: str, quantity_change: int) -> dict:
    """Update product inventory. Use negative values to decrease stock."""
    await product_repo.init_db()
    success = await product_repo.update_stock(product_id, quantity_change)
    if success:
        new_stock = await product_repo.check_stock(product_id)
        return {"status": "success", "product_id": product_id, "new_stock": new_stock["quantity"], "message": f"Stock updated by {quantity_change}"}
    return {"status": "error", "message": "Failed to update stock. Product not found or insufficient stock."}

async def set_product_discount(product_id: str, discount_percent: float) -> dict:
    """Set a discount percentage for a product (0-100)."""
    await product_repo.init_db()
    if discount_percent < 0 or discount_percent > 100:
        return {"status": "error", "message": "Discount must be between 0 and 100"}
    success = await product_repo.set_discount(product_id, discount_percent)
    if success:
        return {"status": "success", "product_id": product_id, "discount_percent": discount_percent, "message": f"Discount of {discount_percent}% applied"}
    return {"status": "error", "message": "Product not found"}

def compare_products(product_ids: List[str]) -> dict:
    """Compare multiple products side by side (basic version)."""
    return {"comparison": f"Comparing {len(product_ids)} products", "product_ids": product_ids}

def get_shipping_info(product_id: str, zip_code: Optional[str] = None) -> dict:
    """Get shipping information for a product."""
    # Calculate shipping based on zip code distance (simplified)
    base_cost = 5.99
    days = "3-5"
    if zip_code:
        # Premium zip codes get faster shipping
        if zip_code.startswith(("1", "2", "3")):
            days = "1-2"
            base_cost = 9.99
        elif zip_code.startswith(("4", "5", "6")):
            days = "2-3"
            base_cost = 7.99
    return {"product_id": product_id, "zip_code": zip_code, "shipping_cost": base_cost, "estimated_delivery": f"{days} business days", "free_shipping_eligible": base_cost < 8}

async def apply_coupon(coupon_code: str, user_id: str = "guest") -> dict:
    """Apply a coupon code to the current cart."""
    await product_repo.init_db()
    coupon = await product_repo.get_coupon(coupon_code)
    if not coupon:
        return {"valid": False, "message": "Invalid coupon code"}
    
    # Check expiry
    from datetime import datetime
    try:
        expiry = datetime.fromisoformat(coupon.expiry_date)
        if expiry < datetime.now():
            return {"valid": False, "message": "Coupon has expired"}
    except:
        pass
    
    if coupon.status != "active":
        return {"valid": False, "message": "Coupon is not active"}
    
    # Get cart and apply discount
    cart = await get_cart_summary(user_id)
    if cart["total_items"] == 0:
        return {"valid": False, "message": "Cart is empty"}
    
    discount_amount = cart["subtotal"] * (coupon.discount_percent / 100)
    new_total = cart["subtotal"] - discount_amount
    
    return {
        "valid": True,
        "coupon_code": coupon_code,
        "discount_percent": coupon.discount_percent,
        "discount_amount": round(discount_amount, 2),
        "original_total": cart["subtotal"],
        "new_total": round(new_total, 2),
        "message": f"Coupon applied! You saved ${round(discount_amount, 2)}"
    }

async def add_new_product(product_id: str, name: str, category: str, description: str, price: float, ratings: float = 0.0, reviews: int = 0, image: str = "", badge: str = "", stock_quantity: int = 100):
    """Add a new product to the catalog with inventory."""
    product = Product(id=product_id, name=name, categoryId=category, description=description, price=price, ratings=ratings, reviews=reviews, image=image, badge=badge, stock_quantity=stock_quantity)
    return await product_service.create_product(product)

async def delete_product(product_id: str, category: str):
    """Delete a product from the catalog."""
    return await product_service.delete_product(product_id, category)

async def update_product(product_id: str, category: str, name: Optional[str] = None, description: Optional[str] = None, price: Optional[float] = None, ratings: Optional[float] = None, reviews: Optional[int] = None, image: Optional[str] = None, badge: Optional[str] = None):
    """Update an existing product's information."""
    existing = await product_service.get_product(product_id, category)
    product = Product(
        id=product_id,
        name=name or existing.name,
        categoryId=category,
        description=description or existing.description,
        price=price if price is not None else existing.price,
        ratings=ratings if ratings is not None else existing.ratings,
        reviews=reviews if reviews is not None else existing.reviews,
        image=image or existing.image,
        badge=badge or existing.badge
    )
    return await product_service.update_product(product)

async def get_total_products_count() -> dict:
    """Get the total number of products in the catalog."""
    products = await product_service.get_products_by_query("SELECT * FROM c")
    return {"total_products": len(products)}

async def get_products_count_by_category(category: str) -> dict:
    """Get the number of products in a specific category."""
    products = await product_service.get_products_by_query(f"SELECT * FROM c WHERE category = '{category}'")
    return {"category": category, "count": len(products)}

async def get_category_with_highest_rating() -> dict:
    """Get the category with the highest average rating."""
    products = await product_service.get_products_by_query("SELECT * FROM c")
    category_ratings = {}
    for p in products:
        if p.categoryId not in category_ratings:
            category_ratings[p.categoryId] = []
        category_ratings[p.categoryId].append(p.ratings)
    
    category_avg = {cat: sum(ratings)/len(ratings) for cat, ratings in category_ratings.items()}
    highest_cat = max(category_avg, key=category_avg.get)
    return {"category": highest_cat, "average_rating": category_avg[highest_cat]}

async def get_product_with_most_reviews() -> dict:
    """Get the product with the maximum number of reviews."""
    products = await product_service.get_products_by_query("SELECT * FROM c")
    max_product = max(products, key=lambda p: p.reviews)
    return {"product_id": max_product.id, "product_name": max_product.name, "reviews": max_product.reviews}

async def get_most_recently_added_product() -> dict:
    """Get the product that was added most recently."""
    products = await product_service.get_products_by_query("SELECT * FROM c")
    recent_product = max(products, key=lambda p: p.created_at or "")
    return {"product_id": recent_product.id, "product_name": recent_product.name, "created_at": recent_product.created_at}

async def get_products_added_last_7_days() -> dict:
    """List all products added in the last 7 days."""
    from datetime import datetime, timedelta
    products = await product_service.get_products_by_query("SELECT * FROM c")
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_products = [p for p in products if p.created_at and datetime.fromisoformat(p.created_at.replace('Z', '+00:00')) > seven_days_ago]
    return {"count": len(recent_products), "products": [{"id": p.id, "name": p.name, "created_at": p.created_at} for p in recent_products]}

async def get_category_with_most_additions_this_month() -> dict:
    """Get the product category with the most new additions this month."""
    from datetime import datetime
    products = await product_service.get_products_by_query("SELECT * FROM c")
    current_month = datetime.now().month
    current_year = datetime.now().year
    month_products = [p for p in products if p.created_at and datetime.fromisoformat(p.created_at.replace('Z', '+00:00')).month == current_month and datetime.fromisoformat(p.created_at.replace('Z', '+00:00')).year == current_year]
    
    category_counts = {}
    for p in month_products:
        category_counts[p.categoryId] = category_counts.get(p.categoryId, 0) + 1
    
    if not category_counts:
        return {"message": "No products added this month"}
    
    top_category = max(category_counts, key=category_counts.get)
    return {"category": top_category, "additions_count": category_counts[top_category]}

async def add_seller(seller_id: str, name: str, location: str, rating: float) -> dict:
    """Add a new seller to the system."""
    await product_repo.init_db()
    seller = Seller(seller_id=seller_id, name=name, location=location, rating=rating)
    await product_repo.insert_seller(seller)
    return {"seller_id": seller_id, "name": name, "status": "added"}

async def get_products_count_by_seller(seller_name: str) -> dict:
    """Get the number of products sold by a specific seller."""
    products = await product_service.get_products_by_query("SELECT * FROM c")
    await product_repo.init_db()
    sellers = await product_repo.get_all_sellers()
    seller = next((s for s in sellers if s.name == seller_name), None)
    if not seller:
        return {"message": f"Seller '{seller_name}' not found"}
    seller_products = [p for p in products if p.seller_id == seller.seller_id]
    return {"seller_name": seller_name, "product_count": len(seller_products)}

async def get_seller_with_most_5star_products() -> dict:
    """Get the seller with the most 5-star rated products."""
    products = await product_service.get_products_by_query("SELECT * FROM c")
    await product_repo.init_db()
    sellers = await product_repo.get_all_sellers()
    
    seller_5star_counts = {}
    for p in products:
        if p.ratings >= 5.0 and p.seller_id:
            seller_5star_counts[p.seller_id] = seller_5star_counts.get(p.seller_id, 0) + 1
    
    if not seller_5star_counts:
        return {"message": "No 5-star products found"}
    
    top_seller_id = max(seller_5star_counts, key=seller_5star_counts.get)
    top_seller = next((s for s in sellers if s.seller_id == top_seller_id), None)
    return {"seller_name": top_seller.name if top_seller else top_seller_id, "five_star_count": seller_5star_counts[top_seller_id]}

async def get_location_with_highest_product_count() -> dict:
    """Get the location with the highest product count overall."""
    products = await product_service.get_products_by_query("SELECT * FROM c")
    await product_repo.init_db()
    sellers = await product_repo.get_all_sellers()
    
    location_counts = {}
    for p in products:
        if p.seller_id:
            seller = next((s for s in sellers if s.seller_id == p.seller_id), None)
            if seller:
                location_counts[seller.location] = location_counts.get(seller.location, 0) + 1
    
    if not location_counts:
        return {"message": "No products with seller locations found"}
    
    top_location = max(location_counts, key=location_counts.get)
    return {"location": top_location, "product_count": location_counts[top_location]}

async def create_order(product_id: str, quantity: int, user_id: str, delivery_address: str) -> dict:
    """Place an order for a product."""
    await product_repo.init_db()
    products = await product_service.get_products_by_query(f"SELECT * FROM c WHERE id = '{product_id}'")
    if not products:
        return {"error": "Product not found"}
    product = products[0]
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    total_price = product.price * quantity
    order = Order(order_id=order_id, product_id=product_id, user_id=user_id, quantity=quantity, total_price=total_price, status="Order Placed", delivery_address=delivery_address)
    await product_repo.insert_order(order)
    return {"order_id": order_id, "total_price": total_price, "status": "Order Placed", "message": "Order created successfully"}

async def get_order_details(order_id: str) -> dict:
    """Get details of a specific order."""
    await product_repo.init_db()
    order = await product_repo.get_order(order_id)
    if not order:
        return {"error": "Order not found"}
    return {"order_id": order.order_id, "product_id": order.product_id, "quantity": order.quantity, "total_price": order.total_price, "status": order.status, "delivery_address": order.delivery_address, "order_date": order.order_date}

async def get_user_orders(user_id: str) -> dict:
    """Get all orders for a specific user."""
    await product_repo.init_db()
    orders = await product_repo.get_user_orders(user_id)
    return {"user_id": user_id, "order_count": len(orders), "orders": [{"order_id": o.order_id, "product_id": o.product_id, "total_price": o.total_price, "status": o.status, "order_date": o.order_date} for o in orders]}

async def process_payment(order_id: str, payment_method: str) -> dict:
    """Process payment for an order."""
    await product_repo.init_db()
    order = await product_repo.get_order(order_id)
    if not order:
        return {"error": "Order not found"}
    payment_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
    payment = Payment(payment_id=payment_id, order_id=order_id, amount=order.total_price, method=payment_method, status="Completed")
    await product_repo.insert_payment(payment)
    await product_repo.update_order_status(order_id, "Processing")
    return {"payment_id": payment_id, "order_id": order_id, "amount": order.total_price, "status": "Completed", "message": "Payment processed successfully"}

async def get_payment_status(order_id: str) -> dict:
    """Get payment status for an order."""
    await product_repo.init_db()
    payment = await product_repo.get_payment(order_id)
    if not payment:
        return {"message": "No payment found for this order"}
    return {"payment_id": payment.payment_id, "order_id": payment.order_id, "amount": payment.amount, "method": payment.method, "status": payment.status, "timestamp": payment.timestamp}

async def track_order(order_id: str) -> dict:
    """Get real-time tracking information for an order."""
    await product_repo.init_db()
    order = await product_repo.get_order(order_id)
    if not order:
        return {"error": "Order not found", "message": f"No order found with ID {order_id}"}
    tracking_history = await product_repo.get_tracking_history(order_id)
    return {"order_id": order_id, "product_id": order.product_id, "quantity": order.quantity, "total_price": order.total_price, "current_status": order.status, "delivery_address": order.delivery_address, "order_date": order.order_date, "tracking_history": [{"status": t.status, "location": t.location, "timestamp": t.timestamp} for t in tracking_history] if tracking_history else []}

async def update_order_status(order_id: str, status: str, location: str) -> dict:
    """Update delivery status of an order."""
    await product_repo.init_db()
    await product_repo.update_order_status(order_id, status)
    tracking_id = f"TRK-{uuid.uuid4().hex[:8].upper()}"
    tracking = OrderTracking(tracking_id=tracking_id, order_id=order_id, status=status, location=location)
    await product_repo.insert_tracking(tracking)
    return {"order_id": order_id, "status": status, "location": location, "message": "Order status updated"}

async def get_estimated_delivery(order_id: str) -> dict:
    """Get estimated delivery date for an order."""
    await product_repo.init_db()
    order = await product_repo.get_order(order_id)
    if not order:
        return {"error": "Order not found"}
    order_date = datetime.fromisoformat(order.order_date) if order.order_date else datetime.now()
    estimated_delivery = order_date + timedelta(days=5)
    return {"order_id": order_id, "estimated_delivery": estimated_delivery.strftime("%Y-%m-%d"), "days_remaining": (estimated_delivery - datetime.now()).days}

async def get_delivery_history(order_id: str) -> dict:
    """Get complete delivery status timeline for an order."""
    await product_repo.init_db()
    tracking_history = await product_repo.get_tracking_history(order_id)
    return {"order_id": order_id, "history_count": len(tracking_history), "history": [{"status": t.status, "location": t.location, "timestamp": t.timestamp} for t in tracking_history]}

async def recommend_products_by_budget(budget: float, category: Optional[str] = None) -> dict:
    """Recommend products within a specific budget."""
    products = await product_service.get_products_by_query("SELECT * FROM c")
    filtered = [p for p in products if p.price <= budget]
    if category:
        filtered = [p for p in filtered if p.categoryId == category]
    sorted_products = sorted(filtered, key=lambda p: p.ratings, reverse=True)[:10]
    return {
        "budget": budget, 
        "category": category, 
        "recommendations": [
            {
                "id": p.id, 
                "name": p.name, 
                "price": p.price, 
                "rating": p.ratings,
                "image": p.image or "",
                "description": p.description or ""
            } for p in sorted_products
        ]
    }

async def recommend_similar_products(product_id: str) -> dict:
    """Recommend similar products based on category and price range."""
    products = await product_service.get_products_by_query(f"SELECT * FROM c WHERE id = '{product_id}'")
    if not products:
        return {"error": "Product not found"}
    product = products[0]
    all_products = await product_service.get_products_by_query("SELECT * FROM c")
    similar = [p for p in all_products if p.categoryId == product.categoryId and p.id != product_id and abs(p.price - product.price) <= product.price * 0.3]
    sorted_similar = sorted(similar, key=lambda p: p.ratings, reverse=True)[:5]
    return {"product_id": product_id, "similar_products": [{"id": p.id, "name": p.name, "price": p.price, "rating": p.ratings} for p in sorted_similar]}

async def recommend_by_preferences(min_rating: float, max_price: float, category: Optional[str] = None) -> dict:
    """Get personalized product recommendations based on preferences."""
    products = await product_service.get_products_by_query("SELECT * FROM c")
    filtered = [p for p in products if p.ratings >= min_rating and p.price <= max_price]
    if category:
        filtered = [p for p in filtered if p.categoryId == category]
    sorted_products = sorted(filtered, key=lambda p: (p.ratings, -p.price), reverse=True)[:10]
    return {"preferences": {"min_rating": min_rating, "max_price": max_price, "category": category}, "recommendations": [{"id": p.id, "name": p.name, "price": p.price, "rating": p.ratings} for p in sorted_products]}

async def get_best_deals() -> dict:
    """Get top deals and highly rated products."""
    products = await product_service.get_products_by_query("SELECT * FROM c")
    best_deals = sorted(products, key=lambda p: (p.ratings / (p.price + 1)), reverse=True)[:5]
    return {"best_deals": [{"id": p.id, "name": p.name, "price": p.price, "rating": p.ratings, "value_score": round(p.ratings / (p.price + 1), 2)} for p in best_deals]}

async def add_to_wishlist_tool(user_id: str, product_id: str) -> dict:
    """Add a product to user's wishlist."""
    await product_repo.init_db()
    wishlist_id = f"WISH-{uuid.uuid4().hex[:8].upper()}"
    wishlist = Wishlist(wishlist_id=wishlist_id, user_id=user_id, product_id=product_id)
    await product_repo.add_to_wishlist(wishlist)
    return {"message": "Product added to wishlist", "wishlist_id": wishlist_id}

async def get_wishlist_tool(user_id: str) -> dict:
    """Get user's wishlist."""
    await product_repo.init_db()
    wishlist = await product_repo.get_wishlist(user_id)
    return {"user_id": user_id, "wishlist_count": len(wishlist), "items": [{"product_id": w.product_id, "added_date": w.added_date} for w in wishlist]}

async def remove_from_wishlist_tool(user_id: str, product_id: str) -> dict:
    """Remove a product from user's wishlist."""
    await product_repo.init_db()
    removed = await product_repo.remove_from_wishlist(user_id, product_id)
    if removed:
        return {"message": "Product removed from wishlist"}
    return {"message": "Product not found in wishlist"}

async def add_review_tool(product_id: str, user_id: str, rating: float, comment: str) -> dict:
    """Add a review for a product."""
    await product_repo.init_db()
    review_id = f"REV-{uuid.uuid4().hex[:8].upper()}"
    review = Review(review_id=review_id, product_id=product_id, user_id=user_id, rating=rating, comment=comment)
    await product_repo.add_review(review)
    return {"message": "Review added successfully", "review_id": review_id}

async def get_product_reviews_tool(product_id: str) -> dict:
    """Get all reviews for a product."""
    await product_repo.init_db()
    reviews = await product_repo.get_product_reviews(product_id)
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
    return {"product_id": product_id, "review_count": len(reviews), "average_rating": round(avg_rating, 2), "reviews": [{"user_id": r.user_id, "rating": r.rating, "comment": r.comment, "date": r.review_date} for r in reviews]}

async def create_coupon_tool(coupon_code: str, discount_percent: float, expiry_date: str) -> dict:
    """Create a new coupon code."""
    await product_repo.init_db()
    coupon = Coupon(coupon_code=coupon_code, discount_percent=discount_percent, expiry_date=expiry_date, status="active")
    await product_repo.insert_coupon(coupon)
    return {"message": "Coupon created", "coupon_code": coupon_code, "discount": f"{discount_percent}%"}

async def validate_coupon_tool(coupon_code: str) -> dict:
    """Validate a coupon code."""
    await product_repo.init_db()
    coupon = await product_repo.get_coupon(coupon_code)
    if not coupon:
        return {"valid": False, "message": "Coupon not found"}
    expiry = datetime.fromisoformat(coupon.expiry_date)
    if expiry < datetime.now():
        return {"valid": False, "message": "Coupon expired"}
    if coupon.status != "active":
        return {"valid": False, "message": "Coupon inactive"}
    return {"valid": True, "discount_percent": coupon.discount_percent, "expiry_date": coupon.expiry_date}

async def search_products_advanced(query: str, min_price: Optional[float] = None, max_price: Optional[float] = None, min_rating: Optional[float] = None, category: Optional[str] = None) -> dict:
    """Advanced product search with multiple filters."""
    products = await product_service.get_products_by_query("SELECT * FROM c")
    filtered = [p for p in products if query.lower() in p.name.lower() or query.lower() in p.description.lower()]
    if min_price:
        filtered = [p for p in filtered if p.price >= min_price]
    if max_price:
        filtered = [p for p in filtered if p.price <= max_price]
    if min_rating:
        filtered = [p for p in filtered if p.ratings >= min_rating]
    if category:
        filtered = [p for p in filtered if p.categoryId == category]
    return {"query": query, "result_count": len(filtered), "products": [{"id": p.id, "name": p.name, "price": p.price, "rating": p.ratings, "image": p.image or "", "description": p.description or ""} for p in filtered[:20]]}

async def get_trending_products() -> dict:
    """Get trending products based on ratings and reviews."""
    products = await product_service.get_products_by_query("SELECT * FROM c")
    trending = sorted(products, key=lambda p: (p.ratings * p.reviews), reverse=True)[:10]
    return {"trending_products": [{"id": p.id, "name": p.name, "price": p.price, "rating": p.ratings, "reviews": p.reviews, "image": p.image or "", "description": p.description or ""} for p in trending]}

async def cancel_order_tool(order_id: str) -> dict:
    """Cancel an order if it hasn't been delivered yet."""
    await product_repo.init_db()
    order = await product_repo.get_order(order_id)
    if not order:
        return {"error": "Order not found", "message": f"No order found with ID {order_id}"}
    if order.status in ['Delivered', 'Cancelled']:
        return {"error": "Cannot cancel", "message": f"Order is already {order.status}"}
    await product_repo.update_order_status(order_id, 'Cancelled')
    return {"order_id": order_id, "status": "Cancelled", "message": "Order cancelled successfully"}

async def filter_products_by_category_and_price(category: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None, badge: Optional[str] = None) -> dict:
    """Filter products by category, price range, and badge."""
    products = await product_service.get_products_by_query("SELECT * FROM c")
    filtered = products
    if category:
        filtered = [p for p in filtered if p.categoryId == category]
    if min_price is not None:
        filtered = [p for p in filtered if p.price >= min_price]
    if max_price is not None:
        filtered = [p for p in filtered if p.price <= max_price]
    if badge:
        filtered = [p for p in filtered if p.badge == badge]
    return {"filters": {"category": category, "min_price": min_price, "max_price": max_price, "badge": badge}, "result_count": len(filtered), "products": [{"id": p.id, "name": p.name, "category": p.categoryId, "price": p.price, "rating": p.ratings, "badge": p.badge, "image": p.image or "", "description": p.description or ""} for p in filtered]}

async def get_all_categories() -> dict:
    """Get list of all product categories."""
    products = await product_service.get_products_by_query("SELECT * FROM c")
    categories = list(set(p.categoryId for p in products))
    return {"categories": categories, "count": len(categories)}

async def get_all_badges() -> dict:
    """Get list of all product badges."""
    products = await product_service.get_products_by_query("SELECT * FROM c")
    badges = list(set(p.badge for p in products if p.badge))
    return {"badges": badges, "count": len(badges)}

async def get_analytics_summary() -> dict:
    """Get analytics summary with product statistics."""
    products = await product_service.get_products_by_query("SELECT * FROM c")
    if not products:
        return {"message": "No products available"}
    total = len(products)
    avg_price = sum(p.price for p in products) / total
    avg_rating = sum(p.ratings for p in products) / total
    categories = list(set(p.categoryId for p in products))
    category_counts = {cat: len([p for p in products if p.categoryId == cat]) for cat in categories}
    return {"total_products": total, "average_price": round(avg_price, 2), "average_rating": round(avg_rating, 2), "total_categories": len(categories), "categories": category_counts, "price_range": {"min": min(p.price for p in products), "max": max(p.price for p in products)}}

async def compare_products_tool(product_ids: List[str]) -> dict:
    """Compare multiple products side by side."""
    products = await product_service.get_products_by_query("SELECT * FROM c")
    comparison = []
    for pid in product_ids:
        product = next((p for p in products if p.id == pid), None)
        if product:
            comparison.append({"id": product.id, "name": product.name, "price": product.price, "rating": product.ratings, "reviews": product.reviews, "category": product.categoryId, "badge": product.badge})
    return {"comparison": comparison, "count": len(comparison)}
