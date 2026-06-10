import React, { useEffect, useState, useCallback } from 'react';
import { adminApi, extractError } from '../api/client';
import { Spinner, Alert, Badge, Button } from '../components/UI';

// ── Stat card ─────────────────────────────────────────────────
const S = ({ label, value, color }) => (
  <div style={{ background:'var(--bg3)', border:'1px solid var(--border)', borderRadius:'var(--rl)', padding:'18px 22px' }}>
    <p style={{ fontSize:11, color:'var(--muted)', marginBottom:8, fontWeight:600, letterSpacing:'.05em', textTransform:'uppercase' }}>{label}</p>
    <p style={{ fontFamily:'var(--fh)', fontSize:34, fontWeight:700, color:color||'var(--text)' }}>{value}</p>
  </div>
);

// ── Admin Overview ────────────────────────────────────────────
export function AdminOverview() {
  const [stats, setStats] = useState(null);
  const [loading, setL]   = useState(true);

  useEffect(() => {
    adminApi.dashboard().then(r => setStats(r.data.data.stats)).catch(()=>{}).finally(()=>setL(false));
  }, []);

  return (
    <div className="fade-in">
      <h1 style={{ fontFamily:'var(--fh)', fontSize:24, fontWeight:700, marginBottom:6 }}>Admin overview</h1>
      <p style={{ color:'var(--muted)', fontSize:14, marginBottom:28 }}>System-wide statistics</p>
      {loading ? <div style={{ display:'flex', justifyContent:'center', padding:60 }}><Spinner size={26}/></div>
       : <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(150px,1fr))', gap:12 }}>
           <S label="Total users"  value={stats?.totalUsers} />
           <S label="Total tasks"  value={stats?.totalTasks} />
           <S label="To do"        value={stats?.tasksByStatus?.todo}        color="var(--muted)"   />
           <S label="In progress"  value={stats?.tasksByStatus?.in_progress} color="var(--warning)" />
           <S label="Done"         value={stats?.tasksByStatus?.done}        color="var(--success)" />
         </div>
      }
    </div>
  );
}

