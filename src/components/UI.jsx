import React from 'react';

export const Spinner = ({ size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" style={{ animation: 'spin .7s linear infinite', flexShrink: 0 }}>
    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2.5" opacity=".2" />
    <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
  </svg>
);

export const Button = ({ children, variant = 'primary', size = 'md', loading, disabled, full, style, ...p }) => {
  const base = { display:'inline-flex', alignItems:'center', justifyContent:'center', gap:8, fontFamily:'var(--fb)', fontWeight:600, border:'none', borderRadius:'var(--r)', cursor: disabled||loading ? 'not-allowed' : 'pointer', opacity: disabled||loading ? .5 : 1, transition:'all var(--t)', width: full ? '100%' : 'auto', letterSpacing:'.01em', fontSize: size==='sm'?13:size==='lg'?16:14, padding: size==='sm'?'6px 13px':size==='lg'?'12px 26px':'9px 18px' };
  const vars = {
    primary:   { background:'var(--accent)',                      color:'#fff' },
    secondary: { background:'var(--bg3)', border:'1px solid var(--border)',  color:'var(--text)' },
    danger:    { background:'rgba(255,61,90,.12)', border:'1px solid rgba(255,61,90,.28)', color:'var(--danger)' },
    ghost:     { background:'transparent', border:'1px solid var(--border)', color:'var(--muted)' },
  };
  return <button style={{ ...base, ...vars[variant], ...style }} disabled={disabled||loading} {...p}>{loading && <Spinner size={14}/>}{children}</button>;
};

export const FormField = ({ label, error, children }) => (
  <div style={{ marginBottom:18 }}>
    {label && <label style={{ display:'block', fontSize:12, fontWeight:500, color:'var(--muted)', marginBottom:6, letterSpacing:'.03em', textTransform:'uppercase' }}>{label}</label>}
    {children}
    {error && <p style={{ fontSize:12, color:'var(--danger)', marginTop:5 }}>{error}</p>}
  </div>
);

export const Alert = ({ type='info', children, onClose }) => {
  const c = { success:{bg:'rgba(37,208,122,.08)',border:'rgba(37,208,122,.22)',text:'var(--success)'}, error:{bg:'rgba(255,61,90,.08)',border:'rgba(255,61,90,.22)',text:'var(--danger)'}, info:{bg:'rgba(61,123,255,.08)',border:'rgba(61,123,255,.22)',text:'var(--accent)'}, warning:{bg:'rgba(240,160,32,.08)',border:'rgba(240,160,32,.22)',text:'var(--warning)'} }[type];
  return (
    <div style={{ background:c.bg, border:`1px solid ${c.border}`, borderRadius:'var(--r)', padding:'11px 15px', fontSize:13, color:c.text, display:'flex', alignItems:'flex-start', gap:10, marginBottom:16 }}>
      <span style={{ flex:1 }}>{children}</span>
      {onClose && <button onClick={onClose} style={{ background:'none', border:'none', color:c.text, fontSize:18, lineHeight:1, cursor:'pointer', opacity:.6, padding:0 }}>×</button>}
    </div>
  );
};

export const Badge = ({ label, type }) => {
  const c = { todo:{bg:'rgba(110,122,144,.12)',color:'var(--todo)'}, in_progress:{bg:'rgba(240,160,32,.12)',color:'var(--progress)'}, done:{bg:'rgba(37,208,122,.12)',color:'var(--done)'}, high:{bg:'rgba(255,61,90,.12)',color:'var(--danger)'}, medium:{bg:'rgba(240,160,32,.12)',color:'var(--warning)'}, low:{bg:'rgba(61,123,255,.12)',color:'var(--accent)'}, admin:{bg:'rgba(124,91,255,.15)',color:'var(--purple)'}, user:{bg:'rgba(110,122,144,.1)',color:'var(--muted)'} }[type] || {bg:'rgba(110,122,144,.1)',color:'var(--muted)'};
  return <span style={{ ...c, fontSize:10, fontWeight:600, padding:'2px 8px', borderRadius:5, fontFamily:'var(--fm)', letterSpacing:'.06em', textTransform:'uppercase', whiteSpace:'nowrap' }}>{label || type?.replace('_',' ')}</span>;
};

export const Card = ({ children, style }) => (
  <div style={{ background:'var(--bg2)', border:'1px solid var(--border)', borderRadius:'var(--rl)', padding:24, ...style }}>{children}</div>
);