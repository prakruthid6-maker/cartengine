import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import styles from './page.module.css';

export default function HomePage() {
  return (
    <div className={styles.container}>
      {/* Hero Section */}
      <section className={styles.hero}>
        <div className={styles.heroContent}>
          <span className={styles.badge}>🚀 AI-Powered Shopping</span>
          <h1 className={styles.title}>
            Shop Smarter with
            <span className={styles.gradient}> AI</span>
          </h1>
          <p className={styles.subtitle}>
            Experience the future of e-commerce with voice search, intelligent recommendations,
            and a conversational AI assistant that understands your needs.
          </p>
          <div className={styles.cta}>
            <Link href="/products">
              <Button variant="primary" size="lg">
                Start Shopping
              </Button>
            </Link>
            <Link href="/chat">
              <Button variant="outline" size="lg">
                Chat with AI
              </Button>
            </Link>
          </div>
        </div>

        {/* Floating cards decoration */}
        <div className={styles.heroVisual}>
          <div className={`${styles.floatingCard} ${styles.card1}`}>
            <span>🎧</span>
            <p>Electronics</p>
          </div>
          <div className={`${styles.floatingCard} ${styles.card2}`}>
            <span>👕</span>
            <p>Fashion</p>
          </div>
          <div className={`${styles.floatingCard} ${styles.card3}`}>
            <span>📚</span>
            <p>Books</p>
          </div>
          <div className={`${styles.floatingCard} ${styles.card4}`}>
            <span>🏠</span>
            <p>Home</p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className={styles.features}>
        <h2 className={styles.sectionTitle}>Why Shop with AI?</h2>
        <div className={styles.featureGrid}>
          <div className={styles.feature}>
            <div className={styles.featureIcon}>🎤</div>
            <h3>Voice Search</h3>
            <p>Just speak to search. Say &quot;Show me electronics under $100&quot; and watch the magic happen.</p>
          </div>
          <div className={styles.feature}>
            <div className={styles.featureIcon}>🤖</div>
            <h3>AI Assistant</h3>
            <p>Get personalized recommendations, track orders, and manage your wishlist through conversation.</p>
          </div>
          <div className={styles.feature}>
            <div className={styles.featureIcon}>⚡</div>
            <h3>Smart Recommendations</h3>
            <p>Our AI learns your preferences to suggest products you&apos;ll actually love.</p>
          </div>
          <div className={styles.feature}>
            <div className={styles.featureIcon}>📦</div>
            <h3>Real-time Tracking</h3>
            <p>Track your orders in real-time with detailed delivery status updates.</p>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className={styles.stats}>
        <div className={styles.stat}>
          <span className={styles.statNumber}>50+</span>
          <span className={styles.statLabel}>AI Tools</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statNumber}>4</span>
          <span className={styles.statLabel}>Categories</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statNumber}>24/7</span>
          <span className={styles.statLabel}>AI Support</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statNumber}>100%</span>
          <span className={styles.statLabel}>Voice-Enabled</span>
        </div>
      </section>
    </div>
  );
}
