'use client';

import { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './ImagePreview.module.css';

interface ImagePreviewProps {
    src: string;
    alt: string;
    onClose: () => void;
}

export function ImagePreview({ src, alt, onClose }: ImagePreviewProps) {
    const [scale, setScale] = useState(1);
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [isDragging, setIsDragging] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);
    const dragStart = useRef({ x: 0, y: 0 });

    const handleWheel = useCallback((e: React.WheelEvent) => {
        e.preventDefault();
        const delta = e.deltaY > 0 ? -0.1 : 0.1;
        setScale((prev) => Math.min(Math.max(prev + delta, 0.5), 4));
    }, []);

    const handleMouseDown = (e: React.MouseEvent) => {
        if (scale > 1) {
            setIsDragging(true);
            dragStart.current = { x: e.clientX - position.x, y: e.clientY - position.y };
        }
    };

    const handleMouseMove = (e: React.MouseEvent) => {
        if (isDragging) {
            setPosition({
                x: e.clientX - dragStart.current.x,
                y: e.clientY - dragStart.current.y,
            });
        }
    };

    const handleMouseUp = () => {
        setIsDragging(false);
    };

    const resetView = () => {
        setScale(1);
        setPosition({ x: 0, y: 0 });
    };

    const zoomIn = () => setScale((prev) => Math.min(prev + 0.5, 4));
    const zoomOut = () => setScale((prev) => Math.max(prev - 0.5, 0.5));

    return (
        <AnimatePresence>
            <motion.div
                className={styles.overlay}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={onClose}
            >
                <motion.div
                    className={styles.container}
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.8, opacity: 0 }}
                    onClick={(e) => e.stopPropagation()}
                >
                    {/* Controls */}
                    <div className={styles.controls}>
                        <button onClick={zoomOut} title="Zoom out">−</button>
                        <span>{Math.round(scale * 100)}%</span>
                        <button onClick={zoomIn} title="Zoom in">+</button>
                        <button onClick={resetView} title="Reset">⟲</button>
                        <button onClick={onClose} className={styles.closeBtn} title="Close">✕</button>
                    </div>

                    {/* Image Container */}
                    <div
                        ref={containerRef}
                        className={styles.imageContainer}
                        onWheel={handleWheel}
                        onMouseDown={handleMouseDown}
                        onMouseMove={handleMouseMove}
                        onMouseUp={handleMouseUp}
                        onMouseLeave={handleMouseUp}
                        style={{ cursor: scale > 1 ? (isDragging ? 'grabbing' : 'grab') : 'zoom-in' }}
                    >
                        <motion.img
                            src={src}
                            alt={alt}
                            className={styles.image}
                            style={{
                                transform: `scale(${scale}) translate(${position.x / scale}px, ${position.y / scale}px)`,
                            }}
                            draggable={false}
                        />
                    </div>

                    {/* Caption */}
                    <div className={styles.caption}>{alt}</div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
}
