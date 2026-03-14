import React from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement,
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const CHART_TOOLTIP = {
    backgroundColor: 'rgba(15, 23, 42, 0.95)',
    titleFont: { size: 13, weight: 'bold' },
    bodyFont: { size: 12 },
    padding: 12,
    cornerRadius: 8,
    borderColor: 'rgba(99,102,241,0.3)',
    borderWidth: 1,
};

const AXIS_STYLE = {
    y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
    x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
};

const Charts = ({ distribution, confidence_histogram, feature_importance }) => {
    if (!distribution) return null;

    const decisionLabels = Object.keys(distribution);
    const decisionValues = Object.values(distribution);

    const COLOR_MAP = {
        'Hot Lead': { bg: 'rgba(239,68,68,0.7)', border: '#ef4444' },
        'Warm Lead': { bg: 'rgba(245,158,11,0.7)', border: '#f59e0b' },
        'Cold Lead': { bg: 'rgba(99,102,241,0.7)', border: '#6366f1' },
    };

    const barColors = decisionLabels.map(l => COLOR_MAP[l]?.bg || 'rgba(99,102,241,0.6)');
    const borderColors = decisionLabels.map(l => COLOR_MAP[l]?.border || '#6366f1');

    const baseOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: CHART_TOOLTIP },
        scales: AXIS_STYLE,
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginBottom: '2.5rem' }}>

            {/* Row 1: Distribution Bar + Donut */}
            <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '1.5rem' }}>
                <div className="glass-panel" style={{ padding: '1.5rem' }}>
                    <h3 style={{ marginBottom: '1rem', fontSize: '0.875rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        Lead Priority Distribution
                    </h3>
                    <div style={{ height: '260px' }}>
                        <Bar options={baseOptions} data={{
                            labels: decisionLabels,
                            datasets: [{ label: 'Count', data: decisionValues, backgroundColor: barColors, borderColor: borderColors, borderWidth: 1, borderRadius: 6 }]
                        }} />
                    </div>
                </div>

                <div className="glass-panel" style={{ padding: '1.5rem' }}>
                    <h3 style={{ marginBottom: '1rem', fontSize: '0.875rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        Conversion Split
                    </h3>
                    <div style={{ height: '260px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                        <Doughnut
                            data={{
                                labels: decisionLabels,
                                datasets: [{ data: decisionValues, backgroundColor: barColors, borderColor: borderColors, borderWidth: 2, hoverOffset: 8 }]
                            }}
                            options={{
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: {
                                    legend: { position: 'bottom', labels: { color: '#94a3b8', padding: 16, font: { size: 12 } } },
                                    tooltip: CHART_TOOLTIP
                                },
                                cutout: '65%',
                            }}
                        />
                    </div>
                </div>
            </div>

            {/* Row 2: Confidence Histogram + Feature Importance */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                {confidence_histogram && confidence_histogram.length > 0 && (
                    <div className="glass-panel" style={{ padding: '1.5rem' }}>
                        <h3 style={{ marginBottom: '1rem', fontSize: '0.875rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            Confidence Score Distribution
                        </h3>
                        <div style={{ height: '220px' }}>
                            <Bar
                                options={{ ...baseOptions, plugins: { ...baseOptions.plugins, tooltip: CHART_TOOLTIP } }}
                                data={{
                                    labels: confidence_histogram.map(d => d.range),
                                    datasets: [{
                                        label: 'Leads',
                                        data: confidence_histogram.map(d => d.count),
                                        backgroundColor: confidence_histogram.map((_, i) => {
                                            const hue = Math.round(200 - i * 30);
                                            return `hsla(${hue}, 70%, 60%, 0.7)`;
                                        }),
                                        borderWidth: 0,
                                        borderRadius: 4,
                                    }]
                                }}
                            />
                        </div>
                    </div>
                )}

                {feature_importance && feature_importance.length > 0 && (
                    <div className="glass-panel" style={{ padding: '1.5rem' }}>
                        <h3 style={{ marginBottom: '1rem', fontSize: '0.875rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            Feature Importance (Top 5)
                        </h3>
                        <div style={{ height: '220px' }}>
                            <Bar
                                options={{
                                    ...baseOptions,
                                    indexAxis: 'y',
                                    scales: {
                                        x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                                        y: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 11 } } },
                                    }
                                }}
                                data={{
                                    labels: feature_importance.slice(0, 5).map(f => f.feature),
                                    datasets: [{
                                        label: 'Importance',
                                        data: feature_importance.slice(0, 5).map(f => f.importance),
                                        backgroundColor: 'rgba(99,102,241,0.7)',
                                        borderColor: '#6366f1',
                                        borderWidth: 1,
                                        borderRadius: 4,
                                    }]
                                }}
                            />
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Charts;
