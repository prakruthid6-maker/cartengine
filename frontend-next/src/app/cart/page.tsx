'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import styles from './page.module.css';

interface CartItem {
    cart_item_id: string;
    product_id: string;
    name: string;
    unit_price: number;
    quantity: number;
    line_total: number;
}

interface CartResponse {
    user_id: string;
    items: CartItem[];
    total_items: number;
    subtotal: number;
    total_price: number;
    message: string;
}

export default function CartPage() {
    const [items, setItems] = useState<CartItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [checkoutLoading, setCheckoutLoading] = useState(false);
    const [showSuccess, setShowSuccess] = useState(false);
    const userId = 'guest';

    const loadCart = async () => {
        try {
            setLoading(true);
            const response = await fetch(`/api/cart?user_id=${userId}`);
            if (!response.ok) throw new Error('Failed to load cart');

            const data: CartResponse = await response.json();
            setItems(data.items);
            setError(null);
        } catch (err) {
            setError('Failed to load cart');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadCart();

        // Refresh cart when page becomes visible (e.g., navigating back from chat)
        const handleVisibilityChange = () => {
            if (!document.hidden) {
                console.log('[Cart] Page visible, refreshing cart data...');
                loadCart();
            }
        };

        document.addEventListener('visibilitychange', handleVisibilityChange);

        // Also refresh on focus (when clicking between tabs/windows)
        const handleFocus = () => {
            console.log('[Cart] Window focused, refreshing cart data...');
            loadCart();
        };

        window.addEventListener('focus', handleFocus);

        return () => {
            document.removeEventListener('visibilitychange', handleVisibilityChange);
            window.removeEventListener('focus', handleFocus);
        };
    }, []);

    const updateQuantity = async (productId: string, newQuantity: number) => {
        try {
            const response = await fetch('/api/cart/update', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    product_id: productId,
                    quantity: newQuantity,
                }),
            });
            if (!response.ok) throw new Error('Failed to update quantity');
            await loadCart();
        } catch (err) {
            console.error('Failed to update quantity:', err);
        }
    };

    const removeItem = async (productId: string) => {
        try {
            const response = await fetch(`/api/cart/remove?user_id=${userId}&product_id=${productId}`, {
                method: 'DELETE',
            });
            if (!response.ok) throw new Error('Failed to remove item');
            await loadCart();
        } catch (err) {
            console.error('Failed to remove item:', err);
        }
    };

    const handleCheckout = async () => {
        try {
            setCheckoutLoading(true);

            // Create orders for each item
            for (const item of items) {
                const response = await fetch('/api/orders/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: userId,
                        product_id: item.product_id,
                        quantity: item.quantity,
                        delivery_address: 'Default Address'
                    }),
                });
                if (!response.ok) throw new Error(`Failed to create order for ${item.name}`);
            }

            // Clear cart
            await fetch(`/api/cart/clear?user_id=${userId}`, { method: 'DELETE' });

            // Show success
            setShowSuccess(true);
            setTimeout(() => {
                setShowSuccess(false);
                loadCart();
            }, 3000);
        } catch (err) {
            console.error('Checkout failed:', err);
            alert('Checkout failed. Please try again.');
        } finally {
            setCheckoutLoading(false);
        }
    };

    const subtotal = items.reduce((sum, item) => sum + item.line_total, 0);
    const tax = subtotal * 0.08;
    const total = subtotal + tax;

    if (loading) {
        return (
            <div className={styles.container}>
                <div className={styles.loading}>
                    <div className={styles.spinner}></div>
                    <p>Loading cart...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className={styles.container}>
                <div className={styles.error}>
                    <p>{error}</p>
                    <Button onClick={loadCart}>Retry</Button>
                </div>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            <h1 className={styles.title}>🛒 Shopping Cart</h1>

            <AnimatePresence>
                {showSuccess && (
                    <motion.div
                        className={styles.successModal}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                    >
                        <div className={styles.successContent}>
                            <span className={styles.successIcon}>✅</span>
                            <h2>Order Placed Successfully!</h2>
                            <p>Your order has been confirmed.</p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {items.length === 0 ? (
                <div className={styles.empty}>
                    <span>🛍️</span>
                    <p>Your cart is empty</p>
                    <Button variant="primary" onClick={() => (window.location.href = '/products')}>
                        Browse Products
                    </Button>
                </div>
            ) : (
                <div className={styles.content}>
                    <div className={styles.items}>
                        <AnimatePresence>
                            {items.map((item) => (
                                <motion.div
                                    key={item.product_id}
                                    className={styles.item}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: 20 }}
                                >
                                    <div className={styles.itemImage}>
                                        <div className={styles.placeholder}>📦</div>
                                    </div>
                                    <div className={styles.itemDetails}>
                                        <h3>{item.name}</h3>
                                        <p className={styles.price}>${item.unit_price?.toFixed(2) || '0.00'}</p>
                                    </div>
                                    <div className={styles.quantity}>
                                        <button onClick={() => updateQuantity(item.product_id, item.quantity - 1)}>−</button>
                                        <span>{item.quantity}</span>
                                        <button onClick={() => updateQuantity(item.product_id, item.quantity + 1)}>+</button>
                                    </div>
                                    <button className={styles.removeBtn} onClick={() => removeItem(item.product_id)}>✕</button>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    </div>

                    <div className={styles.summary}>
                        <h2>Order Summary</h2>
                        <div className={styles.row}>
                            <span>Subtotal</span>
                            <span>${subtotal.toFixed(2)}</span>
                        </div>
                        <div className={styles.row}>
                            <span>Tax (8%)</span>
                            <span>${tax.toFixed(2)}</span>
                        </div>
                        <div className={`${styles.row} ${styles.total}`}>
                            <span>Total</span>
                            <span>${total.toFixed(2)}</span>
                        </div>
                        <Button
                            variant="primary"
                            size="lg"
                            fullWidth
                            onClick={handleCheckout}
                            disabled={checkoutLoading}
                        >
                            {checkoutLoading ? 'Processing...' : 'Proceed to Checkout'}
                        </Button>
                    </div>
                </div>
            )}
        </div>
    );
}
