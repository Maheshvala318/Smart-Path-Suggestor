import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const DEEPGRAM_API_KEY = import.meta.env.VITE_DEEPGRAM_API_KEY || '';
const GROQ_API_KEY = import.meta.env.VITE_GROQ_API_KEY || '';

const getServerUrl = () => {
  const hostname = window.location.hostname;
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:5050';
  }
  return `http://${hostname}:5050`;
};

const NAVIGATION_SERVER = getServerUrl();

const STATES = {
  IDLE: 'idle',
  LISTENING: 'listening',
  PROCESSING: 'processing',
  SPEAKING: 'speaking',
};

export default function VoiceAssistant({ onNavigate }) {
  const [state, setState] = useState(STATES.IDLE);
  const [transcript, setTranscript] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);
  const [hasWelcomed, setHasWelcomed] = useState(false);
  
  const wsRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const synthRef = useRef(window.speechSynthesis);
  const messagesRef = useRef([]);
  const [messages, setMessages] = useState([]);
  const isActiveRef = useRef(false);
  const reconnectTimeoutRef = useRef(null);

  const addMessage = useCallback((role, content) => {
    const msg = { id: Date.now(), role, content, time: new Date().toLocaleTimeString() };
    messagesRef.current = [...messagesRef.current, msg];
    setMessages(messagesRef.current);
  }, []);

  const speak = useCallback(async (text) => {
    setState(STATES.SPEAKING);
    console.log('Speaking:', text?.substring(0, 100) + '...');
    
    try {
      const response = await fetch(`${NAVIGATION_SERVER}/api/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, model: 'aura-asteria-en' }),
      });
      
      console.log('TTS response status:', response.status);
      
      if (response.ok) {
        const audioBlob = await response.blob();
        console.log('Audio blob size:', audioBlob.size);
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        await new Promise((resolve, reject) => {
          audio.onended = () => {
            URL.revokeObjectURL(audioUrl);
            resolve();
          };
          audio.onerror = (e) => {
            console.error('Audio playback error:', e);
            URL.revokeObjectURL(audioUrl);
            resolve();
          };
          audio.play();
        });
        console.log('Deepgram TTS playback complete');
      } else {
        console.log('Deepgram TTS failed with status:', response.status);
        await browserSpeak(text);
      }
    } catch (error) {
      console.log('TTS error, using browser fallback:', error);
      await browserSpeak(text);
    }
    
    if (isActiveRef.current) {
      setState(STATES.LISTENING);
    } else {
      setState(STATES.IDLE);
    }
  }, []);

  const browserSpeak = useCallback((text) => {
    return new Promise((resolve) => {
      synthRef.current.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.95;
      utterance.onend = () => resolve();
      utterance.onerror = () => resolve();
      synthRef.current.speak(utterance);
    });
  }, []);

  const parseIntentViaServer = useCallback(async (text) => {
    try {
      const response = await fetch(`${NAVIGATION_SERVER}/api/parse-intent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      
      if (response.ok) {
        const data = await response.json();
        return { source: data.source, destination: data.destination, method: data.method };
      }
    } catch (error) {
      console.log('Server intent parse failed, using local fallback');
    }
    return null;
  }, []);

  const parseLocations = useCallback(async (text) => {
    const serverResult = await parseIntentViaServer(text);
    if (serverResult && (serverResult.source || serverResult.destination)) {
      return { source: serverResult.source || null, destination: serverResult.destination || null };
    }

    if (!GROQ_API_KEY) {
      const lower = text.toLowerCase();
      const fromMatch = lower.match(/from\s+(.+?)\s+to/);
      const toMatch = lower.match(/to\s+(.+?)(?:\s*$|from)/);
      
      return {
        source: fromMatch ? fromMatch[1].trim() : null,
        destination: toMatch ? toMatch[1].trim() : null,
      };
    }

    try {
      const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${GROQ_API_KEY}`,
        },
        body: JSON.stringify({
          model: 'llama-3.3-70b-versatile',
          messages: [{
            role: 'user',
            content: `Extract source and destination from this navigation request. 
Return ONLY JSON with "source" and "destination" keys. If not found, use null.

User said: "${text}"

Examples:
"I want to go from Main Gate to Library" -> {"source": "Main Gate", "destination": "Library"}
"Navigate to Computer Science" -> {"source": null, "destination": "Computer Science"}`
          }],
          response_format: { type: 'json_object' },
          temperature: 0.1,
          max_tokens: 100,
        }),
      });

      const data = await response.json();
      const content = data.choices?.[0]?.message?.content || '{}';
      const parsed = JSON.parse(content);
      
      return { source: parsed.source || null, destination: parsed.destination || null };
    } catch (error) {
      console.error('Parse error:', error);
      return { source: null, destination: null };
    }
  }, [parseIntentViaServer]);

  const callNavigationAPI = useCallback(async (source, destination) => {
    try {
      const response = await fetch(`${NAVIGATION_SERVER}/api/find-path`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source, destination }),
      });
      
      if (response.ok) {
        const data = await response.json();
        return data;
      }
    } catch (error) {
      console.log('Navigation API call failed:', error);
    }
    return null;
  }, []);

  const handleTranscript = useCallback(async (text) => {
    if (!text.trim()) return;
    
    setTranscript('');
    setState(STATES.PROCESSING);
    addMessage('user', text);

    const lower = text.toLowerCase();
    
    // Detection commands - check FIRST before navigation
    if (lower.includes('start detection') || lower.includes('start detect') || 
        lower.includes('turn on detection') || lower.includes('enable detection') ||
        lower.includes('begin detection') || lower.includes('open detection') ||
        lower.includes('run detection') || lower.includes('activate detection') ||
        lower.includes('start obstacle') || lower.includes('begin obstacle') ||
        lower.includes('turn on obstacle') || lower.includes('enable obstacle')) {
      addMessage('assistant', 'Starting detection mode');
      await speak('Starting obstacle detection');
      if (onNavigate) {
        onNavigate({ tab: 'detection', action: 'start' });
      }
      return;
    }
    
    if (lower.includes('stop detection') || lower.includes('stop detect') || 
        lower.includes('turn off detection') || lower.includes('disable detection') ||
        lower.includes('end detection') || lower.includes('close detection') ||
        lower.includes('quit detection') || lower.includes('exit detection') ||
        lower.includes('deactivate detection') || lower.includes('stop obstacle') ||
        lower.includes('turn off obstacle') || lower.includes('disable obstacle') ||
        lower.includes('end obstacle') || lower.includes('close obstacle')) {
      addMessage('assistant', 'Stopping detection mode');
      await speak('Obstacle detection stopped');
      if (onNavigate) {
        onNavigate({ tab: 'detection', action: 'stop-detection' });
      }
      return;
    }
    
    if ((lower.includes('detect') || lower.includes('obstacle')) && 
        !lower.includes('stop') && !lower.includes('end') && !lower.includes('turn off')) {
      addMessage('assistant', 'Opening detection mode');
      await speak('Opening detection mode');
      if (onNavigate) {
        onNavigate({ tab: 'detection' });
      }
      return;
    }
    
    // Navigation commands
    if (lower.includes('navigate') || lower.includes('go to') || lower.includes('from') || lower.includes('destination') || lower.includes('to')) {
      const locations = await parseLocations(text);
      
      if (locations.source && locations.destination) {
        if (onNavigate) {
          onNavigate({ source: locations.source, destination: locations.destination });
        }
        
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const routeData = await callNavigationAPI(locations.source, locations.destination);
        
        if (routeData) {
          const totalDist = routeData.total_distance_m ? `${Math.round(routeData.total_distance_m)} meters` : '';
          const totalSteps = routeData.total_steps || 0;
          
          let speechText = '';
          
          if (routeData.voice_script) {
            speechText = `${routeData.voice_script}. Total distance is ${totalDist}, approximately ${totalSteps} steps.`;
          } else {
            speechText = `Route found from ${locations.source} to ${locations.destination}. Total distance is ${totalDist}, approximately ${totalSteps} steps.`;
          }
          
          addMessage('assistant', `Route: ${locations.source} → ${locations.destination} (${totalSteps} steps)`);
          await speak(speechText);
        } else {
          const msg = `Finding route from ${locations.source} to ${locations.destination}`;
          addMessage('assistant', msg);
          await speak(msg);
        }
        return;
      }
      
      if (locations.destination) {
        const msg = `Finding route to ${locations.destination}. Where should I start from?`;
        addMessage('assistant', msg);
        await speak(msg);
        return;
      }
      
      const msg = 'Please tell me both source and destination. Say "From Main Gate to Library"';
      addMessage('assistant', msg);
      await speak(msg);
      return;
    }
    
    if (lower.includes('stop listening') || lower.includes('stop voice')) {
      addMessage('assistant', 'Stopping voice assistant');
      await speak('Voice assistant stopped. Tap the button to restart.');
      isActiveRef.current = false;
      if (wsRef.current) { wsRef.current.close(); wsRef.current = null; }
      if (mediaRecorderRef.current) { mediaRecorderRef.current.stop(); mediaRecorderRef.current = null; }
      if (streamRef.current) { streamRef.current.getTracks().forEach(t => t.stop()); streamRef.current = null; }
      setState(STATES.IDLE);
      return;
    }

    if (lower.includes('stop')) {
      addMessage('assistant', 'Stopping navigation');
      await speak('Navigation stopped');
      return;
    }

    if (lower.includes('hello') || lower.includes('hi')) {
      const msg = 'Hello! Where would you like to go? Tell me your source and destination.';
      addMessage('assistant', msg);
      await speak(msg);
      return;
    }

    if (lower.includes('help')) {
      const msg = 'I can help you navigate. Say "From Main Gate to Library" or "Navigate to Computer Science Department"';
      addMessage('assistant', msg);
      await speak(msg);
      return;
    }

    if (lower.includes('status') || lower.includes('logs')) {
      if (onNavigate) {
        onNavigate({ tab: 'status' });
      }
      addMessage('assistant', 'Showing status logs');
      await speak('Showing logs tab');
      return;
    }

    const msg = 'I can help you navigate. Say "From Main Gate to Library"';
    addMessage('assistant', msg);
    await speak(msg);
  }, [addMessage, speak, parseLocations, onNavigate, callNavigationAPI]);

  const stopListening = useCallback(() => {
    isActiveRef.current = false;
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
    synthRef.current.cancel();
    setState(STATES.IDLE);
    setTranscript('');
  }, []);

  const startListening = useCallback(async () => {
    if (!DEEPGRAM_API_KEY) {
      alert('DEEPGRAM_API_KEY not configured in .env');
      return;
    }

    try {
      isActiveRef.current = true;
      setState(STATES.LISTENING);
      
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      const socket = new WebSocket(
        `wss://api.deepgram.com/v1/listen?model=nova-2&language=en-US&smart_format=true&interim_results=true&endpointing=1500`,
        ['token', DEEPGRAM_API_KEY]
      );
      
      wsRef.current = socket;
      
      socket.onopen = () => {
        const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
        mediaRecorderRef.current = mediaRecorder;
        
        mediaRecorder.ondataavailable = (e) => {
          if (socket.readyState === WebSocket.OPEN && e.data.size > 0 && isActiveRef.current) {
            socket.send(e.data);
          }
        };
        
        mediaRecorder.start(100);
      };
      
      socket.onmessage = (event) => {
        if (!isActiveRef.current) return;
        
        const data = JSON.parse(event.data);
        
        if (data.type === 'Results' && data.channel) {
          const alt = data.channel.alternatives?.[0];
          if (alt?.transcript) {
            setTranscript(alt.transcript);
            
            if (data.is_final) {
              handleTranscript(alt.transcript);
            }
          }
        }
      };
      
      socket.onerror = (e) => {
        console.error('WebSocket error:', e);
      };
      
      socket.onclose = () => {
        if (mediaRecorderRef.current?.state === 'recording') {
          mediaRecorderRef.current.stop();
        }
      };
      
    } catch (error) {
      console.error('Voice error:', error);
      setState(STATES.IDLE);
    }
  }, [handleTranscript]);

  const toggleActive = useCallback(() => {
    if (state === STATES.IDLE) {
      startListening();
    } else {
      stopListening();
    }
  }, [state, startListening, stopListening]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (!hasWelcomed) {
        setHasWelcomed(true);
        addMessage('assistant', 'Welcome! Tap the microphone to start voice navigation.');
      }
    }, 1000);
    
    return () => clearTimeout(timer);
  }, [hasWelcomed, addMessage]);

  useEffect(() => {
    return () => {
      isActiveRef.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      stopListening();
    };
  }, [stopListening]);

  const MicIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
      <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
      <line x1="12" y1="19" x2="12" y2="23"/>
      <line x1="8" y1="23" x2="16" y2="23"/>
    </svg>
  );

  const LoaderIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="animate-spin">
      <line x1="12" y1="2" x2="12" y2="6"/>
      <line x1="12" y1="18" x2="12" y2="22"/>
      <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/>
      <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
      <line x1="2" y1="12" x2="6" y2="12"/>
      <line x1="18" y1="12" x2="22" y2="12"/>
      <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/>
      <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
    </svg>
  );

  const SpeakerIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
      <path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>
      <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
    </svg>
  );

  const stateConfig = {
    [STATES.IDLE]: { color: 'bg-[#6c63ff]', icon: MicIcon, label: 'Tap to speak' },
    [STATES.LISTENING]: { color: 'bg-[#ef4444]', icon: MicIcon, label: 'Listening...' },
    [STATES.PROCESSING]: { color: 'bg-[#f59e0b]', icon: LoaderIcon, label: 'Processing...' },
    [STATES.SPEAKING]: { color: 'bg-[#4ade80]', icon: SpeakerIcon, label: 'Speaking...' },
  };

  const config = stateConfig[state];

  return (
    <>
      <button
        onClick={toggleActive}
        onDoubleClick={() => setIsExpanded(!isExpanded)}
        className={`fixed bottom-24 left-1/2 -translate-x-1/2 z-50 w-14 h-14 rounded-full ${config.color} shadow-lg flex items-center justify-center transition-all text-white ${
          state === STATES.LISTENING ? 'animate-pulse ring-4 ring-white/30' : ''
        }`}
      >
        <config.icon />
      </button>
      
      <div className="fixed bottom-16 left-1/2 -translate-x-1/2 z-50 text-center pointer-events-none">
        <span className="text-[10px] text-[#6b7280] block">{config.label}</span>
        {transcript && (
          <span className="text-[10px] text-[#4ade80] block mt-0.5 italic max-w-[200px] truncate">
            "{transcript}"
          </span>
        )}
      </div>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="fixed bottom-40 left-4 right-4 z-50 bg-[#1a1a2e] border border-[#2a2a4a] rounded-xl shadow-xl max-w-md mx-auto"
          >
            <div className="p-3 border-b border-[#2a2a4a] flex items-center justify-between">
              <span className="text-sm font-semibold text-white">Voice Chat</span>
              <button onClick={() => setIsExpanded(false)} className="text-[#6b7280] hover:text-white">✕</button>
            </div>
            
            <div className="h-40 overflow-y-auto p-3 space-y-2">
              {messages.length === 0 ? (
                <p className="text-[#6b7280] text-xs text-center py-8">No messages yet</p>
              ) : (
                messages.slice(-15).map(msg => (
                  <div key={msg.id} className={`text-xs ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                    <span className={`inline-block px-2 py-1 rounded-lg max-w-[85%] ${
                      msg.role === 'user' ? 'bg-[#6c63ff] text-white' : 'bg-[#2a2a4a] text-[#e8e8f0]'
                    }`}>
                      {msg.content}
                    </span>
                  </div>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
