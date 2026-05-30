import React, { useState } from 'react';

function TextToSpeech({ text }) {
  const [isPlaying, setIsPlaying] = useState(false);

  const speak = () => {
    if (isPlaying) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
      return;
    }

    if (!text) return;

    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1;

    const voices = synth.getVoices();
    const voice = voices.find(v => v.lang.startsWith('en') && v.name.includes('Google'))
      || voices.find(v => v.lang.startsWith('en'));
    if (voice) utterance.voice = voice;

    utterance.onstart = () => setIsPlaying(true);
    utterance.onend = () => setIsPlaying(false);
    utterance.onerror = () => setIsPlaying(false);

    synth.speak(utterance);
  };

  if (!text || !('speechSynthesis' in window)) return null;

  return (
    <button
      onClick={speak}
      style={{
        padding: '6px 12px',
        background: isPlaying ? 'rgba(74, 124, 89, 0.3)' : 'rgba(255,255,255,0.05)',
        border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: '10px',
        color: isPlaying ? '#4ade80' : 'rgba(255,255,255,0.7)',
        fontSize: '12px',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        transition: 'all 0.3s',
      }}
      onMouseOver={(e) => {
        if (!isPlaying) {
          e.target.style.background = 'rgba(255,255,255,0.1)';
          e.target.style.color = '#fff';
        }
      }}
      onMouseOut={(e) => {
        if (!isPlaying) {
          e.target.style.background = 'rgba(255,255,255,0.05)';
          e.target.style.color = 'rgba(255,255,255,0.7)';
        }
      }}
    >
      {isPlaying ? (
        <>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <rect x="6" y="6" width="12" height="12" rx="2" />
          </svg>
          <span>Stop</span>
        </>
      ) : (
        <>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
            <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
            <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
          </svg>
          <span>Listen</span>
        </>
      )}
    </button>
  );
}

export default TextToSpeech;