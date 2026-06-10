import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { tasksApi } from '../api/client';
import { Spinner, Badge } from '../components/UI';

const Stat = ({ label, value, color }) => (
  <div style={{ background:'var(--bg3)', border:'1px solid var(--border)', borderRadius:'var(--rl)', padding:'18px 22px' }}>
    <p style={{ fontSize:11, color:'var(--muted)', marginBottom:8, fontWeight:600, letterSpacing:'.05em', textTransform:'uppercase' }}>{label}</p>
    <p style={{ fontFamily:'var(--fh)', fontSize:34, fontWeight:700, color: color||'var(--text)' }}>{value}</p>
  </div>
);

export default function Dashboard() {
  const { user } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [loading, setL]   = useState(true);

  useEffect(() => {
    tasksApi.list({ limit:5 }).then(r => setTasks(r.data.data.tasks)).catch(()=>{}).finally(()=>setL(false));
  }, []);

  const c = { todo:0, in_progress:0, done:0 };
  tasks.forEach(t => { if(c[t.status]!==undefined) c[t.status]++; });

  return (
    <div className="fade-in">
      <div style={{ marginBottom:28 }}>
        <h1 style={{ fontFamily:'var(--fh)', fontSize:26, fontWeight:700, marginBottom:4 }}>Hey, {user?.name?.split(' ')[0]} 👋</h1>
        <p style={{ color:'var(--muted)', fontSize:14 }}>Here's what's on your plate</p>
      </div>

      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(150px,1fr))', gap:12, marginBottom:32 }}>
        <Stat label="To do"       value={c.todo}        color="var(--muted)"    />
        <Stat label="In progress" value={c.in_progress} color="var(--warning)"  />
        <Stat label="Done"        value={c.done}        color="var(--success)"  />
      </div>

      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:14 }}>
        <h2 style={{ fontFamily:'var(--fh)', fontSize:16, fontWeight:600 }}>Recent tasks</h2>
        <Link to="/tasks" style={{ fontSize:13, color:'var(--accent)', fontWeight:500 }}>View all →</Link>
      </div>

      {loading ? <div style={{ display:'flex', justifyContent:'center', padding:40 }}><Spinner size={26}/></div>
       : tasks.length === 0
         ? <div style={{ textAlign:'center', padding:'48px 24px', border:'1px dashed var(--border)', borderRadius:'var(--rl)', color:'var(--muted)' }}>
             <p style={{ marginBottom:12 }}>No tasks yet</p>
             <Link to="/tasks" style={{ color:'var(--accent)', fontSize:14 }}>Create your first task →</Link>
           </div>
         : <div style={{ display:'flex', flexDirection:'column', gap:7 }}>
             {tasks.map(t => (
               <div key={t.id} style={{ background:'var(--bg2)', border:'1px solid var(--border)', borderRadius:'var(--r)', padding:'13px 18px', display:'flex', alignItems:'center', gap:14 }}>
                 <div style={{ flex:1, minWidth:0 }}>
                   <p style={{ fontWeight:500, fontSize:14, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{t.title}</p>
                   {t.due_date && <p style={{ fontSize:12, color:'var(--dim)', marginTop:2 }}>Due {t.due_date}</p>}
                 </div>
                 <Badge label={t.priority} type={t.priority}/>
                 <Badge label={t.status?.replace('_',' ')} type={t.status}/>
               </div>
             ))}
           </div>
      }
    </div>
  );
}