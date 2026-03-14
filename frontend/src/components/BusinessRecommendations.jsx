import React from 'react';
import { TrendingUp, AlertTriangle, Info, CheckCircle } from 'lucide-react';

const ICONS = {
    success: <CheckCircle size={20} color="#10b981" />,
    warning: <AlertTriangle size={20} color="#f59e0b" />,
    info: <Info size={20} color="#6366f1" />,
    error: <AlertTriangle size={20} color="#ef4444" />,
};

const COLORS = {
    success: { bg: 'rgba(16,185,129,0.08)', border: '#10b981' },
    warning: { bg: 'rgba(245,158,11,0.08)', border: '#f59e0b' },
    info: { bg: 'rgba(99,102,241,0.08)', border: '#6366f1' },
    error: { bg: 'rgba(239,68,68,0.08)', border: '#ef4444' },
};

const BusinessRecommendations = ({ recommendations }) => {
    if (!recommendations || recommendations.length === 0) return null;

    return (
        <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem' }}>
                <TrendingUp size={20} color="var(--primary)" />
                <h3 style={{ fontSize: '1rem', fontWeight: '600' }}>Actionable Intelligence</h3>
                <span style={{ fontSize: '0.75rem', background: 'rgba(99,102,241,0.15)', color: 'var(--primary)', padding: '2px 10px', borderRadius: '20px', fontWeight: '600' }}>
                    AI Insights
                </span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {recommendations.map((rec, i) => {
                    const style = COLORS[rec.type] || COLORS.info;
                    return (
                        <div
                            key={i}
                            style={{
                                display: 'flex',
                                alignItems: 'flex-start',
                                gap: '0.75rem',
                                background: style.bg,
                                border: `1px solid ${style.border}30`,
                                borderLeft: `3px solid ${style.border}`,
                                borderRadius: '8px',
                                padding: '0.875rem 1rem',
                            }}
                        >
                            <div style={{ flexShrink: 0, marginTop: '2px' }}>{ICONS[rec.type] || ICONS.info}</div>
                            <div>
                                <p style={{ fontWeight: '600', marginBottom: '0.25rem', fontSize: '0.9rem' }}>{rec.title}</p>
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: '1.5' }}>{rec.message}</p>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default BusinessRecommendations;
