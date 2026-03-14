import React, { useState } from 'react';
import axios from 'axios';
import { Download, FileSpreadsheet, FileJson, Loader2, LayoutList, Sparkles, FileText } from 'lucide-react';

const ReportExport = ({ filename, summary }) => {
    const [downloading, setDownloading] = useState(null);

    const handleDownload = async (type) => {
        setDownloading(type);
        try {
            const formatMap = {
                'excel': { ext: 'xlsx', mime: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' },
                'predictions': { ext: 'csv', mime: 'text/csv' },
                'analysis': { ext: 'csv', mime: 'text/csv' },
                'insights': { ext: 'txt', mime: 'text/plain' },
                'pdf': { ext: 'pdf', mime: 'application/pdf' }
            };
            const config = formatMap[type] || { ext: 'csv', mime: 'text/csv' };

            const response = await axios.post('http://localhost:5000/reports/download', {
                filename,
                format: type
            }, {
                responseType: 'blob'
            });

            const url = window.URL.createObjectURL(new Blob([response.data], { type: config.mime }));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `lead_${type}_${filename.split('.')[0]}.${config.ext}`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error('Download failed', error);
            alert('Failed to generate report. Please try again.');
        } finally {
            setDownloading(null);
        }
    };

    return (
        <div className="glass-panel" style={{ padding: '1.25rem', marginBottom: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ background: 'rgba(99,102,241,0.1)', padding: '10px', borderRadius: '10px' }}>
                        <Download size={20} color="var(--primary)" />
                    </div>
                    <div>
                        <h3 style={{ fontSize: '0.95rem', fontWeight: '600' }}>Export Analysis Hub</h3>
                        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Generate and download specialized intelligence reports</p>
                    </div>
                </div>
                <button
                    className="btn-primary"
                    style={{ background: 'linear-gradient(135deg, #6366f1, #a855f7)', display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px', fontSize: '0.85rem' }}
                    onClick={() => handleDownload('excel')}
                    disabled={downloading !== null}
                >
                    {downloading === 'excel' ? <Loader2 className="animate-spin" size={16} /> : <FileSpreadsheet size={16} />}
                    Full Excel Dashboard
                </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem', borderTop: '1px solid var(--glass-border)', paddingTop: '1.25rem' }}>
                <button
                    className="btn-secondary"
                    style={{ justifyContent: 'center', gap: '8px', fontSize: '0.8rem' }}
                    onClick={() => handleDownload('pdf')}
                    disabled={downloading !== null}
                    title="Professional PDF Report"
                >
                    {downloading === 'pdf' ? <Loader2 className="animate-spin" size={16} /> : <FileText size={16} color="#ef4444" />}
                    PDF Analytics Report
                </button>
                <button
                    className="btn-secondary"
                    style={{ justifyContent: 'center', gap: '8px', fontSize: '0.8rem' }}
                    onClick={() => handleDownload('analysis')}
                    disabled={downloading !== null}
                >
                    {downloading === 'analysis' ? <Loader2 className="animate-spin" size={16} /> : <LayoutList size={16} />}
                    Statistical Analysis
                </button>
                <button
                    className="btn-secondary"
                    style={{ justifyContent: 'center', gap: '8px', fontSize: '0.8rem' }}
                    onClick={() => handleDownload('predictions')}
                    disabled={downloading !== null}
                >
                    {downloading === 'predictions' ? <Loader2 className="animate-spin" size={16} /> : <FileJson size={16} />}
                    Lead Predictions
                </button>
                <button
                    className="btn-secondary"
                    style={{ justifyContent: 'center', gap: '8px', fontSize: '0.8rem' }}
                    onClick={() => handleDownload('insights')}
                    disabled={downloading !== null}
                >
                    {downloading === 'insights' ? <Loader2 className="animate-spin" size={16} /> : <Sparkles size={16} />}
                    AI Insights (TXT)
                </button>
            </div>
        </div>
    );
};

export default ReportExport;