// ── Admin Users ───────────────────────────────────────────────
export function AdminUsers() {
  const [users, setUsers] = useState([]);
  const [meta, setMeta]   = useState({});
  const [page, setPage]   = useState(1);
  const [loading, setL]   = useState(true);
  const [toast, setToast] = useState(null);

  const toast_ = (msg, type='success') => { setToast({msg,type}); setTimeout(()=>setToast(null), 3000); };

  const load = useCallback(async () => {
    setL(true);
    try { const { data } = await adminApi.users({ page, limit:20 }); setUsers(data.data.users); setMeta(data.meta||{}); }
    catch { toast_('Failed to load','error'); }
    finally { setL(false); }
  }, [page]);

  useEffect(() => { load(); }, [load]);

  const toggleRole = async (u) => {
    try {
      const newRole = u.role === 'admin' ? 'user' : 'admin';
      await adminApi.updateRole(u.id, newRole);
      setUsers(us => us.map(x => x.id===u.id ? {...x, role:newRole} : x));
      toast_(`${u.name} is now ${newRole}`);
    } catch(e) { toast_(extractError(e).message, 'error'); }
  };

  const del = async (u) => {
    if (!window.confirm(`Delete ${u.name}?`)) return;
    try { await adminApi.deleteUser(u.id); setUsers(us=>us.filter(x=>x.id!==u.id)); toast_('User deleted'); }
    catch(e) { toast_(extractError(e).message,'error'); }
  };

  return (
    <div className="fade-in">
      {toast && <div style={{ position:'fixed', top:18, right:18, zIndex:2000, minWidth:260 }}><Alert type={toast.type}>{toast.msg}</Alert></div>}
      <h1 style={{ fontFamily:'var(--fh)', fontSize:24, fontWeight:700, marginBottom:6 }}>Users</h1>
      <p style={{ color:'var(--muted)', fontSize:14, marginBottom:24 }}>{meta.total||0} total accounts</p>

      {loading ? <div style={{ display:'flex', justifyContent:'center', padding:60 }}><Spinner size={26}/></div>
       : <div style={{ display:'flex', flexDirection:'column', gap:7 }}>
           {users.map(u => (
             <div key={u.id} style={{ background:'var(--bg2)', border:'1px solid var(--border)', borderRadius:'var(--r)', padding:'13px 18px', display:'flex', alignItems:'center', gap:14 }}>
               <div style={{ width:34, height:34, borderRadius:'50%', background:'linear-gradient(135deg,var(--accent),var(--purple))', display:'flex', alignItems:'center', justifyContent:'center', fontSize:13, fontWeight:700, color:'#fff', flexShrink:0 }}>{u.name?.[0]?.toUpperCase()}</div>
               <div style={{ flex:1, minWidth:0 }}>
                 <p style={{ fontWeight:500, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{u.name}</p>
                 <p style={{ fontSize:12, color:'var(--dim)', fontFamily:'var(--fm)' }}>{u.email}</p>
               </div>
               <Badge label={u.role} type={u.role}/>
               <div style={{ display:'flex', gap:6, flexShrink:0 }}>
                 <Button variant="ghost" size="sm" onClick={()=>toggleRole(u)}>{u.role==='admin'?'→ user':'→ admin'}</Button>
                 <Button variant="danger" size="sm" onClick={()=>del(u)}>Delete</Button>
               </div>
             </div>
           ))}
         </div>
      }

      {meta.totalPages > 1 && (
        <div style={{ display:'flex', gap:8, justifyContent:'center', marginTop:22 }}>
          <Button variant="secondary" size="sm" disabled={page<=1} onClick={()=>setPage(p=>p-1)}>← Prev</Button>
          <span style={{ padding:'6px 14px', fontSize:13, color:'var(--muted)' }}>Page {page} of {meta.totalPages}</span>
          <Button variant="secondary" size="sm" disabled={page>=meta.totalPages} onClick={()=>setPage(p=>p+1)}>Next →</Button>
        </div>
      )}
    </div>
  );
}

// ── Admin All Tasks ───────────────────────────────────────────
export function AdminTasks() {
  const [tasks, setTasks] = useState([]);
  const [meta, setMeta]   = useState({});
  const [page, setPage]   = useState(1);
  const [loading, setL]   = useState(true);

  const load = useCallback(async () => {
    setL(true);
    try { const { data } = await adminApi.tasks({ page, limit:20 }); setTasks(data.data.tasks); setMeta(data.meta||{}); }
    catch {}
    finally { setL(false); }
  }, [page]);

  useEffect(() => { load(); }, [load]);

  return (
    <div className="fade-in">
      <h1 style={{ fontFamily:'var(--fh)', fontSize:24, fontWeight:700, marginBottom:6 }}>All tasks</h1>
      <p style={{ color:'var(--muted)', fontSize:14, marginBottom:24 }}>{meta.total||0} across all users</p>

      {loading ? <div style={{ display:'flex', justifyContent:'center', padding:60 }}><Spinner size={26}/></div>
       : <div style={{ display:'flex', flexDirection:'column', gap:7 }}>
           {tasks.map(t => (
             <div key={t.id} style={{ background:'var(--bg2)', border:'1px solid var(--border)', borderRadius:'var(--r)', padding:'13px 18px', display:'flex', alignItems:'center', gap:14 }}>
               <div style={{ flex:1, minWidth:0 }}>
                 <p style={{ fontWeight:500, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{t.title}</p>
                 {t.user && <p style={{ fontSize:12, color:'var(--dim)', marginTop:2 }}>by {t.user.name} · {t.user.email}</p>}
               </div>
               <Badge label={t.priority} type={t.priority}/>
               <Badge label={t.status?.replace('_',' ')} type={t.status}/>
             </div>
           ))}
         </div>
      }

      {meta.totalPages > 1 && (
        <div style={{ display:'flex', gap:8, justifyContent:'center', marginTop:22 }}>
          <Button variant="secondary" size="sm" disabled={page<=1} onClick={()=>setPage(p=>p-1)}>← Prev</Button>
          <span style={{ padding:'6px 14px', fontSize:13, color:'var(--muted)' }}>Page {page} of {meta.totalPages}</span>
          <Button variant="secondary" size="sm" disabled={page>=meta.totalPages} onClick={()=>setPage(p=>p+1)}>Next →</Button>
        </div>
      )}
    </div>
  );
}