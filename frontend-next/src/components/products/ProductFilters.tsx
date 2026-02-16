'use client';

import { FilterOptions } from '@/types';
import { Button } from '@/components/ui/Button';
import styles from './ProductFilters.module.css';

interface ProductFiltersProps {
    categories: string[];
    badges: string[];
    filters: FilterOptions;
    onFilterChange: (filters: FilterOptions) => void;
}

export function ProductFilters({
    categories,
    badges,
    filters,
    onFilterChange,
}: ProductFiltersProps) {
    const priceRanges = [
        { label: 'Under $50', min: 0, max: 50 },
        { label: '$50 - $100', min: 50, max: 100 },
        { label: '$100 - $500', min: 100, max: 500 },
        { label: '$500+', min: 500, max: undefined },
    ];

    const sortOptions = [
        { value: 'price-asc', label: 'Price: Low to High' },
        { value: 'price-desc', label: 'Price: High to Low' },
        { value: 'rating-desc', label: 'Highest Rated' },
        { value: 'reviews-desc', label: 'Most Reviews' },
        { value: 'newest-desc', label: 'Newest First' },
    ];

    const handleCategoryChange = (category: string) => {
        onFilterChange({
            ...filters,
            category: filters.category === category ? undefined : category,
        });
    };

    const handlePriceChange = (min: number, max: number | undefined) => {
        const isSelected = filters.minPrice === min && filters.maxPrice === max;
        onFilterChange({
            ...filters,
            minPrice: isSelected ? undefined : min,
            maxPrice: isSelected ? undefined : max,
        });
    };

    const handleBadgeChange = (badge: string) => {
        onFilterChange({
            ...filters,
            badge: filters.badge === badge ? undefined : badge,
        });
    };

    const handleSortChange = (value: string) => {
        const [sortBy, sortOrder] = value.split('-') as [FilterOptions['sortBy'], FilterOptions['sortOrder']];
        onFilterChange({
            ...filters,
            sortBy,
            sortOrder,
        });
    };

    const handleReset = () => {
        onFilterChange({});
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h3>Filters</h3>
                <button className={styles.resetBtn} onClick={handleReset}>
                    Reset All
                </button>
            </div>

            {/* Category Filter */}
            <div className={styles.section}>
                <h4 className={styles.sectionTitle}>Category</h4>
                <div className={styles.options}>
                    {categories.map((category) => (
                        <button
                            key={category}
                            className={`${styles.chip} ${filters.category === category ? styles.active : ''}`}
                            onClick={() => handleCategoryChange(category)}
                        >
                            {category}
                        </button>
                    ))}
                </div>
            </div>

            {/* Price Filter */}
            <div className={styles.section}>
                <h4 className={styles.sectionTitle}>Price Range</h4>
                <div className={styles.options}>
                    {priceRanges.map((range) => (
                        <button
                            key={range.label}
                            className={`${styles.chip} ${filters.minPrice === range.min && filters.maxPrice === range.max
                                    ? styles.active
                                    : ''
                                }`}
                            onClick={() => handlePriceChange(range.min, range.max)}
                        >
                            {range.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Badge Filter */}
            {badges.length > 0 && (
                <div className={styles.section}>
                    <h4 className={styles.sectionTitle}>Badges</h4>
                    <div className={styles.options}>
                        {badges.map((badge) => (
                            <button
                                key={badge}
                                className={`${styles.chip} ${filters.badge === badge ? styles.active : ''}`}
                                onClick={() => handleBadgeChange(badge)}
                            >
                                {badge}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Sort */}
            <div className={styles.section}>
                <h4 className={styles.sectionTitle}>Sort By</h4>
                <select
                    className={styles.select}
                    value={filters.sortBy && filters.sortOrder ? `${filters.sortBy}-${filters.sortOrder}` : ''}
                    onChange={(e) => handleSortChange(e.target.value)}
                >
                    <option value="">Default</option>
                    {sortOptions.map((option) => (
                        <option key={option.value} value={option.value}>
                            {option.label}
                        </option>
                    ))}
                </select>
            </div>
        </div>
    );
}
