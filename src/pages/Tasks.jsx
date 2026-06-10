import React, { useState, useEffect, useCallback } from 'react';
import { tasksApi, extractError } from '../api/client';
import { Button, Alert, Badge, Spinner, FormField } from '../components/UI';

const STATUSES   = ['todo','in_progress','done'];
const PRIORITIES = ['low','medium','high'];

function Modal({ task, onClose, onSaved }) {
  const editing = !!task?.id;
  const [form, setF] = useState({ title:task?.title||'', description:task?.description||'', status:task?.status||'todo', priority:task?.priority||'medium', due_date:task?.due_date||'' });
  const [err, setErr] = useState('');
  const [fe, setFe]   = useState({});
  const [loading, setL] = useState(false);
  const s = k => e => setF({...form,[k]:e.target.value});

  const submit = async e => {
    e.preventDefault(); setErr(''); setFe({}); setL(true);
    try {
      const p = { ...form, due_date: form.due_date||null };
      if (editing) await tasksApi.update(task.id, p); else await tasksApi.create(p);
      onSaved(); onClose();
    } catch(e) { const {message,fields}=extractError(e); setErr(message); setFe(fields); }
    finally { setL(false); }
  };

  return (
    <div style={{ position:'fixed', inset:0, background:'rgba(0,0,0,.75)', display:'flex', alignItems:'center', justifyContent:'center', zIndex:1000, padding:16 }} onClick={e=>e.target===e.currentTarget&&onClose()}>
      <div style={{ background:'var(--bg2)', border:'1px solid var(--border)', borderRadius:'var(--rl)', padding:30, width:'100%', maxWidth:480 }} className="fade-in">
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:22 }}>
          <h2 style={{ fontFamily:'var(--fh)', fontSize:19, fontWeight:700 }}>{editing ? 'Edit task' : 'New task'}</h2>
          <button onClick={onClose} style={{ background:'none', border:'none', color:'var(--muted)', fontSize:22, cursor:'pointer', lineHeight:1 }}>×</button>
        </div>
        {err && <Alert type="error" onClose={()=>setErr('')}>{err}</Alert>}
        <form onSubmit={submit}>
          <FormField label="Title *" error={fe.title}><input value={form.title} onChange={s('title')} placeholder="Task title" required /></FormField>
          <FormField label="Description" error={fe.description}><textarea value={form.description} onChange={s('description')} placeholder="Optional…" rows={3} style={{ resize:'vertical' }}/></FormField>
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:12 }}>
            <FormField label="Status"><select value={form.status} onChange={s('status')}>{STATUSES.map(s=><option key={s} value={s}>{s.replace('_',' ')}</option>)}</select></FormField>
            <FormField label="Priority"><select value={form.priority} onChange={s('priority')}>{PRIORITIES.map(p=><option key={p} value={p}>{p}</option>)}</select></FormField>
          </div>
          <FormField label="Due date"><input type="date" value={form.due_date} onChange={s('due_date')}/></FormField>
          <div style={{ display:'flex', gap:9, justifyContent:'flex-end', marginTop:6 }}>
            <Button variant="secondary" type="button" onClick={onClose}>Cancel</Button>
            <Button type="submit" loading={loading}>{editing ? 'Save changes' : 'Create task'}</Button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [meta, setMeta]   = useState({});
  const [loading, setL]   = useState(true);
  const [modal, setModal] = useState(null);
  const [filters, setFilters] = useState({ status:'', priority:'', page:1 });
  const [toast, setToast] = useState(null);
  const [deleting, setDel]= useState(null);

  const toast_ = (msg, type='success') => { setToast({msg,type}); setTimeout(()=>setToast(null), 3000); };

  const load = useCallback(async () => {
    setL(true);
    try {
      const p = { page:filters.page, limit:15 };
      if (filters.status)   p.status   = filters.status;
      if (filters.priority) p.priority = filters.priority;
      const { data } = await tasksApi.list(p);
      setTasks(data.data.tasks); setMeta(data.meta||{});
    } catch { toast_('Failed to load tasks','error'); }
    finally { setL(false); }
  }, [filters]);

  useEffect(() => { load(); }, [load]);

  const del = async id => {
    setDel(id);
    try { await tasksApi.remove(id); setTasks(t=>t.filter(x=>x.id!==id)); toast_('Task deleted'); }
    catch(e) { toast_(extractError(e).message,'error'); }
    finally { setDel(null); }
  };

  return (
    <div className="fade-in">
      {toast && <div style={{ position:'fixed', top:18, right:18, zIndex:2000, minWidth:260 }}><Alert type={toast.type}>{toast.msg}</Alert></div>}
      {modal !== null && <Modal task={modal==='new'?null:modal} onClose={()=>setModal(null)} onSaved={()=>{ load(); toast_(modal==='new'?'Task created!':'Task updated!'); }}/>}

      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:22 }}>
        <div>
          <h1 style={{ fontFamily:'var(--fh)', fontSize:24, fontWeight:700 }}>My tasks</h1>
          <p style={{ color:'var(--muted)', fontSize:13, marginTop:2 }}>{meta.total||0} total</p>
        </div>
        <Button onClick={()=>setModal('new')}>+ New task</Button>
      </div>

      <div style={{ display:'flex', gap:9, marginBottom:18, flexWrap:'wrap' }}>
        {[{k:'status',opts:STATUSES},{k:'priority',opts:PRIORITIES}].map(({k,opts})=>(
          <select key={k} value={filters[k]} onChange={e=>setFilters({...filters,[k]:e.target.value,page:1})} style={{ width:'auto', padding:'7px 12px', fontSize:13 }}>
            <option value="">All {k}s</option>
            {opts.map(o=><option key={o} value={o}>{o.replace('_',' ')}</option>)}
          </select>
        ))}
        {(filters.status||filters.priority) && <Button variant="ghost" size="sm" onClick={()=>setFilters({status:'',priority:'',page:1})}>Clear</Button>}
      </div>

      {loading
        ? <div style={{ display:'flex', justifyContent:'center', padding:60 }}><Spinner size={26}/></div>
        : tasks.length===0
          ? <div style={{ textAlign:'center', padding:'56px 24px', border:'1px dashed var(--border)', borderRadius:'var(--rl)', color:'var(--muted)' }}>
              <p style={{ marginBottom:14 }}>No tasks found</p>
              <Button onClick={()=>setModal('new')}>Create your first task</Button>
            </div>
          : <div style={{ display:'flex', flexDirection:'column', gap:7 }}>
              {tasks.map(t=>(
                <div key={t.id} style={{ background:'var(--bg2)', border:'1px solid var(--border)', borderRadius:'var(--r)', padding:'14px 18px', display:'flex', alignItems:'center', gap:14, transition:'border-color var(--t)' }}
                  onMouseEnter={e=>e.currentTarget.style.borderColor='var(--border2)'}
                  onMouseLeave={e=>e.currentTarget.style.borderColor='var(--border)'}
                >
                  <div style={{ flex:1, minWidth:0 }}>
                    <p style={{ fontWeight:500, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{t.title}</p>
                    {t.due_date && <span style={{ fontSize:12, color:'var(--dim)', fontFamily:'var(--fm)' }}>Due {t.due_date}</span>}
                  </div>
                  <Badge label={t.priority} type={t.priority}/>
                  <Badge label={t.status?.replace('_',' ')} type={t.status}/>
                  <div style={{ display:'flex', gap:6, flexShrink:0 }}>
                    <Button variant="ghost" size="sm" onClick={()=>setModal(t)}>Edit</Button>
                    <Button variant="danger" size="sm" loading={deleting===t.id} onClick={()=>del(t.id)}>Delete</Button>
                  </div>
                </div>
              ))}
            </div>
      }

      {meta.totalPages > 1 && (
        <div style={{ display:'flex', gap:8, justifyContent:'center', marginTop:22 }}>
          <Button variant="secondary" size="sm" disabled={filters.page<=1} onClick={()=>setFilters({...filters,page:filters.page-1})}>← Prev</Button>
          <span style={{ padding:'6px 14px', fontSize:13, color:'var(--muted)' }}>Page {filters.page} of {meta.totalPages}</span>
          <Button variant="secondary" size="sm" disabled={filters.page>=meta.totalPages} onClick={()=>setFilters({...filters,page:filters.page+1})}>Next →</Button>
        </div>
      )}
    </div>
  );
}