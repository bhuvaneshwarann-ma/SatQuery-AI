import React, { useState, useRef } from 'react';

interface DropZoneProps {
  label: string;
  sublabel?: string;
  badge?: string;
  file: File | null;
  previewUrl: string | null;
  onFileSelect: (file: File) => void;
  onFileRemove: () => void;
  accept?: string;
  maxSizeBytes?: number;
  disabled?: boolean;
}

export const DropZone: React.FC<DropZoneProps> = ({
  label,
  sublabel = 'Click or drag satellite raster file',
  badge,
  file,
  previewUrl,
  onFileSelect,
  onFileRemove,
  accept = 'image/jpeg,image/png,image/webp,image/tiff',
  maxSizeBytes = 25 * 1024 * 1024,
  disabled = false,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateAndHandle = (candidate: File) => {
    setValidationError(null);

    const validExtensions = ['.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff'];
    const nameLower = candidate.name.toLowerCase();
    const isExtensionValid = validExtensions.some((ext) => nameLower.endsWith(ext));
    const isMimeValid = candidate.type.startsWith('image/') || candidate.type === '';

    if (!isExtensionValid && !isMimeValid) {
      setValidationError('Unsupported format. Please upload GeoTIFF, JPEG, PNG, or WebP imagery.');
      return;
    }

    if (candidate.size > maxSizeBytes) {
      setValidationError(`File exceeds size limit (${(maxSizeBytes / (1024 * 1024)).toFixed(0)}MB).`);
      return;
    }

    onFileSelect(candidate);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (disabled) return;
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (disabled) return;
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndHandle(e.dataTransfer.files[0]);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndHandle(e.target.files[0]);
    }
  };

  return (
    <div className={`dropzone-technical ${isDragging ? 'dropzone-active' : ''}`}>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleInputChange}
        style={{ display: 'none' }}
        disabled={disabled}
      />

      {previewUrl ? (
        <div className="dropzone-thumb-row" onClick={() => !disabled && inputRef.current?.click()}>
          <img src={previewUrl} alt={file?.name || 'Satellite Scene'} className="dropzone-thumb-img" />
          <div className="dropzone-meta">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span className="dropzone-title">{label}</span>
              <button
                type="button"
                style={{ background: 'transparent', border: 'none', color: 'var(--color-error)', fontSize: '0.7rem', cursor: 'pointer' }}
                onClick={(e) => {
                  e.stopPropagation();
                  onFileRemove();
                }}
              >
                ✕ Clear
              </button>
            </div>
            <span className="dropzone-status-text">✓ Verified Raster Source</span>
            {file && (
              <span style={{ fontSize: '0.68rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                {file.name} ({(file.size / 1024).toFixed(0)} KB)
              </span>
            )}
          </div>
        </div>
      ) : (
        <div
          style={{ display: 'flex', flexDirection: 'column', gap: '4px', textAlign: 'center' }}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => !disabled && inputRef.current?.click()}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span className="dropzone-title">{label}</span>
            {badge && <span style={{ fontSize: '0.62rem', fontFamily: 'var(--font-mono)', color: 'var(--accent-teal)' }}>{badge}</span>}
          </div>
          <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>{sublabel}</span>
        </div>
      )}

      {validationError && (
        <div style={{ marginTop: '6px', fontSize: '0.72rem', color: 'var(--color-error)' }}>
          ⚠ {validationError}
        </div>
      )}
    </div>
  );
};
