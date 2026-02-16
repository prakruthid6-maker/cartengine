'use client';

import { useState, useCallback, useRef, useEffect } from 'react';

interface UseVoiceOptions {
    onResult?: (transcript: string) => void;
    onError?: (error: string) => void;
    language?: string;
    continuous?: boolean;
}

interface UseVoiceReturn {
    isListening: boolean;
    isSupported: boolean;
    transcript: string;
    startListening: () => void;
    stopListening: () => void;
    speak: (text: string) => void;
    isSpeaking: boolean;
    cancelSpeech: () => void;
}

/**
 * Custom hook for voice input (Speech-to-Text) and output (Text-to-Speech)
 * using Web Speech API.
 */
export function useVoice({
    onResult,
    onError,
    language = 'en-US',
    continuous = false,
}: UseVoiceOptions = {}): UseVoiceReturn {
    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [isSupported, setIsSupported] = useState(false);

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const recognitionRef = useRef<any>(null);
    const synthRef = useRef<SpeechSynthesis | null>(null);

    // Check for browser support
    useEffect(() => {
        if (typeof window !== 'undefined') {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const SpeechRecognitionAPI = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
            setIsSupported(!!SpeechRecognitionAPI && !!window.speechSynthesis);

            if (SpeechRecognitionAPI) {
                recognitionRef.current = new SpeechRecognitionAPI();
                recognitionRef.current.continuous = continuous;
                recognitionRef.current.interimResults = true;
                recognitionRef.current.lang = language;

                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                recognitionRef.current.onresult = (event: any) => {
                    const results = Array.from(event.results) as SpeechRecognitionResult[];
                    const current = results[results.length - 1];

                    if (current.isFinal) {
                        const finalTranscript = current[0].transcript;
                        setTranscript(finalTranscript);
                        onResult?.(finalTranscript);
                    } else {
                        // Show interim results
                        setTranscript(current[0].transcript);
                    }
                };

                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                recognitionRef.current.onerror = (event: any) => {
                    // Network errors are common when offline - handle gracefully
                    if (event.error === 'network') {
                        console.warn('Speech recognition unavailable - check internet connection');
                    } else if (event.error !== 'aborted' && event.error !== 'no-speech') {
                        console.error('Speech recognition error:', event.error);
                    }
                    setIsListening(false);
                    onError?.(event.error);
                };

                recognitionRef.current.onend = () => {
                    setIsListening(false);
                };
            }

            synthRef.current = window.speechSynthesis;
        }

        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.abort();
            }
            if (synthRef.current) {
                synthRef.current.cancel();
            }
        };
    }, [language, continuous, onResult, onError]);

    const startListening = useCallback(() => {
        if (recognitionRef.current && !isListening) {
            setTranscript('');
            setIsListening(true);
            try {
                recognitionRef.current.start();
            } catch (e) {
                console.error('Failed to start speech recognition:', e);
                setIsListening(false);
            }
        }
    }, [isListening]);

    const stopListening = useCallback(() => {
        if (recognitionRef.current && isListening) {
            recognitionRef.current.stop();
            setIsListening(false);
        }
    }, [isListening]);

    const speak = useCallback((text: string) => {
        if (synthRef.current) {
            // Cancel any ongoing speech
            synthRef.current.cancel();

            // Clean text for TTS (remove markdown, emojis, etc.)
            const cleanText = text
                .replace(/[*#`]/g, '')
                .replace(/\n+/g, '. ')
                .replace(/[^\w\s.,!?'-]/g, '');

            const utterance = new SpeechSynthesisUtterance(cleanText);
            utterance.lang = language;
            utterance.rate = 1.0;
            utterance.pitch = 1.0;

            // Get a natural-sounding voice
            const voices = synthRef.current.getVoices();
            const preferredVoice = voices.find(
                (v) => v.lang.startsWith('en') && v.name.includes('Google')
            ) || voices.find((v) => v.lang.startsWith('en') && v.localService === false)
                || voices.find((v) => v.lang.startsWith('en'));

            if (preferredVoice) {
                utterance.voice = preferredVoice;
            }

            utterance.onstart = () => setIsSpeaking(true);
            utterance.onend = () => setIsSpeaking(false);
            utterance.onerror = () => setIsSpeaking(false);

            synthRef.current.speak(utterance);
        }
    }, [language]);

    const cancelSpeech = useCallback(() => {
        if (synthRef.current) {
            synthRef.current.cancel();
            setIsSpeaking(false);
        }
    }, []);

    return {
        isListening,
        isSupported,
        transcript,
        startListening,
        stopListening,
        speak,
        isSpeaking,
        cancelSpeech,
    };
}
