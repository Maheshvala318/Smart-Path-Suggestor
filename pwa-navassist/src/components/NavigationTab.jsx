import React, { useState, useRef, useEffect } from 'react';

const getServerUrl = () => {
  const hostname = window.location.hostname;
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:5050';
  }
  return `http://${hostname}:5050`;
};

const NAVIGATION_SERVER = getServerUrl();

export default function NavigationTab({ initialParams }) {
  const iframeRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentUrl, setCurrentUrl] = useState(NAVIGATION_SERVER);

  useEffect(() => {
    if (initialParams && initialParams.source && initialParams.destination) {
      const url = `${NAVIGATION_SERVER}?source=${encodeURIComponent(initialParams.source)}&destination=${encodeURIComponent(initialParams.destination)}`;
      setCurrentUrl(url);
      setIsLoading(true);
    }
  }, [initialParams]);

  const handleIframeLoad = () => {
    setIsLoading(false);
  };

  const handleIframeError = () => {
    setError('Cannot connect to server. Please start it.');
  };

  return (
    <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: '#0f0f1a' }}>
      {isLoading && !error && (
        <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#0f0f1a', zIndex: 10 }}>
          <div style={{ textAlign: 'center' }}>
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#6c63ff" strokeWidth="2" style={{ animation: 'spin 1s linear infinite', margin: '0 auto 16px', display: 'block' }}>
              <line x1="12" y1="2" x2="12" y2="6"/>
              <line x1="12" y1="18" x2="12" y2="22"/>
              <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/>
              <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
              <line x1="2" y1="12" x2="6" y2="12"/>
              <line x1="18" y1="12" x2="22" y2="12"/>
              <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/>
              <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
            </svg>
            <p style={{ color: '#6b7280', fontSize: 14 }}>Loading navigation...</p>
          </div>
        </div>
      )}

      {error && (
        <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#0f0f1a', zIndex: 20 }}>
          <div style={{ maxWidth: 320, width: '100%', textAlign: 'center', padding: 24 }}>
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="2" style={{ margin: '0 auto 16px', display: 'block' }}>
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            <h2 style={{ fontSize: 18, fontWeight: 'bold', color: 'white', marginBottom: 8 }}>Server Not Running</h2>
            <p style={{ color: '#ef4444', fontSize: 14, marginBottom: 16 }}>{error}</p>
            <button 
              onClick={() => {
                setError(null);
                setIsLoading(true);
                if (iframeRef.current) {
                  iframeRef.current.src = currentUrl;
                }
              }}
              style={{ marginTop: 16, padding: '8px 16px', backgroundColor: '#6c63ff', color: 'white', fontSize: 14, borderRadius: 8, border: 'none', cursor: 'pointer' }}
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {!error && (
        <iframe
          ref={iframeRef}
          src={currentUrl}
          onLoad={handleIframeLoad}
          onError={handleIframeError}
          style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none' }}
          title="Department Navigation"
          allow="microphone; camera; geolocation"
        />
      )}
    </div>
  );
}
