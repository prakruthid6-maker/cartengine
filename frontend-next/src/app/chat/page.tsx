'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import { VoiceButton } from '@/components/voice/VoiceButton';
import { useVoice } from '@/hooks/useVoice';
import { useAuth } from '@/contexts/AuthContext';
import { ChatProductGrid, parseProductsFromMessage, parseCartFromMessage, ChatProduct } from '@/components/chat/ChatProductCard';
import { cartApi } from '@/lib/api';
import styles from './page.module.css';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    products?: ChatProduct[];
    cart?: { items: ChatProduct[]; total: number; count: number };
}

export default function ChatPage() {
    const { user } = useAuth();

    // Initialize messages from sessionStorage or use default welcome message
    const [messages, setMessages] = useState<Message[]>(() => {
        if (typeof window !== 'undefined') {
            try {
                const saved = sessionStorage.getItem('chat_messages');
                if (saved) {
                    const parsed = JSON.parse(saved);
                    // Convert timestamp strings back to Date objects
                    return parsed.map((msg: any) => ({
                        ...msg,
                        timestamp: new Date(msg.timestamp)
                    }));
                }
            } catch (error) {
                console.error('Failed to load chat history:', error);
            }
        }
        // Default welcome message
        return [
            {
                id: '1',
                role: 'assistant',
                content: "👋 Hi! I'm your AI shopping assistant. I can help you find products, track orders, get recommendations, and more. Try asking me something like:\n\n• \"Show me electronics under $100\"\n• \"What are the best rated products?\"\n• \"Help me find a gift for a tech lover\"",
                timestamp: new Date(),
            },
        ];
    });
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Voice integration
    const handleVoiceResult = useCallback((transcript: string) => {
        setInput(transcript);
    }, []);

    const {
        isListening,
        isSupported,
        transcript,
        startListening,
        stopListening,
        isSpeaking,
        cancelSpeech,
    } = useVoice({
        onResult: handleVoiceResult,
        language: 'en-US',
    });

    const handleVoiceToggle = () => {
        if (isListening) {
            stopListening();
        } else {
            cancelSpeech();
            startListening();
        }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    // Save messages to sessionStorage whenever they change
    useEffect(() => {
        if (typeof window !== 'undefined') {
            try {
                sessionStorage.setItem('chat_messages', JSON.stringify(messages));
            } catch (error) {
                console.error('Failed to save chat history:', error);
            }
        }
    }, [messages]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Handle adding product to cart from chat
    const handleAddToCart = async (productId: string) => {
        try {
            const userId = user?.id || 'guest';
            console.log('[Chat] Adding to cart:', { productId, userId });

            const response = await cartApi.add(productId, userId, 1);
            console.log('[Chat] Cart add response:', response);

            // Add a message confirming the action
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                role: 'assistant',
                content: `✅ Added to cart! Would you like to view your cart or continue shopping?`,
                timestamp: new Date(),
            }]);
        } catch (error) {
            console.error('[Chat] Failed to add to cart:', error);
            // Show error message to user
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                role: 'assistant',
                content: `❌ Sorry, I couldn't add that to your cart. ${error instanceof Error ? error.message : 'Please try again.'}`,
                timestamp: new Date(),
            }]);
        }
    };

    // Handle viewing product details
    const handleViewDetails = (productId: string) => {
        // Navigate to products page (no individual product detail page exists yet)
        window.open('/products', '_blank');
    };

    // Handle new chat button - clears conversation and starts fresh
    const handleNewChat = () => {
        if (messages.length > 1 && confirm('Start a new conversation? Current chat will be cleared.')) {
            // Clear sessionStorage
            if (typeof window !== 'undefined') {
                sessionStorage.removeItem('chat_messages');
                sessionStorage.removeItem('chat_session_id');
            }
            // Reset to welcome message
            setMessages([{
                id: '1',
                role: 'assistant',
                content: "👋 Hi! I'm your AI shopping assistant. I can help you find products, track orders, get recommendations, and more. Try asking me something like:\n\n• \"Show me electronics under $100\"\n• \"What are the best rated products?\"\n• \"Help me find a gift for a tech lover\"",
                timestamp: new Date(),
            }]);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input.trim(),
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        const assistantId = (Date.now() + 1).toString();
        setMessages((prev) => [
            ...prev,
            {
                id: assistantId,
                role: 'assistant',
                content: '',
                timestamp: new Date(),
            },
        ]);

        try {
            const response = await fetch('/api/chat/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: userMessage.content,
                    session_id: sessionStorage.getItem('chat_session_id') || undefined,
                    user_id: user?.id || 'guest',
                }),
            });

            if (!response.ok) throw new Error('Chat request failed');

            const reader = response.body?.getReader();
            if (!reader) throw new Error('No response stream');

            const decoder = new TextDecoder();
            let fullContent = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            if (data.content) {
                                fullContent += data.content;

                                // Parse products and cart from content
                                const { products, textContent: prodText } = parseProductsFromMessage(fullContent);
                                const { cart, textContent } = parseCartFromMessage(prodText);

                                setMessages((prev) =>
                                    prev.map((msg) =>
                                        msg.id === assistantId
                                            ? { ...msg, content: textContent || fullContent, products, cart: cart || undefined }
                                            : msg
                                    )
                                );
                            }
                            if (data.session_id) {
                                sessionStorage.setItem('chat_session_id', data.session_id);
                            }
                        } catch {
                            // Skip invalid JSON
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Chat error:', error);
            setMessages((prev) =>
                prev.map((msg) =>
                    msg.id === assistantId
                        ? { ...msg, content: 'Sorry, I encountered an error. Please try again.' }
                        : msg
                )
            );
        } finally {
            setIsLoading(false);
        }
    };

    const suggestedQueries = [
        "Show me trending products",
        "What's in my cart?",
        "Fashion products under $200",
    ];

    // Render message content with product cards
    const renderMessageContent = (message: Message) => {
        return (
            <>
                {/* Render product cards if present */}
                {message.products && message.products.length > 0 && (
                    <ChatProductGrid
                        products={message.products}
                        onAddToCart={handleAddToCart}
                        onViewDetails={handleViewDetails}
                    />
                )}

                {/* Render cart summary if present */}
                {message.cart && message.cart.items && message.cart.items.length > 0 && (
                    <div className={styles.cartSummary}>
                        <h4>🛒 Your Cart ({message.cart.count || message.cart.items.length} items)</h4>
                        {message.cart.items.map((item, i) => (
                            <div key={i} className={styles.cartItem}>
                                <span>{item?.name || 'Unknown item'}</span>
                                <span>${item?.price ? item.price.toFixed(2) : '0.00'}</span>
                            </div>
                        ))}
                        <div className={styles.cartTotal}>
                            <span>Total:</span>
                            <span>${message.cart.total ? message.cart.total.toFixed(2) : '0.00'}</span>
                        </div>
                    </div>
                )}

                {/* Render text content */}
                {message.content && message.content.split('\n').map((line, i) => (
                    <p key={i}>{line}</p>
                ))}
            </>
        );
    };

    return (
        <div className={styles.container}>
            {/* Chat Header */}
            <div className={styles.header}>
                <div className={styles.headerInfo}>
                    <span className={styles.avatar}>🤖</span>
                    <div>
                        <h1>AI Shopping Assistant</h1>
                        <p>Powered by Google Gemini</p>
                    </div>
                </div>
                <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                    <button
                        onClick={handleNewChat}
                        className={styles.newChatBtn}
                        title="Start new conversation"
                    >
                        ✨ New Chat
                    </button>
                    {user && (
                        <span className={styles.userBadge}>
                            {user.role === 'admin' ? '👑' : '👤'} {user.username}
                        </span>
                    )}
                </div>
            </div>

            {/* Messages */}
            <div className={styles.messages}>
                <AnimatePresence>
                    {messages.map((message) => (
                        <motion.div
                            key={message.id}
                            className={`${styles.message} ${styles[message.role]}`}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.3 }}
                        >
                            <div className={styles.messageContent}>
                                {renderMessageContent(message)}
                            </div>
                            <span className={styles.timestamp}>
                                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {isLoading && (
                    <motion.div
                        className={`${styles.message} ${styles.assistant}`}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                    >
                        <div className={styles.typing}>
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </motion.div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Suggested Queries */}
            {messages.length === 1 && (
                <div className={styles.suggestions}>
                    {suggestedQueries.map((query) => (
                        <button
                            key={query}
                            className={styles.suggestion}
                            onClick={() => setInput(query)}
                        >
                            {query}
                        </button>
                    ))}
                </div>
            )}

            {/* Input Form */}
            <form onSubmit={handleSubmit} className={styles.inputForm}>
                <VoiceButton
                    isListening={isListening}
                    isSupported={isSupported}
                    isSpeaking={isSpeaking}
                    onClick={handleVoiceToggle}
                    transcript={transcript}
                />
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder={isListening ? 'Listening...' : 'Ask me anything about products, orders, or recommendations...'}
                    disabled={isLoading}
                />
                <Button
                    type="submit"
                    variant="primary"
                    disabled={!input.trim() || isLoading}
                    isLoading={isLoading}
                >
                    Send
                </Button>
            </form>
        </div>
    );
}
