'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { Button } from '@/components/ui/Button';
import styles from './Header.module.css';

interface HeaderProps {
    cartItemCount?: number;
}

export function Header({ cartItemCount = 0 }: HeaderProps) {
    const pathname = usePathname();
    const { user, logout, isAuthenticated } = useAuth();
    const { theme, toggleTheme } = useTheme();

    const navItems = [
        { href: '/', label: 'Home', icon: '🏠' },
        { href: '/products', label: 'Products', icon: '🛍️' },
        { href: '/chat', label: 'AI Assistant', icon: '🤖' },
        { href: '/orders', label: 'My Orders', icon: '📦' },
    ];

    // Admin-only nav items
    const adminItems = [
        { href: '/analytics', label: 'Analytics', icon: '📊' },
    ];

    const allNavItems = user?.role === 'admin' ? [...navItems, ...adminItems] : navItems;

    return (
        <motion.header
            className={styles.header}
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            transition={{ duration: 0.5, type: 'spring', stiffness: 100 }}
        >
            <div className={styles.container}>
                {/* Logo */}
                <Link href="/" className={styles.logo}>
                    <span className={styles.logoIcon}>🛒</span>
                    <span className={styles.logoText}>ShopAI</span>
                </Link>

                {/* Navigation */}
                <nav className={styles.nav}>
                    <ul className={styles.navList}>
                        {allNavItems.map((item) => (
                            <li key={item.href}>
                                <Link
                                    href={item.href}
                                    className={`${styles.navLink} ${pathname === item.href ? styles.active : ''}`}
                                >
                                    <span className={styles.navIcon}>{item.icon}</span>
                                    <span>{item.label}</span>
                                    {pathname === item.href && (
                                        <motion.div
                                            className={styles.activeIndicator}
                                            layoutId="activeNav"
                                            transition={{ duration: 0.3, type: 'spring', stiffness: 500, damping: 30 }}
                                        />
                                    )}
                                </Link>
                            </li>
                        ))}
                    </ul>
                </nav>

                {/* Actions */}
                <div className={styles.actions}>
                    {/* Cart */}
                    <Link href="/cart" className={styles.cartBtn}>
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <circle cx="9" cy="21" r="1" />
                            <circle cx="20" cy="21" r="1" />
                            <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
                        </svg>
                        {cartItemCount > 0 && (
                            <span className={styles.cartBadge}>{cartItemCount}</span>
                        )}
                    </Link>

                    {/* Theme Toggle */}
                    <button
                        className={styles.themeBtn}
                        onClick={toggleTheme}
                        aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
                    >
                        {theme === 'light' ? '🌙' : '☀️'}
                    </button>

                    {/* User Menu */}
                    {isAuthenticated ? (
                        <div className={styles.userMenu}>
                            <span className={styles.userName}>
                                {user?.role === 'admin' && '👑 '}
                                {user?.username}
                            </span>
                            <Button variant="ghost" size="sm" onClick={logout}>
                                Logout
                            </Button>
                        </div>
                    ) : (
                        <Link href="/login">
                            <Button variant="primary" size="sm">
                                Login
                            </Button>
                        </Link>
                    )}
                </div>
            </div>
        </motion.header>
    );
}
