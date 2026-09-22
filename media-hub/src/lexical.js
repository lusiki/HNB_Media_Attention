(() => {
  'use strict';
  const data = JSON.parse(document.querySelector('#lexical-data').textContent);
  const select = document.querySelector('#lexical-term'), body = document.querySelector('#lexical-quarter-rows');
  const hr = document.documentElement.lang === 'hr', t = (en, cr) => hr ? cr : en;
  const number = new Intl.NumberFormat(hr ? 'hr-HR' : 'en-GB');
  const percent = new Intl.NumberFormat(hr ? 'hr-HR' : 'en-GB', {style:'percent',maximumFractionDigits:1});
  document.querySelectorAll('[data-lexical-js]').forEach(x => x.hidden = false);
  function render(fromURL = false) {
    const params = new URLSearchParams(location.search), desired = fromURL ? params.get('lexical') : select.value;
    const valid = [...select.options].some(o => o.value === desired);
    select.value = valid ? desired : 'term:banka';
    const [kind, term] = select.value.split(':');
    body.replaceChildren();
    for (const r of data.quarterly.filter(r => r.kind === kind && r.term === term)) {
      const row = document.createElement('tr');
      const frequency = r.status === 'below_reporting_threshold' ? t('Below reporting threshold','Ispod praga prikaza') : r.frequency === null ? t('Unavailable','Nedostupno') : percent.format(r.frequency);
      [r.quarter+(r.coverage_state === 'complete'?'':' *'),number.format(r.count),number.format(r.denominator),frequency,r.regime === 'legacy'?t('Before 2024','Prije 2024.'):t('From 2024','Od 2024.')].forEach((v,i) => {const cell=document.createElement(i?'td':'th');if(!i)cell.scope='row';cell.textContent=v;row.append(cell);});
      body.append(row);
    }
    document.querySelector('#lexical-selection').textContent = term+' · '+t('quarterly document presence','tromjesečna prisutnost u tekstovima')+(desired&&!valid?' · '+t('Invalid selection reset','Neispravan odabir vraćen na početni'): '');
    if(!fromURL){params.set('lexical',select.value);history.pushState(null,'','?'+params.toString()+location.hash);}
    const link = document.querySelector('#media-language');
    if(link){const u=new URL(link.href);u.searchParams.set('lexical',select.value);link.href=u.href;}
  }
  select.addEventListener('change',()=>render());window.addEventListener('popstate',()=>render(true));render(true);
  // The main controller rewrites its language link after chart selections.
  document.querySelector('#media-language').addEventListener('click',e=>{const u=new URL(e.currentTarget.href);u.searchParams.set('lexical',select.value);e.currentTarget.href=u.href;});
})();
