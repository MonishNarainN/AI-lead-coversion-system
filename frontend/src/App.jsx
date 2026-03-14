import React, { useState, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Upload from './components/Upload';
import Charts from './components/Charts';
import Results from './components/Results';
import BusinessRecommendations from './components/BusinessRecommendations';
import ReportExport from './components/ReportExport';
import { getPredictions } from './services/api';
import { Layout, Brain, BarChart3, List, Settings, ArrowLeft, AlertCircle, Zap } from 'lucide-react';

function App() {
    const [filename, setFilename] = useState(null);
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleUploadSuccess = async (name) => {
        setFilename(name);
        setResults(null);
        setError(null);
        setLoading(true);
        try {
            const data = await getPredictions(name);
            setResults(data);
        } catch (err) {
            console.error('Prediction failed', err);
            setError(err.response?.data?.error || 'Analysis failed. Please try a different file.');
        } finally {
            setLoading(false);
        }
    };

    const memoizedStatCards = useMemo(() => {
        if (!results) return null;
        const s = results.summary;
        const m = results.metrics;
        return (
            <div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.5rem', marginBottom: '1.5rem' }}>
                    <StatCard label="Total Leads" value={s.total_leads.toLocaleString()} color="var(--primary)" />
                    <StatCard label="Qualified Leads" value={s.expected_conversions.toLocaleString()} color="var(--accent-success)" />
                    <StatCard label="Avg. Confidence" value={`${(s.avg_probability * 100).toFixed(1)}%`} color="var(--accent-warning)" />
                    <StatCard label="Conversion Est." value={`${(s.conversion_rate * 100).toFixed(1)}%`} color="#c084fc" />
                </div>
                {m && (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
                        <StatCard label="Precision" value={m.precision.toFixed(3)} color="#10b981" />
                        <StatCard label="Recall" value={m.recall.toFixed(3)} color="#6366f1" />
                        <StatCard label="F1-Score" value={m.f1.toFixed(3)} color="#f59e0b" />
                    </div>
                )}
            </div>
        );
    }, [results]);

    return (
        <Router>
            <div className="app-container" style={{ display: 'flex', minHeight: '100vh' }}>
                {/* Sidebar */}
                <aside className="glass-panel" style={{ width: '260px', borderRadius: '0', borderLeft: 'none', borderTop: 'none', borderBottom: 'none', padding: '1.5rem', position: 'sticky', top: 0, height: '100vh', flexShrink: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2.5rem' }}>
                        <div style={{ background: 'linear-gradient(135deg, var(--primary), #8b5cf6)', padding: '8px', borderRadius: '10px' }}>
                            <Brain size={22} color="white" />
                        </div>
                        <div>
                            <h2 className="text-gradient" style={{ fontSize: '1.1rem', lineHeight: 1 }}>LeadPro AI</h2>
                            <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '2px' }}>Enterprise Edition</p>
                        </div>
                    </div>

                    <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                        <NavItem icon={<Layout size={18} />} label="Dashboard" to="/" />
                        <NavItem icon={<BarChart3 size={18} />} label="Analytics" to="/analytics" />
                        <NavItem icon={<List size={18} />} label="Predictions" to="/predictions" />
                        <NavItem icon={<Zap size={18} />} label="Insights" to="/insights" />
                        <div style={{ marginTop: 'auto', paddingTop: '2rem' }}>
                            <NavItem icon={<Settings size={18} />} label="Settings" to="/settings" />
                        </div>
                    </nav>

                    {results && (
                        <div style={{ marginTop: '2rem', padding: '0.875rem', background: 'rgba(99,102,241,0.08)', borderRadius: '10px', border: '1px solid rgba(99,102,241,0.2)' }}>
                            <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>Active Dataset</p>
                            <p style={{ fontSize: '0.8rem', fontWeight: '600', wordBreak: 'break-all' }}>{filename}</p>
                            <p style={{ fontSize: '0.7rem', color: 'var(--accent-success)', marginTop: '0.4rem' }}>
                                {results.cached ? '⚡ Cached result' : '✓ Live analysis'}
                            </p>
                        </div>
                    )}
                </aside>

                {/* Main Content */}
                <main style={{ flex: 1, padding: '2rem', overflowY: 'auto' }}>
                    <Routes>
                        <Route path="/" element={
                            <Dashboard
                                filename={filename}
                                results={results}
                                loading={loading}
                                onUploadSuccess={handleUploadSuccess}
                                onReset={() => { setFilename(null); setResults(null); setError(null); }}
                                memoizedStatCards={memoizedStatCards}
                                error={error}
                            />
                        } />
                        <Route path="/analytics" element={
                            results ? (
                                <div className="animate-fade-in">
                                    <PageHeader title="Analytics" subtitle="Deep-dive into your lead pipeline metrics" />
                                    <Charts
                                        distribution={results.distribution}
                                        confidence_histogram={results.confidence_histogram}
                                        feature_importance={results.feature_importance}
                                    />
                                </div>
                            ) : <NoDataMessage />
                        } />
                        <Route path="/predictions" element={
                            results ? (
                                <div className="animate-fade-in">
                                    <PageHeader title="Predictions" subtitle="Sorted by conversion probability" />
                                    <ReportExport filename={filename} summary={results.summary} />
                                    <Results data={results.data} />
                                </div>
                            ) : <NoDataMessage />
                        } />
                        <Route path="/insights" element={
                            results ? (
                                <div className="animate-fade-in">
                                    <PageHeader title="AI Insights" subtitle="Actionable business intelligence" />
                                    <BusinessRecommendations recommendations={results.recommendations} />
                                    {results.feature_importance && (
                                        <div className="glass-panel" style={{ padding: '1.5rem' }}>
                                            <h3 style={{ marginBottom: '1rem', fontSize: '0.875rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Feature Importance Ranking</h3>
                                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                                                {results.feature_importance.slice(0, 8).map((f, i) => (
                                                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                                        <span style={{ width: '180px', fontSize: '0.825rem', color: '#94a3b8' }}>{f.feature}</span>
                                                        <div style={{ flex: 1, background: 'rgba(255,255,255,0.05)', borderRadius: '4px', height: '8px' }}>
                                                            <div style={{
                                                                width: `${(f.importance / (results.feature_importance[0]?.importance || 1)) * 100}%`,
                                                                height: '100%',
                                                                borderRadius: '4px',
                                                                background: 'linear-gradient(90deg, #6366f1, #8b5cf6)'
                                                            }} />
                                                        </div>
                                                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', width: '50px', textAlign: 'right' }}>{f.importance.toFixed(3)}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ) : <NoDataMessage />
                        } />
                        <Route path="*" element={<div style={{ textAlign: 'center', marginTop: '10rem' }}><h2>Coming Soon</h2><p style={{ color: 'var(--text-muted)' }}>This page is under development.</p></div>} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

const PageHeader = ({ title, subtitle }) => (
    <header style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: '700', marginBottom: '0.25rem' }}>{title}</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{subtitle}</p>
    </header>
);

const Dashboard = ({ filename, results, loading, onUploadSuccess, onReset, memoizedStatCards, error }) => (
    <div className="animate-fade-in">
        <header style={{ marginBottom: '2.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
                <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Lead Conversion Engine</h1>
                <p style={{ color: 'var(--text-muted)' }}>AI-driven predictive scoring & analytics</p>
            </div>
            <div className="glass-panel" style={{ padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--accent-success)', boxShadow: '0 0 6px var(--accent-success)' }} />
                <span style={{ fontSize: '0.875rem' }}>System Online</span>
            </div>
        </header>

        {!filename ? (
            <Upload onUploadSuccess={onUploadSuccess} />
        ) : (
            <div>
                {loading ? (
                    <div style={{ textAlign: 'center', marginTop: '8rem' }}>
                        <div className="animate-spin" style={{ display: 'inline-block', marginBottom: '1.5rem' }}>
                            <Brain size={64} color="var(--primary)" />
                        </div>
                        <h2>Analyzing Dataset...</h2>
                        <p style={{ color: 'var(--text-muted)', maxWidth: '400px', margin: '0.5rem auto' }}>
                            Aligning columns, running preprocessing, and computing predictions.
                        </p>
                    </div>
                ) : error ? (
                    <div style={{ textAlign: 'center', marginTop: '8rem' }}>
                        <AlertCircle size={64} color="var(--accent-error)" style={{ marginBottom: '1.5rem' }} />
                        <h2>Analysis Failed</h2>
                        <p style={{ color: 'var(--text-muted)', maxWidth: '400px', margin: '0.5rem auto' }}>{error}</p>
                        <button className="btn-primary" style={{ marginTop: '1.5rem', marginInline: 'auto' }} onClick={onReset}>Try Again</button>
                    </div>
                ) : (
                    results && (
                        <div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
                                <button
                                    style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid var(--glass-border)', color: 'white', padding: '10px 20px', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}
                                    onClick={onReset}
                                >
                                    <ArrowLeft size={18} /> New Analysis
                                </button>
                                <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                                    Showing results for: <strong>{filename}</strong>
                                    {results.cached && <span style={{ marginLeft: '0.75rem', color: '#f59e0b', fontSize: '0.75rem' }}>⚡ Cached</span>}
                                </div>
                            </div>
                            {memoizedStatCards}
                            <BusinessRecommendations recommendations={results.recommendations} />
                            <Charts
                                distribution={results.distribution}
                                confidence_histogram={results.confidence_histogram}
                                feature_importance={results.feature_importance}
                            />
                            <ReportExport filename={filename} summary={results.summary} />
                            <Results data={results.data} />
                        </div>
                    )
                )}
            </div>
        )}
    </div>
);

const NoDataMessage = () => (
    <div style={{ textAlign: 'center', marginTop: '10rem' }}>
        <Brain size={48} color="var(--text-muted)" style={{ marginBottom: '1rem', opacity: 0.4 }} />
        <h2>No Data Available</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>Upload a dataset in the Dashboard to begin analysis.</p>
        <Link to="/" style={{ color: 'var(--primary)', textDecoration: 'none', fontWeight: '600' }}>← Go to Dashboard</Link>
    </div>
);

const NavItem = ({ icon, label, to }) => {
    const location = useLocation();
    const active = location.pathname === to;
    return (
        <Link to={to} style={{ textDecoration: 'none' }}>
            <div style={{
                padding: '0.7rem 1rem',
                borderRadius: '10px',
                backgroundColor: active ? 'rgba(99,102,241,0.12)' : 'transparent',
                color: active ? 'var(--primary)' : 'var(--text-muted)',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                fontWeight: active ? '600' : '500',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                fontSize: '0.9rem',
            }}>
                {icon}<span>{label}</span>
            </div>
        </Link>
    );
};

const StatCard = ({ label, value, color }) => (
    <div className="glass-panel" style={{ padding: '1.5rem', borderLeft: `3px solid ${color}` }}>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: '0.5rem', fontWeight: '500', textTransform: 'uppercase', letterSpacing: '0.04em' }}>{label}</p>
        <h3 style={{ fontSize: '1.75rem', fontWeight: '700', color: color }}>{value}</h3>
    </div>
);

export default App;
