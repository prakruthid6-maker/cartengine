'use client';

import { useState, useMemo, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { productApi } from '@/lib/api';
import { Product, FilterOptions } from '@/types';
import { ProductGrid } from '@/components/products/ProductGrid';
import { ProductFilters } from '@/components/products/ProductFilters';
import { ProductDetailModal } from '@/components/products/ProductDetailModal';
import { CompareDrawer } from '@/components/products/CompareDrawer';
import styles from './page.module.css';

export default function ProductsPage() {
    const [filters, setFilters] = useState<FilterOptions>({});

    // Modal state for product details
    const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);

    // Compare drawer state
    const [compareProducts, setCompareProducts] = useState<Product[]>([]);
    const [isCompareOpen, setIsCompareOpen] = useState(false);

    const { data: products = [], isLoading, error } = useQuery({
        queryKey: ['products'],
        queryFn: productApi.getAll,
    });

    // Apply filters using useMemo to avoid infinite re-renders
    const filteredProducts = useMemo(() => {
        let result = [...products];

        if (filters.category) {
            result = result.filter(p =>
                p.categoryId.toLowerCase() === filters.category?.toLowerCase()
            );
        }

        if (filters.minPrice !== undefined) {
            result = result.filter(p => p.price >= (filters.minPrice || 0));
        }

        if (filters.maxPrice !== undefined) {
            result = result.filter(p => p.price <= (filters.maxPrice || Infinity));
        }

        if (filters.badge) {
            result = result.filter(p => p.badge === filters.badge);
        }

        // Sorting
        if (filters.sortBy) {
            result.sort((a, b) => {
                let comparison = 0;
                switch (filters.sortBy) {
                    case 'price':
                        comparison = a.price - b.price;
                        break;
                    case 'rating':
                        comparison = a.ratings - b.ratings;
                        break;
                    case 'reviews':
                        comparison = a.reviews - b.reviews;
                        break;
                    case 'newest':
                        comparison = new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime();
                        break;
                }
                return filters.sortOrder === 'desc' ? -comparison : comparison;
            });
        }

        return result;
    }, [products, filters]);

    // Get unique categories and badges for filter options
    const categories = [...new Set(products.map(p => p.categoryId))];
    const badges = [...new Set(products.filter(p => p.badge).map(p => p.badge as string))];

    // ============ BUTTON HANDLERS (Fixed) ============

    /**
     * Fix #1: Add to Cart Handler
     * Now properly integrates with backend cart API (/api/cart/update) to persist changes to database
     */
    const handleAddToCart = useCallback(async (product: Product) => {
        try {
            const userId = 'guest'; // TODO: Get from auth context

            // Call backend API to add to cart
            const response = await fetch('/api/cart/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    product_id: product.id,
                    quantity: 1,
                    action: 'add'
                })
            });

            if (!response.ok) {
                throw new Error('Failed to add to cart');
            }

            // Show success notification
            const notification = document.createElement('div');
            notification.className = 'toast-notification';
            notification.innerHTML = `✓ Added "${product.name}" to cart`;
            notification.style.cssText = `
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                z-index: 10000;
                animation: slideUp 0.3s ease-out;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            `;
            document.body.appendChild(notification);
            setTimeout(() => notification.remove(), 3000);
        } catch (error) {
            console.error('Error adding to cart:', error);
            // Show error notification
            const notification = document.createElement('div');
            notification.className = 'toast-notification';
            notification.innerHTML = `✗ Failed to add to cart`;
            notification.style.cssText = `
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: #ef4444;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                z-index: 10000;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            `;
            document.body.appendChild(notification);
            setTimeout(() => notification.remove(), 3000);
        }
    }, []);

    /**
     * Fix #2: Compare Button Handler
     * Previously only logged to console. Now adds product to compare list and opens drawer.
     */
    const handleCompare = useCallback((product: Product) => {
        // Check if already in compare list
        if (compareProducts.find(p => p.id === product.id)) {
            // Already in list, remove it
            setCompareProducts(prev => prev.filter(p => p.id !== product.id));
        } else {
            // Add to compare (max 4 products)
            if (compareProducts.length >= 4) {
                alert('You can compare up to 4 products at a time. Remove one to add another.');
                return;
            }
            setCompareProducts(prev => [...prev, product]);
            setIsCompareOpen(true);
        }
    }, [compareProducts]);

    /**
     * Fix #3: View Details Handler  
     * Previously only logged to console. Now opens full product modal.
     */
    const handleViewDetails = useCallback((product: Product) => {
        setSelectedProduct(product);
        setIsModalOpen(true);
    }, []);

    // Compare drawer handlers
    const handleRemoveFromCompare = useCallback((productId: string) => {
        setCompareProducts(prev => prev.filter(p => p.id !== productId));
    }, []);

    const handleClearCompare = useCallback(() => {
        setCompareProducts([]);
    }, []);

    if (error) {
        return (
            <div className={styles.error}>
                <h2>Error loading products</h2>
                <p>{(error as Error).message}</p>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1 className={styles.title}>Our Products</h1>
                <p className={styles.subtitle}>
                    Discover {products.length} amazing products with AI-powered recommendations
                </p>
            </div>

            <div className={styles.content}>
                <aside className={styles.sidebar}>
                    <ProductFilters
                        categories={categories}
                        badges={badges}
                        filters={filters}
                        onFilterChange={setFilters}
                    />
                </aside>

                <main className={styles.main}>
                    <div className={styles.resultsHeader}>
                        <span className={styles.resultCount}>
                            {filteredProducts.length} products
                        </span>
                        {compareProducts.length > 0 && (
                            <button
                                className={styles.compareBtn}
                                onClick={() => setIsCompareOpen(true)}
                            >
                                📊 Compare ({compareProducts.length})
                            </button>
                        )}
                    </div>

                    <ProductGrid
                        products={filteredProducts}
                        layout="grid"
                        isLoading={isLoading}
                        onAddToCart={handleAddToCart}
                        onCompare={handleCompare}
                        onViewDetails={handleViewDetails}
                    />
                </main>
            </div>

            {/* Product Detail Modal */}
            <ProductDetailModal
                product={selectedProduct}
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onAddToCart={handleAddToCart}
            />

            {/* Compare Drawer */}
            <CompareDrawer
                products={compareProducts}
                isOpen={isCompareOpen}
                onClose={() => setIsCompareOpen(false)}
                onRemove={handleRemoveFromCompare}
                onClear={handleClearCompare}
            />

            {/* Toast animation styles */}
            <style jsx global>{`
                @keyframes slideUp {
                    from {
                        opacity: 0;
                        transform: translateX(-50%) translateY(20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateX(-50%) translateY(0);
                    }
                }
            `}</style>
        </div>
    );
}
