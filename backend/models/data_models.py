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




