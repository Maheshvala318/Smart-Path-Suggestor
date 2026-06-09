const GROQ_API_KEY = import.meta.env.VITE_GROQ_API_KEY;
const DEEPGRAM_API_KEY = import.meta.env.VITE_DEEPGRAM_API_KEY;
const CLAUDE_API_KEY = import.meta.env.VITE_CLAUDE_API_KEY;
const SARVAM_API_KEY = import.meta.env.VITE_SARVAM_API_KEY;

const API_CONFIG = {
  groq: {
    url: 'https://api.groq.com/openai/v1/chat/completions',
    model: 'llama-3.3-70b-versatile',
    headers: (apiKey) => ({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
    }),
  },
  claude: {
    url: 'https://api.anthropic.com/v1/messages',
    model: 'claude-sonnet-4-20250514',
    headers: (apiKey) => ({
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
    }),
  },
};

const STT_CONFIG = {
  browser: {
    name: 'Web Speech API',
    supported: typeof window !== 'undefined' && ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window),
  },
  deepgram: {
    name: 'Deepgram',
    url: 'wss://api.deepgram.com/v1/listen',
    model: 'nova-2',
    language: 'en-US',
  },
  sarvam: {
    name: 'Sarvam AI',
    url: 'https://api.sarvam.ai/speech-to-text',
    languages: ['en', 'hi', 'gu', 'ta', 'te', 'kn', 'ml', 'bn', 'mr', 'pa'],
  },
};

const TTS_CONFIG = {
  browser: {
    name: 'Web Speech Synthesis',
    supported: typeof window !== 'undefined' && 'speechSynthesis' in window,
  },
  deepgram: {
    name: 'Deepgram TTS',
    url: 'https://api.deepgram.com/v1/speak',
    model: 'aura-asteria-en',
  },
  sarvam: {
    name: 'Sarvam TTS',
    url: 'https://api.sarvam.ai/text-to-speech',
    languages: ['en', 'hi', 'gu', 'ta', 'te', 'kn', 'ml', 'bn', 'mr', 'pa'],
  },
};

export class VoiceProvider {
  constructor(config = {}) {
    this.llmProvider = config.llmProvider || 'groq';
    this.sttProvider = config.sttProvider || 'browser';
    this.ttsProvider = config.ttsProvider || 'browser';
    this.language = config.language || 'en-US';
    this.deepgramApiKey = config.deepgramApiKey || DEEPGRAM_API_KEY;
    this.groqApiKey = config.groqApiKey || GROQ_API_KEY;
    this.claudeApiKey = config.claudeApiKey || CLAUDE_API_KEY;
    this.sarvamApiKey = config.sarvamApiKey || SARVAM_API_KEY;
  }

  setProvider(type, provider) {
    if (type === 'llm') this.llmProvider = provider;
    else if (type === 'stt') this.sttProvider = provider;
    else if (type === 'tts') this.ttsProvider = provider;
  }

  setLanguage(lang) {
    this.language = lang;
  }

  async classifyIntent(transcript, context = {}) {
    const prompt = this.buildIntentPrompt(transcript, context);

    if (this.llmProvider === 'groq') {
      return this.classifyWithGroq(prompt);
    } else if (this.llmProvider === 'claude') {
      return this.classifyWithClaude(prompt);
    }
    
    return this.fallbackIntentClassification(transcript);
  }

  buildIntentPrompt(transcript, context) {
    return `You are an intent classifier for a blind navigation assistant.
Classify the user's speech into exactly one of these intents:
- NAVIGATE: user wants to go from one place to another (extract: from, to)
- DETECTION_ON: user wants to enable obstacle detection
- DETECTION_OFF: user wants to disable obstacle detection
- WHERE_AM_I: user asks about current location or direction
- NEXT_STEP: user asks what to do next
- STATUS: user asks about system status
- UNKNOWN: none of the above

Current context:
- Active navigation: ${context.navigationActive || false}
- Detection active: ${context.detectionActive || false}

Respond ONLY in JSON: {"intent": "...", "from": "...", "to": "...", "confidence": 0.0-1.0, "response": "..."}

User said: "${transcript}"`;
  }

  async classifyWithGroq(prompt) {
    if (!this.groqApiKey) {
      throw new Error('GROQ_API_KEY not configured');
    }

    try {
      const response = await fetch(API_CONFIG.groq.url, {
        method: 'POST',
        headers: API_CONFIG.groq.headers(this.groqApiKey),
        body: JSON.stringify({
          model: API_CONFIG.groq.model,
          messages: [{ role: 'user', content: prompt }],
          temperature: 0.3,
          max_tokens: 512,
          response_format: { type: 'json_object' },
        }),
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`Groq API error: ${response.status} - ${error}`);
      }

      const data = await response.json();
      const content = data.choices[0]?.message?.content || '';
      
      return JSON.parse(content);
    } catch (error) {
      console.error('Groq classification error:', error);
      throw error;
    }
  }

