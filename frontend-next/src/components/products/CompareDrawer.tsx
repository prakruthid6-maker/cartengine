'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { Product } from '@/types';
import { Button } from '@/components/ui/Button';
import styles from './CompareDrawer.module.css';

interface CompareDrawerProps {
    products: Product[];
    isOpen: boolean;
    onClose: () => void;
    onRemove: (productId: string) => void;
    onClear: () => void;
}

export function CompareDrawer({
    products,
    isOpen,
    onClose,
    onRemove,
    onClear,
}: CompareDrawerProps) {
    // Generate comparison attributes
    const attributes = ['Price', 'Rating', 'Reviews', 'Badge', 'Category'];

    const getAttributeValue = (product: Product, attr: string): string => {
        switch (attr) {
            case 'Price':
                return `$${product.price.toFixed(2)}`;
            case 'Rating':
                return `${product.ratings} ★`;
            case 'Reviews':
                return `${product.reviews} reviews`;
            case 'Badge':
                return product.badge || '—';
            case 'Category':
                return product.categoryId;
            default:
                return '—';
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        className={styles.backdrop}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                    />

                    {/* Drawer */}
                    <motion.div
                        className={styles.drawer}
                        initial={{ x: '100%' }}
                        animate={{ x: 0 }}
                        exit={{ x: '100%' }}
                        transition={{ type: 'spring', damping: 30, stiffness: 300 }}
                        role="dialog"
                        aria-label="Compare products"
                    >
                        {/* Header */}
                        <div className={styles.header}>
                            <h2>Compare Products</h2>
                            <div className={styles.headerActions}>
                                {products.length > 0 && (
                                    <button className={styles.clearBtn} onClick={onClear}>
                                        Clear All
                                    </button>
                                )}
                                <button className={styles.closeBtn} onClick={onClose} aria-label="Close">
                                    ✕
                                </button>
                            </div>
                        </div>

                        {/* Content */}
                        <div className={styles.content}>
                            {products.length === 0 ? (
                                <div className={styles.empty}>
                                    <span>📊</span>
                                    <p>No products to compare</p>
                                    <p className={styles.hint}>
                                        Click the compare icon on product cards to add items
                                    </p>
                                </div>
                            ) : (
                                <>
                                    {/* Products Row */}
                                    <div className={styles.productsRow}>
                                        <div className={styles.attributeLabel}></div>
                                        {products.map((product) => (
                                            <div key={product.id} className={styles.productCard}>
                                                <button
                                                    className={styles.removeBtn}
                                                    onClick={() => onRemove(product.id)}
                                                    aria-label={`Remove ${product.name}`}
                                                >
                                                    ✕
                                                </button>
                                                <img
                                                    src={product.image || '/placeholder.jpg'}
                                                    alt={product.name}
                                                    className={styles.productImage}
                                                />
                                                <h3 className={styles.productName}>{product.name}</h3>
                                            </div>
                                        ))}
                                    </div>

                                    {/* Comparison Table */}
                                    <div className={styles.comparisonTable}>
                                        {attributes.map((attr) => (
                                            <div key={attr} className={styles.row}>
                                                <div className={styles.attributeLabel}>{attr}</div>
                                                {products.map((product) => (
                                                    <div key={product.id} className={styles.attributeValue}>
                                                        {getAttributeValue(product, attr)}
                                                    </div>
                                                ))}
                                            </div>
                                        ))}
                                    </div>

                                    {/* Best Choice Highlight */}
                                    {products.length >= 2 && (
                                        <div className={styles.bestChoice}>
                                            <span>🏆 Best Value:</span>
                                            {' '}
                                            {products.reduce((best, p) =>
                                                (p.ratings / p.price) > (best.ratings / best.price) ? p : best
                                            ).name}
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
