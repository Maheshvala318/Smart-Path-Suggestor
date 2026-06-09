import React, { useState, useEffect } from 'react';

const MicIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
    <line x1="12" y1="19" x2="12" y2="23"/>
    <line x1="8" y1="23" x2="16" y2="23"/>
  </svg>
);

const CameraIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
    <circle cx="12" cy="13" r="4"/>
  </svg>
);

const SpeakerIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
    <path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>
    <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
  </svg>
);

const CompassIcon = () => (
  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#4ade80" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>
  </svg>
);

const CheckIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);

const XIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18"/>
    <line x1="6" y1="6" x2="18" y2="18"/>
  </svg>
);

export default function PermissionGate({ onComplete }) {
  const [status, setStatus] = useState({
    microphone: 'pending',
    camera: 'pending',
    speaker: 'pending',
  });

  useEffect(() => {
    let mounted = true;

    const requestAll = async () => {
      try {
        if (!mounted) return;
        setStatus(s => ({ ...s, microphone: 'requesting' }));
        const mic = await navigator.mediaDevices.getUserMedia({ audio: true });
        mic.getTracks().forEach(t => t.stop());
        if (!mounted) return;
        setStatus(s => ({ ...s, microphone: 'granted' }));
      } catch {
        if (!mounted) return;
        setStatus(s => ({ ...s, microphone: 'denied' }));
      }

      await new Promise(r => setTimeout(r, 200));

      try {
        if (!mounted) return;
        setStatus(s => ({ ...s, camera: 'requesting' }));
        const cam = await navigator.mediaDevices.getUserMedia({ video: true });
        cam.getTracks().forEach(t => t.stop());
        if (!mounted) return;
        setStatus(s => ({ ...s, camera: 'granted' }));
      } catch {
        if (!mounted) return;
        setStatus(s => ({ ...s, camera: 'denied' }));
      }

      await new Promise(r => setTimeout(r, 200));

      if (!mounted) return;
      setStatus(s => ({ ...s, speaker: 'requesting' }));
      if ('speechSynthesis' in window) {
        setStatus(s => ({ ...s, speaker: 'granted' }));
      } else {
        setStatus(s => ({ ...s, speaker: 'denied' }));
      }

      await new Promise(r => setTimeout(r, 300));
      
      if (mounted) {
        onComplete();
      }
    };

    requestAll();

    return () => { mounted = false; };
  }, [onComplete]);

  const getStyle = (s) => {
    if (s === 'granted') return 'border-[#4ade80]';
    if (s === 'denied') return 'border-[#ef4444]';
    if (s === 'requesting') return 'border-[#f59e0b] animate-pulse';
    return 'border-[#3a3a5a]';
  };

  const getStatusIcon = (s) => {
    if (s === 'granted') return <span className="w-4 h-4 text-[#4ade80]"><CheckIcon /></span>;
    if (s === 'denied') return <span className="w-4 h-4 text-[#ef4444]"><XIcon /></span>;
    if (s === 'requesting') return <span className="w-4 h-4 h-4 border-2 border-[#f59e0b] border-t-transparent rounded-full animate-spin inline-block" />;
    return <span className="w-3 h-3 rounded-full bg-[#6b7280]" />;
  };

  const items = [
    { key: 'microphone', icon: MicIcon, title: 'Microphone' },
    { key: 'camera', icon: CameraIcon, title: 'Camera' },
    { key: 'speaker', icon: SpeakerIcon, title: 'Speaker' },
  ];

  return (
    <div className="min-h-screen bg-[#0f0f1a] flex items-center justify-center p-6">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <CompassIcon />
          <h1 className="text-2xl font-bold text-white mt-4">NavAssist</h1>
          <p className="text-[#6b7280] text-sm">Setting up permissions...</p>
        </div>

        <div className="space-y-3">
          {items.map(item => (
            <div key={item.key} className={`flex items-center gap-4 p-4 bg-[#1a1a2e] rounded-xl border ${getStyle(status[item.key])}`}>
              <span className="text-[#9ca3af]"><item.icon /></span>
              <span className="flex-1 text-white font-medium">{item.title}</span>
              {getStatusIcon(status[item.key])}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
