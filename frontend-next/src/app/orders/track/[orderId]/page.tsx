'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import styles from './page.module.css';

interface TrackingEvent {
    event_id: string;
    order_id: string;
    status: string;
    timestamp: string;
    location?: string;
    notes?: string;
}

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

export default function TrackOrderPage() {
    const params = useParams();
    const orderId = params?.orderId as string;

    const [order, setOrder] = useState<Order | null>(null);
    const [tracking, setTracking] = useState<TrackingEvent[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!orderId) return;

        const loadTracking = async () => {
            try {
                setLoading(true);
                const response = await fetch(`/api/orders/track/${orderId}`);
                if (!response.ok) throw new Error('Failed to load tracking info');

                const data = await response.json();
                setOrder(data.order);
                setTracking(data.tracking || []);
                setError(null);
            } catch (err) {
                setError('Failed to load tracking information');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        loadTracking();
    }, [orderId]);

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'Order Placed':
                return '📦';
            case 'Processing':
                return '⚙️';
            case 'Shipped':
                return '🚚';
            case 'Out for Delivery':
                return '🏃';
            case 'Delivered':
                return '✅';
            case 'Cancelled':
                return '❌';
            default:
                return '📍';
        }
    };

    if (loading) {
        return (
            <div className={styles.container}>
                <div className={styles.loading}>
                    <div className={styles.spinner}></div>
                    <p>Loading tracking info...</p>
                </div>
            </div>
        );
    }

    if (error || !order) {
        return (
            <div className={styles.container}>
                <div className={styles.error}>
                    <p>{error || 'Order not found'}</p>
                    <Button onClick={() => window.location.href = '/orders'}>Back to Orders</Button>
                </div>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <Button variant="secondary" onClick={() => window.location.href = '/orders'}>
                    ← Back to Orders
                </Button>
                <h1 className={styles.title}>📍 Track Order</h1>
            </div>

            {/* Order Summary Card */}
            <motion.div
                className={styles.orderCard}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                <div className={styles.orderHeader}>
                    <div>
                        <h2>Order #{order.order_id}</h2>
                        <p className={styles.orderDate}>
                            {order.order_date ? new Date(order.order_date).toLocaleDateString() : 'N/A'}
                        </p>
                    </div>
                    <div className={styles.currentStatus}>
                        {getStatusIcon(order.status)} {order.status}
                    </div>
                </div>

                <div className={styles.orderDetails}>
                    <div className={styles.detailItem}>
                        <span className={styles.label}>Product:</span>
                        <span>{order.product_name || `Product ${order.product_id}`}</span>
                    </div>
                    <div className={styles.detailItem}>
                        <span className={styles.label}>Quantity:</span>
                        <span>{order.quantity}</span>
                    </div>
                    <div className={styles.detailItem}>
                        <span className={styles.label}>Total:</span>
                        <span className={styles.price}>${order.total_price.toFixed(2)}</span>
                    </div>
                    <div className={styles.detailItem}>
                        <span className={styles.label}>Delivery Address:</span>
                        <span>{order.delivery_address}</span>
                    </div>
                </div>
            </motion.div>

            {/* Tracking Timeline */}
            <div className={styles.trackingSection}>
                <h2 className={styles.sectionTitle}>Tracking History</h2>

                {tracking.length === 0 ? (
                    <div className={styles.noTracking}>
                        <p>No tracking events yet</p>
                    </div>
                ) : (
                    <div className={styles.timeline}>
                        {tracking.map((event, index) => (
                            <motion.div
                                key={event.event_id}
                                className={styles.timelineItem}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.1 }}
                            >
                                <div className={styles.timelineIcon}>
                                    {getStatusIcon(event.status)}
                                </div>
                                <div className={styles.timelineContent}>
                                    <h3>{event.status}</h3>
                                    <p className={styles.timelineDate}>
                                        {new Date(event.timestamp).toLocaleString()}
                                    </p>
                                    {event.location && (
                                        <p className={styles.timelineLocation}>📍 {event.location}</p>
                                    )}
                                    {event.notes && (
                                        <p className={styles.timelineNotes}>{event.notes}</p>
                                    )}
                                </div>
                            </motion.div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
