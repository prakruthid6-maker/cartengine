"""
E-Commerce AI Platform - Main FastAPI Application

Enhanced with:
- JWT Authentication
- Role-based access control
- CORS configuration
- Health check endpoint
"""

import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.adk.cli.fast_api import get_fast_api_app
from dotenv import load_dotenv

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.product_service import ProductService
from routers import products, orders, auth, chat, cart

load_dotenv()

# Initialize services
product_service = ProductService("products.db")

# Get the directory where main.py is located (parent of techai_agent)
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure allowed origins for CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",     # Next.js dev server
    "http://localhost:8080",     # FastAPI dev
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    "https://cartengine-zgwc.vercel.app",  # Vercel production
    "*",  # Allow all origins for deployment
]

# Web interface flag
SERVE_WEB_INTERFACE = True

# Get the FastAPI app with ADK integration
app = get_fast_api_app(
    agents_dir=AGENT_DIR,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)


# ============ Health Check ============

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {
        "status": "healthy",
        "service": "e-commerce-ai",
        "version": "2.0.0"
    }


# ============ Include Routers ============

# Authentication routes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Product routes
app.include_router(products.router, prefix="/products", tags=["Products"])

# Order routes
app.include_router(orders.router, prefix="/orders", tags=["Orders"])

# Chat routes
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

# Cart routes (NEW - syncs with AI agent)
app.include_router(cart.router, prefix="/cart", tags=["Cart"])


# ============ Run Server ============

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # Enable hot reload in development
        log_level="info"
    )