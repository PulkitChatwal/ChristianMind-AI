import React from 'react';

function ImagePanel({ imageResult }) {
  if (!imageResult) return null;

  if (!imageResult.success) {
    return (
      <div style={{
        background: 'rgba(248,113,113,0.1)',
        border: '1px solid rgba(248,113,113,0.2)',
        borderRadius: '16px',
        padding: '24px',
        textAlign: 'center',
        maxWidth: '85%',
        margin: '0 auto',
      }}>
        <span style={{ fontSize: '32px' }}>🖼️</span>
        <div style={{ color: '#f87171', marginTop: '8px', fontWeight: '600' }}>Image Blocked</div>
        <div style={{ color: 'rgba(255,255,255,0.6)', fontSize: '14px', marginTop: '4px' }}>{imageResult.error}</div>
      </div>
    );
  }

  return (
    <div style={{
      background: 'rgba(255,255,255,0.03)',
      borderRadius: '16px',
      overflow: 'hidden',
      border: '1px solid rgba(255,255,255,0.08)',
      maxWidth: '500px',
      margin: '0 auto',
    }}>
      <img
        src={imageResult.image_url}
        alt="Christian art"
        style={{
          width: '100%',
          display: 'block',
          borderRadius: '12px',
        }}
      />
      <div style={{
        padding: '14px 18px',
        background: 'rgba(255,255,255,0.02)',
        borderTop: '1px solid rgba(255,255,255,0.05)',
      }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 10px',
          background: 'rgba(74,124,89,0.2)',
          color: '#4ade80',
          borderRadius: '8px',
          fontSize: '11px',
          fontWeight: '600',
          marginBottom: '8px',
        }}>
          ✓ Theologically Reviewed
        </div>
        <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.5)', marginBottom: '4px' }}>
          Prompt
        </div>
        <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.7)', fontStyle: 'italic' }}>
          "{imageResult.sanitized_prompt}"
        </div>
      </div>
    </div>
  );
}

export default ImagePanel;