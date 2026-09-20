import React from 'react';

interface ErrorBannerProps {
  status?: string | null;
  errorType?: string | null;
  message: string;
  clarificationPrompt?: string | null;
  validationErrors?: string[];
  onDismiss?: () => void;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({
  status,
  errorType,
  message,
  clarificationPrompt,
  validationErrors,
  onDismiss,
}) => {
  const isClarification = status === 'NEEDS_CLARIFICATION' || errorType === 'NEEDS_CLARIFICATION';

  const getTitle = () => {
    if (isClarification) return 'Clarification Required';
    if (errorType === 'INVALID_PARAMETER') return 'Parameter Security Violation';
    if (errorType === 'IMAGE_NOT_FOUND' || errorType === 'INVALID_IMAGE') return 'Invalid Satellite Asset';
    if (status === 'INVALID_INPUT') return 'Input Requirements Not Met';
    return 'Analysis Request Failed';
  };

  return (
    <div className={`error-banner ${isClarification ? 'banner-clarification' : 'banner-error'}`}>
      <div className="error-banner-header">
        <div className="error-badge-group">
          <span className="error-icon-symbol">
            {isClarification ? 'ℹ' : '⚠'}
          </span>
          <h4 className="error-banner-title">{getTitle()}</h4>
          {errorType && <span className="error-type-tag">{errorType}</span>}
        </div>
        {onDismiss && (
          <button type="button" className="error-dismiss-btn" onClick={onDismiss} aria-label="Dismiss">
            ✕
          </button>
        )}
      </div>

      <p className="error-banner-message">{message}</p>

      {clarificationPrompt && (
        <div className="clarification-callout">
          <strong>Suggested Action:</strong> {clarificationPrompt}
        </div>
      )}

      {validationErrors && validationErrors.length > 0 && (
        <ul className="validation-error-list">
          {validationErrors.map((err, idx) => (
            <li key={idx}>{err}</li>
          ))}
        </ul>
      )}
    </div>
  );
};
