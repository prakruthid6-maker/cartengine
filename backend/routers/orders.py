from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from repos.products_repo import ProductRepo
from models.data_models import Order, Payment
import uuid

router = APIRouter()
product_repo = ProductRepo("products.db")

class OrderRequest(BaseModel):
    product_id: str
    quantity: int
    user_id: str
    delivery_address: str
    payment_method: str = "Credit Card"

@router.post("/create")
async def create_order_api(request: OrderRequest):
    await product_repo.init_db()
    
    # Get product to calculate price
    from services.product_service import ProductService
    product_service = ProductService(product_repo)
    products = await product_service.get_products_by_query(f"SELECT * FROM c WHERE id = '{request.product_id}'")
    
    if not products:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = products[0]
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    total_price = product.price * request.quantity
    
    order = Order(
        order_id=order_id,
        product_id=request.product_id,
        user_id=request.user_id,
        quantity=request.quantity,
        total_price=total_price,
        status="Order Placed",
        delivery_address=request.delivery_address
    )
    
    await product_repo.insert_order(order)
    
    # Create payment record
    payment_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
    payment = Payment(
        payment_id=payment_id,
        order_id=order_id,
        amount=total_price,
        method=request.payment_method,
        status="Completed"
    )
    await product_repo.insert_payment(payment)
    
    return {
        "order_id": order_id,
        "total_price": total_price,
        "status": "Order Placed",
        "message": "Order created successfully"
    }

@router.get("/user/{user_id}")
async def get_user_orders_api(user_id: str):
    await product_repo.init_db()
    orders = await product_repo.get_user_orders(user_id)
    return {"orders": orders}

@router.get("/track/{order_id}")
async def track_order_api(order_id: str):
    await product_repo.init_db()
    order = await product_repo.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    tracking = await product_repo.get_tracking_history(order_id)
    return {
        "order": order,
        "tracking": tracking
    }

@router.post("/cancel/{order_id}")
async def cancel_order_api(order_id: str):
    await product_repo.init_db()
    order = await product_repo.get_order(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.get('status') in ['Delivered', 'Cancelled']:
        raise HTTPException(status_code=400, detail=f"Cannot cancel order with status: {order.get('status')}")
    
    await product_repo.update_order_status(order_id, 'Cancelled')
    
    return {
        "order_id": order_id,
        "status": "Cancelled",
        "message": "Order cancelled successfully"
    }
