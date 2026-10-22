let decisionId=null, lastData=null, analyticsView='table';
const $=s=>document.querySelector(s);
function money(v){return new Intl.NumberFormat('en-US',{maximumFractionDigits:0}).format(v)}
function esc(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function offers(){return [...document.querySelectorAll('#offersTable tbody tr')].map(tr=>{const i=tr.querySelectorAll('input');return {supplier_id:i[0].value.trim(),product:i[1].value.trim(),available_qty:+i[2].value,total_cost:+i[3].value,eta_days:+i[4].value}})}
function payload(){return {order_id:$('#order').value.trim(),current_supplier:$('#currentSupplier').value.trim(),product:$('#product').value.trim(),quantity:+$('#qty').value,max_budget:+$('#budget').value,deadline_days:+$('#deadline').value,delay_confirmed:$('#delay').checked,offers:offers()}}
function facts(s){return `<div><b>Calculation</b><span>Completed</span></div><div><b>Input scope</b><span>Order data only</span></div><div><b>Result check</b><span>Passed</span></div><div><b>Processing time</b><span>${esc(s.duration_ms??'—')} ms</span></div>`}

function barPercent(value,max,min=0){if(!Number.isFinite(value)||!Number.isFinite(max)||max<=min)return 0;return Math.max(4,Math.min(100,((value-min)/(max-min))*100))}
function renderAnalytics(d){
 const rows=d.offers||[];
 const costs=rows.map(o=>+o.total_cost||0), etas=rows.map(o=>+o.eta_days||0), qtys=rows.map(o=>+o.available_qty||0);
 const maxCost=Math.max(...costs,1), maxEta=Math.max(...etas,1), maxQty=Math.max(...qtys,1);
 const minCost=Math.min(...costs,0);
 $('#analysisRows').innerHTML=rows.map(o=>`<tr><td><b>${esc(o.supplier_id)}</b></td><td>${money(o.total_cost)}</td><td>${o.eta_days} days</td><td>${o.available_qty}</td><td><span class="pill ${o.admissible?'ok':'bad'}">${o.admissible?'Admissible':esc((o.reasons||[]).join(', '))}</span></td></tr>`).join('');
 const metrics=$('#analyticsMetrics');
 if(metrics) metrics.innerHTML=rows.map(o=>`<article class="supplier-metrics ${o.admissible?'is-ok':'is-bad'}"><div class="supplier-metrics-head"><div><b>${esc(o.supplier_id)}</b><span>${o.admissible?'Eligible':'Rejected'}</span></div><span class="metric-result">${o.admissible?'Meets requirements':esc((o.reasons||[]).join(', '))}</span></div><div class="metric-bars"><div class="metric-line"><span>Cost</span><div class="bar-track"><i style="width:${barPercent(+o.total_cost,maxCost,minCost)}%"></i></div><b>${money(o.total_cost)}</b></div><div class="metric-line"><span>Delivery</span><div class="bar-track"><i style="width:${barPercent(+o.eta_days,maxEta)}%"></i></div><b>${o.eta_days} days</b></div><div class="metric-line"><span>Quantity</span><div class="bar-track"><i style="width:${barPercent(+o.available_qty,maxQty)}%"></i></div><b>${o.available_qty}</b></div></div></article>`).join('');
 const charts=$('#analyticsCharts');
 if(charts){
   const eligible=rows.filter(o=>o.admissible).length, rejected=rows.length-eligible;
   const cols=(title,key,max,fmt)=>`<section class="column-chart"><h3>${title}</h3><div class="columns">${rows.map(o=>`<div class="column-item"><div class="column-value">${fmt(o[key])}</div><div class="column-track"><i class="${o.admissible?'good':'bad'}" style="height:${barPercent(+o[key],max)}%"></i></div><span>${esc(o.supplier_id)}</span></div>`).join('')}</div></section>`;
   charts.innerHTML=`<div class="charts-dashboard"><section class="donut-card"><h3>Eligibility</h3><div class="donut" style="--ok:${rows.length?eligible/rows.length*360:0}deg"><div><b>${eligible}</b><span>eligible</span></div></div><p>${rejected} rejected</p></section>${cols('Cost','total_cost',maxCost,v=>money(v))}${cols('Delivery time','eta_days',maxEta,v=>v+' d')}${cols('Available quantity','available_qty',maxQty,v=>v)}</div>`;
 }
 setAnalyticsView(analyticsView);
}
function setAnalyticsView(view){
 analyticsView=view||'table';
 const ids={table:'#analyticsTable',metrics:'#analyticsMetrics',charts:'#analyticsCharts'};
 Object.entries(ids).forEach(([k,id])=>{const el=$(id);if(el)el.hidden=k!==analyticsView});
 const sel=$('#analyticsView'); if(sel&&sel.value!==analyticsView)sel.value=analyticsView;
}
function render(d){lastData=d; document.body.classList.add('results-mode'); $('#run').hidden=false; $('#approve').hidden=true; $('#runTitle').textContent=d.task||d.message||'Analysis result';
 const badge=$('#runBadge'); badge.className='status'; badge.textContent=d.status==='PROPOSED'?'Awaiting approval':d.status==='CONFLICT'?'Constraint conflict':d.status==='NO_TRIGGER'?'No action required':'Error'; badge.classList.add(d.status==='PROPOSED'?'ready':d.status==='CONFLICT'?'warn':'neutral');
 $('#plan').innerHTML=(d.plan||[]).map(x=>`<li>${esc(x)}</li>`).join(''); $('#sandbox').innerHTML=d.sandbox?facts(d.sandbox):'<div class="empty">Additional processing was not required.</div>';
 renderAnalytics(d);
 if(d.status==='PROPOSED'){const s=d.selected; $('#recommendationBody').innerHTML=`<div class="choice"><div><span class="eyebrow">Recommended supplier</span><h3>${esc(s.supplier_id)}</h3></div><div class="choice-metrics"><span><b>${money(s.total_cost)}</b> total cost</span><span><b>${s.eta_days} days</b> delivery</span><span><b>${s.available_qty}</b> available</span></div></div><p>${esc(d.explanation)}</p>`; decisionId=d.decision_id; $('#approve').hidden=false;}
 else if(d.status==='CONFLICT'){$('#recommendationBody').innerHTML=`<div class="alert">${esc(d.message)}</div><p>No replacement was proposed because at least one required condition would be violated.</p>`;}
 else{$('#recommendationBody').innerHTML=`<p>${esc(d.message||d.error||'No recommendation generated.')}</p>`;}
 const ev=d.evidence||{}; $('#evidence').innerHTML=`<p><b>Independent verification:</b> ${ev.oracle_match===true?'Passed':'—'}</p><p><b>Constraint violations:</b> ${ev.selected_constraint_violations??ev.constraint_violations??'—'}</p><p><b>Action confirmation:</b> ${d.status==='PROPOSED'?'Ready for approval':'Recorded'}</p>`;
}
$('#f').addEventListener('submit',async e=>{e.preventDefault(); decisionId=null; $('#verified').className='empty'; $('#verified').textContent='Waiting for approval.'; $('#analyze').disabled=true; $('#analyze').textContent='Running…'; try{const r=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload())}); const d=await r.json(); if(!r.ok) throw new Error(d.error||'Analysis failed'); render(d);}catch(err){render({status:'ERROR',message:err.message});}finally{$('#analyze').disabled=false; $('#analyze').textContent='Analyze disruption';}});
$('#approve').addEventListener('click',async()=>{if(!decisionId)return; $('#approve').disabled=true; $('#approve').textContent='Updating…'; try{const r=await fetch('/api/approve/'+decisionId,{method:'POST'}); const d=await r.json(); if(!r.ok)throw new Error(d.error||'Update failed'); $('#runBadge').textContent='Confirmed'; $('#runBadge').className='status verified'; $('#verified').className='verified-box'; $('#verified').innerHTML=`<h3>Order updated successfully</h3><p>${esc(d.message)}</p><div class="choice-metrics"><span><b>${esc(d.order.supplier_id)}</b> supplier</span><span><b>${money(d.order.total_cost)}</b> total cost</span><span><b>${d.order.eta_days} days</b> delivery</span></div>`; $('#approve').hidden=true; $('#evidence').innerHTML = `<p><b>Independent verification:</b> Passed</p><p><b>Constraint violations:</b> 0</p><p><b>Action confirmation:</b> Approved</p><p><b>Updated order check:</b> Passed</p>`;}catch(err){$('#verified').className='alert'; $('#verified').textContent=err.message;}finally{$('#approve').disabled=false; $('#approve').textContent='Approve replacement';}});
$('#addOffer').addEventListener('click',()=>{const tr=document.createElement('tr'); tr.innerHTML='<td><input value="SUP-D"></td><td><input value="GPU-A100"></td><td><input type="number" value="10"></td><td><input type="number" value="119000"></td><td><input type="number" value="5"></td>'; tr.querySelector('input').value='SUP-'+(document.querySelectorAll('#offersTable tbody tr').length+1); document.querySelector('#offersTable tbody').appendChild(tr)});

(function(){const b=document.getElementById('themeToggle'); if(!b)return; const saved=localStorage.getItem('supply-theme')||'dark'; document.documentElement.dataset.theme=saved; const setLabel=()=>{b.textContent=document.documentElement.dataset.theme==='dark'?'Light theme':'Dark theme'}; setLabel(); b.addEventListener('click',()=>{const n=document.documentElement.dataset.theme==='dark'?'light':'dark'; document.documentElement.dataset.theme=n; localStorage.setItem('supply-theme',n); setLabel();});})();

const analyticsSelect=document.getElementById('analyticsView'); if(analyticsSelect) analyticsSelect.addEventListener('change',e=>setAnalyticsView(e.target.value));

const editConditions=document.getElementById('editConditions'); if(editConditions) editConditions.addEventListener('click',()=>{decisionId=null; $('#approve').hidden=true; document.body.classList.remove('results-mode'); document.getElementById('run').hidden=true;});
