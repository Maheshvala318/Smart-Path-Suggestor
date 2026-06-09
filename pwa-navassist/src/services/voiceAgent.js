import { VoiceProvider, voiceProviderConfig } from './voiceProvider';

export class VoiceAgentEngine {
  constructor(actions, addLog, config = {}) {
    this.actions = actions;
    this.addLog = addLog;
    this.provider = new VoiceProvider(config);
    this.recognition = null;
    this.speechQueue = [];
    this.isSpeaking = false;
    this.isListening = false;
    this.wakeWord = 'hey nav';
    this.onIntentDetected = null;
    this.isExplicitActivation = false;
    this.config = {
      wakeWordEnabled: config.wakeWordEnabled ?? false,
      continuousListening: config.continuousListening ?? true,
      ...config,
    };
  }

  setProvider(type, providerName) {
    this.provider.setProvider(type, providerName);
    this.addLog({ type: 'config', message: `${type} provider set to ${providerName}` });
  }

  setLanguage(language) {
    this.provider.setLanguage(language);
    
    if (this.recognition?.instance) {
      this.recognition.instance.lang = language;
    }
    
    this.addLog({ type: 'config', message: `Language set to ${language}` });
  }

  getAvailableProviders() {
    return voiceProviderConfig;
  }

  async init() {
    try {
      this.recognition = await this.provider.createSpeechRecognition();
      
      this.recognition.onResult(({ final: finalTranscript, interim: interimTranscript }) => {
        if (interimTranscript) {
          this.actions.setVoiceState({ lastTranscript: interimTranscript });
        }
        
        if (finalTranscript) {
          this.handleTranscript(finalTranscript);
        }
      });

      this.recognition.onError((error) => {
        if (error === 'no-speech') return;
        console.error('Speech recognition error:', error);
        this.addLog({ type: 'error', message: `Speech error: ${error}` });
      });

      this.recognition.onEnd(() => {
        if (this.isListening && this.config.continuousListening) {
          setTimeout(() => {
            try {
              this.recognition.start();
            } catch (e) {
              console.log('Recognition restart error:', e);
            }
          }, 100);
        } else {
          this.actions.setVoiceState({ isListening: false, status: 'idle' });
        }
      });

      this.addLog({ 
        type: 'voice', 
        message: `Voice engine initialized (STT: ${this.provider.sttProvider}, LLM: ${this.provider.llmProvider})` 
      });
      
      return true;
    } catch (error) {
      console.error('Voice engine init error:', error);
      this.addLog({ type: 'error', message: `Voice init error: ${error.message}` });
      return false;
    }
  }

  startListening() {
    if (!this.recognition) {
      this.addLog({ type: 'error', message: 'Voice engine not initialized' });
      return;
    }
    
    this.isListening = true;
    this.actions.setVoiceState({ isListening: true, status: 'listening' });
    
    try {
      this.recognition.start();
    } catch (e) {
      if (e.message?.includes('already started')) {
        return;
      }
      console.log('Recognition start error:', e);
    }
    
    this.addLog({ type: 'voice', message: 'Started listening' });
  }

  stopListening() {
    if (!this.recognition) return;
    
    this.isListening = false;
    this.actions.setVoiceState({ isListening: false, status: 'idle' });
    
    try {
      this.recognition.stop();
    } catch (e) {
      console.log('Recognition stop error:', e);
    }
    
    this.addLog({ type: 'voice', message: 'Stopped listening' });
  }

  toggleListening() {
    if (this.isListening) {
      this.stopListening();
    } else {
      this.startListening();
    }
  }

  async handleTranscript(transcript) {
    this.addLog({ type: 'user', message: transcript });
    this.actions.setVoiceState({ lastTranscript: transcript });

    const lowerTranscript = transcript.toLowerCase();
    
    if (this.config.wakeWordEnabled && 
        !lowerTranscript.includes(this.wakeWord) && 
        !this.isExplicitActivation) {
      return;
    }

    this.actions.setVoiceState({ isProcessing: true, status: 'processing' });
    
    try {
      const context = this.getContext();
      const intent = await this.provider.classifyIntent(transcript, context);
      
      this.addLog({ 
        type: 'intent', 
        message: `Intent: ${intent.intent} (${Math.round((intent.confidence || 0) * 100)}%)` 
      });
      
      if (this.onIntentDetected) {
        await this.onIntentDetected(intent, transcript);
      }
    } catch (error) {
      console.error('Intent classification error:', error);
      this.addLog({ type: 'error', message: `Classification error: ${error.message}` });
      await this.speak('Sorry, I encountered an error. Please try again.');
    }

    this.actions.setVoiceState({ isProcessing: false, status: this.isListening ? 'listening' : 'idle' });
    this.isExplicitActivation = false;
  }

  getContext() {
    return {
      navigationActive: false,
      detectionActive: false,
    };
  }

  async speak(text, options = {}) {
    this.addLog({ type: 'assistant', message: text });
    
    if (options.priority) {
      this.stopSpeaking();
    }

    this.speechQueue.push({ text, options });
    
    if (!this.isSpeaking) {
      await this.processQueue();
    }
  }

  async processQueue() {
    if (this.speechQueue.length === 0) {
      this.isSpeaking = false;
      this.actions.setVoiceState({ isSpeaking: false });
      return;
    }

    const { text, options } = this.speechQueue.shift();
    this.isSpeaking = true;
    this.actions.setVoiceState({ isSpeaking: true, status: 'speaking', lastResponse: text });

    try {
      await this.provider.speak(text, options);
    } catch (error) {
      console.error('Speech error:', error);
    }

    this.actions.setVoiceState({ isSpeaking: false });
    
    setTimeout(() => this.processQueue(), 100);
  }

  stopSpeaking() {
    this.speechQueue = [];
    this.isSpeaking = false;
    this.actions.setVoiceState({ isSpeaking: false });
    
    if (this.provider.ttsProvider === 'browser' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
  }

  activate() {
    this.isExplicitActivation = true;
    this.actions.setVoiceState({ status: 'listening' });
    this.addLog({ type: 'voice', message: 'Voice activated' });
  }

  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
    this.addLog({ type: 'config', message: `Config updated: ${JSON.stringify(newConfig)}` });
  }
}

export function createVoiceAgent(actions, addLog, config = {}) {
  return new VoiceAgentEngine(actions, addLog, config);
}
