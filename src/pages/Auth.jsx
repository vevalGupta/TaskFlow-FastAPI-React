import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button, FormField, Alert } from '../components/UI';
import { extractError } from '../api/client';

const pageWrap = { minHeight:'100vh', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', padding:24, background:'var(--bg)' };
const formCard  = { width:'100%', maxWidth:420, background:'var(--bg2)', border:'1px solid var(--border)', borderRadius:'var(--rl)', padding:36 };
const h1style   = { fontFamily:'var(--fh)', fontSize:24, fontWeight:700, marginBottom:6 };
const subStyle  = { color:'var(--muted)', fontSize:14, marginBottom:28 };

// ── Login ─────────────────────────────────────────────────────
export function Login() {
  const { login } = useAuth();
  const navigate  = useNavigate();
  const [form, setForm] = useState({ email:'', password:'' });
  const [err, setErr]   = useState('');
  const [fe, setFe]     = useState({});
  const [loading, setL] = useState(false);

  const submit = async e => {
    e.preventDefault(); setErr(''); setFe(''); setL(true);
    try { const u = await login(form); navigate(u.role === 'admin' ? '/admin' : '/dashboard'); }
    catch(e) { const {message,fields} = extractError(e); setErr(message); setFe(fields); }
    finally { setL(false); }
  };

  return (
    <div style={pageWrap}>
      <div style={{ marginBottom:36 }}><span style={{ fontFamily:'var(--fh)', fontSize:22, fontWeight:800 }}>Task<span style={{ color:'var(--accent)' }}>Flow</span></span></div>
      <div style={formCard}>
        <h1 style={h1style}>Welcome back</h1>
        <p style={subStyle}>Sign in to your account</p>
        {err && <Alert type="error" onClose={()=>setErr('')}>{err}</Alert>}
        <form onSubmit={submit}>
          <FormField label="Email" error={fe.email}><input type="email" placeholder="you@example.com" value={form.email} onChange={e=>setForm({...form,email:e.target.value})} required /></FormField>
          <FormField label="Password" error={fe.password}><input type="password" placeholder="••••••••" value={form.password} onChange={e=>setForm({...form,password:e.target.value})} required /></FormField>
          <Button type="submit" full loading={loading} size="lg" style={{ marginTop:6 }}>Sign in</Button>
        </form>
        <p style={{ marginTop:22, textAlign:'center', fontSize:14, color:'var(--muted)' }}>No account? <Link to="/register" style={{ color:'var(--accent)', fontWeight:500 }}>Create one</Link></p>
      </div>
    </div>
  );
}

// ── Register ──────────────────────────────────────────────────
export function Register() {
  const { register, login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name:'', email:'', password:'' });
  const [err, setErr]   = useState('');
  const [fe, setFe]     = useState({});
  const [loading, setL] = useState(false);
  const s = k => e => setForm({...form, [k]: e.target.value});

  const submit = async e => {
    e.preventDefault(); setErr(''); setFe({}); setL(true);
    try { await register(form); await login({ email:form.email, password:form.password }); navigate('/dashboard'); }
    catch(e) { const {message,fields} = extractError(e); setErr(message); setFe(fields); }
    finally { setL(false); }
  };

  return (
    <div style={pageWrap}>
      <div style={{ marginBottom:36 }}><span style={{ fontFamily:'var(--fh)', fontSize:22, fontWeight:800 }}>Task<span style={{ color:'var(--accent)' }}>Flow</span></span></div>
      <div style={formCard}>
        <h1 style={h1style}>Create account</h1>
        <p style={subStyle}>Start managing your tasks today</p>
        {err && <Alert type="error" onClose={()=>setErr('')}>{err}</Alert>}
        <form onSubmit={submit}>
          <FormField label="Full name" error={fe.name}><input placeholder="Aanya Sharma" value={form.name} onChange={s('name')} required /></FormField>
          <FormField label="Email" error={fe.email}><input type="email" placeholder="you@example.com" value={form.email} onChange={s('email')} required /></FormField>
          <FormField label="Password" error={fe.password}><input type="password" placeholder="Min 8 chars, uppercase, number, special" value={form.password} onChange={s('password')} required /></FormField>
          <p style={{ fontSize:12, color:'var(--dim)', marginTop:-12, marginBottom:18, lineHeight:1.5 }}>Requires uppercase letter, number, and special character</p>
          <Button type="submit" full loading={loading} size="lg">Create account</Button>
        </form>
        <p style={{ marginTop:22, textAlign:'center', fontSize:14, color:'var(--muted)' }}>Already have one? <Link to="/login" style={{ color:'var(--accent)', fontWeight:500 }}>Sign in</Link></p>
      </div>
    </div>
  );
}