import React, { useState } from 'react';

function GroundingPanel({ retrievedVerses = [], verifiedCitations = [], hallucinatedCitations = [], judgeScores = {} }) {
  const [expanded, setExpanded] = useState(false);

  if (!retrievedVerses.length && !verifiedCitations.length && !hallucinatedCitations.length) {
    return null;
  }

  const accuracyScore = judgeScores?.accuracy_score;

  return (
    <div style={{
      background: 'rgba(255,255,255,0.03)',
      borderRadius: '14px',
      padding: '16px',
      marginTop: '8px',
      border: '1px solid rgba(255,255,255,0.05)',
    }}>
      {/* Header */}
      <div
        onClick={() => setExpanded(!expanded)}
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: 'pointer',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '16px' }}>📜</span>
          <span style={{ fontSize: '13px', fontWeight: '600', color: '#fff' }}>
            Scripture Grounding
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {accuracyScore !== null && accuracyScore !== undefined && (
            <div style={{
              background: accuracyScore >= 0.8 ? 'rgba(74,222,128,0.15)' : 'rgba(251,191,36,0.15)',
              color: accuracyScore >= 0.8 ? '#4ade80' : '#fbbf24',
              padding: '3px 10px',
              borderRadius: '10px',
              fontSize: '11px',
              fontWeight: '600',
            }}>
              {Math.round(accuracyScore * 100)}%
            </div>
          )}
          <span style={{ fontSize: '10px', color: 'rgba(255,255,255,0.4)' }}>
            {expanded ? '▲' : '▼'}
          </span>
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: 'flex', gap: '10px', marginTop: '12px' }}>
        <div style={{
          flex: 1,
          background: 'rgba(74,222,128,0.1)',
          borderRadius: '10px',
          padding: '10px',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: '20px', fontWeight: '700', color: '#4ade80' }}>
            {verifiedCitations.length}
          </div>
          <div style={{ fontSize: '10px', color: 'rgba(74,222,128,0.7)' }}>Verified</div>
        </div>
        {hallucinatedCitations.length > 0 && (
          <div style={{
            flex: 1,
            background: 'rgba(251,191,36,0.1)',
            borderRadius: '10px',
            padding: '10px',
            textAlign: 'center',
          }}>
            <div style={{ fontSize: '20px', fontWeight: '700', color: '#fbbf24' }}>
              {hallucinatedCitations.length}
            </div>
            <div style={{ fontSize: '10px', color: 'rgba(251,191,36,0.7)' }}>Unverified</div>
          </div>
        )}
      </div>

      {/* Expanded content */}
      {expanded && (
        <div style={{ marginTop: '12px' }}>
          {retrievedVerses.length > 0 && (
            <div style={{ marginBottom: '10px' }}>
              <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.4)', marginBottom: '6px', fontWeight: '600' }}>
                Sources
              </div>
              {retrievedVerses.map((v, i) => (
                <div key={i} style={{
                  background: 'rgba(255,255,255,0.02)',
                  borderRadius: '8px',
                  padding: '10px',
                  marginBottom: '6px',
                  borderLeft: '2px solid #4a7c59',
                }}>
                  <div style={{ fontSize: '11px', color: '#4a7c59', fontWeight: '600' }}>
                    {v.reference || v.book}
                  </div>
                  <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.6)', lineHeight: '1.5', fontStyle: 'italic' }}>
                    "{v.text || v.content}"
                  </div>
                </div>
              ))}
            </div>
          )}
          {verifiedCitations.length > 0 && (
            <div style={{ marginBottom: '6px' }}>
              <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.4)', marginBottom: '6px', fontWeight: '600' }}>
                Verified
              </div>
              {verifiedCitations.map((c, i) => (
                <span key={i} style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '3px 8px',
                  background: 'rgba(74,222,128,0.1)',
                  color: '#4ade80',
                  borderRadius: '6px',
                  fontSize: '11px',
                  marginRight: '4px',
                  marginBottom: '4px',
                }}>
                  ✓ {c.reference || c}
                </span>
              ))}
            </div>
          )}
          {hallucinatedCitations.length > 0 && (
            <div>
              <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.4)', marginBottom: '6px', fontWeight: '600' }}>
                Unverified
              </div>
              {hallucinatedCitations.map((c, i) => (
                <span key={i} style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '3px 8px',
                  background: 'rgba(251,191,36,0.1)',
                  color: '#fbbf24',
                  borderRadius: '6px',
                  fontSize: '11px',
                  marginRight: '4px',
                  marginBottom: '4px',
                }}>
                  ⚠ {c.reference || c}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default GroundingPanel;