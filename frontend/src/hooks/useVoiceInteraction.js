import { useState, useEffect, useRef, useCallback } from 'react';

const useVoiceInteraction = () => {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [confidence, setConfidence] = useState(0);
  const [error, setError] = useState(null);
  const [voiceMode, setVoiceMode] = useState('hybrid'); // 'full', 'hybrid', 'text'

  const recognitionRef = useRef(null);
  const synthRef = useRef(null);
  const isListeningRef = useRef(false);
  const wakeWordTimeoutRef = useRef(null);
  const wakeWordHandlerRef = useRef(null);

  // Initialize speech recognition and synthesis
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const SpeechSynthesis = window.speechSynthesis;

    if (SpeechRecognition && SpeechSynthesis) {
      setIsSupported(true);
      
      // Initialize recognition
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      // Initialize synthesis
      synthRef.current = SpeechSynthesis;

      // Recognition event handlers
      recognitionRef.current.onstart = () => {
        setIsListening(true);
        isListeningRef.current = true;
        setError(null);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
        isListeningRef.current = false;
        
        // Restart listening if in full voice mode
        if (voiceMode === 'full' && !error) {
          setTimeout(() => {
            startListening();
          }, 1000);
        }
      };

      recognitionRef.current.onerror = (event) => {
        setError(event.error);
        setIsListening(false);
        isListeningRef.current = false;
      };

      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i];
          if (result.isFinal) {
            finalTranscript += result[0].transcript;
            setConfidence(result[0].confidence);
          } else {
            interimTranscript += result[0].transcript;
          }
        }

        setTranscript(finalTranscript || interimTranscript);

        // Check for wake word
        const fullText = (finalTranscript || interimTranscript).toLowerCase();
        if (fullText.includes('hey jarvis') || fullText.includes('jarvis')) {
          handleWakeWord(finalTranscript || interimTranscript);
        }
      };
    } else {
      setIsSupported(false);
      setError('Speech recognition not supported in this browser');
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (wakeWordTimeoutRef.current) {
        clearTimeout(wakeWordTimeoutRef.current);
      }
    };
  }, [voiceMode]);

  // Handle wake word detection
  const handleWakeWord = useCallback((text) => {
    const wakeWordIndex = text.toLowerCase().indexOf('hey jarvis');
    const jarvisIndex = text.toLowerCase().indexOf('jarvis');
    
    let command = '';
    if (wakeWordIndex !== -1) {
      command = text.substring(wakeWordIndex + 10).trim();
    } else if (jarvisIndex !== -1) {
      command = text.substring(jarvisIndex + 6).trim();
    }

    // Clear any existing timeout
    if (wakeWordTimeoutRef.current) {
      clearTimeout(wakeWordTimeoutRef.current);
    }

    // Set timeout for command processing
    wakeWordTimeoutRef.current = setTimeout(() => {
      if (command) {
        try {
          wakeWordHandlerRef.current?.(command);
        } catch (e) {
          console.error('Wake word handler error:', e);
        }
      }
    }, 1000);
  }, []);

  // Start listening
  const startListening = useCallback(() => {
    if (recognitionRef.current && !isListeningRef.current) {
      try {
        recognitionRef.current.start();
      } catch (err) {
        setError('Failed to start speech recognition');
      }
    }
  }, []);

  // Stop listening
  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListeningRef.current) {
      recognitionRef.current.stop();
    }
  }, []);

  // Speak text
  const speak = useCallback((text, options = {}) => {
    if (!synthRef.current || !text) return;

    // Cancel any ongoing speech
    synthRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = options.rate || 1;
    utterance.pitch = options.pitch || 1;
    utterance.volume = options.volume || 1;
    utterance.voice = options.voice || null;

    utterance.onstart = () => {
      setIsSpeaking(true);
    };

    utterance.onend = () => {
      setIsSpeaking(false);
    };

    utterance.onerror = (event) => {
      setError(`Speech synthesis error: ${event.error}`);
      setIsSpeaking(false);
    };

    synthRef.current.speak(utterance);
  }, []);

  // Stop speaking
  const stopSpeaking = useCallback(() => {
    if (synthRef.current) {
      synthRef.current.cancel();
      setIsSpeaking(false);
    }
  }, []);

  // Get available voices
  const getVoices = useCallback(() => {
    if (synthRef.current) {
      return synthRef.current.getVoices();
    }
    return [];
  }, []);

  // Toggle voice mode
  const toggleVoiceMode = useCallback(() => {
    const modes = ['text', 'hybrid', 'full'];
    const currentIndex = modes.indexOf(voiceMode);
    const nextMode = modes[(currentIndex + 1) % modes.length];
    setVoiceMode(nextMode);

    if (nextMode === 'full') {
      startListening();
    } else if (nextMode === 'text') {
      stopListening();
    }
  }, [voiceMode, startListening, stopListening]);

  // Clear transcript
  const clearTranscript = useCallback(() => {
    setTranscript('');
    setConfidence(0);
  }, []);

  const setWakeWordHandler = useCallback((handler) => {
    wakeWordHandlerRef.current = typeof handler === 'function' ? handler : null;
  }, []);

  return {
    // State
    isListening,
    isSpeaking,
    isSupported,
    transcript,
    confidence,
    error,
    voiceMode,

    // Actions
    startListening,
    stopListening,
    speak,
    stopSpeaking,
    toggleVoiceMode,
    clearTranscript,
    getVoices,

    // Utilities
    setVoiceMode,
    setWakeWordHandler
  };
};

export default useVoiceInteraction;