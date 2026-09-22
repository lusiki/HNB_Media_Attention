'use strict';
(()=>{
 const data=JSON.parse(document.getElementById('media-data').textContent),hr=document.documentElement.lang==='hr',t=(a,b)=>hr?b:a;
 const byId=id=>document.getElementById(id),fmt=(n,d=0)=>n==null?'—':new Intl.NumberFormat(hr?'hr-HR':'en-GB',{maximumFractionDigits:d,minimumFractionDigits:d}).format(n);
 const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const periods=data.monthly.map(r=>r.period),sources=['all','stable',...data.selector_sources];
 const defaults={from:periods[0],to:data.summary.last_full_period,source:'all',metric:'count',sort:'count'};
 function validate(input){const s={...defaults,...input};for(const k of ['from','to'])if(!periods.includes(s[k]))s[k]=defaults[k];if(s.from>s.to)[s.from,s.to]=[s.to,s.from];if(!sources.includes(s.source))s.source='all';if(!['count','rate','title','breadth'].includes(s.metric))s.metric='count';if(!['count','name','rate'].includes(s.sort))s.sort='count';return s;}
 function fromURL(){const p=new URL(location.href).searchParams;return validate(Object.fromEntries(Object.keys(defaults).filter(k=>p.has('m_'+k)).map(k=>[k,p.get('m_'+k)])));}
 let state=fromURL(),returnFocus=null;const announce=s=>byId('media-announcement').textContent=s;
 function url(){const u=new URL(location.href);Object.entries(state).forEach(([k,v])=>u.searchParams.set('m_'+k,v));return u;}
 function save(push=true){history[push?'pushState':'replaceState'](null,'',url());}
 const panel=new Set(data.extensions.panel);
 const inPopulation=r=>state.source==='all'||(state.source==='stable'?panel.has(r.source_id):r.source_id===state.source);
 function selectedRows(){return data.monthly.filter(r=>r.period>=state.from&&r.period<=state.to).map(r=>{
   const rs=data.source_monthly.filter(x=>x.period===r.period&&inPopulation(x)),sum=k=>rs.reduce((a,x)=>a+x[k],0);
   const n=rs.length?sum('hnb_count'):null,h=rs.length?sum('hnb_i'):null,b=rs.length?sum('background_i'):null;
   const titles=rs.length?sum('title_mention_count'):null,domains=rs.filter(x=>x.hnb_count>0).length,backgroundDomains=rs.filter(x=>x.background_count>0).length;
   return {...r,n,h,b,rate:b?h/b*10000:null,titles,domains:rs.length?domains:null,backgroundDomains:rs.length?backgroundDomains:null,title:n?100*titles/n:null,breadth:backgroundDomains?100*domains/backgroundDomains:null,coverage_state:rs.length?r.coverage_state:'unavailable'};
 });}
 const sourceLabel=()=>state.source==='all'?t('All eligible sources','Svi prihvatljivi izvori'):state.source==='stable'?t('Sources observed in every full month','Izvori opaženi u svakom punom mjesecu'):state.source;
 const metricLabel=(metric=state.metric)=>({count:t('Publications containing explicit HNB mentions','Objave s izričitim spominjanjem HNB-a'),rate:t('Per 10,000 monitored query-eligible publications','Na 10.000 praćenih objava koje prolaze filtar'),title:t('Title matches / HNB publications (%)','Podudaranja u naslovu / objave o HNB-u (%)'),breadth:t('HNB domains / observed background domains (%)','HNB domene / opažene pozadinske domene (%)')})[metric];
 function svg(rows,width=1000,height=340,metric=state.metric,ceiling=null){
   if(!rows.length)return `<p>${t('No complete months in this selection.','U odabiru nema potpunih mjeseci.')}</p>`;
   const left=width<500?48:62,right=20,top=40,bottom=44,ordinal=p=>Number(p.slice(0,4))*12+Number(p.slice(5,7)),start=ordinal(rows[0].period),end=ordinal(rows.at(-1).period);
   const value=r=>metric==='count'?r.n:r[metric],vals=rows.map(value).filter(v=>v!==null),maximum=Math.max(1,...vals),step=10**Math.floor(Math.log10(maximum)),upper=ceiling??(metric==='count'?Math.max(4,Math.ceil((Math.ceil(maximum/step)*step)/4)*4):Math.ceil(maximum/step)*step);
   const x=p=>left+(width-left-right)*(ordinal(p)-start)/Math.max(1,end-start),y=v=>top+(height-top-bottom)*(1-v/upper);
   let out=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(metricLabel(metric))}"><title>${esc(metricLabel(metric))}</title><rect width="100%" height="100%" fill="white"/>`;
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
 function table(rows){return rows.map(r=>`<tr><th scope="row">${r.period}${r.coverage_state==='partial'?' *':''}</th>${[fmt(r.n),fmt(r.h),fmt(r.b),fmt(r.rate,2),fmt(r.titles),fmt(r.title,2),fmt(r.domains),fmt(r.backgroundDomains),fmt(r.breadth,2)].map(v=>`<td class="num">${v}</td>`).join('')}</tr>`).join('');}
 function sourceEntries(){
   const grouped=new Map();for(const r of data.source_monthly)if(r.period>=state.from&&r.period<=state.to){
     const v=grouped.get(r.source_id)||{id:r.source_id,n:0,h:0,b:0};v.n+=r.hnb_count;v.h+=r.hnb_i;v.b+=r.background_i;grouped.set(r.source_id,v);
   }
   const entries=[...grouped.values()].map(r=>({...r,rate:r.b?10000*r.h/r.b:null,eligible:r.b>=5000&&r.h>=50,rank:null}));
   entries.filter(r=>r.eligible).sort((a,b)=>b.rate-a.rate||a.id.localeCompare(b.id)).forEach((r,i)=>r.rank=i+1);
   entries.sort(state.sort==='name'?(a,b)=>a.id.localeCompare(b.id):state.sort==='rate'?(a,b)=>(a.rank??Infinity)-(b.rank??Infinity)||b.n-a.n||a.id.localeCompare(b.id):(a,b)=>b.n-a.n||a.id.localeCompare(b.id));return entries;
 }
 function renderExtensions(rows){
   const selected=data.source_monthly.filter(r=>r.period>=state.from&&r.period<=state.to&&inPopulation(r)),counts=new Map();
   for(const r of selected)counts.set(r.source_id,(counts.get(r.source_id)||0)+r.hnb_count);
   const positive=[...counts.values()].filter(n=>n>0).sort((a,b)=>b-a),total=positive.reduce((a,b)=>a+b,0),eff=total?total*total/positive.reduce((s,n)=>s+n*n,0):null;
   const bg=new Set(selected.filter(r=>r.background_count>0).map(r=>r.source_id)).size,titles=selected.reduce((s,r)=>s+r.title_mention_count,0);
   byId('extension-scope').textContent=`${sourceLabel()} · ${state.from}–${state.to} · ${t('All HNB contributors; no ranking threshold.','Svi izvori s HNB objavama; bez praga za rangiranje.')}`;
   const values=[['V5',t('Effective domains','Efektivni broj domena'),fmt(eff,2),`${t('Top five / top ten','Prvih pet / prvih deset')}: ${fmt(total?100*positive.slice(0,5).reduce((a,b)=>a+b,0)/total:null,2)}% / ${fmt(total?100*positive.slice(0,10).reduce((a,b)=>a+b,0)/total:null,2)}%. ${t('Domain concentration; ownership and viewpoint diversity are not measured.','Koncentracija domena; vlasništvo i raznolikost stavova nisu izmjereni.')}`],['V6',t('Outlet breadth','Obuhvat izvora'),`${fmt(positive.length)} / ${fmt(bg)}`,`${fmt(bg?100*positive.length/bg:null,2)}%. ${t('Union of domains across selected months. Background domains are observed under the original background-count definition.','Unija domena kroz odabrane mjesece. Pozadinske domene opažene su prema izvornoj definiciji broja pozadinskih objava.')}`],['V7',t('Title-match share','Udio podudaranja u naslovu'),`${fmt(total?100*titles/total:null,2)}%`,`${fmt(titles)} / ${fmt(total)}. ${t('Mechanical title matches; substantive prominence is not validated.','Mehanička podudaranja u naslovu; sadržajna istaknutost nije validirana.')}`]];
   byId('extension-cards').innerHTML=values.map(([id,title,value,note])=>`<article id="${id}"><span class="claim-id">${id}</span><h3>${title}</h3><strong class="indicator-value">${value}</strong><p>${note}</p></article>`).join('');
   const all=data.extensions.monthly.filter(r=>r.scope==='all'&&r.period>=state.from&&r.period<=state.to),stable=all.map(r=>data.extensions.monthly.find(s=>s.scope==='stable'&&s.period===r.period));
   const variants=[all.map(r=>({...r,rate:r.rate_per_10000})),stable.map(r=>({...r,rate:r.rate_per_10000})),stable.map(r=>({...r,rate:r.fixed_weight_rate}))];
   const max=Math.max(1,...variants.flat().map(r=>r.rate??0)),ceiling=Math.ceil(max/10)*10,width=Math.max(310,Math.min(1100,byId('composition-chart').clientWidth));
   let drawing=svg(variants[0],width,340,'rate',ceiling).replaceAll('class="media-observed-series"','class="composition-series-0"');
   if(all.length){for(const [i,color,dash] of [[1,'#b45309','8 4'],[2,'#087d70','3 3']]){
     const layer=svg(variants[i],width,340,'rate',ceiling).match(/<(?:polyline|circle)\b[^>]*>/g)||[];
     drawing=drawing.replace('</svg>',layer.join('').replaceAll('#165ce0',color).replaceAll('class="media-observed-series"',`class="composition-series-${i}" stroke-dasharray="${dash}"`)+'</svg>');
   }}
   byId('composition-chart').innerHTML=drawing;
   byId('composition-rows').innerHTML=all.map((r,i)=>`<tr><th scope="row">${r.period}</th><td>${fmt(r.rate_per_10000,2)}</td><td>${fmt(stable[i].rate_per_10000,2)}</td><td>${fmt(stable[i].fixed_weight_rate,2)}</td></tr>`).join('');
 }
 function render(){
   Object.keys(defaults).forEach(k=>{if(byId('media-'+k))byId('media-'+k).value=state[k];});
   const rows=selectedRows(),total=rows.reduce((n,r)=>n+(r.n??0),0),available=rows.some(r=>(state.metric==='count'?r.n:r[state.metric])!==null);
   byId('media-view-status').textContent=`${sourceLabel()} · ${state.from}–${state.to} · ${fmt(total)} ${t('observed publications','opaženih objava')}`;
   byId('media-chart').innerHTML=svg(rows,Math.max(310,Math.min(1100,byId('media-chart').clientWidth)));
   byId('media-numeric-rows').innerHTML=table(rows);byId('media-empty').hidden=available&&total!==0;
   byId('media-empty').textContent=available?t('No publications in the selected set.','Nema objava u odabranom skupu.'):t('Data are unavailable for the selected view.','Podaci nisu dostupni za odabrani prikaz.');
   byId('media-chart-label').textContent=metricLabel();
   byId('media-selected-note').textContent=t('Record dates; source eligibility is fixed to this release. January 2024 changes collection and filtering. Observed counts do not establish a national attention trend.','Datumi zapisa; prihvatljivost izvora određena je ovim izdanjem. U siječnju 2024. mijenjaju se prikupljanje i filtriranje. Opaženi brojevi ne utvrđuju nacionalni trend pozornosti.')+(state.to==='2026-09'?' '+t('September is partial through the 10th; the hollow point marks it.','Rujan je djelomičan, do 10. dana; označen je praznim kružićem.'):'')+(state.metric==='rate'?' '+t('Numerator and denominator both pass the same i filter. This is a monitored-archive rate.','Brojnik i nazivnik prolaze isti filtar i. Stopa opisuje praćeni arhiv.'):'');
   const entries=sourceEntries(),sourceTotal=entries.reduce((s,r)=>s+r.n,0);
   byId('media-source-rows').innerHTML=entries.slice(0,25).map(r=>`<tr><th scope="row">${esc(r.id)}</th><td class="num">${fmt(r.n)}</td><td class="num">${fmt(sourceTotal?100*r.n/sourceTotal:null,2)}%</td><td class="num">${fmt(r.h)}</td><td class="num">${fmt(r.b)}</td><td class="num">${fmt(r.rate,2)}</td><td>${r.eligible?fmt(r.rank):t('Unranked','Nerangirano')}</td></tr>`).join('');
   byId('media-source-scope').textContent=`${state.from}–${state.to} · ${fmt(entries.filter(r=>r.n>0).length)} ${t('HNB-carrying domains','domena s HNB objavama')} · ${fmt(entries.filter(r=>r.eligible).length)} ${t('rate-eligible domains','domena prihvatljivih za poredak stopa')} · ${t('all eligible sources; first 25 shown','svi prihvatljivi izvori; prikazano prvih 25')}`;
   renderExtensions(rows);
   const language=new URL(hr?'index.html':'hr.html',location.href);language.search=url().search;language.hash=location.hash;byId('media-language').href=language.href;
 }
 function download(text,type,name){const u=URL.createObjectURL(new Blob([text],{type})),a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);announce(t('Download prepared.','Preuzimanje je pripremljeno.'));}
 document.querySelectorAll('[data-media-js]').forEach(e=>e.hidden=false);
 Object.keys(defaults).forEach(k=>byId('media-'+k)?.addEventListener('change',e=>{state=validate({...state,[k]:e.target.value});save();render();}));
 byId('media-reset').addEventListener('click',()=>{state={...defaults};save();render();announce(t('Default view restored.','Vraćen je početni prikaz.'));});
 byId('media-copy').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(url().href);announce(t('Link copied.','Poveznica je kopirana.'));}catch{const f=byId('media-copy-fallback');f.hidden=false;f.value=url().href;f.focus();f.select();}});
 byId('media-export-csv').addEventListener('click',()=>{const rows=selectedRows(),keys=['period','source','hnb_count','hnb_i','background_i','rate_per_10000','coverage_state','denominator_id','data_version','method_version','presentation_version','title_mention_count','title_share','hnb_domains','background_domains','breadth_share','indicator_version','selected_metric'];
   const records=rows.map(r=>[r.period,state.source,r.n,r.h,r.b,r.rate,r.coverage_state,'AEM_web_query_i_publications_v1',data.release.data_version,data.release.method_version,data.presentation_version,r.titles,r.title===null?null:r.title/100,r.domains,r.backgroundDomains,r.breadth===null?null:r.breadth/100,data.extensions.indicator_version,state.metric]);
   const cell=v=>'"'+String(v??'').replace(/"/g,'""')+'"';download([keys,...records].map(r=>r.map(cell).join(',')).join('\r\n'),'text/csv;charset=utf-8','hnb-media-selected.csv');});
 byId('media-export-sources').addEventListener('click',()=>{
   const header=['source_id','period_start','period_end','hnb_count','hnb_i','background_i','rate_per_10000','eligible','rank','data_version','indicator_version'];
   const rows=sourceEntries().map(r=>[r.id,state.from,state.to,r.n,r.h,r.b,r.rate,r.eligible?1:0,r.rank,data.release.data_version,data.extensions.indicator_version]);
   download([header,...rows].map(r=>r.map(v=>'"'+String(v??'').replace(/"/g,'""')+'"').join(',')).join('\r\n'),'text/csv;charset=utf-8','hnb-media-sources-selected.csv');
 });
 document.querySelectorAll('[data-source-window]').forEach(button=>button.addEventListener('click',()=>{
   const windows={pooled:[periods[0],data.summary.last_full_period],legacy:[periods[0],'2023-12'],api:['2024-01',data.summary.last_full_period]};
   [state.from,state.to]=windows[button.dataset.sourceWindow];save();render();
 }));
 byId('media-export-svg').addEventListener('click',()=>{let out=svg(selectedRows(),1100,340).replace('<svg ','<svg width="1100" height="440" ').replace('viewBox="0 0 1100 340"','viewBox="0 0 1100 440"');
   out=out.replace('</svg>',`<text x="62" y="370" font-family="Arial" font-size="16" fill="#112838">${esc(metricLabel())}</text><text x="62" y="398" font-family="Arial" font-size="13" fill="#4f6470">${esc(sourceLabel())} · ${state.from}–${state.to} · HNB_MEDIA ${data.release.data_version}</text><text x="62" y="423" font-family="Arial" font-size="12" fill="#4f6470">${esc(t('01/2024 collection change; September 2026 partial. Counts describe the monitored sample.','01/2024 promjena prikupljanja; rujan 2026. djelomičan. Brojevi opisuju praćeni uzorak.'))}</text><metadata>${esc(JSON.stringify({state,release:data.release,presentation:data.presentation_version,denominator:'AEM_web_query_i_publications_v1'}))}</metadata></svg>`);download(out,'image/svg+xml;charset=utf-8','hnb-media-selected.svg');});
 byId('media-definition-open').addEventListener('click',()=>{returnFocus=document.activeElement;byId('media-definition').showModal();});
 byId('media-definition-close').addEventListener('click',()=>byId('media-definition').close());byId('media-definition').addEventListener('close',()=>returnFocus?.focus({preventScroll:true}));
 byId('media-definition').addEventListener('keydown',event=>{if(event.key==='Tab'){event.preventDefault();byId('media-definition-close').focus();}});
 addEventListener('popstate',()=>{state=fromURL();render();});let resize;addEventListener('resize',()=>{clearTimeout(resize);resize=setTimeout(render,120);});
 const observer=new IntersectionObserver(entries=>{for(const e of entries)if(e.isIntersecting){document.querySelectorAll('.contents a').forEach(a=>a.removeAttribute('aria-current'));document.querySelector(`.contents a[href="#${e.target.id}"]`)?.setAttribute('aria-current','location');}},{rootMargin:'-15% 0px -65% 0px'});document.querySelectorAll('main>.section').forEach(e=>observer.observe(e));
 const params=new URL(location.href).searchParams,invalid=Object.keys(defaults).some(k=>params.has('m_'+k)&&params.get('m_'+k)!==state[k]);
 save(false);render();if(invalid){byId('media-state-warning').hidden=false;byId('media-state-warning').textContent=t('Invalid or reversed URL selections were reset to supported values; dates are shown in chronological order.','Nevaljani ili obrnuti odabiri iz poveznice vraćeni su na podržane vrijednosti; datumi su prikazani kronološki.');}
})();
