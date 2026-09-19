'use strict';
const byId=id=>document.getElementById(id);
const hr=document.documentElement.lang==='hr';
const t=(en,cr)=>hr?cr:en;
const E=JSON.parse(byId('research-data').textContent);
const I=JSON.parse(byId('inspection-data').textContent);
const esc=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fixed=(value,n=2)=>{const v=Number(value).toFixed(n);return (Number(v)===0?(0).toFixed(n):v).replace('.',hr?',':'.');};
const precise=value=>Math.abs(value)>0&&Math.abs(value)<.01?Number(value.toPrecision(3)).toString().replace('.',hr?',':'.'):fixed(value,3);
const number=value=>new Intl.NumberFormat(hr?'hr-HR':'en-GB',{maximumFractionDigits:0}).format(value);
const pp=t('pp','pb');
const root=hr?'grafikon':'overview';
const titles={share:t('Weighted institutional visibility','Ponderirana institucionalna vidljivost'),gap:t('Attention gap','Jaz u pažnji'),article:t('Article share','Udio objava'),centrality:t('Network centrality','Mrežna centralnost'),hhi:t('Concentration of institutional weight','Koncentracija institucionalnog pondera')};
const units={share:'%',gap:pp,article:'%',centrality:t('index units','indeksnih jedinica'),hhi:'HHI'};
const defaults={window:'all',metric:'share',period:'2026-05',sample:'primary',frequency:'weekly',specification:'9b',lens:'none',from:'2024-04',to:'2026-05',finding:'F1',mode:'read',inspect:'',sort:'name'};
const choices={window:['all','new'],metric:Object.keys(titles),sample:['primary','common'],frequency:['weekly','monthly'],specification:['9b','9a'],lens:['none','visibility','composition','inflation','understanding'],finding:['F1','F2','F3','F4'],mode:['read','inspect','compare'],inspect:['',...Object.keys(I.indicators.en)],sort:['name','items','weight']};
function validate(input){
  const s={...defaults,...input};
  for(const [key,allowed] of Object.entries(choices))if(!allowed.includes(s[key]))s[key]=defaults[key];
  const periods=I.observations.filter(r=>s.window==='all'||r.period>='2024-04').map(r=>r.period);
  for(const key of ['period','from','to'])if(!periods.includes(s[key]))s[key]=key==='from'?periods[0]:periods.at(-1);
  if(s.from>s.to)[s.from,s.to]=[s.to,s.from];
  if(s.mode==='inspect'&&!s.inspect)s.mode='read';
  return s;
}
function fromURL(){const params=new URL(location.href).searchParams;return validate(Object.fromEntries(Object.keys(defaults).filter(k=>params.has(k)).map(k=>[k,params.get(k)])));}
let state=fromURL(),updating=false,dialogOrigin=null,dialogScroll=0,dialogReturnMode='read',closingDialog=false;
const sampleLabel=(sample=state.sample)=>sample==='common'?t('Common sources','Zajednički izvori'):t('Primary corpus','Primarni korpus');
const frequencyLabel=()=>state.frequency==='weekly'?t('weekly models','tjedni modeli'):t('monthly models','mjesečni modeli');
const selectedRow=()=>I.observations.find(r=>r.period===state.period);
const selectedData=()=>selectedRow()[state.sample];
function visibleRows(){return I.observations.filter(r=>state.window==='all'||r.period>='2024-04').map(r=>({...r[state.sample],period:r.period,inflation:r.inflation,gap:r[state.sample].gap/100}));}
function stateURL(anchor){
  const url=new URL(location.href);
  for(const [key,value] of Object.entries(state)){if(value==='')url.searchParams.delete(key);else url.searchParams.set(key,value);}
  url.searchParams.set('lang',hr?'hr':'en');
  if(anchor!==undefined)url.hash=anchor;
  return url;
}
function saveURL(mode='replace',anchor){try{history[mode==='push'?'pushState':'replaceState'](null,'',stateURL(anchor));}catch{/* Some local-file previews restrict history changes. */}}
function setState(patch,{historyMode='push',anchor}={}){state=validate({...state,...patch});saveURL(historyMode,anchor);render();}
function announce(message){for(const id of ['action-status','share-status','dialog-status','global-status'])if(byId(id))byId(id).textContent=message;}
function selectOptions(id,periods,value){
  const el=byId(id);if(!el)return;
  if([...el.options].map(o=>o.value).join(',')!==periods.join(','))el.replaceChildren(...periods.map(p=>new Option(p,p)));
  el.value=value;
}
function controls(){
  const periods=visibleRows().map(r=>r.period);
  for(const id of ['window','metric','sample','frequency','specification'])if(byId(id))byId(id).value=state[id];
  selectOptions('period',periods,state.period);selectOptions('compare-from',periods,state.from);selectOptions('compare-to',periods,state.to);
  byId('compare-finding').value=state.finding;byId('source-sort').value=state.sort;
  document.querySelectorAll('[data-bind]').forEach(el=>el.value=state[el.dataset.bind]);
  document.querySelectorAll('[data-lens]').forEach(el=>el.setAttribute('aria-pressed',String(state.lens===el.dataset.lens)));
  document.querySelectorAll('[data-mode]').forEach(el=>el.setAttribute('aria-pressed',String(state.mode===el.dataset.mode)));
  byId('comparison').open=state.mode==='compare';
  byId('desk-context').textContent=`${state.period} · ${sampleLabel()} · ${titles[state.metric]} · ${frequencyLabel()}`;
  const lensText={
    none:t('Choose a question to configure the view, or use the controls below.','Odaberite pitanje za prilagodbu prikaza ili koristite kontrole u nastavku.'),
    visibility:t('Visibility lens: the recent period, weighted share and F2 trend comparisons. The level is one month; the fitted trend describes the stated window.','Vidljivost: kasnije razdoblje, ponderirani udio i usporedbe trenda F2. Razina opisuje jedan mjesec, a procijenjeni trend navedeno razdoblje.'),
    composition:t('Source lens: the common-source series and F2 comparison, alongside the selected month’s weight concentration. Source labels are not ownership groups.','Izvori: serija zajedničkih izvora i usporedba F2 uz koncentraciju pondera odabranog mjeseca. Oznake izvora nisu vlasničke grupe.'),
    inflation:t('Inflation lens: aligned monthly series and F1 models. The predefined checks ask whether time controls, volume and measurement choices affect the association.','Inflacija: poravnate mjesečne serije i modeli F1. Provjere ispituju utjecaj vremenskih kontrola, obujma i konstrukcije pokazatelja na povezanost.'),
    understanding:t('Understanding lens: article share and F3 expectations comparisons. A survey balance, potential exposure and comprehension answer different questions.','Razumijevanje: udio objava i usporedbe očekivanja F3. Anketni saldo, potencijalna izloženost i razumijevanje odgovaraju na različita pitanja.')};
  byId('lens-interpretation').textContent=lensText[state.lens];
}
function renderCharts(){
  const rows=visibleRows();
  for(const [id,metric] of [['gap-chart',state.metric],['inflation-chart','inflation']]){
    const el=byId(id);el.innerHTML=timelineSVG(rows,metric,Math.max(280,Math.round(el.getBoundingClientRect().width)),state.period);
    el.setAttribute('aria-label',`${metric==='inflation'?'HICP':titles[metric]} · ${sampleLabel()} · ${rows[0].period}–${rows.at(-1).period} · ${t('selected month','odabrani mjesec')} ${state.period}`);
  }
  byId('visibility-title').textContent=titles[state.metric];
  byId('visibility-unit').textContent=state.metric==='share'?t('Weighted share (%) · higher means more visible','Ponderirani udio (%) · više znači veću vidljivost'):state.metric==='gap'?t('Percentage points · higher means less visible','Postotni bodovi · više znači manju vidljivost'):`${titles[state.metric]} · ${units[state.metric]}`;
  const scale=timelineScale(rows,state.metric),range=`${fixed(scale[0],scale[0]%1?1:0)}–${fixed(scale[1],scale[1]%1?1:0)} ${units[state.metric]}`;
  byId('chart-scope').textContent=`${sampleLabel()} · ${rows[0].period}–${rows.at(-1).period} · ${range}. `+t('Monthly observations. Scales depend on the selected view.','Mjesečna opažanja. Skale ovise o odabranom prikazu.')+(state.metric==='gap'?' '+t('Zero is a reference, not a target.','Nula je referenca, a ne cilj.'):'');
  const d=selectedData(),r=selectedRow();
  byId('period-values').textContent=`${state.period} · ${t('share','udio')} ${fixed(d.share)}% · ${t('gap','jaz')} ${fixed(d.gap)} ${pp} · HICP ${fixed(r.inflation,1)}%`;
  byId('period-context').textContent=`${sampleLabel()} · ${t('numerator','brojnik')} ${number(d.numerator)} / ${t('denominator','nazivnik')} ${number(d.denominator)} × 100 = ${fixed(d.share)}%. `+t('Denominator includes the formula’s +1. Underlying values retain full precision.','Nazivnik uključuje +1 iz formule. Temeljne vrijednosti zadržavaju punu preciznost.');
  const values=I.observations.map(r=>r[state.sample].share).sort((a,b)=>a-b),q1=values[Math.floor(values.length*.25)],q3=values[Math.floor(values.length*.75)];
  byId('observation-note').textContent=d.share>q3+1.5*(q3-q1)?t('Unusual high share: above Q3 + 1.5 × IQR. Inspect the source contributions below; the flag does not identify a cause.','Neuobičajeno visok udio: iznad Q3 + 1,5 × IQR. Pregledajte doprinose izvora; oznaka ne utvrđuje uzrok.'):'';
  byId('observation-note').hidden=!byId('observation-note').textContent;
  byId('monthly-caption').textContent=`${sampleLabel()} · ${titles[state.metric]} (${units[state.metric]}) · HICP (%)`;
  byId('monthly-head').innerHTML=`<tr><th scope="col">${t('Month','Mjesec')}</th><th scope="col">${esc(titles[state.metric])} (${units[state.metric]})</th><th scope="col">HICP (%)</th></tr>`;
  byId('monthly-body').innerHTML=rows.map(r=>`<tr><th scope="row">${r.period}</th><td>${fixed(state.metric==='gap'?r.gap*100:r[state.metric],['centrality','hhi'].includes(state.metric)?4:2)}</td><td>${fixed(r.inflation,1)}</td></tr>`).join('');
}
function evidenceLabel(){
  if(state.finding==='F1')return t('Sensitive to time controls','Osjetljivo na vremenske kontrole');
  if(state.finding==='F2')return t('Same direction across source definitions','Isti smjer u definicijama izvora');
  if(state.finding==='F3')return t('Depends on survey assignment','Ovisi o pridruživanju ankete');
  const row=I.robustness.find(r=>r.finding==='F4'&&r.frequency===state.frequency&&r.key==='common');
  return row.lo<=0&&row.hi>=0?t('Direction uncertain','Neizvjestan smjer'):t('Interval on one side of zero','Interval s jedne strane nule');
}
function renderEndpoints(){
  const a=I.observations.find(r=>r.period===state.from)[state.sample][state.metric],b=I.observations.find(r=>r.period===state.to)[state.sample][state.metric],delta=b-a;
  const unit=['share','article','gap'].includes(state.metric)?pp:units[state.metric];
  const digits=['centrality','hhi'].includes(state.metric)?4:3;
  byId('state-level').textContent=`${fixed(selectedData()[state.metric],digits)} ${units[state.metric]}`;
  byId('level-context').textContent=`${state.period} · ${sampleLabel()} · ${titles[state.metric]}`;
  byId('state-direction').textContent=delta===0?t('Unchanged','Nepromijenjeno'):delta>0?t('↑ Increasing','↑ Raste'):t('↓ Decreasing','↓ Pada');
  byId('direction-context').textContent=`${state.from} → ${state.to} · ${delta>0?'+':''}${fixed(delta,digits)} ${unit}. `+t('Descriptive endpoint difference.','Opisna razlika krajnjih točaka.');
  byId('state-evidence').textContent=evidenceLabel();
  byId('evidence-context').textContent=`${state.finding} · ${frequencyLabel()}. `+t('The label applies to the named research finding, not to the selected month.','Oznaka se odnosi na navedeni nalaz, a ne na odabrani mjesec.');
  byId('endpoint-result').innerHTML=`<div><span>${state.from}</span><strong>${fixed(a,digits)} ${units[state.metric]}</strong></div><span aria-hidden="true">→</span><div><span>${state.to}</span><strong>${fixed(b,digits)} ${units[state.metric]}</strong></div><div><span>${t('Difference','Razlika')}</span><strong>${delta>0?'+':''}${fixed(delta,digits)} ${unit}</strong></div>`;
  byId('comparison-basis').textContent=`${sampleLabel()} · ${titles[state.metric]}. `+(state.sample==='common'?t('Both endpoints restrict the institutional numerator and inflation denominator to the same 258 source labels: present in 2023 and July–December 2024. Activity and contributions can still vary within that set.','Obje točke ograničavaju institucionalni brojnik i inflacijski nazivnik na istih 258 oznaka izvora prisutnih u 2023. i srpnju – prosincu 2024. Aktivnost i doprinosi unutar skupa mogu varirati.'):t('Both endpoints use the primary corpus and the stated measure. The common-source option asks how the result looks under a fixed set of source labels; it does not hold publication volume constant.','Obje točke koriste primarni korpus i navedeni pokazatelj. Opcija zajedničkih izvora ispituje rezultat za fiksni skup oznaka izvora; ne drži obujam objava nepromijenjenim.'));
  byId('toggle-sample').textContent=state.sample==='primary'?t('Compare common sources','Usporedi zajedničke izvore'):t('Show primary series','Prikaži primarnu seriju');
}
const checkLabels={
  '9b':()=>t('Primary · media volume included','Primarni · s medijskim obujmom'),
  '9a':()=>t('Without media-volume control','Bez kontrole medijskog obujma'),
  trend:()=>t('Additional period trends','Dodatni trendovi razdoblja'),
  year:()=>t('Calendar-year effects','Učinci kalendarske godine'),
  common:()=>t('Common-source definition','Definicija zajedničkih izvora'),
  winsor:()=>t('Reach limited at the 1st / 99th percentiles','Doseg ograničen na 1. / 99. percentil'),
  primary:()=>t('Primary corpus','Primarni korpus'),
  reconstructed:()=>t('Full-source reconstructed network','Rekonstruirana mreža svih izvora')};
