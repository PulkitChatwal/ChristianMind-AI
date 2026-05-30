import React from 'react';

const DENOMINATIONS = [
  { value: 'NONDENOMINATIONAL', label: 'Non-denominational' },
  { value: 'CATHOLIC', label: 'Catholic' },
  { value: 'PROTESTANT', label: 'Protestant' },
  { value: 'ORTHODOX', label: 'Eastern Orthodox' },
  { value: 'EVANGELICAL', label: 'Evangelical' },
];

const styles = {
  container: {
    padding: '12px 16px',
    backgroundColor: '#faf8f5',
    borderBottom: '1px solid #e8e4df',
  },
  label: {
    fontSize: '12px',
    fontWeight: '600',
    color: '#6b5b4f',
    marginBottom: '6px',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  select: {
    width: '100%',
    padding: '8px 12px',
    fontSize: '14px',
    fontFamily: 'inherit',
    border: '1px solid #d4cdc5',
    borderRadius: '6px',
    backgroundColor: '#fff',
    color: '#3d3229',
    cursor: 'pointer',
    outline: 'none',
    transition: 'border-color 0.2s, box-shadow 0.2s',
  },
};

export default function DenominationSelector({ value, onChange }) {
  const handleChange = (e) => {
    onChange(e.target.value);
  };

  return (
    <div style={styles.container}>
      <div style={styles.label}>Denominational Context</div>
      <select
        style={styles.select}
        value={value}
        onChange={handleChange}
        onFocus={(e) => {
          e.target.style.borderColor = '#8b7355';
          e.target.style.boxShadow = '0 0 0 2px rgba(139, 115, 85, 0.1)';
        }}
        onBlur={(e) => {
          e.target.style.borderColor = '#d4cdc5';
          e.target.style.boxShadow = 'none';
        }}
      >
        {DENOMINATIONS.map((d) => (
          <option key={d.value} value={d.value}>
            {d.label}
          </option>
        ))}
      </select>
    </div>
  );
}
