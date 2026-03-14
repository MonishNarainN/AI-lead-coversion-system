import React, { useState, useCallback } from 'react';
import { Upload as UploadIcon, File, X, CheckCircle, Loader2 } from 'lucide-react';
import { uploadFile } from '../services/api';

const Upload = ({ onUploadSuccess }) => {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState(null);
    const [dragActive, setDragActive] = useState(false);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFile(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) return;
        setUploading(true);
        setError(null);
        try {
            const result = await uploadFile(file);
            onUploadSuccess(result.filename);
        } catch (err) {
            setError(err.response?.data?.error || "Failed to upload file");
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="glass-panel" style={{ padding: '2rem', maxWidth: '600px', margin: '2rem auto' }}>
            <h2 style={{ marginBottom: '1.5rem', textAlign: 'center' }}>Upload Lead Dataset</h2>

            <div
                className={`glass-panel ${dragActive ? 'drag-active' : ''}`}
                style={{
                    border: dragActive ? '2px dashed var(--primary)' : '2px dashed var(--glass-border)',
                    padding: '3rem',
                    textAlign: 'center',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    backgroundColor: dragActive ? 'rgba(99, 102, 241, 0.1)' : 'transparent'
                }}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => document.getElementById('file-upload').click()}
            >
                <input
                    id="file-upload"
                    type="file"
                    accept=".csv, .xlsx, .xls"
                    onChange={handleChange}
                    style={{ display: 'none' }}
                />

                {!file ? (
                    <>
                        <UploadIcon size={48} style={{ color: 'var(--primary)', marginBottom: '1rem' }} />
                        <p style={{ color: 'var(--text-muted)' }}>Drag and drop your CSV or Excel file here</p>
                        <p style={{ fontSize: '0.875rem', marginTop: '0.5rem' }}>Supporting up to 50MB</p>
                    </>
                ) : (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem' }}>
                        <File size={32} style={{ color: 'var(--primary)' }} />
                        <div style={{ textAlign: 'left' }}>
                            <p style={{ fontWeight: '600' }}>{file.name}</p>
                            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                        </div>
                        <X
                            size={20}
                            style={{ cursor: 'pointer', color: 'var(--accent-error)' }}
                            onClick={(e) => { e.stopPropagation(); setFile(null); }}
                        />
                    </div>
                )}
            </div>

            {error && (
                <p style={{ color: 'var(--accent-error)', marginTop: '1rem', textAlign: 'center' }}>{error}</p>
            )}

            <button
                className="btn-primary"
                style={{ width: '100%', marginTop: '1.5rem', justifyContent: 'center' }}
                disabled={!file || uploading}
                onClick={handleUpload}
            >
                {uploading ? (
                    <>
                        <Loader2 size={20} className="animate-spin" />
                        Uploading...
                    </>
                ) : (
                    "Start Prediction Engine"
                )}
            </button>
        </div>
    );
};

export default Upload;
