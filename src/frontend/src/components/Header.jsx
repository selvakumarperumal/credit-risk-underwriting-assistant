import { useState, useEffect } from 'react';
import { checkHealth } from '../services/api';
import './Header.css';

export default function Header() {
    const [health, setHealth] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchHealth = async () => {
            setLoading(true);
            const result = await checkHealth();
            setHealth(result);
            setLoading(false);
        };

        fetchHealth();

        // Poll health status every 30 seconds
        const interval = setInterval(fetchHealth, 30000);
        return () => clearInterval(interval);
    }, []);

    const getStatusInfo = () => {
        if (loading) return { status: 'checking', label: 'Checking...', color: 'warning' };
        if (!health || health.error) return { status: 'offline', label: 'Offline', color: 'error' };
        if (health.status === 'ready') return { status: 'ready', label: 'Ready', color: 'success' };
        if (health.status === 'waiting_for_api_key') return { status: 'waiting', label: 'Need API Key', color: 'warning' };
        return { status: 'healthy', label: 'Healthy', color: 'success' };
    };

    const statusInfo = getStatusInfo();

    return (
        <header className="header">
            <div className="container header-content">
                <div className="header-brand">
                    <div className="logo">
                        <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <rect width="36" height="36" rx="8" fill="url(#logo-gradient)" />
                            <path d="M10 18C10 13.5817 13.5817 10 18 10V10C22.4183 10 26 13.5817 26 18V18C26 22.4183 22.4183 26 18 26V26C13.5817 26 10 22.4183 10 18V18Z" stroke="white" strokeWidth="2" />
                            <path d="M14 18L17 21L22 15" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            <defs>
                                <linearGradient id="logo-gradient" x1="0" y1="0" x2="36" y2="36" gradientUnits="userSpaceOnUse">
                                    <stop stopColor="#3b82f6" />
                                    <stop offset="1" stopColor="#8b5cf6" />
                                </linearGradient>
                            </defs>
                        </svg>
                    </div>
                    <div className="header-title">
                        <h1 className="gradient-text">Credit Risk Assistant</h1>
                        <p className="header-subtitle">AI-Powered Underwriting Analysis</p>
                    </div>
                </div>

                <div className="header-status">
                    <div className="status-indicator">
                        <span className={`status-dot ${statusInfo.color}`}></span>
                        <span className="status-label">{statusInfo.label}</span>
                    </div>
                    {health && !health.error && (
                        <div className="status-model">
                            <span className="badge badge-info">{health.model || 'Gemini'}</span>
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
}
