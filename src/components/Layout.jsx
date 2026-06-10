import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Badge } from './UI';

const N = ({ to, icon, label }) => (
  <NavLink to={to} style={({ isActive }) => ({ display:'flex', alignItems:'center', gap:9, padding:'8px 12px', borderRadius:'var(--r)', fontSize:14, fontWeight:500, transition:'all var(--t)', color:isActive?'var(--text)':'var(--muted)', background:isActive?'var(--bg3)':'transparent', textDecoration:'none' })}>
    <span style={{ fontSize:16, lineHeight:1 }}>{icon}</span>{label}
  </NavLink>
);

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const onLogout = async () => { await logout(); navigate('/login'); };

  return (
    <div style={{ display:'flex', minHeight:'100vh' }}>
      <aside style={{ width:210, flexShrink:0, background:'var(--bg2)', borderRight:'1px solid var(--border)', display:'flex', flexDirection:'column', padding:'22px 12px', position:'sticky', top:0, height:'100vh', overflowY:'auto' }}>
        <div style={{ marginBottom:28, paddingLeft:4 }}>
          <span style={{ fontFamily:'var(--fh)', fontSize:20, fontWeight:800 }}>Task<span style={{ color:'var(--accent)' }}>Flow</span></span>
        </div>
        <nav style={{ flex:1, display:'flex', flexDirection:'column', gap:3 }}>
          <N to="/dashboard" icon="⊞" label="Dashboard" />
          <N to="/tasks"     icon="✓" label="My tasks"  />
          {user?.role === 'admin' && <>
            <div style={{ height:1, background:'var(--border)', margin:'10px 4px' }} />
            <p style={{ fontSize:10, color:'var(--dim)', padding:'0 4px', marginBottom:4, fontWeight:600, letterSpacing:'.08em', textTransform:'uppercase' }}>Admin</p>
            <N to="/admin"       icon="◎" label="Overview"  />
            <N to="/admin/users" icon="◈" label="Users"     />
            <N to="/admin/tasks" icon="◉" label="All tasks" />
          </>}
        </nav>
        <div style={{ borderTop:'1px solid var(--border)', paddingTop:14, marginTop:14 }}>
          <div style={{ display:'flex', alignItems:'center', gap:9, marginBottom:11 }}>
            <div style={{ width:32, height:32, borderRadius:'50%', background:'linear-gradient(135deg, var(--accent), var(--purple))', display:'flex', alignItems:'center', justifyContent:'center', fontSize:13, fontWeight:700, color:'#fff', flexShrink:0 }}>{user?.name?.[0]?.toUpperCase()}</div>
            <div style={{ minWidth:0 }}>
              <p style={{ fontSize:13, fontWeight:600, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{user?.name}</p>
              <Badge label={user?.role} type={user?.role} />
            </div>
          </div>
          <button onClick={onLogout} style={{ width:'100%', padding:'7px', borderRadius:'var(--r)', background:'transparent', border:'1px solid var(--border)', color:'var(--muted)', fontSize:13, cursor:'pointer', fontFamily:'var(--fb)', transition:'all var(--t)' }}
            onMouseEnter={e => { e.target.style.borderColor='var(--danger)'; e.target.style.color='var(--danger)'; }}
            onMouseLeave={e => { e.target.style.borderColor='var(--border)'; e.target.style.color='var(--muted)'; }}>
            Sign out
          </button>
        </div>
      </aside>
      <main style={{ flex:1, padding:'30px 36px', overflowY:'auto', minWidth:0 }}>
        {children}
      </main>
    </div>
  );
}