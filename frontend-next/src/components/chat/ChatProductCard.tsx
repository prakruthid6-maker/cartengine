'use client';

import { motion } from 'framer-motion';
import Image from 'next/image';
import styles from './ChatProductCard.module.css';

export interface ChatProduct {
    id: string;
    name: string;
    price: number;
    rating: number;
    image?: string;
    description?: string;
}

interface ChatProductCardProps {
    product: ChatProduct;
    onAddToCart?: (productId: string) => void;
    onViewDetails?: (productId: string) => void;
}

export function ChatProductCard({ product, onAddToCart, onViewDetails }: ChatProductCardProps) {
    const placeholderImage = `https://placehold.co/200x200/1a1a2e/eee?text=${encodeURIComponent(product.name.slice(0, 10))}`;

    return (
        <motion.div
            className={styles.card}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
            whileHover={{ scale: 1.02 }}
        >
            <div className={styles.imageContainer}>
                <Image
                    src={product.image || placeholderImage}
                    alt={product.name}
                    width={150}
                    height={150}
                    className={styles.image}
                    unoptimized
                />
            </div>
            <div className={styles.content}>
                <h4 className={styles.name}>{product.name}</h4>
                <div className={styles.rating}>
                    <span className={styles.stars}>{'⭐'.repeat(Math.round(product.rating))}</span>
                    <span className={styles.ratingValue}>{product.rating.toFixed(1)}</span>
                </div>
                <p className={styles.price}>${product.price.toFixed(2)}</p>
                {product.description && (
                    <p className={styles.description}>{product.description}</p>
                )}
                <div className={styles.actions}>
                    <button
                        className={styles.addBtn}
                        onClick={() => onAddToCart?.(product.id)}
                    >
                        🛒 Add
                    </button>
                    <button
                        className={styles.viewBtn}
                        onClick={() => onViewDetails?.(product.id)}
                    >
                        View
                    </button>
                </div>
            </div>
        </motion.div>
    );
}

interface ChatProductGridProps {
    products: ChatProduct[];
    onAddToCart?: (productId: string) => void;
    onViewDetails?: (productId: string) => void;
}

export function ChatProductGrid({ products, onAddToCart, onViewDetails }: ChatProductGridProps) {
    if (!products || products.length === 0) return null;

    return (
        <div className={styles.grid}>
            {products.map((product, index) => (
                <motion.div
                    key={product.id || index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                >
                    <ChatProductCard
                        product={product}
                        onAddToCart={onAddToCart}
                        onViewDetails={onViewDetails}
                    />
                </motion.div>
            ))}
        </div>
    );
}

// Utility to parse product blocks from AI response
export function parseProductsFromMessage(content: string): {
    products: ChatProduct[];
    textContent: string;
} {
    const productMatch = content.match(/:::PRODUCTS:::([\s\S]*?):::END_PRODUCTS:::/);

    if (!productMatch) {
        return { products: [], textContent: content };
    }

    try {
        const jsonStr = productMatch[1].trim();
        const products = JSON.parse(jsonStr) as ChatProduct[];
        const textContent = content
            .replace(/:::PRODUCTS:::[\s\S]*?:::END_PRODUCTS:::/, '')
            .trim();

        return { products, textContent };
    } catch (e) {
        console.error('Failed to parse products JSON:', e);
        return { products: [], textContent: content };
    }
}

// Parse cart block from AI response
export function parseCartFromMessage(content: string): {
    cart: { items: ChatProduct[]; total: number; count: number } | null;
    textContent: string;
} {
    const cartMatch = content.match(/:::CART:::([\s\S]*?):::END_CART:::/);

    if (!cartMatch) {
        return { cart: null, textContent: content };
    }

    try {
        const jsonStr = cartMatch[1].trim();
        const cart = JSON.parse(jsonStr);
        const textContent = content
            .replace(/:::CART:::[\s\S]*?:::END_CART:::/, '')
            .trim();

        return { cart, textContent };
    } catch (e) {
        console.error('Failed to parse cart JSON:', e);
        return { cart: null, textContent: content };
    }
}
