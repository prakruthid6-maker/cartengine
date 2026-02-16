'use client';

import { forwardRef, ReactNode, MouseEvent } from 'react';
import { motion } from 'framer-motion';
import styles from './Button.module.css';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps {
    variant?: ButtonVariant;
    size?: ButtonSize;
    isLoading?: boolean;
    leftIcon?: ReactNode;
    rightIcon?: ReactNode;
    fullWidth?: boolean;
    children: ReactNode;
    className?: string;
    disabled?: boolean;
    type?: 'button' | 'submit' | 'reset';
    onClick?: (e: MouseEvent<HTMLButtonElement>) => void;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
    (
        {
            variant = 'primary',
            size = 'md',
            isLoading = false,
            leftIcon,
            rightIcon,
            fullWidth = false,
            children,
            className = '',
            disabled,
            type = 'button',
            onClick,
        },
        ref
    ) => {
        const classNames = [
            styles.button,
            styles[variant],
            styles[size],
            fullWidth ? styles.fullWidth : '',
            isLoading ? styles.loading : '',
            className,
        ]
            .filter(Boolean)
            .join(' ');

        return (
            <motion.button
                ref={ref}
                type={type}
                className={classNames}
                disabled={disabled || isLoading}
                whileHover={{ scale: disabled || isLoading ? 1 : 1.02 }}
                whileTap={{ scale: disabled || isLoading ? 1 : 0.98 }}
                transition={{ duration: 0.15 }}
                onClick={onClick}
            >
                {isLoading ? (
                    <span className={styles.spinner} />
                ) : (
                    <>
                        {leftIcon && <span className={styles.leftIcon}>{leftIcon}</span>}
                        <span>{children}</span>
                        {rightIcon && <span className={styles.rightIcon}>{rightIcon}</span>}
                    </>
                )}
            </motion.button>
        );
    }
);

Button.displayName = 'Button';
