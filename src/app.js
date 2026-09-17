'use strict';
const evidence=JSON.parse(document.getElementById('research-data').textContent);
const byId=id=>document.getElementById(id);
const fixed=(v,n=2)=>Number(v).toFixed(n);
const pp=(v,n=2)=>fixed(v*100,n);

function chart(rows,metric,width){
  const height=width<500?200:210,left=36,right=15,top=36,bottom=33;
  const pw=width-left-right,ph=height-top-bottom,isGap=metric==='gap';
  const [lo,hi]=isGap?[-12.5,5]:[-.7,14.5],ticks=isGap?[-12,-8,-4,0,4]:[0,4,8,12];
  const color=isGap?'#9bc4ff':'#ffb17f',x=i=>left+pw*i/Math.max(1,rows.length-1),y=v=>top+(hi-v)/(hi-lo)*ph;
  let svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" aria-hidden="true">`;
  const missing=rows.map((r,i)=>r[metric]===null?i:null).filter(i=>i!==null);
  if(missing.length){const a=x(missing[0])-pw/(rows.length-1)/2,b=x(missing.at(-1))+pw/(rows.length-1)/2;svg+=`<rect x="${a}" y="${top}" width="${b-a}" height="${ph}" fill="white" opacity=".07"/>`;}
  ticks.forEach(t=>{svg+=`<line x1="${left}" x2="${width-right}" y1="${y(t)}" y2="${y(t)}" stroke="#6c8393" opacity="${t===0?.8:.3}" stroke-dasharray="${t===0?'4 4':'0'}"/><text x="${left-10}" y="${y(t)+4}" fill="#cedbe5" text-anchor="end" font-size="12" font-family="Segoe UI,Arial">${t}</text>`;});
  let paths=[],points=[],lastSource=null;
  rows.forEach((r,i)=>{if(r[metric]===null){if(points.length)paths.push(points);points=[];lastSource=null;return;}if(lastSource&&r.source!==lastSource){if(points.length)paths.push(points);points=[];}points.push(`${x(i)},${y(r[metric]*(isGap?100:1))}`);lastSource=r.source;});
  if(points.length)paths.push(points);
  paths.forEach(points=>svg+=`<polyline fill="none" stroke="${color}" stroke-width="2.4" stroke-linejoin="round" points="${points.join(' ')}"/>`);
  const boundary=rows.findIndex(r=>r.period==='2024-04');
  if(boundary>=0){const xx=x(boundary),label=width<500?'Apr 2024 · new source':'Apr 2024 · source change';svg+=`<line x1="${xx}" x2="${xx}" y1="${top-4}" y2="${height-bottom}" stroke="#d5dfe6" stroke-dasharray="4 4" opacity=".7"/><text x="${Math.min(xx+8,width-150)}" y="21" fill="#d5dfe6" font-size="12" font-family="Segoe UI,Arial">${label}</text>`;}
  let indices=rows.map((r,i)=>r.period.endsWith('-01')?i:null).filter(i=>i!==null);
  if(rows.length<35)indices=[0,...indices.filter(i=>i>3),rows.length-1];
  if(width<500&&rows.length>35)indices=indices.filter((_,i)=>i%2===0);
  if(width<500&&rows.length<35)indices=[0,Math.floor(rows.length/2),rows.length-1];
  indices.forEach(i=>{const label=rows.length>35?rows[i].period.slice(0,4):rows[i].period;svg+=`<text x="${Math.min(Math.max(x(i),42),width-34)}" y="${height-9}" fill="#cedbe5" text-anchor="middle" font-size="12" font-family="Segoe UI,Arial">${label}</text>`;});
  return svg+'</svg>';
}
function renderCharts(){
  const rows=evidence.observations.filter(r=>byId('window').value==='all'||r.period>='2024-04');
  for(const metric of ['gap','inflation']){const el=byId(metric+'-chart'),width=Math.max(280,Math.round(el.getBoundingClientRect().width));el.innerHTML=chart(rows,metric,width);}
  const previous=byId('period').value,included=rows.filter(r=>r.gap!==null);
  byId('period').replaceChildren(...included.map(r=>new Option(r.period,r.period)));
  byId('period').value=included.some(r=>r.period===previous)?previous:included.at(-1).period;
  inspectPeriod();
}
function inspectPeriod(){const r=evidence.observations.find(r=>r.period===byId('period').value);byId('period-values').textContent=`${r.period} · gap ${pp(r.gap)} pp · inflation ${fixed(r.inflation,1)}%`;}
function renderModel(){
  const r=evidence.models.find(r=>r.frequency===byId('frequency').value&&r.specification===byId('specification').value);
  byId('model-estimate').innerHTML=pp(r.estimate)+'<span> percentage points</span>';
  byId('model-ci').textContent=`95% confidence interval: ${pp(r.lo)} to ${pp(r.hi)} percentage points`;
  byId('model-note').textContent=`S1 · ${r.N} fitted ${r.frequency==='weekly'?'weeks':'months'} · segment-aware Newey–West intervals · p ${r.p<.001?'< 0.001':'= '+fixed(r.p,3)}`;
  const x=v=>25+v*100/.5*360;
  byId('model-plot').innerHTML=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 80" aria-hidden="true"><line x1="25" x2="385" y1="34" y2="34" stroke="#a9bac6"/><line x1="${x(r.lo)}" x2="${x(r.hi)}" y1="34" y2="34" stroke="#165ce0" stroke-width="4"/><circle cx="${x(r.estimate)}" cy="34" r="5" fill="#165ce0"/><text x="25" y="65" font-size="13" fill="#4f6470">0</text><text x="385" y="65" text-anchor="end" font-size="13" fill="#4f6470">0.5 pp</text></svg>`;
  byId('model-plot').setAttribute('aria-label',`Estimate ${pp(r.estimate)} percentage points; 95 percent confidence interval ${pp(r.lo)} to ${pp(r.hi)}.`);
}
byId('window').addEventListener('change',renderCharts);
byId('period').addEventListener('change',inspectPeriod);
byId('frequency').addEventListener('change',renderModel);
byId('specification').addEventListener('change',renderModel);
let lastWidth=0;
new ResizeObserver(entries=>{const width=Math.round(entries[0].contentRect.width);if(width!==lastWidth){lastWidth=width;renderCharts();}}).observe(byId('gap-chart'));
renderCharts();renderModel();
