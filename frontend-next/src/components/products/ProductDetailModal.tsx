'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Product } from '@/types';
import { Button } from '@/components/ui/Button';
import styles from './ProductDetailModal.module.css';

interface ProductDetailModalProps {
    product: Product | null;
    isOpen: boolean;
    onClose: () => void;
    onAddToCart?: (product: Product) => void;
}

export function ProductDetailModal({
    product,
    isOpen,
    onClose,
    onAddToCart,
}: ProductDetailModalProps) {
    const [selectedImage, setSelectedImage] = useState(0);
    const [quantity, setQuantity] = useState(1);
    const [activeTab, setActiveTab] = useState<'specs' | 'reviews' | 'shipping'>('specs');

    // Close on escape key
    useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };
        if (isOpen) {
            document.addEventListener('keydown', handleEscape);
            document.body.style.overflow = 'hidden';
        }
        return () => {
            document.removeEventListener('keydown', handleEscape);
            document.body.style.overflow = 'unset';
        };
    }, [isOpen, onClose]);

    if (!product) return null;

    // Mock specifications (extend from product.specs when available)
    const specifications = product.specifications || {
        sku: `SKU-${product.id.toUpperCase()}`,
        dimensions: '12 x 8 x 4 inches',
        weight: '2.5 lbs',
        material: 'Premium Grade',
        warranty: '1 Year Limited',
        origin: 'Imported',
    };

    // Mock gallery images
    const images = [
        product.image,
        product.image, // Would be different angles in real implementation
        product.image,
    ];

    const handleAddToCart = () => {
        if (onAddToCart) {
            for (let i = 0; i < quantity; i++) {
                onAddToCart(product);
            }
        }
        onClose();
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    className={styles.overlay}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={onClose}
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="modal-title"
                >
                    <motion.div
                        className={styles.modal}
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                        onClick={(e) => e.stopPropagation()}
                    >
                        {/* Close Button */}
                        <button
                            className={styles.closeBtn}
                            onClick={onClose}
                            aria-label="Close modal"
                        >
                            ✕
                        </button>

                        <div className={styles.content}>
                            {/* Left: Image Gallery */}
                            <div className={styles.gallery}>
                                <div className={styles.mainImage}>
                                    <img
                                        src={images[selectedImage] || '/placeholder.jpg'}
                                        alt={product.name}
                                    />
                                    {product.badge && (
                                        <span className={styles.badge}>{product.badge}</span>
                                    )}
                                </div>
                                <div className={styles.thumbnails}>
                                    {images.map((img, idx) => (
                                        <button
                                            key={idx}
                                            className={`${styles.thumbnail} ${selectedImage === idx ? styles.active : ''}`}
                                            onClick={() => setSelectedImage(idx)}
                                        >
                                            <img src={img || '/placeholder.jpg'} alt={`View ${idx + 1}`} />
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Right: Product Info */}
                            <div className={styles.info}>
                                <span className={styles.category}>{product.categoryId}</span>
                                <h2 id="modal-title" className={styles.title}>{product.name}</h2>

                                {/* Rating */}
                                <div className={styles.rating}>
                                    <div className={styles.stars}>
                                        {'★'.repeat(Math.floor(product.ratings))}
                                        {'☆'.repeat(5 - Math.floor(product.ratings))}
                                    </div>
                                    <span className={styles.ratingValue}>{product.ratings}</span>
                                    <span className={styles.reviews}>({product.reviews} reviews)</span>
                                </div>

                                {/* Price */}
                                <div className={styles.priceSection}>
                                    <span className={styles.price}>${product.price.toFixed(2)}</span>
                                    <span className={styles.stock}>✓ In Stock</span>
                                </div>

                                {/* Description */}
                                <p className={styles.description}>{product.description}</p>

                                {/* Tabs */}
                                <div className={styles.tabs}>
                                    <button
                                        className={`${styles.tab} ${activeTab === 'specs' ? styles.activeTab : ''}`}
                                        onClick={() => setActiveTab('specs')}
                                    >
                                        Specifications
                                    </button>
                                    <button
                                        className={`${styles.tab} ${activeTab === 'reviews' ? styles.activeTab : ''}`}
                                        onClick={() => setActiveTab('reviews')}
                                    >
                                        Reviews
                                    </button>
                                    <button
                                        className={`${styles.tab} ${activeTab === 'shipping' ? styles.activeTab : ''}`}
                                        onClick={() => setActiveTab('shipping')}
                                    >
                                        Shipping
                                    </button>
                                </div>

                                {/* Tab Content */}
                                <div className={styles.tabContent}>
                                    {activeTab === 'specs' && (
                                        <div className={styles.specs}>
                                            {Object.entries(specifications).map(([key, value]) => (
                                                <div key={key} className={styles.specRow}>
                                                    <span className={styles.specLabel}>
                                                        {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                                                    </span>
                                                    <span className={styles.specValue}>{value}</span>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                    {activeTab === 'reviews' && (
                                        <div className={styles.reviewsTab}>
                                            <p>⭐ {product.reviews} verified reviews</p>
                                            <p className={styles.reviewHighlight}>
                                                97% of customers recommend this product
                                            </p>
                                        </div>
                                    )}
                                    {activeTab === 'shipping' && (
                                        <div className={styles.shippingTab}>
                                            <p>🚚 Free shipping on orders over $50</p>
                                            <p>📦 Usually ships in 1-2 business days</p>
                                            <p>↩️ 30-day return policy</p>
                                        </div>
                                    )}
                                </div>

                                {/* Quantity & Add to Cart */}
                                <div className={styles.actions}>
                                    <div className={styles.quantity}>
                                        <button
                                            onClick={() => setQuantity(Math.max(1, quantity - 1))}
                                            disabled={quantity <= 1}
                                        >
                                            −
                                        </button>
                                        <span>{quantity}</span>
                                        <button onClick={() => setQuantity(quantity + 1)}>+</button>
                                    </div>
                                    <Button
                                        variant="primary"
                                        size="lg"
                                        onClick={handleAddToCart}
                                        leftIcon={
                                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                <circle cx="9" cy="21" r="1" />
                                                <circle cx="20" cy="21" r="1" />
                                                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
                                            </svg>
                                        }
                                    >
                                        Add to Cart — ${(product.price * quantity).toFixed(2)}
                                    </Button>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
