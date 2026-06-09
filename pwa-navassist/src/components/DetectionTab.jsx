import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const getServerUrl = () => {
  if (import.meta.env.VITE_DETECTION_SERVER) {
    return import.meta.env.VITE_DETECTION_SERVER;
  }
  const hostname = window.location.hostname;
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:5000';
  }
  return `http://${hostname}:5000`;
};

const DETECTION_SERVER = getServerUrl();

export default function DetectionTab({ action, timestamp }) {
  const iframeRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showError, setShowError] = useState(false);
  const lastTimestampRef = useRef(null);
  const [iframeSrc, setIframeSrc] = useState(DETECTION_SERVER);
  const hasLoadedRef = useRef(false);

  useEffect(() => {
    if (!action || !timestamp || timestamp === lastTimestampRef.current) return;
    
    lastTimestampRef.current = timestamp;
    
    if (action === 'start') {
      setIframeSrc(`${DETECTION_SERVER}/?autostart=true&t=${timestamp}`);
    } else if (action === 'stop-detection') {
      console.log('DetectionTab: Sending stopDetection via postMessage');
      if (iframeRef.current && iframeRef.current.contentWindow) {
        iframeRef.current.contentWindow.postMessage({ command: 'stopDetection' }, '*');
      }
    }
  }, [action, timestamp]);

  useEffect(() => {
    if (!iframeRef.current) return;
    iframeRef.current.src = iframeSrc;
  }, [iframeSrc]);

  const handleIframeLoad = () => {
    setIsLoading(false);
    
    const urlParams = new URLSearchParams(iframeSrc.split('?')[1] || '');
    const shouldAutostart = urlParams.get('autostart') === 'true';
    const shouldAutostop = urlParams.get('autostop') === 'true';
    
    if (shouldAutostart || shouldAutostop) {
      setTimeout(() => {
        if (iframeRef.current && iframeRef.current.contentWindow) {
          const command = shouldAutostart ? 'startDetection' : 'stopDetection';
          console.log('Sending postMessage to iframe:', command);
          iframeRef.current.contentWindow.postMessage({ command }, '*');
        }
      }, 1000);
    }
  };

  const handleIframeError = () => {
    setShowError(true);
    setIsLoading(false);
  };

  return (
    <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: '#0a0a0a' }}>
      <AnimatePresence>
        {isLoading && !showError && (
          <motion.div
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-10 flex items-center justify-center bg-[#0a0a0a]"
          >
            <div className="text-center">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#4ade80" strokeWidth="2" className="animate-spin mx-auto mb-4">
                <line x1="12" y1="2" x2="12" y2="6"/>
                <line x1="12" y1="18" x2="12" y2="22"/>
                <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/>
                <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
                <line x1="2" y1="12" x2="6" y2="12"/>
                <line x1="18" y1="12" x2="22" y2="12"/>
                <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/>
                <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
              </svg>
              <p className="text-[#6b7280]">Loading detection...</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <iframe
        ref={iframeRef}
        src={iframeSrc}
        onLoad={handleIframeLoad}
        onError={handleIframeError}
        style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none' }}
        title="Object Detection"
        allow="microphone; camera"
      />

      <AnimatePresence>
        {showError && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute inset-0 z-20 flex items-center justify-center bg-[#0a0a0a]"
          >
            <div className="max-w-sm w-full text-center p-6">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" className="mx-auto mb-4">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <h2 className="text-lg font-bold text-white mb-2">Detection Server Offline</h2>
              <p className="text-[#6b7280] text-sm mb-4">
                Start the server to use obstacle detection
              </p>
              <div className="bg-[#111827] rounded-lg p-3 font-mono text-xs text-left">
                <p className="text-[#4ade80]">cd object_detection_navigation</p>
                <p className="text-[#f59e0b]">python server.py</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
