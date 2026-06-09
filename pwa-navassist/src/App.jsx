import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import PermissionGate from './components/PermissionGate';
import NavigationTab from './components/NavigationTab';
import DetectionTab from './components/DetectionTab';
import StatusTab from './components/StatusTab';
import VoiceAssistant from './components/VoiceAssistant';

const NavigateIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>
  </svg>
);

const DetectIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
    <circle cx="12" cy="12" r="3"/>
  </svg>
);

const LogsIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
    <line x1="16" y1="13" x2="8" y2="13"/>
    <line x1="16" y1="17" x2="8" y2="17"/>
    <polyline points="10 9 9 9 8 9"/>
  </svg>
);

const TABS = [
  { id: 'navigation', label: 'Navigate', icon: NavigateIcon },
  { id: 'detection', label: 'Detect', icon: DetectIcon },
  { id: 'status', label: 'Logs', icon: LogsIcon },
];

export default function App() {
  const [ready, setReady] = useState(false);
  const [activeTab, setActiveTab] = useState('navigation');
  const [navParams, setNavParams] = useState(null);
  const [detectionAction, setDetectionAction] = useState(null);

  const handleNavigate = useCallback((params) => {
    if (params.tab) {
      setActiveTab(params.tab);
      if (params.action) {
        setDetectionAction({ type: params.action, timestamp: Date.now() });
      }
      return;
    }
    
    if (params.source && params.destination) {
      setNavParams({ source: params.source, destination: params.destination });
      setActiveTab('navigation');
    }
  }, []);

  if (!ready) {
    return <PermissionGate onComplete={() => setReady(true)} />;
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'navigation': 
        return <NavigationTab initialParams={navParams} activeTab={activeTab} />;
      case 'detection': 
        return <DetectionTab action={detectionAction?.type} timestamp={detectionAction?.timestamp} />;
      case 'status': 
        return <StatusTab />;
      default: 
        return <NavigationTab initialParams={navParams} activeTab={activeTab} />;
    }
  };

  return (
    <div className="h-screen w-screen bg-[#0f0f1a] flex flex-col overflow-hidden">
      <header className="flex-shrink-0 bg-[#1a1a2e] border-b border-[#2a2a4a] py-3 px-4">
        <div className="flex items-center justify-between max-w-md mx-auto">
          <div className="flex items-center gap-2">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#4ade80" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>
            </svg>
            <h1 className="font-bold text-white">NavAssist</h1>
          </div>
          <span className="text-[10px] px-2 py-1 bg-[#4ade80]/20 text-[#4ade80] rounded-full flex items-center gap-1">
            <svg width="8" height="8" viewBox="0 0 24 24" fill="#4ade80">
              <circle cx="12" cy="12" r="10"/>
            </svg>
            Voice Ready
          </span>
        </div>
      </header>

      <main className="flex-1 relative overflow-hidden">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="absolute inset-0"
            style={{ bottom: '56px' }}
          >
            {renderContent()}
          </motion.div>
        </AnimatePresence>
      </main>

      <VoiceAssistant onNavigate={handleNavigate} />

      <div className="fixed bottom-0 left-0 right-0 h-14 bg-[#0f0f1a] border-t border-[#2a2a4a]">
        <div className="flex justify-around max-w-md mx-auto py-2">
          {TABS.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex flex-col items-center py-2 px-6 rounded-xl transition-colors ${
                activeTab === tab.id ? 'text-[#6c63ff]' : 'text-[#6b7280]'
              }`}
            >
              <tab.icon />
              <span className="text-[10px] mt-0.5">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
