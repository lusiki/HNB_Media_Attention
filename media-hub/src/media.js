'use strict';
(()=>{
 const data=JSON.parse(document.getElementById('media-data').textContent),hr=document.documentElement.lang==='hr',t=(a,b)=>hr?b:a;
 const byId=id=>document.getElementById(id),fmt=(n,d=0)=>n==null?'—':new Intl.NumberFormat(hr?'hr-HR':'en-GB',{maximumFractionDigits:d,minimumFractionDigits:d}).format(n);
 const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const periods=data.monthly.map(r=>r.period),sources=['all','stable',...data.selector_sources];
 const defaults={from:periods[0],to:data.summary.last_full_period,source:'all',metric:'count',sort:'count'};
 function validate(input){const s={...defaults,...input};for(const k of ['from','to'])if(!periods.includes(s[k]))s[k]=defaults[k];if(s.from>s.to)[s.from,s.to]=[s.to,s.from];if(!sources.includes(s.source))s.source='all';if(!['count','rate'].includes(s.metric))s.metric='count';if(!['count','name'].includes(s.sort))s.sort='count';return s;}
 function fromURL(){const p=new URL(location.href).searchParams;return validate(Object.fromEntries(Object.keys(defaults).filter(k=>p.has('m_'+k)).map(k=>[k,p.get('m_'+k)])));}
 let state=fromURL(),returnFocus=null;const announce=s=>byId('media-announcement').textContent=s;
 function url(){const u=new URL(location.href);Object.entries(state).forEach(([k,v])=>u.searchParams.set('m_'+k,v));return u;}
 function save(push=true){history[push?'pushState':'replaceState'](null,'',url());}
 function selectedRows(){return data.monthly.filter(r=>r.period>=state.from&&r.period<=state.to).map(r=>{
   if(state.source==='all')return {...r,n:r.hnb_count,h:r.hnb_i,b:r.background_i,rate:r.rate_per_10000};
   if(state.source==='stable')return {...r,n:r.stable_hnb_count,h:r.stable_hnb_i,b:r.stable_background_i,rate:r.stable_rate_per_10000};
   const d=data.source_monthly.find(x=>x.source_id===state.source&&x.period===r.period);
   return {...r,n:d?d.hnb_count:null,h:d?d.hnb_i:null,b:d?d.background_i:null,rate:d?.background_i?d.hnb_i/d.background_i*10000:null,coverage_state:d?(r.coverage_state==='partial'?'partial':'source_observed'):'unavailable'};
 });}
 const sourceLabel=()=>state.source==='all'?t('All eligible sources','Svi prihvatljivi izvori'):state.source==='stable'?t('Sources observed in every full month','Izvori opaženi u svakom punom mjesecu'):state.source;
 const metricLabel=()=>state.metric==='count'?t('Publications containing explicit HNB mentions','Objave s izričitim spominjanjem HNB-a'):t('Per 10,000 monitored query-eligible publications','Na 10.000 praćenih objava koje prolaze filtar');
 function svg(rows,width=1000,height=340){
   const left=width<500?48:62,right=20,top=40,bottom=44,ordinal=p=>Number(p.slice(0,4))*12+Number(p.slice(5,7)),start=ordinal(rows[0].period),end=ordinal(rows.at(-1).period);
   const value=r=>state.metric==='count'?r.n:r.rate,vals=rows.map(value).filter(v=>v!==null),maximum=Math.max(1,...vals),step=10**Math.floor(Math.log10(maximum)),upper=state.metric==='count'?Math.max(4,Math.ceil((Math.ceil(maximum/step)*step)/4)*4):Math.ceil(maximum/step)*step;
   const x=p=>left+(width-left-right)*(ordinal(p)-start)/Math.max(1,end-start),y=v=>top+(height-top-bottom)*(1-v/upper);
   let out=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(metricLabel())}"><title>${esc(metricLabel())}</title><rect width="100%" height="100%" fill="white"/>`;
   for(let j=0;j<5;j++){const v=upper*j/4,yy=y(v);out+=`<line x1="${left}" x2="${width-right}" y1="${yy}" y2="${yy}" stroke="#dce4ea"/><text x="${left-8}" y="${yy+5}" text-anchor="end" font-family="Arial" font-size="12" fill="#4f6470">${fmt(v,Number.isInteger(v)?0:2)}</text>`;}
   const segments=[];let points=[];for(const r of rows){const v=value(r);if(v===null){if(points.length)segments.push(points);points=[];}else points.push(`${x(r.period)},${y(v)}`);}if(points.length)segments.push(points);
   for(const p of segments)out+=`<polyline class="media-observed-series" points="${p.join(' ')}" fill="none" stroke="#165ce0" stroke-width="3" stroke-linejoin="round"/>`;
   const boundary=ordinal('2024-01');if(start<boundary&&boundary<end){const xx=x('2024-01');out+=`<line class="media-boundary" x1="${xx}" x2="${xx}" y1="${top}" y2="${height-bottom}" stroke="#4f6470" stroke-dasharray="5 5"/><text x="${Math.min(width-70,xx+5)}" y="22" font-family="Arial" font-size="12" fill="#4f6470">01/2024</text>`;}
   for(const r of rows)if(value(r)!==null&&r.coverage_state==='partial')out+=`<circle class="partial-period" cx="${x(r.period)}" cy="${y(value(r))}" r="5" fill="white" stroke="#165ce0" stroke-width="2"/>`;
   let labels=rows.filter((r,i)=>r.period.endsWith('-01')&&i>0);if(rows.length<15)labels=rows.length===1?[rows[0]]:[rows[0],rows.at(-1)];else if(width<500)labels=labels.filter((r,i)=>i%2===0);
   labels.forEach(r=>out+=`<text x="${Math.max(45,Math.min(width-35,x(r.period)))}" y="${height-12}" text-anchor="middle" font-family="Arial" font-size="12" fill="#4f6470">${rows.length<15?r.period:r.period.slice(0,4)}</text>`);
   if(rows.length===1&&value(rows[0])!==null)out+=`<circle cx="${x(rows[0].period)}" cy="${y(value(rows[0]))}" r="4" fill="#165ce0"/>`;
   return out+'</svg>';
 }
 function table(rows){return rows.map(r=>`<tr><th scope="row">${r.period}${r.coverage_state==='partial'?' *':''}</th><td class="num">${fmt(r.n)}</td><td class="num">${fmt(r.h)}</td><td class="num">${fmt(r.b)}</td><td class="num">${fmt(r.rate,2)}</td></tr>`).join('');}
 function render(){
   Object.keys(defaults).forEach(k=>{if(byId('media-'+k))byId('media-'+k).value=state[k];});
   const rows=selectedRows(),total=rows.reduce((n,r)=>n+(r.n??0),0),available=rows.some(r=>state.metric==='rate'?r.rate!==null:r.n!==null);
   byId('media-view-status').textContent=`${sourceLabel()} · ${state.from}–${state.to} · ${fmt(total)} ${t('observed publications','opaženih objava')}`;
   byId('media-chart').innerHTML=svg(rows,Math.max(310,Math.min(1100,byId('media-chart').clientWidth)));
   byId('media-numeric-rows').innerHTML=table(rows);byId('media-empty').hidden=available&&total!==0;
   byId('media-empty').textContent=available?t('No publications in the selected set.','Nema objava u odabranom skupu.'):t('Data are unavailable for the selected view.','Podaci nisu dostupni za odabrani prikaz.');
   byId('media-chart-label').textContent=metricLabel();
   byId('media-selected-note').textContent=t('Record dates; source eligibility is fixed to this release. January 2024 changes collection and filtering. Observed counts do not establish a national attention trend.','Datumi zapisa; prihvatljivost izvora određena je ovim izdanjem. U siječnju 2024. mijenjaju se prikupljanje i filtriranje. Opaženi brojevi ne utvrđuju nacionalni trend pozornosti.')+(state.to==='2026-09'?' '+t('September is partial through the 10th; the hollow point marks it.','Rujan je djelomičan, do 10. dana; označen je praznim kružićem.'):'')+(state.metric==='rate'?' '+t('Numerator and denominator both pass the same i filter. This is a monitored-archive rate.','Brojnik i nazivnik prolaze isti filtar i. Stopa opisuje praćeni arhiv.'):'');
   const grouped=new Map();for(const d of data.source_monthly)if(d.period>=state.from&&d.period<=state.to){grouped.set(d.source_id,(grouped.get(d.source_id)||0)+d.hnb_count);}
   let entries=[...grouped].filter(([id,n])=>n>0);entries.sort(state.sort==='name'?(a,b)=>a[0].localeCompare(b[0]):(a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]));
   const sourceTotal=entries.reduce((s,r)=>s+r[1],0);
   byId('media-source-rows').innerHTML=entries.slice(0,25).map(([id,n])=>`<tr><th scope="row">${esc(id)}</th><td class="num">${fmt(n)}</td><td class="num">${fmt(100*n/sourceTotal,2)}%</td></tr>`).join('');
   byId('media-source-scope').textContent=`${state.from}–${state.to} · ${fmt(entries.length)} ${t('observed sources','opaženih izvora')} · ${t('all eligible sources; first 25 shown','svi prihvatljivi izvori; prikazano prvih 25')}`;
   const language=new URL(hr?'index.html':'hr.html',location.href);language.search=url().search;language.hash=location.hash;byId('media-language').href=language.href;
 }
 function download(text,type,name){const u=URL.createObjectURL(new Blob([text],{type})),a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);announce(t('Download prepared.','Preuzimanje je pripremljeno.'));}
 document.querySelectorAll('[data-media-js]').forEach(e=>e.hidden=false);
 Object.keys(defaults).forEach(k=>byId('media-'+k)?.addEventListener('change',e=>{state=validate({...state,[k]:e.target.value});save();render();}));
 byId('media-reset').addEventListener('click',()=>{state={...defaults};save();render();announce(t('Default view restored.','Vraćen je početni prikaz.'));});
 byId('media-copy').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(url().href);announce(t('Link copied.','Poveznica je kopirana.'));}catch{const f=byId('media-copy-fallback');f.hidden=false;f.value=url().href;f.focus();f.select();}});
 byId('media-export-csv').addEventListener('click',()=>{const rows=selectedRows(),keys=['period','source','hnb_count','hnb_i','background_i','rate_per_10000','coverage_state','denominator_id','data_version','method_version','presentation_version'];
   const records=rows.map(r=>[r.period,state.source,r.n,r.h,r.b,r.rate,r.coverage_state,'AEM_web_query_i_publications_v1',data.release.data_version,data.release.method_version,data.presentation_version]);
   const cell=v=>'"'+String(v??'').replace(/"/g,'""')+'"';download([keys,...records].map(r=>r.map(cell).join(',')).join('\r\n'),'text/csv;charset=utf-8','hnb-media-selected.csv');});
 byId('media-export-svg').addEventListener('click',()=>{let out=svg(selectedRows(),1100,340).replace('<svg ','<svg width="1100" height="440" ').replace('viewBox="0 0 1100 340"','viewBox="0 0 1100 440"');
   out=out.replace('</svg>',`<text x="62" y="370" font-family="Arial" font-size="16" fill="#112838">${esc(metricLabel())}</text><text x="62" y="398" font-family="Arial" font-size="13" fill="#4f6470">${esc(sourceLabel())} · ${state.from}–${state.to} · HNB_MEDIA ${data.release.data_version}</text><text x="62" y="423" font-family="Arial" font-size="12" fill="#4f6470">${esc(t('01/2024 collection change; September 2026 partial. Counts describe the monitored sample.','01/2024 promjena prikupljanja; rujan 2026. djelomičan. Brojevi opisuju praćeni uzorak.'))}</text><metadata>${esc(JSON.stringify({state,release:data.release,presentation:data.presentation_version,denominator:'AEM_web_query_i_publications_v1'}))}</metadata></svg>`);download(out,'image/svg+xml;charset=utf-8','hnb-media-selected.svg');});
 byId('media-definition-open').addEventListener('click',()=>{returnFocus=document.activeElement;byId('media-definition').showModal();});
 byId('media-definition-close').addEventListener('click',()=>byId('media-definition').close());byId('media-definition').addEventListener('close',()=>returnFocus?.focus({preventScroll:true}));
 byId('media-definition').addEventListener('keydown',event=>{if(event.key==='Tab'){event.preventDefault();byId('media-definition-close').focus();}});
 addEventListener('popstate',()=>{state=fromURL();render();});let resize;addEventListener('resize',()=>{clearTimeout(resize);resize=setTimeout(render,120);});
 const observer=new IntersectionObserver(entries=>{for(const e of entries)if(e.isIntersecting){document.querySelectorAll('.contents a').forEach(a=>a.removeAttribute('aria-current'));document.querySelector(`.contents a[href="#${e.target.id}"]`)?.setAttribute('aria-current','location');}},{rootMargin:'-15% 0px -65% 0px'});document.querySelectorAll('main>.section').forEach(e=>observer.observe(e));
 save(false);render();
})();
