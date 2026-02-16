// API client for communicating with FastAPI backend

const API_BASE_URL = '/api'; // Proxied through Next.js rewrites

interface FetchOptions extends RequestInit {
    params?: Record<string, string | number | boolean | undefined>;
}

class ApiClient {
    private baseUrl: string;

    constructor(baseUrl: string = API_BASE_URL) {
        this.baseUrl = baseUrl;
    }

    private async request<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
        const { params, headers, ...rest } = options;

        // Build URL with query params
        let url = `${this.baseUrl}${endpoint}`;
        if (params) {
            const searchParams = new URLSearchParams();
            Object.entries(params).forEach(([key, value]) => {
                if (value !== undefined) {
                    searchParams.append(key, String(value));
                }
            });
            const queryString = searchParams.toString();
            if (queryString) {
                url += `?${queryString}`;
            }
        }

        // Get auth token
        let authToken: string | null = null;
        if (typeof window !== 'undefined') {
            const session = localStorage.getItem('userSession');
            if (session) {
                try {
                    authToken = JSON.parse(session).token;
                } catch {
                    // Invalid session
                }
            }
        }

        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
                ...headers,
            },
            ...rest,
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        // Handle 204 No Content
        if (response.status === 204) {
            return null as T;
        }

        return response.json();
    }

    // GET request
    async get<T>(endpoint: string, params?: Record<string, string | number | boolean | undefined>): Promise<T> {
        return this.request<T>(endpoint, { method: 'GET', params });
    }

    // POST request
    async post<T>(endpoint: string, data?: unknown): Promise<T> {
        return this.request<T>(endpoint, {
            method: 'POST',
            body: data ? JSON.stringify(data) : undefined,
        });
    }

    // PUT request
    async put<T>(endpoint: string, data?: unknown): Promise<T> {
        return this.request<T>(endpoint, {
            method: 'PUT',
            body: data ? JSON.stringify(data) : undefined,
        });
    }

    // DELETE request
    async delete<T>(endpoint: string, params?: Record<string, string | number | boolean | undefined>): Promise<T> {
        return this.request<T>(endpoint, { method: 'DELETE', params });
    }

    // Stream for SSE (Server-Sent Events)
    async *stream(endpoint: string, data: unknown): AsyncGenerator<string> {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Accept: 'text/event-stream',
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            throw new Error(`Stream error: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
            throw new Error('No readable stream');
        }

        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            // Process complete lines
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    yield line.slice(6);
                }
            }
        }

        // Process remaining buffer
        if (buffer.startsWith('data: ')) {
            yield buffer.slice(6);
        }
    }
}

// Export singleton instance
export const api = new ApiClient();

// Product-specific API functions
import { Product, Order } from '@/types';

export const productApi = {
    getAll: () => api.get<Product[]>('/products'),

    getById: (id: string, categoryId: string) =>
        api.get<Product>(`/products/${id}`, { category_id: categoryId }),

    create: (product: Product) => api.post<Product>('/products', product),

    update: (product: Product) => api.put<Product>('/products', product),

    delete: (id: string, categoryId: string) =>
        api.delete<void>(`/products/${id}`, { category_id: categoryId }),

    search: (query: string) => api.get<Product[]>('/products', { query }),
};

export const orderApi = {
    getAll: () => api.get<Order[]>('/orders'),

    getById: (id: string) => api.get<Order>(`/orders/${id}`),

    cancel: (id: string) => api.post<Order>(`/orders/cancel/${id}`),
};

// Cart API - syncs with AI agent's cart database
export interface CartItem {
    cart_item_id: string;
    product_id: string;
    name: string;
    quantity: number;
    unit_price: number;
    line_total: number;
}

export interface CartResponse {
    user_id: string;
    items: CartItem[];
    total_items: number;
    subtotal: number;
    total_price: number;
    message: string;
}

export const cartApi = {
    // Get cart contents
    get: (userId: string = 'guest') =>
        api.get<CartResponse>('/cart', { user_id: userId }),

    // Add item to cart
    add: (productId: string, userId: string = 'guest', quantity: number = 1) =>
        api.post<{ status: string; message: string }>('/cart/add', {
            product_id: productId,
            user_id: userId,
            quantity
        }),

    // Update item quantity
    update: (productId: string, quantity: number, userId: string = 'guest') =>
        api.put<{ status: string; message: string }>('/cart/update', {
            product_id: productId,
            user_id: userId,
            quantity
        }),

    // Remove item from cart
    remove: (productId: string, userId: string = 'guest') =>
        api.delete<{ status: string; message: string }>('/cart/remove', {
            product_id: productId,
            user_id: userId
        }),

    // Clear entire cart
    clear: (userId: string = 'guest') =>
        api.delete<{ status: string; message: string; items_removed: number }>('/cart/clear', {
            user_id: userId
        }),
};
