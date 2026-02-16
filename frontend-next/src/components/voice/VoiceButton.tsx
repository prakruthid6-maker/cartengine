'use client';

import { motion, AnimatePresence } from 'framer-motion';
import styles from './VoiceButton.module.css';

interface VoiceButtonProps {
    isListening: boolean;
    isSupported: boolean;
    isSpeaking?: boolean;
    onClick: () => void;
    transcript?: string;
}

export function VoiceButton({
    isListening,
    isSupported,
    isSpeaking = false,
    onClick,
    transcript,
}: VoiceButtonProps) {
    if (!isSupported) {
        return null;
    }

    return (
        <div className={styles.container}>
            <motion.button
                type="button"
                className={`${styles.button} ${isListening ? styles.listening : ''} ${isSpeaking ? styles.speaking : ''}`}
                onClick={onClick}
                whileTap={{ scale: 0.95 }}
                aria-label={isListening ? 'Stop listening' : 'Start voice input'}
            >
                {isListening ? (
                    <motion.div
                        className={styles.waves}
                        initial={{ scale: 1 }}
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ repeat: Infinity, duration: 1 }}
                    >
                        <span className={styles.wave}></span>
                        <span className={styles.wave}></span>
                        <span className={styles.wave}></span>
                    </motion.div>
                ) : isSpeaking ? (
                    <svg className={styles.icon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M11 5L6 9H2v6h4l5 4V5z" />
                        <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" />
                    </svg>
                ) : (
                    <svg className={styles.icon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                        <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                        <line x1="12" y1="19" x2="12" y2="23" />
                        <line x1="8" y1="23" x2="16" y2="23" />
                    </svg>
                )}
            </motion.button>

            {/* Transcript preview */}
            <AnimatePresence>
                {isListening && transcript && (
                    <motion.div
                        className={styles.transcript}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 10 }}
                    >
                        {transcript}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
