import React from 'react';

const styles = {
  card: {
    backgroundColor: '#faf6f0',
    border: '1px solid #d4cdc5',
    borderRadius: '8px',
    padding: '12px 16px',
    marginTop: '8px',
    marginBottom: '8px',
    fontFamily: '"Crimson Text", Georgia, serif',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '8px',
  },
  reference: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#4a7c59',
  },
  badge: {
    fontSize: '11px',
    fontWeight: '600',
    padding: '2px 8px',
    borderRadius: '12px',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  verifiedBadge: {
    backgroundColor: 'rgba(34, 197, 94, 0.15)',
    color: '#15803d',
  },
  text: {
    fontSize: '15px',
    fontStyle: 'italic',
    color: '#5c4d3d',
    lineHeight: '1.6',
  },
  separator: {
    borderTop: '1px dashed #d4cdc5',
    marginTop: '12px',
    paddingTop: '8px',
    fontSize: '11px',
    color: '#8b7355',
    textAlign: 'center',
  },
};

function ScriptureCard({ verse, reference, verified = true }) {
  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <span style={styles.reference}>{reference}</span>
        <span style={{ ...styles.badge, ...(verified ? styles.verifiedBadge : styles.flaggedBadge) }}>
          {verified ? 'KJV ✓ Verified' : '⚠️ Review'}
        </span>
      </div>
      <div style={styles.text}>{verse}</div>
      <div style={styles.separator}>King James Version</div>
    </div>
  );
}

export default ScriptureCard;
