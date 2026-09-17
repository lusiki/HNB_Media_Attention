'use strict';
const evidence=JSON.parse(document.getElementById('research-data').textContent);
const byId=id=>document.getElementById(id);
const fixed=(v,n=2)=>Number(v).toFixed(n);
const pp=(v,n=2)=>fixed(v*100,n);
const share=r=>100*(evidence.baseline.monthly-r.gap);

function chart(rows,metric,width,selected){
  const height=width<500?235:220,left=38,right=20,top=38,bottom=34;
  const pw=width-left-right,ph=height-top-bottom,later=rows.length<35;
  const scales=metric==='share'?(later?[0,6,[0,2,4,6]]:[0,18,[0,6,12,18]]):metric==='gap'?(later?[-2,5,[-2,0,2,4]]:[-12.5,5,[-12,-8,-4,0,4]]):[-.7,14.5,[0,4,8,12]];
  const [lo,hi,ticks]=scales,color=metric==='inflation'?'#ffb17f':'#9bc4ff';
  const x=i=>left+pw*i/Math.max(1,rows.length-1),y=v=>top+(hi-v)/(hi-lo)*ph;
  const value=r=>metric==='share'?share(r):r[metric]*(metric==='gap'?100:1);
  let svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" aria-hidden="true">`;
  const missing=rows.map((r,i)=>r.gap===null?i:null).filter(i=>i!==null);
  if(missing.length){const a=x(missing[0])-pw/(rows.length-1)/2,b=x(missing.at(-1))+pw/(rows.length-1)/2;svg+=`<rect x="${a}" y="${top}" width="${b-a}" height="${ph}" fill="white" opacity=".07"/>`;}
  ticks.forEach(t=>{svg+=`<line x1="${left}" x2="${width-right}" y1="${y(t)}" y2="${y(t)}" stroke="#6c8393" opacity="${t===0?.8:.3}" stroke-dasharray="${t===0?'4 4':'0'}"/><text x="${left-10}" y="${y(t)+4}" fill="#cedbe5" text-anchor="end" font-size="12" font-family="Segoe UI,Arial">${t}</text>`;});
  let paths=[],points=[],lastSource=null;
  rows.forEach((r,i)=>{if(r.gap===null){if(points.length)paths.push(points);points=[];lastSource=null;return;}if(lastSource&&r.source!==lastSource){if(points.length)paths.push(points);points=[];}points.push(`${x(i)},${y(value(r))}`);lastSource=r.source;});
  if(points.length)paths.push(points);
  paths.forEach(points=>svg+=`<polyline fill="none" stroke="${color}" stroke-width="2.4" stroke-linejoin="round" points="${points.join(' ')}"/>`);
  if(!later){const i=rows.findIndex(r=>r.period==='2024-04');if(i>=0)svg+=`<line x1="${x(i)}" x2="${x(i)}" y1="${top}" y2="${height-bottom}" stroke="#d5dfe6" stroke-dasharray="4 4"/><text x="${Math.min(x(i)+8,width-153)}" y="20" fill="#d5dfe6" font-size="12" font-family="Segoe UI,Arial">Apr 2024 · source break</text>`;}
  const selectedIndex=rows.findIndex(r=>r.period===selected&&r.gap!==null);
  if(selectedIndex>=0){const r=rows[selectedIndex],xx=x(selectedIndex);svg+=`<g class="selected-month" data-period="${r.period}"><line x1="${xx}" x2="${xx}" y1="${top}" y2="${height-bottom}" stroke="white" opacity=".6" stroke-dasharray="2 3"/><circle cx="${xx}" cy="${y(value(r))}" r="4.5" fill="${color}" stroke="#112838" stroke-width="2"/></g>`;}
  let indices=later?[0,...rows.map((r,i)=>r.period.endsWith('-01')&&i>3?i:null).filter(i=>i!==null),rows.length-1]:rows.map((r,i)=>r.period.endsWith('-01')?i:null).filter(i=>i!==null);
  if(width<500)indices=later?[0,Math.floor(rows.length/2),rows.length-1]:indices.filter((_,i)=>i%2===0);
  indices.forEach(i=>{const label=later?rows[i].period:rows[i].period.slice(0,4);svg+=`<text x="${Math.min(Math.max(x(i),43),width-35)}" y="${height-10}" fill="#cedbe5" text-anchor="middle" font-size="12" font-family="Segoe UI,Arial">${label}</text>`;});
  return svg+'</svg>';
}
function visibleRows(){return evidence.observations.filter(r=>byId('window').value==='all'||r.period>='2024-04');}
function drawCharts(){
  const rows=visibleRows(),metric=byId('metric').value,later=byId('window').value==='new',selected=byId('period').value;
  for(const [id,m] of [['gap-chart',metric],['inflation-chart','inflation']]){const el=byId(id);el.innerHTML=chart(rows,m,Math.max(280,Math.round(el.getBoundingClientRect().width)),selected);}
  byId('visibility-title').textContent=metric==='share'?'Weighted institutional visibility':'HNB attention gap';
  byId('visibility-unit').textContent=metric==='share'?'Weighted share (%) · higher means more visible':'Percentage points · higher means less visible';
  byId('gap-chart').setAttribute('aria-label',`${metric==='share'?'Weighted institutional share, higher means more visibility':'Attention gap, higher means less visibility'}. ${later?'April 2024 to May 2026':'January 2021 to May 2026, excluding January to March 2024; levels across April 2024 are not harmonised'}. Selected month ${selected}.`);
  const range=metric==='share'?(later?'0–6%':'0–18%'):(later?'−2 to +5 pp':'−12.5 to +5 pp');
  byId('chart-scope').textContent=(later?'Same collection phase; coverage composition may still vary.':'Two collection phases; levels across April 2024 are not harmonised.')+` ${later?'Focused':'Full-history'} ${metric==='share'?'share':'gap'} scale: ${range}. Scale changes with the selected view. `+(metric==='gap'?'Zero is a historical reference, not a target.':'');
  const r=evidence.observations.find(r=>r.period===selected);
  byId('period-values').textContent=`${r.period} · share ${fixed(share(r))}% · gap ${pp(r.gap)} pp · inflation ${fixed(r.inflation,1)}%`;
}
function changeWindow(){
  const previous=byId('period').value,included=visibleRows().filter(r=>r.gap!==null);
  byId('period').replaceChildren(...included.map(r=>new Option(r.period,r.period)));
  byId('period').value=included.some(r=>r.period===previous)?previous:included.at(-1).period;
  drawCharts();
}
function renderModel(){
  const r=evidence.models.find(r=>r.frequency===byId('frequency').value&&r.specification===byId('specification').value);
  byId('model-estimate').innerHTML=pp(r.estimate)+'<span> percentage points</span>';
  byId('model-ci').textContent=`95% confidence interval: ${pp(r.lo)} to ${pp(r.hi)} percentage points`;
  byId('model-note').textContent=`${r.N} fitted ${r.frequency==='weekly'?'weeks':'months'} · January 2021–May 2026, with exclusions`;
  byId('model-technical').textContent=`Sample S1 · equation ${r.specification} · segment-aware Newey–West intervals · p ${r.p<.001?'< 0.001':'= '+fixed(r.p,3)}`;
  const x=v=>30+(v*100+.1)/.6*355;
  byId('model-plot').innerHTML=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 85" aria-hidden="true"><line x1="30" x2="385" y1="34" y2="34" stroke="#a9bac6"/><line x1="${x(0)}" x2="${x(0)}" y1="13" y2="49" stroke="#4f6470" stroke-dasharray="3 3"/><line x1="${x(r.lo)}" x2="${x(r.hi)}" y1="34" y2="34" stroke="#165ce0" stroke-width="4"/><circle cx="${x(r.estimate)}" cy="34" r="5" fill="#165ce0"/><text x="30" y="70" font-size="13" fill="#4f6470">−0.1</text><text x="${x(0)}" y="70" text-anchor="middle" font-size="13" fill="#4f6470">0</text><text x="385" y="70" text-anchor="end" font-size="13" fill="#4f6470">0.5 pp</text></svg>`;
  byId('model-plot').setAttribute('aria-label',`Estimate ${pp(r.estimate)} percentage points; 95 percent confidence interval ${pp(r.lo)} to ${pp(r.hi)}.`);
}
function openEvidence(){
  const target=document.getElementById(location.hash.slice(1));
  if(target?.tagName==='DETAILS'){target.open=true;target.scrollIntoView({block:'start'});}
}
document.querySelectorAll('a[data-evidence]').forEach(a=>a.addEventListener('click',()=>{
  const target=document.querySelector(a.getAttribute('href'));
  if(target?.tagName==='DETAILS')target.open=true;
}));
window.addEventListener('hashchange',openEvidence);
byId('window').addEventListener('change',changeWindow);
byId('metric').addEventListener('change',drawCharts);
byId('period').addEventListener('change',drawCharts);
byId('frequency').addEventListener('change',renderModel);
byId('specification').addEventListener('change',renderModel);
let lastWidth=0;
new ResizeObserver(entries=>{const width=Math.round(entries[0].contentRect.width);if(width!==lastWidth){lastWidth=width;drawCharts();}}).observe(byId('gap-chart'));
changeWindow();renderModel();openEvidence();