  async classifyWithClaude(prompt) {
    if (!this.claudeApiKey) {
      throw new Error('CLAUDE_API_KEY not configured');
    }

    try {
      const response = await fetch(API_CONFIG.claude.url, {
        method: 'POST',
        headers: API_CONFIG.claude.headers(this.claudeApiKey),
        body: JSON.stringify({
          model: API_CONFIG.claude.model,
          max_tokens: 512,
          messages: [{ role: 'user', content: prompt }],
        }),
      });

      if (!response.ok) {
        throw new Error(`Claude API error: ${response.status}`);
      }

      const data = await response.json();
      const content = data.content[0]?.text || '';
      
      const jsonMatch = content.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      
      throw new Error('Failed to parse Claude response');
    } catch (error) {
      console.error('Claude classification error:', error);
      throw error;
    }
  }

  fallbackIntentClassification(transcript) {
    const lower = transcript.toLowerCase();
    
    const patterns = [
      { keywords: ['detection on', 'turn on detection', 'start detection', 'detect mode on'], intent: 'DETECTION_ON', response: 'Activating detection mode' },
      { keywords: ['detection off', 'turn off detection', 'stop detection'], intent: 'DETECTION_OFF', response: 'Closing detection mode' },
      { keywords: ['where am i', 'my location', 'current position', 'where is this'], intent: 'WHERE_AM_I', response: 'Checking your location' },
      { keywords: ['what next', 'next step', 'what now'], intent: 'NEXT_STEP', response: 'Checking next step' },
      { keywords: ['system status', 'status check', 'how is everything'], intent: 'STATUS', response: 'Checking system status' },
      { keywords: ['navigate', 'go to', 'find', 'path to', 'route to', 'way to', 'i want to go'], intent: 'NAVIGATE' },
    ];

    for (const pattern of patterns) {
      if (pattern.keywords.some(kw => lower.includes(kw))) {
        if (pattern.intent === 'NAVIGATE') {
          const toMatch = lower.match(/to\s+(.+?)(?:\s+from|\s*$)/);
          const fromMatch = lower.match(/from\s+(.+?)(?:\s+to|\s*$)/);
          return {
            intent: 'NAVIGATE',
            confidence: 0.85,
            to: toMatch ? toMatch[1].trim() : null,
            from: fromMatch ? fromMatch[1].trim() : null,
            response: `Finding route${toMatch ? ` to ${toMatch[1]}` : ''}`,
          };
        }
        return {
          intent: pattern.intent,
          confidence: 0.9,
          response: pattern.response,
        };
      }
    }
    
    return { intent: 'UNKNOWN', confidence: 0.5, response: 'I did not understand. Please try again.' };
  }

  createSpeechRecognition() {
    if (this.sttProvider === 'browser') {
      return this.createBrowserRecognition();
    } else if (this.sttProvider === 'deepgram') {
      return this.createDeepgramRecognition();
    } else if (this.sttProvider === 'sarvam') {
      return this.createSarvamRecognition();
    }
    
    return this.createBrowserRecognition();
  }

