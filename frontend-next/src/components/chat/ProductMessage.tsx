'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { ProductCarousel } from './ProductCarousel';
import { ImagePreview } from './ImagePreview';
import styles from './ProductMessage.module.css';

interface Product {
    id: string;
    name: string;
    price: number;
    image: string;
    description?: string;
    rating?: number;
    reviews?: number;
    badge?: string;
    categoryId?: string;
}

interface ProductMessageProps {
    products: Product[];
    title?: string;
    onAddToCart?: (product: Product) => void;
}

export function ProductMessage({ products, title, onAddToCart }: ProductMessageProps) {
    const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
    const [previewImage, setPreviewImage] = useState<{ src: string; alt: string } | null>(null);

    const handleProductClick = (product: Product) => {
        setSelectedProduct(product);
    };

    const handleImageClick = (product: Product) => {
        setPreviewImage({ src: product.image, alt: product.name });
    };

    const handleAddToCart = () => {
        if (selectedProduct && onAddToCart) {
            onAddToCart(selectedProduct);
            setSelectedProduct(null);
        }
    };

    return (
        <div className={styles.container}>
            <ProductCarousel
                products={products}
                title={title}
                onProductClick={handleProductClick}
                onImageClick={handleImageClick}
            />

            {/* Product Details Modal */}
            {selectedProduct && (
                <motion.div
                    className={styles.modal}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={() => setSelectedProduct(null)}
                >
                    <motion.div
                        className={styles.modalContent}
                        initial={{ scale: 0.9, y: 20 }}
                        animate={{ scale: 1, y: 0 }}
                        exit={{ scale: 0.9, y: 20 }}
                        onClick={(e) => e.stopPropagation()}
                    >
                        <button
                            className={styles.closeBtn}
                            onClick={() => setSelectedProduct(null)}
                        >
                            ✕
                        </button>

                        <div className={styles.productDetails}>
                            <div
                                className={styles.productImage}
                                onClick={() => handleImageClick(selectedProduct)}
                            >
                                <img src={selectedProduct.image} alt={selectedProduct.name} />
                                {selectedProduct.badge && (
                                    <span className={styles.badge}>{selectedProduct.badge}</span>
                                )}
                            </div>

                            <div className={styles.productInfo}>
                                <h3>{selectedProduct.name}</h3>

                                {selectedProduct.rating && (
                                    <div className={styles.rating}>
                                        {'★'.repeat(Math.floor(selectedProduct.rating))}
                                        {'☆'.repeat(5 - Math.floor(selectedProduct.rating))}
                                        <span>{selectedProduct.rating}</span>
                                        {selectedProduct.reviews && (
                                            <span>({selectedProduct.reviews} reviews)</span>
                                        )}
                                    </div>
                                )}

                                <p className={styles.price}>${selectedProduct.price.toFixed(2)}</p>

                                {selectedProduct.description && (
                                    <p className={styles.description}>{selectedProduct.description}</p>
                                )}

                                <div className={styles.actions}>
                                    <button className={styles.addToCart} onClick={handleAddToCart}>
                                        🛒 Add to Cart
                                    </button>
                                    <button
                                        className={styles.viewDetails}
                                        onClick={() => window.open(`/products/${selectedProduct.id}`, '_blank')}
                                    >
                                        View Full Details →
                                    </button>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </motion.div>
            )}

            {/* Image Preview Lightbox */}
            {previewImage && (
                <ImagePreview
                    src={previewImage.src}
                    alt={previewImage.alt}
                    onClose={() => setPreviewImage(null)}
                />
            )}
        </div>
    );
}
