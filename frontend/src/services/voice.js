// Simple voice utilities using Web Speech API with backend fallbacks
import ApiService from './api';

const isBrowserSpeechAvailable = () => {
  return (
    typeof window !== 'undefined' &&
    (window.SpeechRecognition || window.webkitSpeechRecognition)
  );
};

export const VoiceService = {
  speak: async (text) => {
    try {
      // Try browser TTS first
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
        return { success: true, mode: 'browser' };
      }
      // Fallback to backend
      await ApiService.textToSpeech(text);
      return { success: true, mode: 'backend' };
    } catch (error) {
      console.error('Voice speak error:', error);
      return { success: false, error: error?.message || String(error) };
    }
  },

  startRecognition: async () => {
    try {
      // Prefer backend via preload API for consistency
      if (typeof window !== 'undefined' && window.api?.startVoiceRecognition) {
        const result = await window.api.startVoiceRecognition();
        return result; // { text, confidence }
      }

      // Fallback to Web Speech API
      if (isBrowserSpeechAvailable()) {
        const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new Recognition();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        return new Promise((resolve, reject) => {
          recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            resolve({ text: transcript, confidence: event.results[0][0].confidence });
          };
          recognition.onerror = (event) => {
            reject(event.error || 'speech_error');
          };
          recognition.onend = () => {
            // no-op
          };
          recognition.start();
        });
      }

      throw new Error('No speech recognition available');
    } catch (error) {
      console.error('Voice recognition error:', error);
      return { error: error?.message || String(error) };
    }
  },

  stopRecognition: async () => {
    try {
      if (typeof window !== 'undefined' && window.api?.stopVoiceRecognition) {
        return await window.api.stopVoiceRecognition();
      }
      // Web Speech API will stop automatically; no-op
      return { success: true };
    } catch (error) {
      console.error('Voice stop error:', error);
      return { success: false, error: error?.message || String(error) };
    }
  },
};

export default VoiceService;