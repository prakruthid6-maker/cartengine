'use client';

import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { User, AuthState } from '@/types';

interface AuthContextType extends AuthState {
    login: (username: string, password: string) => Promise<boolean>;
    logout: () => void;
    isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Demo credentials (replace with real auth in production)
const DEMO_USERS = {
    user: { password: 'user123', role: 'customer' as const },
    admin: { password: 'admin123', role: 'admin' as const },
};

export function AuthProvider({ children }: { children: ReactNode }) {
    const [authState, setAuthState] = useState<AuthState>({
        user: null,
        token: null,
        isAuthenticated: false,
    });
    const [isLoading, setIsLoading] = useState(true);

    // Check for existing session on mount
    useEffect(() => {
        const savedSession = localStorage.getItem('userSession');
        if (savedSession) {
            try {
                const session = JSON.parse(savedSession);
                setAuthState({
                    user: session.user,
                    token: session.token,
                    isAuthenticated: true,
                });
            } catch {
                localStorage.removeItem('userSession');
            }
        }
        setIsLoading(false);
    }, []);

    const login = useCallback(async (username: string, password: string): Promise<boolean> => {
        setIsLoading(true);

        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 500));

        const demoUser = DEMO_USERS[username as keyof typeof DEMO_USERS];

        if (demoUser && demoUser.password === password) {
            const user: User = {
                id: `user-${Date.now()}`,
                username,
                role: demoUser.role,
            };

            // In production, this would be a real JWT from the backend
            const token = `demo-token-${Date.now()}`;

            const session = { user, token };
            localStorage.setItem('userSession', JSON.stringify(session));

            setAuthState({
                user,
                token,
                isAuthenticated: true,
            });

            setIsLoading(false);
            return true;
        }

        setIsLoading(false);
        return false;
    }, []);

    const logout = useCallback(() => {
        localStorage.removeItem('userSession');
        setAuthState({
            user: null,
            token: null,
            isAuthenticated: false,
        });
    }, []);

    return (
        <AuthContext.Provider value={{ ...authState, login, logout, isLoading }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
