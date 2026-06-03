// Product and API types for the e-commerce platform

export interface Product {
    id: string;
    name: string;
    categoryId: string;
    description: string;
    price: number;
    ratings: number;
    reviews: number;
    image: string;
    badge?: string;
    seller_id?: string;
    created_at?: string;
    stock_quantity?: number;
    discount_percent?: number;
    original_price?: number;
    sku?: string;
    specifications?: any;
}

export interface CartItem {
    product: Product;
    quantity: number;
}

export interface Order {
    order_id: string;
    product_id: string;
    user_id: string;
    quantity: number;
    total_price: number;
    status: OrderStatus;
    delivery_address: string;
    order_date: string;
}

export type OrderStatus =
    | 'Order Placed'
    | 'Processing'
    | 'Shipped'
    | 'Out for Delivery'
    | 'Delivered'
    | 'Cancelled';

export interface User {
    id: string;
    username: string;
    role: 'customer' | 'admin';
}

export interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
}

export interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    images?: string[];
}

export interface ApiResponse<T> {
    data: T;
    success: boolean;
    message?: string;
}

export interface FilterOptions {
    category?: string;
    minPrice?: number;
    maxPrice?: number;
    badge?: string;
    sortBy?: 'price' | 'rating' | 'reviews' | 'newest';
    sortOrder?: 'asc' | 'desc';
}
