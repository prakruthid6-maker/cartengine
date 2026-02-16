'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import styles from './page.module.css';

interface Order {
    order_id: string;
    product_id: string;
    product_name?: string;
    quantity: number;
    total_price: number;
    status: string;
    delivery_address: string;
    order_date?: string;
}

export default function OrdersPage() {
    const [orders, setOrders] = useState<Order[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const userId = 'guest';

    const loadOrders = async () => {
        try {
            setLoading(true);
            const response = await fetch(`/api/orders/user/${userId}`);
            if (!response.ok) throw new Error('Failed to load orders');

            const data = await response.json();
            setOrders(data.orders || []);
            setError(null);
        } catch (err) {
            setError('Failed to load orders');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadOrders();
    }, []);

    const cancelOrder = async (orderId: string) => {
        try {
            const response = await fetch(`/api/orders/cancel/${orderId}`, {
                method: 'POST',
            });

            if (!response.ok) {
                let errorMessage = 'Failed to cancel order';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } catch {
                    errorMessage = `Server error (${response.status})`;
                }
                throw new Error(errorMessage);
            }

            alert('Order cancelled successfully!');
            await loadOrders();
        } catch (err: any) {
            console.error('Cancel error:', err);
            alert(err.message || 'Failed to cancel order');
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'Order Placed':
                return '#3b82f6';
            case 'Shipped':
                return '#8b5cf6';
            case 'Delivered':
                return '#10b981';
            case 'Cancelled':
                return '#ef4444';
            default:
                return '#6b7280';
        }
    };

    if (loading) {
        return (
            <div className={styles.container}>
                <div className={styles.loading}>
                    <div className={styles.spinner}></div>
                    <p>Loading orders...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className={styles.container}>
                <div className={styles.error}>
                    <p>{error}</p>
                    <Button onClick={loadOrders}>Retry</Button>
                </div>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1 className={styles.title}>📦 My Orders</h1>
                <p className={styles.subtitle}>Track and manage your orders</p>
            </div>

            {orders.length === 0 ? (
                <div className={styles.empty}>
                    <span>📭</span>
                    <p>No orders yet</p>
                    <Button variant="primary" onClick={() => (window.location.href = '/products')}>
                        Start Shopping
                    </Button>
                </div>
            ) : (
                <div className={styles.orders}>
                    {orders.map((order) => (
                        <motion.div
                            key={order.order_id}
                            className={styles.orderCard}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                        >
                            <div className={styles.orderHeader}>
                                <div>
                                    <h3 className={styles.orderId}>Order #{order.order_id}</h3>
                                    {order.order_date && (
                                        <p className={styles.orderDate}>
                                            {new Date(order.order_date).toLocaleDateString()}
                                        </p>
                                    )}
                                </div>
                                <div
                                    className={styles.status}
                                    style={{ background: getStatusColor(order.status) }}
                                >
                                    {order.status}
                                </div>
                            </div>

                            <div className={styles.orderBody}>
                                <div className={styles.productInfo}>
                                    <span className={styles.productIcon}>📦</span>
                                    <div>
                                        <p className={styles.productName}>
                                            {order.product_name || `Product ${order.product_id}`}
                                        </p>
                                        <p className={styles.quantity}>Quantity: {order.quantity}</p>
                                    </div>
                                </div>

                                <div className={styles.orderDetails}>
                                    <div className={styles.detailRow}>
                                        <span>Total:</span>
                                        <span className={styles.price}>${order.total_price.toFixed(2)}</span>
                                    </div>
                                    <div className={styles.detailRow}>
                                        <span>Address:</span>
                                        <span className={styles.address}>{order.delivery_address}</span>
                                    </div>
                                </div>
                            </div>

                            <div className={styles.orderActions}>
                                <Button variant="secondary" size="sm" onClick={() => window.location.href = `/orders/track/${order.order_id}`}>
                                    Track Order
                                </Button>
                                {order.status === 'Order Placed' && (
                                    <Button
                                        variant="secondary"
                                        size="sm"
                                        onClick={() => {
                                            if (confirm('Are you sure you want to cancel this order?')) {
                                                cancelOrder(order.order_id);
                                            }
                                        }}
                                    >
                                        Cancel Order
                                    </Button>
                                )}
                            </div>
                        </motion.div>
                    ))}
                </div>
            )}
        </div>
    );
}
