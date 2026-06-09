import React from 'react';
import { motion } from 'framer-motion';
import { useAppState } from '../context/AppContext';

const LogEntry = ({ log }) => {
  const typeColors = {
    error: 'text-[#ef4444]',
    user: 'text-[#60a5fa]',
    assistant: 'text-[#4ade80]',
    intent: 'text-[#f59e0b]',
    navigation: 'text-[#a78bfa]',
    detection: 'text-[#2dd4bf]',
    system: 'text-[#6c63ff]',
  };

  const time = new Date(log.timestamp).toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false 
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 5 }}
      animate={{ opacity: 1, y: 0 }}
      className="text-xs p-2 rounded-lg bg-[#0f0f1a] font-mono"
    >
      <span className="text-[#4a4a6a]">{time}</span>
      <span className={`${typeColors[log.type] || 'text-[#e8e8f0]'} ml-2`}>
        [{log.type}]
      </span>
      <span className="text-[#c8c8d0] ml-2">{log.message}</span>
    </motion.div>
  );
};

export default function StatusTab() {
  const { state } = useAppState();
  const { ui, permissions } = state;

  const PermDot = ({ status }) => {
    const colors = {
      granted: 'bg-[#4ade80]',
      denied: 'bg-[#ef4444]',
      pending: 'bg-[#6b7280]',
    };
    return <span className={`w-2 h-2 rounded-full ${colors[status] || colors.pending}`} />;
  };

  return (
    <div className="min-h-screen bg-[#0f0f1a] p-4 pb-20">
      <div className="max-w-md mx-auto space-y-4">
        
        <div className="bg-[#1a1a2e] rounded-xl p-4">
          <h2 className="text-xs font-bold text-[#6c63ff] uppercase tracking-wider mb-4">Permissions</h2>
          <div className="flex justify-around">
            <div className="text-center">
              <span className="text-xl">🎤</span>
              <div className="flex items-center justify-center gap-1 mt-2">
                <PermDot status={permissions.microphone} />
                <span className="text-[10px] text-[#6b7280]">Mic</span>
              </div>
            </div>
            <div className="text-center">
              <span className="text-xl">📷</span>
              <div className="flex items-center justify-center gap-1 mt-2">
                <PermDot status={permissions.camera} />
                <span className="text-[10px] text-[#6b7280]">Camera</span>
              </div>
            </div>
            <div className="text-center">
              <span className="text-xl">🔊</span>
              <div className="flex items-center justify-center gap-1 mt-2">
                <PermDot status={permissions.speaker} />
                <span className="text-[10px] text-[#6b7280]">Speaker</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-[#1a1a2e] rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-xs font-bold text-[#6c63ff] uppercase tracking-wider">Activity Log</h2>
            <span className="text-[10px] text-[#4a4a6a]">{ui.logs.length} entries</span>
          </div>
          
          <div className="space-y-1 max-h-80 overflow-y-auto">
            {ui.logs.length === 0 ? (
              <p className="text-[#4a4a6a] text-xs text-center py-8">No activity yet</p>
            ) : (
              ui.logs.slice(0, 50).map(log => <LogEntry key={log.id} log={log} />)
            )}
          </div>
        </div>

        <div className="bg-[#1a1a2e] rounded-xl p-4">
          <h2 className="text-xs font-bold text-[#6c63ff] uppercase tracking-wider mb-3">Servers</h2>
          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between bg-[#0f0f1a] rounded-lg p-2">
              <span className="text-[#6b7280]">Navigation</span>
              <span className="text-[#4ade80]">localhost:5050</span>
            </div>
            <div className="flex justify-between bg-[#0f0f1a] rounded-lg p-2">
              <span className="text-[#6b7280]">Detection</span>
              <span className="text-[#4ade80]">localhost:5000</span>
            </div>
          </div>
        </div>

        <p className="text-center text-[10px] text-[#3a3a5a]">
          NavAssist v1.0 — Voice Navigation for Visually Impaired
        </p>
      </div>
    </div>
  );
}
