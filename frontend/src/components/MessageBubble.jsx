import React from 'react';
import TextToSpeech from './TextToSpeech';

const VERDICT_COLORS = {
  PASS: '#4ade80',
  FLAG: '#fbbf24',
  REWRITE: '#f87171',
};

function MessageBubble({ message, isUser, verdict, citations = [] }) {
  const verdictColor = VERDICT_COLORS[verdict] || VERDICT_COLORS.PASS;

  // Process citations
  const renderMessage = () => {
    if (!citations?.length) return message;

    let result = message;
    citations.forEach((cite) => {
      const ref = cite.reference || cite;
      const isVerified = cite.status === 'verified';
      const replacement = isVerified
        ? `<span style="background: rgba(74,222,128,0.15); color: #4ade80; padding: 2px 6px; border-radius: 6px; font-size: 12px; font-weight: 500;">${ref}</span>`
        : `<span style="background: rgba(251,191,36,0.15); color: #fbbf24; padding: 2px 6px; border-radius: 6px; font-size: 12px; font-weight: 500;">⚠ ${ref}</span>`;
      result = result.replace(ref, replacement);
    });
    return <span dangerouslySetInnerHTML={{ __html: result }} />;
  };

  return (
    <div style={{
      maxWidth: '85%',
      padding: '14px 16px',
      borderRadius: '16px',
      position: 'relative',
      ...(isUser ? {
        background: 'linear-gradient(135deg, #4a7c59, #3d6b4a)',
        color: '#fff',
        borderBottomRightRadius: '4px',
      } : {
        background: 'rgba(255,255,255,0.05)',
        border: '1px solid rgba(255,255,255,0.06)',
        borderBottomLeftRadius: '4px',
      }),
    }}>
      {/* Verdict indicator */}
      {verdict && (
        <div style={{
          position: 'absolute',
          top: '10px',
          right: '10px',
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          background: verdictColor,
          boxShadow: `0 0 8px ${verdictColor}`,
        }} />
      )}

      {/* Role label */}
      <div style={{
        fontSize: '11px',
        fontWeight: '600',
        marginBottom: '6px',
        opacity: 0.6,
        textAlign: isUser ? 'right' : 'left',
      }}>
        {isUser ? 'You' : 'ChristianMind'}
      </div>

      {/* Message content */}
      <div style={{
        fontSize: '14px',
        lineHeight: '1.55',
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word',
      }}>
        {renderMessage()}
      </div>

      {/* Action buttons */}
      {!isUser && (
        <div style={{
          display: 'flex',
          gap: '6px',
          marginTop: '10px',
          paddingTop: '10px',
          borderTop: '1px solid rgba(255,255,255,0.05)',
        }}>
          <TextToSpeech text={message} />
        </div>
      )}
    </div>
  );
}

export default MessageBubble;