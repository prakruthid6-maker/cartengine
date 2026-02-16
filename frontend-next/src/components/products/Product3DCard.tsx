'use client';

import { useState } from 'react';
import Image from 'next/image';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';
import { Product } from '@/types';
import { Button } from '@/components/ui/Button';
import styles from './Product3DCard.module.css';

interface Product3DCardProps {
    product: Product;
    onAddToCart?: (product: Product) => void;
    onCompare?: (product: Product) => void;
    onViewDetails?: (product: Product) => void;
}

export function Product3DCard({
    product,
    onAddToCart,
    onCompare,
    onViewDetails,
}: Product3DCardProps) {
    const [isHovered, setIsHovered] = useState(false);

    // Mouse position for 3D effect
    const x = useMotionValue(0);
    const y = useMotionValue(0);

    // Smooth spring animation
    const rotateX = useSpring(useTransform(y, [-100, 100], [10, -10]), { stiffness: 300, damping: 30 });
    const rotateY = useSpring(useTransform(x, [-100, 100], [-10, 10]), { stiffness: 300, damping: 30 });

    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        x.set(e.clientX - centerX);
        y.set(e.clientY - centerY);
    };

    const handleMouseLeave = () => {
        x.set(0);
        y.set(0);
        setIsHovered(false);
    };

    // Star rating display
    const renderStars = (rating: number) => {
        const stars = [];
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;

        for (let i = 0; i < 5; i++) {
            if (i < fullStars) {
                stars.push(<span key={i} className={styles.starFull}>★</span>);
            } else if (i === fullStars && hasHalfStar) {
                stars.push(<span key={i} className={styles.starHalf}>★</span>);
            } else {
                stars.push(<span key={i} className={styles.starEmpty}>★</span>);
            }
        }
        return stars;
    };

    return (
        <motion.div
            className={styles.cardWrapper}
            style={{
                rotateX,
                rotateY,
                transformPerspective: 1200,
                transformStyle: 'preserve-3d',
            }}
            onMouseMove={handleMouseMove}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={handleMouseLeave}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
        >
            <div className={styles.card}>
                {/* Glow effect on hover */}
                <motion.div
                    className={styles.glow}
                    animate={{ opacity: isHovered ? 1 : 0 }}
                />

                {/* Badge */}
                {product.badge && (
                    <span className={`${styles.badge} ${product.badge === 'Sale' ? styles.badgeSale : styles.badgeNew}`}>
                        {product.badge}
                    </span>
                )}

                {/* Image Container */}
                <div className={styles.imageContainer}>
                    <Image
                        src={product.image || '/placeholder-product.png'}
                        alt={product.name}
                        fill
                        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                        className={styles.image}
                        style={{ objectFit: 'cover' }}
                    />

                    {/* Overlay actions */}
                    <motion.div
                        className={styles.overlay}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: isHovered ? 1 : 0 }}
                    >
                        <button
                            className={styles.overlayBtn}
                            onClick={() => onViewDetails?.(product)}
                            aria-label="View details"
                        >
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <circle cx="11" cy="11" r="8" />
                                <line x1="21" y1="21" x2="16.65" y2="16.65" />
                            </svg>
                        </button>
                        <button
                            className={styles.overlayBtn}
                            onClick={() => onCompare?.(product)}
                            aria-label="Compare"
                        >
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M16 3h5v5M4 20L21 3M21 16v5h-5M15 15l6 6M4 4l5 5" />
                            </svg>
                        </button>
                    </motion.div>
                </div>

                {/* Content */}
                <div className={styles.content}>
                    <p className={styles.category}>{product.categoryId}</p>
                    <h3 className={styles.name}>{product.name}</h3>

                    <div className={styles.ratingRow}>
                        <div className={styles.stars}>{renderStars(product.ratings)}</div>
                        <span className={styles.reviewCount}>({product.reviews})</span>
                    </div>

                    <p className={styles.description}>{product.description}</p>

                    <div className={styles.footer}>
                        <span className={styles.price}>${product.price.toFixed(2)}</span>
                        <Button
                            variant="primary"
                            size="sm"
                            onClick={() => onAddToCart?.(product)}
                            leftIcon={
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <circle cx="9" cy="21" r="1" />
                                    <circle cx="20" cy="21" r="1" />
                                    <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
                                </svg>
                            }
                        >
                            Add
                        </Button>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