const checkQuestions={
  '9b':()=>t('What does the reference model estimate?','Što procjenjuje referentni model?'),
  '9a':()=>t('Does accounting for institutional item volume matter?','Utječe li kontrola obujma institucionalnih objava?'),
  trend:()=>t('Could gradual time patterns account for the association?','Mogu li postupni vremenski obrasci objasniti povezanost?'),
  year:()=>t('Could differences between calendar years account for it?','Mogu li je objasniti razlike među kalendarskim godinama?'),
  common:()=>t('What changes when both corpora use a fixed source set?','Što se mijenja uz fiksni skup izvora u oba korpusa?'),
  winsor:()=>t('Does limiting extreme reach weights change the estimate?','Mijenja li ograničavanje ekstremnog dosega procjenu?'),
  primary:()=>t('What is the controlled trend in the primary corpus?','Kakav je kontrolirani trend primarnog korpusa?'),
  reconstructed:()=>t('Does the broader reconstructed network point the same way?','Pokazuje li šira rekonstruirana mreža isti smjer?')};
function comparisonRows(){return I.robustness.filter(r=>r.finding===state.finding&&r.frequency===state.frequency).map(r=>({...r,b:r.estimate*r.transform,lower:Math.min(r.lo*r.transform,r.hi*r.transform),upper:Math.max(r.lo*r.transform,r.hi*r.transform)}));}
function comparisonUnit(){return state.finding==='F1'?t('Weighted-share pp per +1 pp inflation','Pb ponderiranog udjela uz +1 pb inflacije'):state.finding==='F2'?`${t('Weighted-share','Ponderirani udio')} ${pp} / ${state.frequency==='weekly'?t('week','tjedan'):t('month','mjesec')}`:`${t('Centrality index units','Indeksne jedinice centralnosti')} / ${state.frequency==='weekly'?t('week','tjedan'):t('month','mjesec')}`;}
function renderForest(){
  const el=byId('robustness-chart');if(state.finding==='F3'){el.innerHTML='';el.hidden=true;return;}el.hidden=false;
  const rows=comparisonRows(),width=Math.max(300,Math.round(el.getBoundingClientRect().width)||600),narrow=width<450,rowStep=narrow?110:94,height=rows.length*rowStep+50;
  let lo=Math.min(0,...rows.map(r=>r.lower)),hi=Math.max(0,...rows.map(r=>r.upper)),span=hi-lo;
  if(span===0)span=1;lo-=span*.12;hi+=span*.12;
  const x=v=>22+(v-lo)/(hi-lo)*(width-44),zero=x(0);
  let svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" aria-hidden="true"><line x1="${zero}" x2="${zero}" y1="20" y2="${height-38}" stroke="#607687" stroke-dasharray="3 3"/>`;
  rows.forEach((r,i)=>{
    const y=(narrow?62:46)+i*rowStep,limit=Math.floor((width-40)/7.5),lines=[''];
    for(const word of checkLabels[r.key]().split(' ')){const last=lines.length-1;if(lines[last]&&(lines[last]+' '+word).length>limit)lines.push(word);else lines[last]+=(lines[last]?' ':'')+word;}
    svg+=`<text font-size="14" font-family="Segoe UI,Arial" fill="#112838">${lines.map((line,j)=>`<tspan x="20" y="${22+i*rowStep+j*17}">${esc(line)}</tspan>`).join('')}</text><line x1="${x(r.lower)}" x2="${x(r.upper)}" y1="${y}" y2="${y}" stroke="#165ce0" stroke-width="4"/><circle cx="${x(r.b)}" cy="${y}" r="5" fill="#165ce0"/><text x="20" y="${y+26}" font-size="13" font-family="Segoe UI,Arial" fill="#4f6470">${precise(r.b)} (${precise(r.lower)} ${t('to','do')} ${precise(r.upper)})</text>`;
  });
  const ticks=[];for(const v of [0,lo+(hi-lo)*.1,hi-(hi-lo)*.1])if(ticks.every(other=>Math.abs(x(v)-x(other))>=60))ticks.push(v);
  ticks.forEach(v=>svg+=`<text data-forest-tick x="${x(v)}" y="${height-12}" text-anchor="middle" font-size="12" fill="#4f6470">${v===0?'0':precise(v)}</text>`);
  el.innerHTML=svg+'</svg>';el.setAttribute('aria-label',`${state.finding} · ${comparisonUnit()}. ${t('Points are estimates, lines are 95% intervals. Exact values follow in the table.','Točke su procjene, crte 95%-tni intervali. Točne vrijednosti slijede u tablici.')}`);
}
function renderRobustness(){
  const isExpectations=state.finding==='F3',rows=comparisonRows();
  byId('robustness-intro').textContent=isExpectations?t('F3 · Article-share exposure, baseline controls. Compare survey assignments and model frequency explicitly. The horizons are weeks or months, as labelled.','F3 · Udio objava, osnovne kontrole. Uspoređuju se pridruživanje ankete i frekvencija modela. Horizonti su tjedni ili mjeseci, kako je označeno.'):`${state.finding} · ${frequencyLabel()} · ${comparisonUnit()} · ${t('95% intervals','95%-tni intervali')}. `+t('This is a predefined set of saved checks, not every combination of controls.','Ovo je unaprijed određen skup spremljenih provjera, a ne svaka kombinacija kontrola.');
  if(isExpectations){
    byId('robustness-table').innerHTML=`<caption>${t('Future horizons passing the saved multiple-testing correction','Budući horizonti koji prolaze spremljenu korekciju višestrukog testiranja')}</caption><thead><tr><th scope="col">${t('Assignment','Pridruživanje')}</th><th scope="col">${t('Frequency','Frekvencija')}</th><th scope="col">${t('Future horizons','Budući horizonti')}</th></tr></thead><tbody>`+E.expectations.map((r,i)=>`<tr><th scope="row">${[t('Linear survey assignment','Linearno pridruživanje ankete'),t('Step survey assignment','Stepenasto pridruživanje ankete'),t('Original monthly survey','Izvorna mjesečna anketa')][i]}</th><td>${r.frequency==='weekly'?t('Weekly','Tjedno'):t('Monthly','Mjesečno')}</td><td>${r.significant_horizons.length?r.significant_horizons.join(', '):t('No future horizon passes','Nijedan budući horizont ne prolazi')} ${r.significant_horizons.length?(r.frequency==='weekly'?t('weeks','tjedna'):t('months','mjeseci')):''}</td></tr>`).join('')+'</tbody>';
    byId('robustness-conclusion').textContent=t('The set of significant future horizons changes with survey assignment and frequency. This is specification sensitivity, not a reliable prediction of understanding, trust or anchoring.','Skup značajnih budućih horizonata mijenja se s pridruživanjem ankete i frekvencijom. To opisuje osjetljivost specifikacija, a ne pouzdano predviđanje razumijevanja, povjerenja ili usidrenosti.');
  }else{
    byId('robustness-table').innerHTML=`<caption>${comparisonUnit()} · ${t('same scale within this panel','ista skala unutar ovog prikaza')}</caption><thead><tr><th scope="col">${t('Check and question','Provjera i pitanje')}</th><th scope="col">${t('Estimate','Procjena')}</th><th scope="col">95% ${t('interval','interval')}</th><th scope="col">N</th></tr></thead><tbody>`+rows.map(r=>`<tr><th scope="row">${esc(checkLabels[r.key]())}<small>${esc(checkQuestions[r.key]())}</small><small>${sampleLabel(r.sample)} · ${r.finding==='F1'?'2021-01–2026-05':'2024-04–2026-05'}</small></th><td>${precise(r.b)}</td><td>${precise(r.lower)} ${t('to','do')} ${precise(r.upper)}<small>${r.lower<=0&&r.upper>=0?t('Includes zero','Obuhvaća nulu'):t('Does not include zero','Ne obuhvaća nulu')}</small></td><td>${r.N}</td></tr>`).join('')+'</tbody>';
    const direction=rows.every(r=>r.b<0)?t('All displayed point estimates are negative.','Sve prikazane točkaste procjene su negativne.'):rows.every(r=>r.b>0)?t('All displayed point estimates are positive.','Sve prikazane točkaste procjene su pozitivne.'):t('Point estimates differ in direction.','Točkaste procjene razlikuju se u smjeru.');
    const includes=rows.filter(r=>r.lower<=0&&r.upper>=0);
    byId('robustness-conclusion').textContent=direction+' '+(includes.length?t('Intervals including zero: ','Intervali koji obuhvaćaju nulu: ')+includes.map(r=>checkLabels[r.key]()).join('; ')+'.':t('The displayed intervals are on the same side of zero.','Prikazani intervali nalaze se s iste strane nule.'))+' '+t('These comparisons do not establish a causal effect or a policy target.','Ove usporedbe ne utvrđuju uzročni učinak ni cilj politike.');
  }
  renderForest();
}
function renderDiagnostics(){
  const d=selectedData();byId('diagnostic-context').textContent=`${state.period} · ${sampleLabel()}`;
  const cards=[[number(d.relevant_items),t('inflation-relevant institutional items','institucionalnih objava relevantnih za inflaciju')],[number(d.inflation_items),t('items in the inflation denominator corpus','objava u inflacijskom nazivniku')],[fixed(d.top5,1)+'%',t('of institutional weight from the five largest source contributions','institucionalnog pondera iz pet najvećih doprinosa izvora')],[fixed(d.top10,1)+'%',t('of institutional weight from the ten highest-weight items','institucionalnog pondera iz deset objava najveće težine')],[fixed(d.hhi,4),t('HHI of institutional weight across sources','HHI institucionalnog pondera među izvorima')],[number(d.weighted_sources),t('source labels with a positive institutional contribution','oznaka izvora s pozitivnim institucionalnim doprinosom')]];
  byId('diagnostic-values').innerHTML=cards.map(([value,label])=>`<article><strong>${value}</strong><p>${label}</p></article>`).join('');
  byId('diagnostic-definition').textContent=t('Each relevant item contributes its salience × potential reach. Source weights sum those item contributions; each displayed share divides a contribution by the full institutional numerator. HHI sums squared source shares. This diagnostic is distinct from the broad source-reach regression control.','Svaka relevantna objava doprinosi umnoškom istaknutosti i potencijalnog dosega. Ponder izvora zbraja doprinose njegovih objava; prikazani udio dijeli doprinos cijelim institucionalnim brojnikom. HHI zbraja kvadrate udjela izvora. Ova se dijagnostika razlikuje od regresijske kontrole ukupnog dosega izvora.');
  const domains=[...d.domains].sort(state.sort==='name'?(a,b)=>a.source.localeCompare(b.source):state.sort==='items'?(a,b)=>b.relevant_items-a.relevant_items||a.source.localeCompare(b.source):(a,b)=>b.contribution-a.contribution||a.source.localeCompare(b.source));
  byId('source-table').innerHTML=`<caption>${state.period} · ${sampleLabel()} · ${t('domain-form source labels','oznake izvora u obliku domena')}</caption><thead><tr><th scope="col">${t('Domain','Domena')}</th><th scope="col">${t('Relevant items','Relevantne objave')}</th><th scope="col">${t('Numerator contribution (%)','Doprinos brojniku (%)')}</th></tr></thead><tbody>`+domains.map(r=>`<tr><th scope="row">${esc(r.source)}</th><td>${number(r.relevant_items)}</td><td>${r.contribution>0&&r.contribution<.01?'&lt;'+fixed(.01):fixed(r.contribution,2)}%</td></tr>`).join('')+'</tbody>';
  byId('domain-scope').textContent=`${number(domains.length)} ${t('domain labels','oznaka domena')} · ${fixed(domains.reduce((sum,r)=>sum+r.contribution,0),1)}% ${t('of the institutional numerator. Other channel labels contribute to the full totals above.','institucionalnog brojnika. Oznake ostalih kanala ulaze u ukupne iznose iznad.')}`;
}
function renderPrincipalModel(){
  if(!byId('model-estimate'))return;
  const r=E.models.find(r=>r.frequency===state.frequency&&r.specification===state.specification);
  byId('model-estimate').innerHTML=`${fixed(r.estimate*100)}<span> ${t('percentage points','postotnih bodova')}</span>`;
  byId('model-ci').textContent=`95% ${t('confidence interval','interval pouzdanosti')}: ${precise(r.lo*100)} ${t('to','do')} ${precise(r.hi*100)} ${t('percentage points','postotnih bodova')}`;
  byId('model-note').textContent=`${r.N} ${r.frequency==='weekly'?'fitted weeks':'fitted months'} · January 2021–May 2026 · Primary corpus`;
  byId('model-technical').textContent=`Sample S1 · equation ${r.specification} · Newey–West intervals · p ${r.p<.001?'< 0.001':'= '+fixed(r.p,3)}`;
  byId('model-interpretation').textContent=r.lo<=0&&r.hi>=0?'This interval includes zero; this model does not establish the direction of the association.':'This interval is above zero: a wider gap corresponds to lower weighted visibility.';
  const x=v=>30+(v*100+.1)/.6*355;
  byId('model-plot').innerHTML=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 85" aria-hidden="true"><line x1="30" x2="385" y1="34" y2="34" stroke="#a9bac6"/><line x1="${x(0)}" x2="${x(0)}" y1="13" y2="49" stroke="#4f6470" stroke-dasharray="3 3"/><line x1="${x(r.lo)}" x2="${x(r.hi)}" y1="34" y2="34" stroke="#165ce0" stroke-width="4"/><circle cx="${x(r.estimate)}" cy="34" r="5" fill="#165ce0"/><text x="30" y="70" font-size="13" fill="#4f6470">−0.1</text><text x="${x(0)}" y="70" text-anchor="middle" font-size="13" fill="#4f6470">0</text><text x="385" y="70" text-anchor="end" font-size="13" fill="#4f6470">0.5 pp</text></svg>`;
  byId('model-plot').setAttribute('aria-label',`Estimate ${fixed(r.estimate*100)} percentage points; 95 percent confidence interval ${precise(r.lo*100)} to ${precise(r.hi*100)}.`);
}
function contextLinks(){
  const hashMap={overview:'grafikon',measure:'mjera',findings:'nalazi',implications:'znacenje',paper:'rad',methods:'rad',evidence:'analysis-desk','inflation-evidence':'analysis-desk','trend-evidence':'analysis-desk','expectations-evidence':'analysis-desk',centrality:'record-F4'};
  document.querySelectorAll('a[href]').forEach(a=>{
    const raw=a.dataset.originalHref||a.getAttribute('href');
    if(!raw||!/^((index|hr)\.html)([?#]|$)/.test(raw))return;
    a.dataset.originalHref=raw;
    const u=new URL(raw,location.href),targetHR=u.pathname.endsWith('hr.html'),targetLang=targetHR?'hr':'en';
    const current=stateURL();u.search=current.search;u.searchParams.set('lang',targetLang);
    // Language switches follow the current semantic section; evidence links retain their intended target.
    if(!new URL(raw,location.href).hash&&location.hash){
      const key=location.hash.slice(1);
      u.hash=targetHR?(hashMap[key]||key):(Object.entries(hashMap).find(([en,cr])=>cr===key)?.[0]||key);
    }
    a.href=u.href;
  });
}
function render(){
  updating=true;controls();renderCharts();renderEndpoints();renderRobustness();renderDiagnostics();renderPrincipalModel();contextLinks();renderDialog();updating=false;
}
const interpretations={
  share:()=>t('Higher means a larger relative weighted presence. There is no policy-performance threshold.','Više znači veću relativnu ponderiranu zastupljenost. Nema praga uspješnosti politike.'),
  gap:()=>t('Higher means lower visibility relative to the historical reference. A negative value means a share above that reference.','Više znači manju vidljivost prema povijesnoj referenci. Negativna vrijednost znači udio iznad reference.'),
  article:()=>t('Higher means more relevant institutional items relative to the inflation item count.','Više znači više relevantnih institucionalnih objava u odnosu na broj inflacijskih objava.'),
  centrality:()=>t('Higher means a more central relative network position, not more trust or influence.','Više znači središnjiji relativni mrežni položaj, a ne više povjerenja ili utjecaja.'),
  hhi:()=>t('Higher means that a smaller number of source contributions carry more of the institutional weight.','Više znači da manji broj doprinosa izvora nosi veći dio institucionalnog pondera.'),
  relevance:()=>t('Qualifying items enter the institutional numerator. Relevance is not a judgment of accuracy.','Relevantne objave ulaze u institucionalni brojnik. Relevantnost ne ocjenjuje točnost.'),
  prominence:()=>t('A higher salience score gives an item a larger contribution for the same potential reach.','Viša ocjena istaknutosti povećava doprinos uz isti potencijalni doseg.'),
  reach:()=>t('Higher potential reach gives an item more weight; it does not establish more unique readers.','Veći potencijalni doseg daje objavi veći ponder; ne utvrđuje više jedinstvenih čitatelja.'),
  expectations:()=>t('A higher balance indicates more responses tilted toward price increases; it is not an expected inflation rate in percent.','Viši saldo znači više odgovora usmjerenih prema porastu cijena; nije očekivana stopa inflacije u postotcima.')};
function findingForIndicator(key){return key==='expectations'?'F3':key==='centrality'?'F4':key==='hhi'?'F2':'F1';}
function renderDialog(){
  const dialog=byId('indicator-dialog');
  if(!state.inspect){if(dialog.open){closingDialog=true;dialog.close();closingDialog=false;}return;}
  const item=I.indicators[hr?'hr':'en'][state.inspect],d=selectedData(),r=selectedRow();
  if(!dialog.open){if(!dialogOrigin){dialogOrigin=document.activeElement;dialogScroll=scrollY;}dialog.showModal();}
  byId('indicator-choice').value=state.inspect;
  byId('indicator-title').textContent=item.title;
  byId('indicator-context').textContent=`${state.period} · ${sampleLabel()} · ${frequencyLabel()} · ${I.data_version}`;
  byId('indicator-value').textContent=state.inspect==='prominence'?t('Rule weights: 0.30 / 0.25 / 0.20 / 0.25','Ponderi pravila: 0,30 / 0,25 / 0,20 / 0,25'):state.inspect==='relevance'?`${number(d.relevant_items)} ${t('relevant institutional items','relevantnih institucionalnih objava')}`:state.inspect==='reach'?`${number(d.denominator-1)} ${t('potential-reach units in the inflation corpus','jedinica potencijalnog dosega u inflacijskom korpusu')}`:state.inspect==='expectations'?`${fixed(r.expectations,1)} ${t('survey balance points','bodova anketnog salda')}`:`${fixed(d[state.inspect],['hhi','centrality'].includes(state.inspect)?4:3)} ${units[state.inspect]}`;
  const scope=`${sampleLabel()} · ${visibleRows()[0].period}–${visibleRows().at(-1).period}. `+(state.sample==='common'?t('Both corpus sums use the same 258 source labels, selected by presence in 2023 and July–December 2024.','Oba korpusa koriste istih 258 oznaka izvora odabranih prema prisutnosti u 2023. i srpnju – prosincu 2024.'):t('Institutional matching includes formal names, acronyms and generic central-bank references across the study’s monitored channels.','Institucionalno prepoznavanje uključuje formalne nazive, kratice i generičke reference na središnju banku u praćenim kanalima.'));
  const inputContext=state.inspect==='share'?` ${t('Selected month: weighted numerator','Odabrani mjesec: ponderirani brojnik')} ${new Intl.NumberFormat(hr?'hr-HR':'en-GB',{maximumFractionDigits:3}).format(d.numerator)}; ${t('denominator including +1','nazivnik s uključenim +1')}: ${number(d.denominator)}.`:state.inspect==='article'?` ${t('Selected month','Odabrani mjesec')}: 100 × ${number(d.relevant_items)} / (${number(d.inflation_items)} + 1).`:state.inspect==='gap'?` ${t('Selected source definition: baseline','Odabrana definicija izvora: referentni udio')} ${fixed(d.share+d.gap,3)}%; ${t('current share','tekući udio')} ${fixed(d.share,3)}%.`:'';
  const entries=[[t('Meaning','Značenje'),item.meaning],[t('Construction','Izračun'),item.construction+inputContext],[t('Scope','Obuhvat'),state.inspect==='expectations'?t('Monthly consumer survey; the source selection changes the media series, not the survey population.','Mjesečna anketa potrošača; izbor izvora mijenja medijsku seriju, a ne anketnu populaciju.'):scope],[t('Interpretation','Tumačenje'),interpretations[state.inspect]()],[t('Limitations','Ograničenja'),item.limitations],[t('Evidence','Dokazi'),`${findingForIndicator(state.inspect)} · ${I.method_version}. `+t('The selected-month chart, aggregate values and fixed finding record retain this context.','Grafikon odabranog mjeseca, agregati i stalni zapis nalaza zadržavaju ovaj kontekst.')]];
  byId('indicator-details').innerHTML=entries.map(([label,value])=>`<dt>${label}</dt><dd>${esc(value)}</dd>`).join('')+`<dt>${t('Values and methods','Vrijednosti i metode')}</dt><dd><a href="data/inspection.json" download>${t('Inspection data · JSON ↓','Podatci za pregled · JSON ↓')}</a></dd>`;
}
function openInspector(key){dialogOrigin=document.activeElement;dialogScroll=scrollY;dialogReturnMode=state.mode==='compare'?'compare':'read';setState({inspect:key,mode:'inspect'});byId('close-indicator').focus({preventScroll:true});}
function closeInspector(){
  const focus=dialogOrigin,y=dialogScroll;
  state=validate({...state,inspect:'',mode:dialogReturnMode});closingDialog=true;byId('indicator-dialog').close();closingDialog=false;saveURL('replace');render();
  focus?.focus({preventScroll:true});window.scrollTo({top:y,behavior:'instant'});
}
async function copy(text){
  try{await navigator.clipboard.writeText(text);announce(t('Copied. The link preserves the complete selected context.','Kopirano. Poveznica čuva cijeli odabrani kontekst.'));}
  catch{
    const field=byId('copy-fallback');field.hidden=false;field.value=text;
    if(byId('indicator-dialog').open)byId('indicator-dialog').append(field);else byId('copy-fallback-area').append(field);
    field.focus();field.select();announce(t('Copy the selected text below.','Kopirajte označeni tekst ispod.'));
  }
}
function download(text,type,name){const url=URL.createObjectURL(new Blob([text],{type})),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1500);announce(t('Exported ','Izvezeno ')+name+'.');}
const csvCell=v=>'"'+String(v).replace(/"/g,'""')+'"';
const csv=rows=>rows.map(row=>row.map(csvCell).join(',')).join('\r\n');
function openEvidence(){let id=location.hash.slice(1);try{id=decodeURIComponent(id);}catch{}const target=byId(id);if(target?.tagName==='DETAILS')target.open=true;}

document.querySelectorAll('[data-js]').forEach(el=>el.hidden=false);
for(const key of ['window','metric','sample','period','frequency','specification'])byId(key)?.addEventListener('change',event=>setState({[key]:event.target.value}));
document.querySelectorAll('[data-bind]').forEach(el=>el.addEventListener('change',()=>setState({[el.dataset.bind]:el.value})));
byId('compare-from').addEventListener('change',event=>setState({from:event.target.value}));
byId('compare-to').addEventListener('change',event=>setState({to:event.target.value}));
byId('compare-finding').addEventListener('change',event=>setState({finding:event.target.value,mode:'compare'}));
byId('source-sort').addEventListener('change',event=>setState({sort:event.target.value}));
byId('toggle-sample').addEventListener('click',()=>setState({sample:state.sample==='primary'?'common':'primary'}));
document.querySelectorAll('[data-lens]').forEach(button=>button.addEventListener('click',()=>{
  const presets={visibility:{window:'new',metric:'share',sample:'primary',frequency:'monthly',finding:'F2'},composition:{window:'new',metric:'share',sample:'common',frequency:'monthly',finding:'F2'},inflation:{window:'all',metric:'share',sample:'primary',finding:'F1'},understanding:{window:'all',metric:'article',sample:'primary',finding:'F3'}};
  setState({...presets[button.dataset.lens],lens:button.dataset.lens,mode:'compare',from:'2024-04',to:'2026-05'});
}));
document.querySelectorAll('[data-mode]').forEach(button=>button.addEventListener('click',()=>button.dataset.mode==='inspect'?openInspector(state.metric):setState({mode:button.dataset.mode})));
document.querySelectorAll('[data-open-compare]').forEach(button=>button.addEventListener('click',()=>{setState({mode:'compare'}, {anchor:'analysis-desk'});byId('analysis-desk').scrollIntoView({block:'start'});}));
byId('comparison').addEventListener('toggle',()=>{if(updating)return;const next=byId('comparison').open?'compare':'read';if(state.mode!==next&&state.mode!=='inspect'){state.mode=next;saveURL('replace');document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===next)));renderForest();}});
byId('inspect-current').addEventListener('click',()=>openInspector(state.metric));
document.querySelectorAll('[data-inspect]').forEach(button=>button.addEventListener('click',()=>openInspector(button.dataset.inspect)));
byId('indicator-choice').replaceChildren(...Object.entries(I.indicators[hr?'hr':'en']).map(([key,item])=>new Option(item.title,key)));
byId('indicator-choice').addEventListener('change',event=>setState({inspect:event.target.value},{historyMode:'replace'}));
byId('close-indicator').addEventListener('click',closeInspector);
byId('indicator-dialog').addEventListener('cancel',event=>{event.preventDefault();closeInspector();});
byId('indicator-dialog').addEventListener('close',()=>{if(!closingDialog&&state.inspect)closeInspector();});
byId('copy-indicator').addEventListener('click',()=>copy(stateURL(root).href));
byId('indicator-evidence').addEventListener('click',()=>{const finding=findingForIndicator(state.inspect);closeInspector();setState({finding,mode:'compare'},{anchor:`record-${finding}`});byId('record-'+finding).open=true;byId('record-'+finding).scrollIntoView({block:'start'});});
document.querySelectorAll('[data-copy]').forEach(button=>button.addEventListener('click',()=>copy(stateURL(button.dataset.copy).href)));
document.querySelectorAll('[data-record-compare]').forEach(button=>button.addEventListener('click',()=>{setState({finding:button.dataset.recordCompare,mode:'compare'},{anchor:'analysis-desk'});byId('analysis-desk').scrollIntoView({block:'start'});}));
document.querySelectorAll('[data-cite]').forEach(button=>button.addEventListener('click',()=>{const r=I.findings.find(r=>r.id===button.dataset.cite);copy(`Palić, P., & Sikić, L. (2026). ${r.id}: ${hr?r.finding_hr:r.finding} ${hr?r.reference_hr:r.reference}. ${t('Extended manuscript, 17 September 2026.','Prošireni rukopis, 17. rujna 2026.')} ${t('Data','Podatci')} ${r.data_version}; ${t('method','metoda')} ${r.method_version}; ${t('presentation','prezentacija')} ${I.version}. ${stateURL('record-'+r.id).href}`);}));
byId('reset-view').addEventListener('click',()=>{state={...defaults};saveURL('push');render();announce(t('Selections reset to full history, weighted share and the primary weekly model.','Vraćeno cijelo razdoblje, ponderirani udio i primarni tjedni model.'));});
byId('export-csv').addEventListener('click',()=>{
  const rows=visibleRows(),table=[['period','sample','weighted_share_percent','attention_gap_pp','hicp_percent','selected_metric','selected_value','selected_unit','selected_month','model_frequency','model_specification','language','data_version','method_version','presentation_version'],...rows.map(r=>[r.period,state.sample,r.share,r.gap*100,r.inflation,state.metric,state.metric==='gap'?r.gap*100:r[state.metric],state.metric==='gap'?'percentage_points':state.metric==='share'||state.metric==='article'?'percent':'index',state.period,state.frequency,state.specification,hr?'hr':'en',I.data_version,I.method_version,I.version])];
  download(csv(table),'text/csv;charset=utf-8',`hnb-selected-period-${rows[0].period}-${rows.at(-1).period}-${state.sample}.csv`);
});
byId('export-svg').addEventListener('click',()=>{
  const rows=visibleRows(),wrap=(s,y)=>s.replace('<svg ',`<svg x="35" y="${y}" width="1130" height="220" `),label=`${titles[state.metric]} (${units[state.metric]})`;
  const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="760" viewBox="0 0 1200 760"><title>${esc(t('HNB selected chart view','HNB odabrani prikaz'))}</title><metadata>${esc(JSON.stringify({state,data_version:I.data_version,method_version:I.method_version,presentation_version:I.version,language:hr?'hr':'en'}))}</metadata><rect width="1200" height="760" fill="#112838"/><g fill="white" font-family="Arial"><text x="40" y="44" font-size="26">${esc(t('HNB in Croatia’s inflation debate','HNB u hrvatskoj raspravi o inflaciji'))}</text><text x="40" y="78" font-size="17">${esc(sampleLabel())} · ${rows[0].period}–${rows.at(-1).period} · ${t('selected month','odabrani mjesec')}: ${state.period}</text><text x="40" y="115" font-size="18">${esc(label)}</text>${wrap(timelineSVG(rows,state.metric,1130,state.period),120)}<text x="40" y="380" font-size="18">HICP · ${t('year-on-year','godišnja stopa')} (%)</text>${wrap(timelineSVG(rows,'inflation',1130,state.period),385)}<text x="40" y="641" font-size="16">${esc(t('Constructed media measure; potential reach is not observed readership. Separate scales.','Konstruirani medijski pokazatelj; potencijalni doseg nije čitanost. Zasebne skale.'))}</text><text x="40" y="675" font-size="16">Palić &amp; Sikić · ${I.data_version} · ${I.version}</text><text x="40" y="709" font-size="16">${esc(t('Model context','Kontekst modela'))}: ${state.frequency} / ${state.specification} · ${state.finding} · ${state.from} → ${state.to}</text></g></svg>`;
  download(svg,'image/svg+xml;charset=utf-8',`hnb-selected-${state.metric}-${state.sample}-${rows[0].period}-${rows.at(-1).period}.svg`);
});
byId('export-sources').addEventListener('click',()=>download(csv([['period','sample','domain','institutional_items','relevant_items','institutional_numerator_contribution_percent','data_version','presentation_version'],...selectedData().domains.map(d=>[state.period,state.sample,d.source,d.items,d.relevant_items,d.contribution,I.data_version,I.version])]),'text/csv;charset=utf-8',`hnb-domain-contributions-${state.sample}-${state.period}.csv`));
byId('export-comparison').addEventListener('click',()=>{
  const from=I.observations.find(r=>r.period===state.from)[state.sample][state.metric],to=I.observations.find(r=>r.period===state.to)[state.sample][state.metric];
  const valueUnit=state.metric==='gap'?'percentage_points':['share','article'].includes(state.metric)?'percent':'index_units';
  const differenceUnit=['share','article','gap'].includes(state.metric)?'percentage_points':'index_units';
  const metadata=[I.data_version,I.method_version,I.version,hr?'hr':'en',state.metric,state.period,state.sample,state.from,state.to,from,to,to-from,valueUnit,differenceUnit];
  const metadataHeaders=['data_version','method_version','presentation_version','language','chart_metric','selected_month','chart_sample','comparison_from','comparison_to','comparison_from_value','comparison_to_value','comparison_difference','comparison_value_unit','comparison_difference_unit'];
  const table=state.finding==='F3'?[['finding','assignment','frequency','future_horizons_passing_correction','unit',...metadataHeaders],...E.expectations.map(r=>['F3',r.label,r.frequency,r.significant_horizons.join(';')||'none',r.frequency==='weekly'?'weeks':'months',...metadata])]:[['finding','check','model_frequency','model_sample','estimate','ci_lower','ci_upper','units','N','source_table','source_selection',...metadataHeaders],...comparisonRows().map(r=>[state.finding,r.key,r.frequency,r.sample,r.b,r.lower,r.upper,r.units,r.N,r.file,r.selection,...metadata])];
  download(csv(table),'text/csv;charset=utf-8',`hnb-${state.finding}-${state.frequency}-comparison.csv`);
});
window.addEventListener('popstate',()=>{state=fromURL();render();openEvidence();});
window.addEventListener('hashchange',()=>{openEvidence();contextLinks();});
document.querySelectorAll('a[data-evidence]').forEach(a=>a.addEventListener('click',()=>{const target=byId(a.hash.slice(1));if(target?.tagName==='DETAILS')target.open=true;}));

const contents=document.querySelector('.contents');
const sectionLinks=[...document.querySelectorAll('.contents a[href^="#"]')];
function activeContents(){const cutoff=(contents?.getBoundingClientRect().height||0)+Math.min(innerHeight*.2,160);let active=sectionLinks[0];for(const a of sectionLinks){const section=byId(a.hash.slice(1));if(section&&section.getBoundingClientRect().top<=cutoff)active=a;}sectionLinks.forEach(a=>{if(a===active)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});}
let scrollFrame=false;window.addEventListener('scroll',()=>{if(scrollFrame)return;scrollFrame=true;requestAnimationFrame(()=>{scrollFrame=false;activeContents();});},{passive:true});
if(contents)new ResizeObserver(()=>{document.documentElement.style.setProperty('--contents-height',`${Math.ceil(contents.getBoundingClientRect().height)}px`);activeContents();}).observe(contents);
let chartWidth=0;new ResizeObserver(entries=>{const width=Math.round(entries[0].contentRect.width);if(width!==chartWidth){chartWidth=width;renderCharts();renderForest();}}).observe(byId('gap-chart'));
let forestWidth=0;new ResizeObserver(entries=>{const width=Math.round(entries[0].contentRect.width);if(width&&width!==forestWidth){forestWidth=width;renderForest();}}).observe(byId('robustness-chart'));
new ResizeObserver(entries=>byId('indicator-dialog').style.setProperty('--dialog-header-height',`${Math.ceil(entries[0].target.getBoundingClientRect().height)}px`)).observe(document.querySelector('.dialog-header'));
saveURL('replace');render();openEvidence();activeContents();
