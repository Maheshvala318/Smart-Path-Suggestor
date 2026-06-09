import React, { useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppState } from '../context/AppContext';

const WaveformBars = ({ isAnimating, color = 'bg-white' }) => (
  <div className="flex items-center justify-center gap-0.5 h-6">
    {[...Array(5)].map((_, i) => (
      <motion.div
        key={i}
        className={`w-0.5 rounded-full ${color}`}
        animate={
          isAnimating
            ? {
                height: [6, 18, 6],
                transition: {
                  duration: 0.4,
                  repeat: Infinity,
                  delay: i * 0.05,
                },
              }
            : { height: 6 }
        }
      />
    ))}
  </div>
);

export default function VoiceOrb({ onActivate }) {
  const { state } = useAppState();
  const { voice } = state;

  const getStatus = () => {
    if (voice.isSpeaking) return 'speaking';
    if (voice.isProcessing) return 'processing';
    if (voice.isListening) return 'listening';
    return 'idle';
  };

  const currentStatus = getStatus();

  const statusConfig = {
    idle: {
      bg: 'bg-[#6c63ff]',
      ring: 'ring-[#6c63ff]/40',
      shadow: 'shadow-[0_0_20px_rgba(108,99,255,0.4)]',
      label: 'Tap to speak',
    },
    listening: {
      bg: 'bg-[#ef4444]',
      ring: 'ring-[#ef4444]/40',
      shadow: 'shadow-[0_0_25px_rgba(239,68,68,0.5)]',
      label: 'Listening...',
    },
    processing: {
      bg: 'bg-[#f59e0b]',
      ring: 'ring-[#f59e0b]/40',
      shadow: 'shadow-[0_0_25px_rgba(245,158,11,0.5)]',
      label: 'Thinking...',
    },
    speaking: {
      bg: 'bg-[#4ade80]',
      ring: 'ring-[#4ade80]/40',
      shadow: 'shadow-[0_0_25px_rgba(74,222,128,0.5)]',
      label: 'Speaking...',
    },
  };

  const config = statusConfig[currentStatus];

  return (
    <div className="fixed bottom-20 left-1/2 -translate-x-1/2 z-50 flex flex-col items-center">
      <motion.button
        onClick={onActivate}
        whileTap={{ scale: 0.95 }}
        className={`relative w-16 h-16 rounded-full ${config.bg} ${config.shadow} flex items-center justify-center ring-4 ${config.ring}`}
        animate={{
          scale: currentStatus === 'listening' ? [1, 1.05, 1] : 1,
        }}
        transition={{
          duration: 1.5,
          repeat: currentStatus === 'listening' ? Infinity : 0,
        }}
      >
        <AnimatePresence mode="wait">
          {currentStatus === 'idle' && (
            <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <WaveformBars isAnimating={true} color="bg-white" />
            </motion.div>
          )}

          {currentStatus === 'listening' && (
            <motion.div key="listening" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <div className="w-6 h-6 rounded-full bg-white/30 flex items-center justify-center">
                <div className="w-3 h-3 rounded-full bg-white animate-pulse" />
              </div>
            </motion.div>
          )}

          {currentStatus === 'processing' && (
            <motion.div
              key="processing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"
            />
          )}

          {currentStatus === 'speaking' && (
            <motion.div key="speaking" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <WaveformBars isAnimating={true} color="bg-white" />
            </motion.div>
          )}
        </AnimatePresence>

        {currentStatus === 'listening' && (
          <motion.div
            className="absolute inset-0 rounded-full ring-2 ring-[#ef4444]/30"
            animate={{ scale: [1, 1.3], opacity: [0.6, 0] }}
            transition={{ duration: 1, repeat: Infinity }}
          />
        )}
      </motion.button>

      <span className="text-[10px] text-[#6b7280] mt-2 font-medium">{config.label}</span>
    </div>
  );
}
