import React, { useState, useMemo } from 'react';
import { ChevronRight, ExternalLink, ChevronLeft, ChevronRight as ChevronRightIcon } from 'lucide-react';

const PAGE_SIZE = 20;

const Results = ({ data }) => {
    const [currentPage, setCurrentPage] = useState(1);

    const totalPages = Math.ceil(data.length / PAGE_SIZE);

    const currentData = useMemo(() => {
        const start = (currentPage - 1) * PAGE_SIZE;
        return data.slice(start, start + PAGE_SIZE);
    }, [data, currentPage]);

    if (!data || !data.length) return null;

    return (
        <div className="glass-panel animate-fade-in" style={{ marginTop: '2rem', overflow: 'hidden' }}>
            <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h3 style={{ fontSize: '1.25rem' }}>Detailed Predictions</h3>
                    <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Showing {Math.min(data.length, (currentPage - 1) * PAGE_SIZE + 1)}-{Math.min(data.length, currentPage * PAGE_SIZE)} of {data.length} leads</p>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                        onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                        disabled={currentPage === 1}
                        style={{ padding: '8px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'transparent', color: 'white', cursor: currentPage === 1 ? 'not-allowed' : 'pointer', opacity: currentPage === 1 ? 0.5 : 1 }}
                    >
                        <ChevronLeft size={18} />
                    </button>
                    <button
                        onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                        disabled={currentPage === totalPages}
                        style={{ padding: '8px', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'transparent', color: 'white', cursor: currentPage === totalPages ? 'not-allowed' : 'pointer', opacity: currentPage === totalPages ? 0.5 : 1 }}
                    >
                        <ChevronRightIcon size={18} />
                    </button>
                </div>
            </div>

            <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                    <thead>
                        <tr style={{ background: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--glass-border)' }}>
                            <th style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)', fontWeight: '500' }}>Lead ID</th>
                            <th style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)', fontWeight: '500' }}>Source</th>
                            <th style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)', fontWeight: '500' }}>Occupation</th>
                            <th style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)', fontWeight: '500' }}>Probability</th>
                            <th style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)', fontWeight: '500' }}>Decision</th>
                            <th style={{ padding: '1rem 1.5rem', textAlign: 'right' }}></th>
                        </tr>
                    </thead>
                    <tbody>
                        {currentData.map((row, idx) => (
                            <tr key={idx} style={{ borderBottom: '1px solid var(--glass-border)', transition: 'background 0.2s' }} className="table-row-hover">
                                <td style={{ padding: '1rem 1.5rem' }}>#{1000 + (currentPage - 1) * PAGE_SIZE + idx}</td>
                                <td style={{ padding: '1rem 1.5rem' }}>{row.LeadSource || row.leadsource || 'Unknown'}</td>
                                <td style={{ padding: '1rem 1.5rem' }}>{row.WhatIsYourCurrentOccupation || row.whatisyourcurrentoccupation || 'Unknown'}</td>
                                <td style={{ padding: '1rem 1.5rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <div style={{ flex: 1, height: '6px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '3px', maxWidth: '60px' }}>
                                            <div style={{
                                                height: '100%',
                                                width: `${row.Conversion_Probability * 100}% `,
                                                background: row.Conversion_Probability > 0.7 ? 'var(--accent-success)' : row.Conversion_Probability > 0.4 ? 'var(--accent-warning)' : 'var(--accent-error)',
                                                borderRadius: '3px'
                                            }}></div>
                                        </div>
                                        {(row.Conversion_Probability * 100).toFixed(0)}%
                                    </div>
                                </td>
                                <td style={{ padding: '1rem 1.5rem' }}>
                                    <span style={{
                                        padding: '4px 10px',
                                        borderRadius: '20px',
                                        fontSize: '0.75rem',
                                        background: row.Conversion_Probability > 0.7 ? 'rgba(16, 185, 129, 0.1)' : row.Conversion_Probability > 0.4 ? 'rgba(245, 158, 11, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                                        color: row.Conversion_Probability > 0.7 ? 'var(--accent-success)' : row.Conversion_Probability > 0.4 ? 'var(--accent-warning)' : 'var(--accent-error)',
                                        border: `1px solid ${row.Conversion_Probability > 0.7 ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.1)'} `
                                    }}>
                                        {row.Decision}
                                    </span>
                                </td>
                                <td style={{ padding: '1rem 1.5rem', textAlign: 'right' }}>
                                    <ChevronRight size={18} style={{ color: 'var(--text-muted)', cursor: 'pointer' }} />
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Results;
