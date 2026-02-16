'use client';

import { ReactNode } from 'react';
import { motion } from 'framer-motion';
import styles from './Card.module.css';

interface CardProps {
    variant?: 'default' | 'elevated' | 'glass' | 'outlined';
    padding?: 'none' | 'sm' | 'md' | 'lg';
    hover?: boolean;
    children: ReactNode;
    className?: string;
    onClick?: () => void;
}

export function Card({
    variant = 'default',
    padding = 'md',
    hover = false,
    children,
    className = '',
    onClick,
}: CardProps) {
    const classNames = [
        styles.card,
        styles[variant],
        styles[`padding-${padding}`],
        hover ? styles.hoverable : '',
        className,
    ]
        .filter(Boolean)
        .join(' ');

    return (
        <motion.div
            className={classNames}
            whileHover={hover ? { y: -4 } : undefined}
            transition={{ duration: 0.2 }}
            onClick={onClick}
        >
            {children}
        </motion.div>
    );
}

// Card Header component
interface CardHeaderProps {
    children: ReactNode;
    className?: string;
}

export function CardHeader({ children, className = '' }: CardHeaderProps) {
    return <div className={`${styles.cardHeader} ${className}`}>{children}</div>;
}

// Card Content component
interface CardContentProps {
    children: ReactNode;
    className?: string;
}

export function CardContent({ children, className = '' }: CardContentProps) {
    return <div className={`${styles.cardContent} ${className}`}>{children}</div>;
}

// Card Footer component
interface CardFooterProps {
    children: ReactNode;
    className?: string;
}

export function CardFooter({ children, className = '' }: CardFooterProps) {
    return <div className={`${styles.cardFooter} ${className}`}>{children}</div>;
}
