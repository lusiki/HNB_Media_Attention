'use strict';
function timelineScale(rows,metric){
  const later=rows.length<35,values=rows.map(r=>metric==='gap'?r.gap*100:Number(r[metric])),maximum=Math.max(...values),minimum=Math.min(...values);
  if(metric==='share'){const hi=Math.max(later?6:18,Math.ceil(maximum/2)*2),step=hi<=8?2:6;return [0,hi,Array.from({length:Math.floor(hi/step)+1},(_,i)=>i*step)];}
  if(metric==='gap'){const lo=later?Math.min(-2,Math.floor(minimum/2)*2):Math.min(-12.5,Math.floor(minimum/4)*4);return [lo,5,later?Array.from({length:Math.floor((4-lo)/2)+1},(_,i)=>lo+i*2):[-12,-8,-4,0,4]];}
  if(['centrality','hhi'].includes(metric))return [0,1,[0,.25,.5,.75,1]];
  if(metric==='article'){const hi=Math.max(1,Math.ceil(maximum/5)*5);return [0,hi,[0,hi/3,hi*2/3,hi]];}
  return [-.7,14.5,[0,4,8,12]];
}
function timelineSVG(rows,metric,width,selected){
  const height=width<500?235:220,left=38,right=20,top=38,bottom=34;
  const pw=width-left-right,ph=height-top-bottom,later=rows.length<35;
  const scales=timelineScale(rows,metric);
  const [lo,hi,ticks]=scales,color=metric==='inflation'?'#ffb17f':'#9bc4ff';
  const ordinal=p=>Number(p.slice(0,4))*12+Number(p.slice(5,7));
  const start=ordinal(rows[0].period),end=ordinal(rows.at(-1).period);
  const x=i=>left+pw*(ordinal(rows[i].period)-start)/Math.max(1,end-start),y=v=>top+(hi-v)/(hi-lo)*ph;
  const value=r=>metric==='share'?r.share:r[metric]*(metric==='gap'?100:1);
  let svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" aria-hidden="true">`;
  ticks.forEach(t=>{svg+=`<line x1="${left}" x2="${width-right}" y1="${y(t)}" y2="${y(t)}" stroke="#6c8393" opacity="${t===0?.8:.3}" stroke-dasharray="${t===0?'4 4':'0'}"/><text x="${left-10}" y="${y(t)+4}" fill="#cedbe5" text-anchor="end" font-size="12" font-family="Segoe UI,Arial">${Number(t.toFixed(2))}</text>`;});
  const segments=[];let points=[],previous=null;
  rows.forEach((r,i)=>{const available=metric==='inflation'?r.inflation!==null:r[metric]!==null;
    if(!available||(previous!==null&&ordinal(r.period)-previous>1)){if(points.length)segments.push(points);points=[];}
    if(available)points.push(`${x(i)},${y(value(r))}`);previous=ordinal(r.period);});
  if(points.length)segments.push(points);
  segments.forEach(p=>svg+=`<polyline class="observed-series" fill="none" stroke="${color}" stroke-width="2.4" stroke-linejoin="round" points="${p.join(' ')}"/>`);
  const boundary=ordinal('2024-04');if(start<boundary&&boundary<end){const bx=left+pw*(boundary-start)/(end-start);svg+=`<line class="collection-boundary" x1="${bx}" x2="${bx}" y1="${top}" y2="${height-bottom}" stroke="#cedbe5" stroke-dasharray="5 5"/><text x="${bx+4}" y="20" fill="#cedbe5" font-size="11">04/2024</text>`;}
  const selectedIndex=rows.findIndex(r=>r.period===selected&&(metric==='inflation'?r.inflation!==null:r[metric]!==null));
  if(selectedIndex>=0){const r=rows[selectedIndex],xx=x(selectedIndex);svg+=`<g class="selected-month" data-period="${r.period}"><line x1="${xx}" x2="${xx}" y1="${top}" y2="${height-bottom}" stroke="white" opacity=".6" stroke-dasharray="2 3"/><circle cx="${xx}" cy="${y(value(r))}" r="4.5" fill="${color}" stroke="#112838" stroke-width="2"/></g>`;}
  let labels;
  if(later){
    let indices=[0,...rows.map((r,i)=>r.period.endsWith('-01')&&i>3?i:null).filter(i=>i!==null),rows.length-1];
    if(width<500)indices=[0,Math.floor(rows.length/2),rows.length-1];
    labels=indices.map(i=>({label:rows[i].period,position:x(i)}));
  }else{
    labels=Array.from({length:Number(rows.at(-1).period.slice(0,4))-Number(rows[0].period.slice(0,4))+1},(_,i)=>Number(rows[0].period.slice(0,4))+i)
      .filter((year,i)=>width>=500||i%2===0)
      .map(year=>({label:String(year),position:left+pw*(ordinal(`${year}-01`)-start)/Math.max(1,end-start)}));
  }
  labels.forEach(({label,position})=>{svg+=`<text x="${Math.min(Math.max(position,43),width-35)}" y="${height-10}" fill="#cedbe5" text-anchor="middle" font-size="12" font-family="Segoe UI,Arial">${label}</text>`;});
  return svg+'</svg>';
}
