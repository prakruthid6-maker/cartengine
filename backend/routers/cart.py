"""
Cart API router for managing shopping cart.

Provides REST endpoints for cart operations that sync with
the same database the AI agent uses.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid

from repos.products_repo import ProductRepo
from models.data_models import CartItem

router = APIRouter()

# Initialize repository
cart_repo = ProductRepo("products.db")


# ============ Request Models ============

class AddToCartRequest(BaseModel):
    product_id: str
    user_id: str = "guest"
    quantity: int = 1


class UpdateCartRequest(BaseModel):
    product_id: str
    user_id: str = "guest"
    quantity: int


class RemoveFromCartRequest(BaseModel):
    product_id: str
    user_id: str = "guest"


# ============ Endpoints ============

@router.get("/")
async def get_cart(user_id: str = "guest"):
    """
    Get cart contents for a user.
    Returns all items with product details, quantities, and totals.
    """
    await cart_repo.init_db()
    items = await cart_repo.get_cart(user_id)
    
    if not items:
        return {
            "user_id": user_id,
            "items": [],
            "total_items": 0,
            "subtotal": 0.0,
            "total_price": 0.0,
            "message": "Cart is empty"
        }
    
    total_items = sum(item.quantity for item in items)
    subtotal = sum((item.product_price or 0) * item.quantity for item in items)
    
    return {
        "user_id": user_id,
        "items": [
            {
                "cart_item_id": item.cart_item_id,
                "product_id": item.product_id,
                "name": item.product_name,
                "quantity": item.quantity,
                "unit_price": item.product_price,
                "line_total": round((item.product_price or 0) * item.quantity, 2)
            }
            for item in items
        ],
        "total_items": total_items,
        "subtotal": round(subtotal, 2),
        "total_price": round(subtotal, 2),
        "message": f"Cart has {total_items} item(s)"
    }


@router.post("/add")
async def add_to_cart(request: AddToCartRequest):
    """
    Add a product to cart.
    Validates stock before adding.
    """
    await cart_repo.init_db()
    
    # Check stock
    stock_info = await cart_repo.check_stock(request.product_id)
    if not stock_info["available"]:
        raise HTTPException(status_code=400, detail="Product is out of stock")
    
    if stock_info["quantity"] < request.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Only {stock_info['quantity']} items available"
        )
    
    # Create cart item
    cart_item = CartItem(
        cart_item_id=f"CART-{uuid.uuid4().hex[:8].upper()}",
        user_id=request.user_id,
        product_id=request.product_id,
        quantity=request.quantity
    )
    
    await cart_repo.add_to_cart(cart_item)
    
    return {
        "status": "success",
        "message": f"Added {request.quantity} x {stock_info['product_name']} to cart",
        "product_id": request.product_id,
        "user_id": request.user_id
    }


@router.put("/update")
async def update_cart_item(request: UpdateCartRequest):
    """
    Update quantity of an item in cart.
    Set quantity to 0 to remove the item.
    """
    await cart_repo.init_db()
    
    if request.quantity <= 0:
        # Remove item
        result = await cart_repo.remove_from_cart(request.user_id, request.product_id)
        if result > 0:
            return {"status": "success", "message": "Item removed from cart"}
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    result = await cart_repo.update_cart_quantity(
        request.user_id,
        request.product_id,
        request.quantity
    )
    
    if result > 0:
        return {"status": "success", "message": f"Quantity updated to {request.quantity}"}
    
    raise HTTPException(status_code=404, detail="Item not found in cart")


@router.post("/update")
async def update_cart_item_post(request: dict):
    """
    POST version of update endpoint for frontend compatibility.
    Handles 'action' parameter for add/remove operations.
    """
    await cart_repo.init_db()
    
    user_id = request.get("user_id", "guest")
    product_id = request.get("product_id")
    quantity = request.get("quantity", 1)
    action = request.get("action", "add")
    
    if not product_id:
        raise HTTPException(status_code=400, detail="product_id is required")
    
    if action == "add":
        # Check if item already in cart
        cart_items = await cart_repo.get_cart(user_id)
        existing_item = next((item for item in cart_items if item.product_id == product_id), None)
        
        if existing_item:
            # Update quantity (add to existing)
            new_quantity = existing_item.quantity + quantity
            result = await cart_repo.update_cart_quantity(user_id, product_id, new_quantity)
        else:
            # Add new item
            stock_info = await cart_repo.check_stock(product_id)
            if not stock_info["available"]:
                raise HTTPException(status_code=400, detail="Product is out of stock")
            
            cart_item = CartItem(
                cart_item_id=f"CART-{uuid.uuid4().hex[:8].upper()}",
                user_id=user_id,
                product_id=product_id,
                quantity=quantity
            )
            await cart_repo.add_to_cart(cart_item)
            
        return {"status": "success", "message": "Cart updated successfully"}
    
    elif action == "remove":
        result = await cart_repo.remove_from_cart(user_id, product_id)
        if result > 0:
            return {"status": "success", "message": "Item removed from cart"}
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    raise HTTPException(status_code=400, detail="Invalid action")


@router.delete("/remove")
async def remove_from_cart(product_id: str, user_id: str = "guest"):
    """
    Remove an item from cart.
    """
    await cart_repo.init_db()
    result = await cart_repo.remove_from_cart(user_id, product_id)
    
    if result > 0:
        return {"status": "success", "message": "Item removed from cart"}
    
    raise HTTPException(status_code=404, detail="Item not found in cart")


@router.delete("/clear")
async def clear_cart(user_id: str = "guest"):
    """
    Clear all items from cart.
    """
    await cart_repo.init_db()
    count = await cart_repo.clear_cart(user_id)
    
    return {
        "status": "success",
        "message": f"Removed {count} item(s) from cart",
        "items_removed": count
    }