  createBrowserRecognition() {
    if (!STT_CONFIG.browser.supported) {
      throw new Error('Browser speech recognition not supported');
    }

    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SR();
    
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = this.language;

    return {
      type: 'browser',
      instance: recognition,
      start: () => recognition.start(),
      stop: () => recognition.stop(),
      onResult: (callback) => {
        recognition.onresult = (event) => {
          let finalTranscript = '';
          let interimTranscript = '';
          
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += transcript;
            } else {
              interimTranscript += transcript;
            }
          }
          
          callback({
            final: finalTranscript.trim(),
            interim: interimTranscript.trim(),
          });
        };
      },
      onError: (callback) => {
        recognition.onerror = (e) => callback(e.error);
      },
      onEnd: (callback) => {
        recognition.onend = () => callback();
      },
    };
  }

  async createDeepgramRecognition() {
    if (!this.deepgramApiKey) {
      throw new Error('DEEPGRAM_API_KEY not configured');
    }

    const socket = new WebSocket(
      `${STT_CONFIG.deepgram.url}?token=${this.deepgramApiKey}` +
      `&model=${STT_CONFIG.deepgram.model}` +
      `&language=${this.language.split('-')[0]}` +
      `&punctuate=true` +
      `&interim_results=true`
    );

    return new Promise((resolve, reject) => {
      socket.onopen = () => {
        resolve({
          type: 'deepgram',
          instance: socket,
          send: (audioData) => socket.send(audioData),
          close: () => socket.close(),
          onResult: (callback) => {
            socket.onmessage = (event) => {
              const data = JSON.parse(event.data);
              if (data.type === 'Results') {
                const transcript = data.channel?.alternatives?.[0]?.transcript || '';
                callback({
                  final: data.is_final ? transcript : '',
                  interim: data.is_final ? '' : transcript,
                });
              }
            };
          },
          onError: (callback) => {
            socket.onerror = (e) => callback('WebSocket error');
          },
          onEnd: (callback) => {
            socket.onclose = () => callback();
          },
        });
      };
      socket.onerror = (e) => reject(new Error('Failed to connect to Deepgram'));
    });
  }

  async createSarvamRecognition() {
    if (!this.sarvamApiKey) {
      throw new Error('SARVAM_API_KEY not configured');
    }

    return {
      type: 'sarvam',
      instance: null,
      transcribe: async (audioBlob) => {
        const formData = new FormData();
        formData.append('file', audioBlob);
        formData.append('language_code', this.language.split('-')[0]);

        const response = await fetch(STT_CONFIG.sarvam.url, {
          method: 'POST',
          headers: {
            'api-subscription-key': this.sarvamApiKey,
          },
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Sarvam STT error: ${response.status}`);
        }

        const data = await response.json();
        return data.transcript || '';
      },
    };
  }

  async speak(text, options = {}) {
    if (this.ttsProvider === 'browser') {
      return this.browserSpeak(text, options);
    } else if (this.ttsProvider === 'deepgram') {
      return this.deepgramSpeak(text, options);
    } else if (this.ttsProvider === 'sarvam') {
      return this.sarvamSpeak(text, options);
    }
    
    return this.browserSpeak(text, options);
  }

  browserSpeak(text, options = {}) {
    return new Promise((resolve, reject) => {
      if (!TTS_CONFIG.browser.supported) {
        reject(new Error('Browser speech synthesis not supported'));
        return;
      }

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = options.rate || 0.9;
      utterance.pitch = options.pitch || 1;
      utterance.volume = options.volume || 1;
      utterance.lang = this.language;

      if (options.voice) {
        const voices = window.speechSynthesis.getVoices();
        const voice = voices.find(v => v.name === options.voice);
        if (voice) utterance.voice = voice;
      }

      utterance.onend = () => resolve();
      utterance.onerror = (e) => reject(new Error(e.error));

      window.speechSynthesis.speak(utterance);
    });
  }

  async deepgramSpeak(text, options = {}) {
    if (!this.deepgramApiKey) {
      return this.browserSpeak(text, options);
    }

    try {
      const response = await fetch(
        `${TTS_CONFIG.deepgram.url}?model=${TTS_CONFIG.deepgram.model}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Token ${this.deepgramApiKey}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ text }),
        }
      );

      if (!response.ok) {
        throw new Error(`Deepgram TTS error: ${response.status}`);
      }

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      
      await audio.play();
      
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
      };

      return new Promise((resolve) => {
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
          resolve();
        };
      });
    } catch (error) {
      console.error('Deepgram TTS error:', error);
      return this.browserSpeak(text, options);
    }
  }

  async sarvamSpeak(text, options = {}) {
    if (!this.sarvamApiKey) {
      return this.browserSpeak(text, options);
    }

    try {
      const response = await fetch(TTS_CONFIG.sarvam.url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'api-subscription-key': this.sarvamApiKey,
        },
        body: JSON.stringify({
          text,
          language_code: this.language.split('-')[0],
          speaker_id: options.speaker || 'amitm',
        }),
      });

      if (!response.ok) {
        throw new Error(`Sarvam TTS error: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.audios && data.audios.length > 0) {
        const audio = new Audio(`data:audio/wav;base64,${data.audios[0]}`);
        await audio.play();
        return new Promise((resolve) => {
          audio.onended = () => resolve();
        });
      }
      
      throw new Error('No audio returned from Sarvam');
    } catch (error) {
      console.error('Sarvam TTS error:', error);
      return this.browserSpeak(text, options);
    }
  }
}

export const voiceProviderConfig = {
  llm: {
    providers: ['groq', 'claude'],
    default: 'groq',
  },
  stt: {
    providers: ['browser', 'deepgram', 'sarvam'],
    default: 'browser',
  },
  tts: {
    providers: ['browser', 'deepgram', 'sarvam'],
    default: 'browser',
  },
  languages: {
    en: 'English',
    hi: 'Hindi',
    gu: 'Gujarati',
    ta: 'Tamil',
    te: 'Telugu',
    kn: 'Kannada',
    ml: 'Malayalam',
    bn: 'Bengali',
    mr: 'Marathi',
    pa: 'Punjabi',
  },
};
