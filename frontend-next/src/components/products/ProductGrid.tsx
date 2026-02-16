'use client';

import { Product } from '@/types';
import { Product3DCard } from './Product3DCard';
import styles from './ProductGrid.module.css';

type LayoutType = 'grid' | 'masonry';

interface ProductGridProps {
    products: Product[];
    layout?: LayoutType;
    onAddToCart?: (product: Product) => void;
    onCompare?: (product: Product) => void;
    onViewDetails?: (product: Product) => void;
    isLoading?: boolean;
}

export function ProductGrid({
    products,
    layout = 'grid',
    onAddToCart,
    onCompare,
    onViewDetails,
    isLoading = false,
}: ProductGridProps) {
    if (isLoading) {
        return (
            <div className={styles.grid}>
                {Array.from({ length: 8 }).map((_, i) => (
                    <div key={i} className={styles.skeleton}>
                        <div className={styles.skeletonImage} />
                        <div className={styles.skeletonContent}>
                            <div className={styles.skeletonLine} style={{ width: '60%' }} />
                            <div className={styles.skeletonLine} style={{ width: '80%' }} />
                            <div className={styles.skeletonLine} style={{ width: '40%' }} />
                        </div>
                    </div>
                ))}
            </div>
        );
    }

    if (products.length === 0) {
        return (
            <div className={styles.empty}>
                <span className={styles.emptyIcon}>🛒</span>
                <h3>No products found</h3>
                <p>Try adjusting your filters or search query</p>
            </div>
        );
    }

    return (
        <div className={`${styles[layout]} ${styles.container}`}>
            {products.map((product, index) => (
                <div
                    key={product.id}
                    className={styles.item}
                    style={{ animationDelay: `${index * 50}ms` }}
                >
                    <Product3DCard
                        product={product}
                        onAddToCart={onAddToCart}
                        onCompare={onCompare}
                        onViewDetails={onViewDetails}
                    />
                </div>
            ))}
        </div>
    );
}
