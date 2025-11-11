import requests, os, random, json
from typing import Dict
from models.data_models import Product
from services.product_service import ProductService


product_service = ProductService("products.db")

async def fetch_products(query: str) ->  dict:
    return await product_service.get_products_by_query(query= "SELECT * from c")
