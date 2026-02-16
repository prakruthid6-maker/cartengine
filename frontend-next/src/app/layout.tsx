import type { Metadata } from 'next';
import { Outfit } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';
import { Header } from '@/components/layout/Header';

const outfit = Outfit({
  subsets: ['latin'],
  variable: '--font-outfit',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'ShopAI - AI-Powered E-Commerce',
  description: 'An immersive, AI-driven shopping experience with voice search, smart recommendations, and conversational commerce.',
  keywords: ['e-commerce', 'AI shopping', 'voice commerce', 'smart recommendations'],
  authors: [{ name: 'Los_codigos_782' }],
  openGraph: {
    title: 'ShopAI - AI-Powered E-Commerce',
    description: 'An immersive, AI-driven shopping experience',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={outfit.variable} suppressHydrationWarning>
      <body>
        <Providers>
          <Header />
          <main className="main-content">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
