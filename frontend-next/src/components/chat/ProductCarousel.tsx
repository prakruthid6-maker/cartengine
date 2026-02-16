'use client';

import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './ProductCarousel.module.css';

interface Product {
    id: string;
    name: string;
    price: number;
    image: string;
    rating?: number;
    badge?: string;
}

interface ProductCarouselProps {
    products: Product[];
    title?: string;
    onProductClick?: (product: Product) => void;
    onImageClick?: (product: Product) => void;
}

export function ProductCarousel({
    products,
    title,
    onProductClick,
    onImageClick,
}: ProductCarouselProps) {
    const [currentIndex, setCurrentIndex] = useState(0);
    const containerRef = useRef<HTMLDivElement>(null);

    const scrollTo = (index: number) => {
        if (containerRef.current) {
            const cardWidth = 280 + 16; // card width + gap
            containerRef.current.scrollTo({
                left: index * cardWidth,
                behavior: 'smooth',
            });
            setCurrentIndex(index);
        }
    };

    const handlePrev = () => {
        const newIndex = Math.max(0, currentIndex - 1);
        scrollTo(newIndex);
    };

    const handleNext = () => {
        const newIndex = Math.min(products.length - 1, currentIndex + 1);
        scrollTo(newIndex);
    };

    if (!products.length) return null;

    return (
        <div className={styles.wrapper}>
            {title && <h3 className={styles.title}>{title}</h3>}

            <div className={styles.container}>
                {/* Navigation Arrows */}
                <button
                    className={`${styles.navBtn} ${styles.prevBtn}`}
                    onClick={handlePrev}
                    disabled={currentIndex === 0}
                    aria-label="Previous"
                >
                    ‹
                </button>

                {/* Carousel Track */}
                <div className={styles.track} ref={containerRef}>
                    <AnimatePresence mode="popLayout">
                        {products.map((product, index) => (
                            <motion.div
                                key={product.id}
                                className={styles.card}
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.9 }}
                                transition={{ delay: index * 0.05 }}
                                whileHover={{ y: -4 }}
                            >
                                {/* Image */}
                                <div
                                    className={styles.imageWrapper}
                                    onClick={() => onImageClick?.(product)}
                                >
                                    <img
                                        src={product.image}
                                        alt={product.name}
                                        className={styles.image}
                                        loading="lazy"
                                    />
                                    {product.badge && (
                                        <span className={styles.badge}>{product.badge}</span>
                                    )}
                                    <div className={styles.zoom}>🔍</div>
                                </div>

                                {/* Details */}
                                <div
                                    className={styles.details}
                                    onClick={() => onProductClick?.(product)}
                                >
                                    <h4 className={styles.name}>{product.name}</h4>
                                    <div className={styles.meta}>
                                        <span className={styles.price}>${product.price.toFixed(2)}</span>
                                        {product.rating && (
                                            <span className={styles.rating}>
                                                ⭐ {product.rating.toFixed(1)}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </div>

                <button
                    className={`${styles.navBtn} ${styles.nextBtn}`}
                    onClick={handleNext}
                    disabled={currentIndex >= products.length - 1}
                    aria-label="Next"
                >
                    ›
                </button>
            </div>

            {/* Dots Indicator */}
            {products.length > 3 && (
                <div className={styles.dots}>
                    {products.map((_, index) => (
                        <button
                            key={index}
                            className={`${styles.dot} ${index === currentIndex ? styles.active : ''}`}
                            onClick={() => scrollTo(index)}
                            aria-label={`Go to product ${index + 1}`}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}
