import React, { useCallback, useEffect, useState } from 'react';
import { api } from '../services/api';
import './FloorPlan.css';

const statuses = ['available','reserved','occupied','ordering','preparing','ready_to_bill','cleaning'];

function FloorPlan() {
  const [tables,setTables]=useState([]);
  const [orders,setOrders]=useState([]);
  const [selected,setSelected]=useState(null);
  const load=useCallback(()=>Promise.all([api.get('tables/'),api.get('orders/')]).then(([t,o])=>{setTables(t.data);setOrders(o.data)}),[]);
  useEffect(()=>{load()},[load]);
  const update=async(table,status)=>{await api.patch('tables/'+table.id+'/',{status});load();setSelected({...table,status})};
  const markClean=async(table)=>{await update(table,'available')};
  const activeOrder=(table)=>orders.find(o=>o.table===table.id&&!['completed','cancelled'].includes(o.status));
  return <div className="floor-shell">
    <header className="floor-head"><div><span>Live dining room</span><h1>Floor & tables</h1><p>One glance tells the team where every guest is in their experience.</p></div><button onClick={load}><i className="bi bi-arrow-clockwise"/> Refresh</button></header>
    <div className="floor-legend">{statuses.map(s=><span key={s}><i className={'dot '+s}/>{s.replaceAll('_',' ')}</span>)}</div>
    <div className="floor-layout">{tables.map(table=>{const order=activeOrder(table);return <button className={'table-card '+table.status} key={table.id} onClick={()=>setSelected(table)}><small>{table.area||'Main dining'}</small><strong>{table.number}</strong><span><i className="bi bi-people"/> {table.seats} seats</span>{order&&<em>Order #{order.id} · KSh {Number(order.total).toLocaleString()}</em>}</button>})}{!tables.length&&<div className="floor-empty">No tables yet. Add your first tables in Django Admin or through the Tables API.</div>}</div>
    {selected&&<aside className="table-drawer"><button className="drawer-close" onClick={()=>setSelected(null)}>×</button><span>Table</span><h2>{selected.number}</h2><p>{selected.area||'Main dining'} · {selected.seats} seats</p>{selected.status==='cleaning'&&<button className="btn btn-success w-100 mb-3" onClick={()=>markClean(selected)}><i className="bi bi-check2-circle"/> Cleaning complete · Free table</button>}<h4>Change service state</h4><div className="state-grid">{statuses.map(s=><button className={selected.status===s?'active':''} onClick={()=>update(selected,s)} key={s}>{s.replaceAll('_',' ')}</button>)}</div></aside>}
  </div>
}
export default FloorPlan;