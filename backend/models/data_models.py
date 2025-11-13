from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class Product(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.isoformat()})
    id: str
    categoryId: str
    name: str
    description: str
    price: float
    ratings: float
    reviews: float
    image: str
    badge: str
    created_at: Optional[str] = None
    seller_id: Optional[str] = None

class Seller(BaseModel):
    seller_id: str
    name: str
    location: str
    rating: float

class Order(BaseModel):
    order_id: str
    product_id: str
    user_id: str
    quantity: int
    total_price: float
    status: str
    delivery_address: str
    order_date: Optional[str] = None

class Payment(BaseModel):
    payment_id: str
    order_id: str
    amount: float
    method: str
    status: str
    timestamp: Optional[str] = None

class OrderTracking(BaseModel):
    tracking_id: str
    order_id: str
    status: str
    location: str
    timestamp: Optional[str] = None

class Wishlist(BaseModel):
    wishlist_id: str
    user_id: str
    product_id: str
    added_date: Optional[str] = None

class Review(BaseModel):
    review_id: str
    product_id: str
    user_id: str
    rating: float
    comment: str
    review_date: Optional[str] = None

class Coupon(BaseModel):
    coupon_code: str
    discount_percent: float
    expiry_date: str
    status: str




