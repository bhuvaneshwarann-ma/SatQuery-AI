import React, { useState, useRef, useEffect } from 'react';
import { IconZoomIn, IconZoomOut, IconReset, IconFullscreen } from './Icons';

export interface BoundingBox {
  coords: [number, number, number, number];
  label?: string;
  score?: number;
}

interface ImageViewerProps {
  primarySrc: string;
  secondarySrc?: string | null;
  overlaySrc?: string | null;
  boundingBoxes?: BoundingBox[] | null;
  title?: string;
  mode?: 'single' | 'side-by-side';
  showControls?: boolean;
}

export const ImageViewer: React.FC<ImageViewerProps> = ({
  primarySrc,
  secondarySrc,
  overlaySrc,
  boundingBoxes,
  title = '512 × 512 GSD',
  mode = 'single',
  showControls = true,
}) => {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [startPan, setStartPan] = useState({ x: 0, y: 0 });
  const [overlayOpacity, setOverlayOpacity] = useState(0.85);
  const [showBoxes, setShowBoxes] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [viewMode, setViewMode] = useState<'single' | 'side-by-side'>(mode);

  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setViewMode(mode);
  }, [mode]);

  const handleZoomIn = () => setZoom((z) => Math.min(z * 1.25, 8));
  const handleZoomOut = () => setZoom((z) => Math.max(z / 1.25, 0.5));
  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return;
    setIsPanning(true);
    setStartPan({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isPanning) return;
    setPan({ x: e.clientX - startPan.x, y: e.clientY - startPan.y });
  };

  const handleMouseUp = () => setIsPanning(false);

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.15 : 0.88;
    setZoom((z) => Math.min(Math.max(z * factor, 0.5), 8));
  };

  const toggleFullscreen = () => {
    if (!containerRef.current) return;
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen?.();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen?.();
      setIsFullscreen(false);
    }
  };

  useEffect(() => {
    const handleFsChange = () => setIsFullscreen(!!document.fullscreenElement);
    document.addEventListener('fullscreenchange', handleFsChange);
    return () => document.removeEventListener('fullscreenchange', handleFsChange);
  }, []);

  return (
    <div ref={containerRef} style={{ display: 'flex', flexDirection: 'column', height: '100%', width: '100%', background: '#000', position: 'relative' }}>
      {/* Compact Geospatial Toolbar */}
      {showControls && (
        <div className="viewer-toolbar-compact">
          <div className="viewer-toolbar-left">
            <span>CANVAS</span>
            <span>·</span>
            <span>{title}</span>
            <span>·</span>
            <span style={{ color: 'var(--accent-teal)' }}>{(zoom * 100).toFixed(0)}%</span>
          </div>

          <div className="viewer-toolbar-right">
            {overlaySrc && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginRight: '6px', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                <span>OVERLAY</span>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={overlayOpacity}
                  onChange={(e) => setOverlayOpacity(parseFloat(e.target.value))}
                  style={{ width: '60px', height: '3px', cursor: 'pointer' }}
                />
              </div>
            )}

            {boundingBoxes && boundingBoxes.length > 0 && (
              <button
                type="button"
                className={`viewer-tool-btn ${showBoxes ? 'active' : ''}`}
                onClick={() => setShowBoxes(!showBoxes)}
              >
                TARGETS ({boundingBoxes.length})
              </button>
            )}

            {secondarySrc && (
              <button
                type="button"
                className={`viewer-tool-btn ${viewMode === 'side-by-side' ? 'active' : ''}`}
                onClick={() => setViewMode(viewMode === 'side-by-side' ? 'single' : 'side-by-side')}
              >
                {viewMode === 'side-by-side' ? 'SPLIT VIEW' : 'STACKED'}
              </button>
            )}

            <button type="button" className="viewer-tool-btn" onClick={handleZoomOut} title="Zoom Out">
              <IconZoomOut size={13} />
            </button>
            <button type="button" className="viewer-tool-btn" onClick={handleZoomIn} title="Zoom In">
              <IconZoomIn size={13} />
            </button>
            <button type="button" className="viewer-tool-btn" onClick={handleReset} title="Reset View">
              <IconReset size={13} />
            </button>
            <button type="button" className={`viewer-tool-btn ${isFullscreen ? 'active' : ''}`} onClick={toggleFullscreen} title="Toggle Fullscreen">
              <IconFullscreen size={13} />
            </button>
          </div>
        </div>
      )}

      {/* Geospatial Canvas Viewport */}
      <div
        className="viewer-canvas-viewport"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        style={{ cursor: isPanning ? 'grabbing' : 'grab' }}
      >
        <div
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transformOrigin: 'center center',
            transition: isPanning ? 'none' : 'transform 0.05s linear',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {viewMode === 'side-by-side' && secondarySrc ? (
            <div style={{ display: 'flex', gap: '8px' }}>
              <div style={{ position: 'relative', width: '380px', height: '380px', background: '#080b0d', border: '1px solid var(--border-default)' }}>
                <span style={{ position: 'absolute', top: 6, left: 6, background: 'rgba(8,11,13,0.8)', padding: '2px 6px', fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>T1 OPTICAL</span>
                <img src={primarySrc} alt="Primary" style={{ width: '100%', height: '100%', objectFit: 'contain' }} draggable={false} />
              </div>
              <div style={{ position: 'relative', width: '380px', height: '380px', background: '#080b0d', border: '1px solid var(--border-default)' }}>
                <span style={{ position: 'absolute', top: 6, left: 6, background: 'rgba(8,11,13,0.8)', padding: '2px 6px', fontSize: '0.65rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>T2 / COMPARATIVE</span>
                <img src={secondarySrc} alt="Secondary" style={{ width: '100%', height: '100%', objectFit: 'contain' }} draggable={false} />
              </div>
            </div>
          ) : (
            <div style={{ position: 'relative', width: '512px', height: '512px' }}>
              <img src={primarySrc} alt="Satellite Scene" style={{ width: '512px', height: '512px', display: 'block', userSelect: 'none' }} draggable={false} />

              {overlaySrc && (
                <img
                  src={overlaySrc}
                  alt="Overlay"
                  style={{ position: 'absolute', top: 0, left: 0, width: '512px', height: '512px', opacity: overlayOpacity, pointerEvents: 'none', userSelect: 'none' }}
                  draggable={false}
                />
              )}

              {showBoxes && boundingBoxes && boundingBoxes.length > 0 && (
                <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
                  {boundingBoxes.map((box, idx) => {
                    const [y1, x1, y2, x2] = box.coords;
                    const topPct = (y1 / 512) * 100;
                    const leftPct = (x1 / 512) * 100;
                    const widthPct = ((x2 - x1) / 512) * 100;
                    const heightPct = ((y2 - y1) / 512) * 100;

                    return (
                      <div
                        key={idx}
                        style={{
                          position: 'absolute',
                          top: `${topPct}%`,
                          left: `${leftPct}%`,
                          width: `${widthPct}%`,
                          height: `${heightPct}%`,
                          border: '1.5px solid #00a3bf',
                          background: 'rgba(0, 163, 191, 0.1)',
                        }}
                      >
                        <span style={{
                          position: 'absolute',
                          top: -16,
                          left: -1,
                          background: '#00a3bf',
                          color: '#080b0d',
                          fontSize: '0.62rem',
                          fontFamily: 'var(--font-mono)',
                          fontWeight: 700,
                          padding: '1px 4px',
                          borderRadius: '2px',
                          whiteSpace: 'nowrap',
                        }}>
                          {box.label || 'TARGET'}
                          {box.score !== undefined && ` ${(box.score * 100).toFixed(0)}%`}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
