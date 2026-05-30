import React, { useState, useRef, useEffect } from 'react';

function VoiceInput({ onTranscript, disabled }) {
  const [isRecording, setIsRecording] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const recognitionRef = useRef(null);
  const onTranscriptRef = useRef(onTranscript);
  const isMountedRef = useRef(true);

  // Keep the callback ref updated
  useEffect(() => {
    onTranscriptRef.current = onTranscript;
  }, [onTranscript]);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      setIsSupported(true);
    }

    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
      if (recognitionRef.current) {
        recognitionRef.current.abort();
        recognitionRef.current = null;
      }
    };
  }, []);

  const startListening = () => {
    if (!isSupported || disabled || recognitionRef.current) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;

    let finalTranscript = '';

    recognition.onstart = () => {
      if (isMountedRef.current) {
        setIsRecording(true);
        finalTranscript = '';
      }
    };

    recognition.onresult = (event) => {
      let interimTranscript = '';
      let newFinal = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript_part = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          newFinal += transcript_part;
        } else {
          interimTranscript += transcript_part;
        }
      }

      if (newFinal) {
        finalTranscript += ' ' + newFinal;
        if (isMountedRef.current) {
          onTranscriptRef.current(finalTranscript.trim());
        }
      }
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      if (event.error === 'not-allowed') {
        if (isMountedRef.current) {
          setIsRecording(false);
        }
        recognitionRef.current = null;
      }
    };

    recognition.onend = () => {
      if (isMountedRef.current && recognitionRef.current) {
        try {
          recognitionRef.current.start();
        } catch (e) {
          setIsRecording(false);
          recognitionRef.current = null;
        }
      }
    };

    recognitionRef.current = recognition;

    try {
      recognition.start();
    } catch (e) {
      console.error('Failed to start recognition:', e);
      recognitionRef.current = null;
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.onend = null;
      recognitionRef.current.abort();
      recognitionRef.current = null;
    }
    setIsRecording(false);
  };

  const toggleRecording = () => {
    if (disabled) return;

    if (isRecording) {
      stopListening();
    } else {
      startListening();
    }
  };

  if (!isSupported) return null;

  return (
    <button
      onClick={toggleRecording}
      disabled={disabled}
      style={{
        width: '44px',
        height: '44px',
        borderRadius: '14px',
        border: 'none',
        background: isRecording
          ? 'linear-gradient(135deg, #ef4444, #dc2626)'
          : 'rgba(255,255,255,0.1)',
        cursor: disabled ? 'not-allowed' : 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'all 0.3s ease',
        position: 'relative',
        opacity: disabled ? 0.5 : 1,
      }}
      onMouseOver={(e) => {
        if (!disabled && !isRecording) {
          e.target.style.background = 'rgba(74, 124, 89, 0.3)';
          e.target.style.transform = 'scale(1.05)';
        }
      }}
      onMouseOut={(e) => {
        if (!disabled && !isRecording) {
          e.target.style.background = 'rgba(255,255,255,0.1)';
          e.target.style.transform = 'scale(1)';
        }
      }}
      title={isRecording ? 'Stop recording' : 'Start voice input'}
    >
      {/* Mic Icon */}
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill={isRecording ? '#fff' : 'none'}
        stroke={isRecording ? '#fff' : 'rgba(255,255,255,0.8)'}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        style={{
          transition: 'all 0.3s',
          filter: isRecording ? 'drop-shadow(0 0 8px rgba(239,68,68,0.8))' : 'none',
        }}
      >
        {isRecording ? (
          <rect x="6" y="6" width="12" height="12" rx="2" />
        ) : (
          <>
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
            <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
            <line x1="12" y1="19" x2="12" y2="23" />
            <line x1="8" y1="23" x2="16" y2="23" />
          </>
        )}
      </svg>

      {/* Recording indicator ring */}
      {isRecording && (
        <div style={{
          position: 'absolute',
          inset: '-4px',
          borderRadius: '18px',
          border: '2px solid rgba(239,68,68,0.5)',
          animation: 'ripple 1.5s ease-out infinite',
        }} />
      )}

      <style>{`
        @keyframes ripple {
          0% { transform: scale(1); opacity: 1; }
          100% { transform: scale(1.3); opacity: 0; }
        }
      `}</style>
    </button>
  );
}

export default VoiceInput;