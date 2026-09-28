'use strict';
(()=>{
 const data=JSON.parse(document.getElementById('media-data').textContent),hr=document.documentElement.lang==='hr',t=(a,b)=>hr?b:a;
 const byId=id=>document.getElementById(id),fmt=(n,d=0)=>n==null?'—':new Intl.NumberFormat(hr?'hr-HR':'en-GB',{maximumFractionDigits:d,minimumFractionDigits:d}).format(n);
 const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const periods=data.monthly.map(r=>r.period),sources=['all','stable',...data.selector_sources];
 const defaults={from:periods[0],to:data.summary.last_full_period,source:'all',metric:'count',sort:'count',q:'',page:1,inspect:''};
 function validate(input){const s={...defaults,...input};for(const k of ['from','to'])if(!periods.includes(s[k]))s[k]=defaults[k];if(s.from>s.to)[s.from,s.to]=[s.to,s.from];if(!sources.includes(s.source))s.source='all';if(!['count','rate','title','breadth'].includes(s.metric))s.metric='count';if(!['count','name','rate'].includes(s.sort))s.sort='count';s.q=String(s.q).trim().slice(0,200);s.page=Math.max(1,Math.min(10000,parseInt(s.page,10)||1));if(!periods.includes(s.inspect)||s.inspect<s.from||s.inspect>s.to)s.inspect='';return s;}
 function fromURL(){const p=new URL(location.href).searchParams;return validate(Object.fromEntries(Object.keys(defaults).filter(k=>p.has('m_'+k)).map(k=>[k,p.get('m_'+k)])));}
 let state=fromURL(),returnFocus=null;const announce=s=>byId('media-announcement').textContent=s;
 function url(){const u=new URL(location.href);Object.entries(state).forEach(([k,v])=>{if(v===defaults[k])u.searchParams.delete('m_'+k);else u.searchParams.set('m_'+k,v);});return u;}
 function save(push=true){history[push?'pushState':'replaceState'](null,'',url());const link=new URL(hr?'index.html':'hr.html',location.href);link.search=url().search;link.hash=location.hash;byId('media-language').href=link.href;}
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
 function svg(rows,width=1000,height=340,metric=state.metric,ceiling=null,interactive=false,showBoundary=false){
   if(!rows.length)return `<p>${t('No complete months in this selection.','U odabiru nema potpunih mjeseci.')}</p>`;
   const left=width<500?48:62,right=20,top=40,bottom=44,ordinal=p=>Number(p.slice(0,4))*12+Number(p.slice(5,7)),start=ordinal(rows[0].period),end=ordinal(rows.at(-1).period);
   const value=r=>metric==='count'?r.n:r[metric],vals=rows.map(value).filter(v=>v!==null),maximum=Math.max(1,...vals),step=10**Math.floor(Math.log10(maximum)),upper=ceiling??(metric==='count'?Math.max(4,Math.ceil((Math.ceil(maximum/step)*step)/4)*4):Math.ceil(maximum/step)*step);
   const x=p=>left+(width-left-right)*(ordinal(p)-start)/Math.max(1,end-start),y=v=>top+(height-top-bottom)*(1-v/upper);
   let out=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(metricLabel(metric))}"><title>${esc(metricLabel(metric))}</title><rect width="100%" height="100%" fill="white"/>`;
   for(let j=0;j<5;j++){const v=upper*j/4,yy=y(v);out+=`<line x1="${left}" x2="${width-right}" y1="${yy}" y2="${yy}" stroke="#dce4ea"/><text x="${left-8}" y="${yy+5}" text-anchor="end" font-family="Arial" font-size="12" fill="#4f6470">${fmt(v,Number.isInteger(v)?0:2)}</text>`;}
   const segments=[];let points=[];for(const r of rows){const v=value(r);if(v===null){if(points.length)segments.push(points);points=[];}else points.push(`${x(r.period)},${y(v)}`);}if(points.length)segments.push(points);
   for(const p of segments)out+=`<polyline class="media-observed-series" points="${p.join(' ')}" fill="none" stroke="#165ce0" stroke-width="3" stroke-linejoin="round"/>`;
   const boundary=ordinal('2024-01');if(showBoundary&&start<boundary&&boundary<end){const xx=x('2024-01');out+=`<line class="media-boundary" x1="${xx}" x2="${xx}" y1="${top}" y2="${height-bottom}" stroke="#4f6470" stroke-dasharray="5 5"/><text x="${Math.min(width-70,xx+5)}" y="22" font-family="Arial" font-size="12" fill="#4f6470">01/2024</text>`;}
   for(const r of rows)if(value(r)!==null&&r.coverage_state==='partial')out+=`<circle class="partial-period" cx="${x(r.period)}" cy="${y(value(r))}" r="5" fill="white" stroke="#165ce0" stroke-width="2"/>`;
   let labels=rows.filter((r,i)=>r.period.endsWith('-01')&&i>0);if(rows.length<15)labels=rows.length===1?[rows[0]]:[rows[0],rows.at(-1)];else if(width<500)labels=labels.filter((r,i)=>i%2===0);
   labels.forEach(r=>out+=`<text x="${Math.max(45,Math.min(width-35,x(r.period)))}" y="${height-12}" text-anchor="middle" font-family="Arial" font-size="12" fill="#4f6470">${rows.length<15?r.period:r.period.slice(0,4)}</text>`);
   if(rows.length===1&&value(rows[0])!==null)out+=`<circle cx="${x(rows[0].period)}" cy="${y(value(rows[0]))}" r="4" fill="#165ce0"/>`;
   if(interactive)for(const r of rows)if(value(r)!==null)out+=`<circle class="month-point" data-period="${r.period}" cx="${x(r.period)}" cy="${y(value(r))}" r="7" fill="transparent" stroke="transparent"><title>${r.period} · ${fmt(value(r),metric==='count'?0:2)}</title></circle>`;
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
 function renderSources(){
   const entries=sourceEntries(),total=entries.reduce((s,r)=>s+r.n,0),matches=entries.filter(r=>r.id.toLowerCase().includes(state.q.toLowerCase()));
   const pages=Math.max(1,Math.ceil(matches.length/25));state.page=Math.min(state.page,pages);
   const first=(state.page-1)*25,shown=matches.slice(first,first+25);
   const labels=[t('Publications','Objave'),t('Per 10,000','Na 10.000'),t('Share','Udio'),t('HNB, filter','HNB, filtar'),t('Background, filter','Pozadina, filtar'),t('Rate rank','Rang stope')];
   byId('media-source-rows').innerHTML=shown.map(r=>`<tr role="row"><th scope="row" role="rowheader">${esc(r.id)}</th>${[fmt(r.n),fmt(r.rate,2),fmt(total?100*r.n/total:null,2)+'%',fmt(r.h),fmt(r.b),r.eligible?fmt(r.rank):t('Unranked','Nerangirano')].map((v,i)=>`<td role="cell" class="num" data-label="${labels[i]}">${v}</td>`).join('')}</tr>`).join('')||`<tr><td colspan="7">${t('No domains match this search.','Nijedna domena ne odgovara pretrazi.')}</td></tr>`;
   byId('media-source-scope').textContent=`${state.from}–${state.to} · ${fmt(entries.filter(r=>r.n>0).length)} ${t('domains with HNB mentions','domena sa spominjanjem HNB-a')} · ${fmt(entries.length)} ${t('archive domains in the table (including zero counts)','arhivskih domena u tablici (uključujući nule)')} · ${fmt(entries.filter(r=>r.eligible).length)} ${t('eligible for rate ranking','prihvatljivih za poredak stopa')}`;
   byId('media-source-page').textContent=matches.length?`${first+1}–${Math.min(first+25,matches.length)} / ${fmt(matches.length)} · ${t('Page','Stranica')} ${state.page} / ${pages}`:t('No results','Nema rezultata');
   byId('media-source-prev').disabled=state.page===1;byId('media-source-next').disabled=state.page===pages;
   byId('media-search').value=state.q;
 }
 function inspectMonth(period){
   const row=selectedRows().find(r=>r.period===period);if(!row)return;
   byId('media-inspect').value=period;
   byId('media-month-reading').textContent=`${period}${row.coverage_state==='partial'?' *':''} · ${fmt(row.n)} ${t('publications','objava')} · ${fmt(row.rate,2)} ${t('per 10,000','na 10.000')} · ${t('Eligible HNB / archive publications','Prihvatljive HNB / arhivske objave')}: ${fmt(row.h)} / ${fmt(row.b)}`;
   byId('media-month-prev').disabled=period===state.from;byId('media-month-next').disabled=period===state.to;
   byId('media-chart').querySelectorAll('[data-period]').forEach(point=>point.classList.toggle('is-selected',point.dataset.period===period));
 }
 function renderExtensions(rows){
   const selected=data.source_monthly.filter(r=>r.period>=state.from&&r.period<=state.to&&inPopulation(r)),counts=new Map();
   for(const r of selected)counts.set(r.source_id,(counts.get(r.source_id)||0)+r.hnb_count);
   const positive=[...counts.values()].filter(n=>n>0).sort((a,b)=>b-a),total=positive.reduce((a,b)=>a+b,0),eff=total?total*total/positive.reduce((s,n)=>s+n*n,0):null;
   const bg=new Set(selected.filter(r=>r.background_count>0).map(r=>r.source_id)).size,titles=selected.reduce((s,r)=>s+r.title_mention_count,0);
   byId('extension-scope').textContent=`${sourceLabel()} · ${state.from}–${state.to} · ${t('All HNB contributors; no ranking threshold.','Svi izvori s HNB objavama; bez praga za rangiranje.')}`;
   const values=[['V5',t('Effective domains','Efektivni broj domena'),fmt(eff,2),`${t('Top five / top ten','Prvih pet / prvih deset')}: ${fmt(total?100*positive.slice(0,5).reduce((a,b)=>a+b,0)/total:null,2)}% / ${fmt(total?100*positive.slice(0,10).reduce((a,b)=>a+b,0)/total:null,2)}%. ${t('A lower effective count means publications are concentrated in fewer domains; a higher one means a more even spread. It does not measure ownership.','Manji efektivni broj znači koncentraciju objava na manje domena, a veći ravnomjerniji raspored. Ne mjeri vlasništvo.')}`],['V6',t('Outlet breadth','Obuhvat izvora'),`${fmt(positive.length)} / ${fmt(bg)}`,`${fmt(bg?100*positive.length/bg:null,2)}%. ${t('The share of observed archive domains that carry at least one HNB publication in this period. It describes spread across sources, not audience reach.','Udio opaženih arhivskih domena s najmanje jednom objavom o HNB-u u ovom razdoblju. Opisuje rasprostranjenost među izvorima, a ne doseg publike.')}`],['V7',t('Title-match share','Udio podudaranja u naslovu'),`${fmt(total?100*titles/total:null,2)}%`,`${fmt(titles)} / ${fmt(total)}. ${t('The share of HNB publications that also name the bank in the headline. This indicates title presence, not the article’s stance.','Udio objava o HNB-u koje navode banku i u naslovu. Pokazuje prisutnost u naslovu, a ne stav članka.')}`]];
   byId('extension-cards').innerHTML=values.map(([id,title,value,note])=>`<article id="${id}"><h3>${title}</h3><strong class="indicator-value">${value}</strong><p>${note}</p></article>`).join('');
   const all=data.extensions.monthly.filter(r=>r.scope==='all'&&r.period>=state.from&&r.period<=state.to),stable=all.map(r=>data.extensions.monthly.find(s=>s.scope==='stable'&&s.period===r.period));
   const variants=[all.map(r=>({...r,rate:r.rate_per_10000})),stable.map(r=>({...r,rate:r.rate_per_10000})),stable.map(r=>({...r,rate:r.fixed_weight_rate}))];
   const max=Math.max(1,...variants.flat().map(r=>r.rate??0)),ceiling=Math.ceil(max/10)*10,width=Math.max(310,Math.min(1100,byId('composition-chart').clientWidth));
   let drawing=svg(variants[0],width,340,'rate',ceiling,false,true).replaceAll('class="media-observed-series"','class="composition-series-0"');
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
   byId('media-chart').innerHTML=svg(rows,Math.max(310,Math.min(1100,byId('media-chart').clientWidth)),340,state.metric,null,true);
   byId('media-numeric-rows').innerHTML=table(rows);byId('media-empty').hidden=available&&total!==0;
   byId('media-empty').textContent=available?t('No publications in the selected set.','Nema objava u odabranom skupu.'):t('Data are unavailable for the selected view.','Podaci nisu dostupni za odabrani prikaz.');
   byId('media-chart-label').textContent=metricLabel();
   byId('media-selected-note').textContent=t('Counts and rates describe the monitored archive. The numeric table and downloads retain the matching numerator and denominator.','Brojevi i stope opisuju praćeni arhiv. Brojčana tablica i datoteke za preuzimanje zadržavaju usklađeni brojnik i nazivnik.')+(state.to==='2026-09'?' '+t('September is partial through the 10th; the hollow point marks it.','Rujan je djelomičan, do 10. dana; označen je praznim kružićem.'):'');
   byId('media-inspect').innerHTML=rows.map(r=>`<option value="${r.period}">${r.period}${r.coverage_state==='partial'?' *':''}</option>`).join('');
   inspectMonth(rows.some(r=>r.period===state.inspect)?state.inspect:rows.at(-1)?.period);
   renderSources();
   renderExtensions(rows);
   const language=new URL(hr?'index.html':'hr.html',location.href);language.search=url().search;language.hash=location.hash;byId('media-language').href=language.href;
 }
 function download(text,type,name){const u=URL.createObjectURL(new Blob([text],{type})),a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);announce(t('Download prepared.','Preuzimanje je pripremljeno.'));}
 document.querySelectorAll('[data-media-js]').forEach(e=>e.hidden=false);
 ['from','to','source','metric','sort'].forEach(k=>byId('media-'+k)?.addEventListener('change',e=>{state=validate({...state,[k]:e.target.value,page:1});render();save();}));
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
   [state.from,state.to]=windows[button.dataset.sourceWindow];state.page=1;state.inspect='';render();save();
 }));
 byId('media-export-svg').addEventListener('click',()=>{let out=svg(selectedRows(),1100,340).replace('<svg ','<svg width="1100" height="440" ').replace('viewBox="0 0 1100 340"','viewBox="0 0 1100 440"');
   out=out.replace('</svg>',`<text x="62" y="370" font-family="Arial" font-size="16" fill="#112838">${esc(metricLabel())}</text><text x="62" y="398" font-family="Arial" font-size="13" fill="#4f6470">${esc(sourceLabel())} · ${state.from}–${state.to} · HNB_MEDIA ${data.release.data_version}</text><text x="62" y="423" font-family="Arial" font-size="12" fill="#4f6470">${esc(t('Counts and rates describe the monitored archive.','Brojevi i stope opisuju praćeni arhiv.')+(state.to==='2026-09'?' '+t('September 2026 is partial.','Rujan 2026. je djelomičan.'):''))}</text><metadata>${esc(JSON.stringify({state,release:data.release,presentation:data.presentation_version,denominator:'AEM_web_query_i_publications_v1'}))}</metadata></svg>`);download(out,'image/svg+xml;charset=utf-8','hnb-media-selected.svg');});
 byId('media-definition-open').addEventListener('click',()=>{returnFocus=document.activeElement;byId('media-definition').showModal();});
 byId('media-definition-close').addEventListener('click',()=>byId('media-definition').close());byId('media-definition').addEventListener('close',()=>returnFocus?.focus({preventScroll:true}));
 byId('media-definition').addEventListener('keydown',event=>{if(event.key==='Tab'){event.preventDefault();byId('media-definition-close').focus();}});
 document.documentElement.classList.add('media-enhanced');
 const menu=byId('media-menu'),nav=byId('media-nav-links');
 menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));nav.classList.toggle('is-open',open);});
 nav.addEventListener('click',e=>{if(e.target.closest('a')){menu.setAttribute('aria-expanded','false');nav.classList.remove('is-open');}});
 nav.addEventListener('keydown',e=>{if(e.key==='Escape'){menu.setAttribute('aria-expanded','false');nav.classList.remove('is-open');menu.focus();}});
 document.querySelectorAll('[data-chart-window]').forEach(button=>button.addEventListener('click',()=>{
   const complete=periods.filter(p=>p<=data.summary.last_full_period);
   state.from=button.dataset.chartWindow==='latest'?complete.at(-12):button.dataset.chartWindow==='api'?'2024-01':periods[0];
   state.to=data.summary.last_full_period;state.page=1;state.inspect='';render();save();
 }));
 byId('media-search').addEventListener('input',e=>{state.q=e.target.value.slice(0,200);state.page=1;const position=e.target.selectionStart;renderSources();e.target.setSelectionRange(position,position);save(false);});
 byId('media-search-clear').addEventListener('click',()=>{state.q='';state.page=1;renderSources();save();byId('media-search').focus();});
 for(const [id,step] of [['media-source-prev',-1],['media-source-next',1]])byId(id).addEventListener('click',()=>{state.page+=step;renderSources();save();byId('media-source-rows').closest('.table-wrap').scrollIntoView({block:'start',behavior:'instant'});});
 function chooseMonth(period){state.inspect=period;inspectMonth(period);save(false);}
 byId('media-inspect').addEventListener('change',e=>chooseMonth(e.target.value));
 for(const [id,step] of [['media-month-prev',-1],['media-month-next',1]])byId(id).addEventListener('click',()=>chooseMonth(periods[periods.indexOf(byId('media-inspect').value)+step]));
 byId('media-chart').addEventListener('click',e=>{const point=e.target.closest('[data-period]');if(point)chooseMonth(point.dataset.period);});
 byId('media-chart').addEventListener('pointerover',e=>{const point=e.target.closest('[data-period]');if(point)inspectMonth(point.dataset.period);});
 byId('media-chart').addEventListener('pointerleave',()=>inspectMonth(state.inspect||state.to));
 function revealFragment(){let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}const target=byId(id);if(!target)return;let detail=target.closest('details');while(detail){detail.open=true;detail=detail.parentElement?.closest('details');}const language=new URL(byId('media-language').href);language.hash=location.hash;byId('media-language').href=language.href;}
 addEventListener('hashchange',revealFragment);revealFragment();
 addEventListener('popstate',()=>{state=fromURL();render();});let resize;addEventListener('resize',()=>{clearTimeout(resize);resize=setTimeout(render,120);});
 const observer=new IntersectionObserver(entries=>{for(const e of entries)if(e.isIntersecting){document.querySelectorAll('.contents a').forEach(a=>a.removeAttribute('aria-current'));document.querySelector(`.contents a[href="#${e.target.id}"]`)?.setAttribute('aria-current','location');}},{rootMargin:'-15% 0px -65% 0px'});document.querySelectorAll('main>.section').forEach(e=>observer.observe(e));
 const params=new URL(location.href).searchParams,invalid=Object.keys(defaults).some(k=>params.has('m_'+k)&&params.get('m_'+k)!==String(state[k]));
 save(false);render();if(invalid){byId('media-state-warning').hidden=false;byId('media-state-warning').textContent=t('Invalid or reversed URL selections were reset to supported values; dates are shown in chronological order.','Nevaljani ili obrnuti odabiri iz poveznice vraćeni su na podržane vrijednosti; datumi su prikazani kronološki.');}
})();
