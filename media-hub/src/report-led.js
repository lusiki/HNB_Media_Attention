'use strict';
(() => {
  const data = JSON.parse(document.querySelector('#page-data').textContent);
  const hr = document.documentElement.lang === 'hr';
  const format = new Intl.NumberFormat(hr ? 'hr-HR' : 'en-GB');

  const carousel = document.querySelector('.headline-carousel');
  const track = carousel.querySelector('.finding-track');
  const cards = [...carousel.querySelectorAll('.finding-card')];
  const selectors = [...carousel.querySelectorAll('.finding-selector')];
  const previous = carousel.querySelector('.finding-prev');
  const next = carousel.querySelector('.finding-next');
  const status = carousel.querySelector('.finding-status');
  let activeFinding = 0;
  let announcementTimer;
  function syncFinding() {
    activeFinding = Math.max(0, Math.min(cards.length-1, Math.round(track.scrollLeft/track.clientWidth)));
    selectors.forEach((button, index) => button.setAttribute('aria-pressed', String(index===activeFinding)));
    cards.forEach((card, index) => card.setAttribute('aria-hidden', String(index!==activeFinding)));
    previous.setAttribute('aria-disabled', String(activeFinding===0));
    next.setAttribute('aria-disabled', String(activeFinding===cards.length-1));
  }
  function goToFinding(index) {
    const target = Math.max(0, Math.min(cards.length-1,index));
    track.scrollTo({left:target*track.clientWidth, behavior:matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
  }
  previous.addEventListener('click', () => goToFinding(activeFinding-1));
  next.addEventListener('click', () => goToFinding(activeFinding+1));
  selectors.forEach((button,index) => button.addEventListener('click', () => goToFinding(index)));
  carousel.addEventListener('keydown', event => {
    if (['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) {
      event.preventDefault();
      goToFinding(event.key==='Home' ? 0 : event.key==='End' ? cards.length-1 : activeFinding+(event.key==='ArrowRight' ? 1 : -1));
    }
  });
  track.addEventListener('scroll', () => {
    syncFinding();
    clearTimeout(announcementTimer);
    announcementTimer = setTimeout(() => {
      const card = cards[activeFinding];
      status.textContent = `${card.getAttribute('aria-label')}. ${card.querySelector('.headline-number').textContent}. ${card.querySelector('.finding-copy').textContent}`;
    },180);
  }, {passive:true});
  let trackWidth = track.clientWidth;
  new ResizeObserver(() => {
    if (trackWidth===track.clientWidth) return;
    trackWidth=track.clientWidth;
    track.scrollTo({left:activeFinding*trackWidth,behavior:'instant'});
    syncFinding();
  }).observe(track);
  carousel.classList.add('enhanced');
  carousel.querySelector('.finding-controls').hidden = false;
  syncFinding();

  const slider = document.querySelector('#month-range');
  const reading = document.querySelector('#month-reading');
  const hits = [...document.querySelectorAll('.month-hit')];
  function inspect(index, updateSlider = false) {
    const row = data.months[index];
    if (!row) return;
    reading.replaceChildren(document.createTextNode(row.label+' '));
    const value = document.createElement('strong');
    value.textContent = format.format(row.count);
    reading.append(value);
    if (updateSlider) slider.value = index;
    if (Number(slider.value) === index) slider.setAttribute('aria-valuetext', row.label+': '+format.format(row.count)+' '+(hr ? 'objava' : 'publications'));
    for (const svg of document.querySelectorAll('.chart-container svg')) {
      const hit = svg.querySelector(`[data-month="${index}"]`);
      const point = svg.querySelector('.inspection-point');
      point.setAttribute('cx', hit.getAttribute('cx'));
      point.setAttribute('cy', hit.getAttribute('cy'));
      point.setAttribute('visibility', 'visible');
    }
  }
  document.querySelector('.trend-inspector').hidden = false;
  slider.addEventListener('input', () => inspect(Number(slider.value)));
  slider.addEventListener('focus', () => inspect(Number(slider.value)));
  for (const hit of hits) {
    hit.addEventListener('pointerenter', () => inspect(Number(hit.dataset.month)));
    hit.addEventListener('click', () => inspect(Number(hit.dataset.month), true));
  }
  document.querySelector('.chart-container').addEventListener('pointerleave', () => inspect(Number(slider.value)));

  document.querySelectorAll('[role="tablist"]').forEach(tablist => {
    const tabs = [...tablist.querySelectorAll('[role="tab"]')];
    function selectTab(selected, focus = false) {
      tabs.forEach(tab => {
        const active = tab === selected;
        tab.setAttribute('aria-selected', String(active));
        tab.tabIndex = active ? 0 : -1;
        document.getElementById(tab.getAttribute('aria-controls')).hidden = !active;
      });
      if (focus) selected.focus();
    }
    tablist.hidden = false;
    selectTab(tabs[0]);
    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => selectTab(tab));
      tab.addEventListener('keydown', event => {
        if (['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) {
          event.preventDefault();
          const next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length-1 : (index+(event.key === 'ArrowRight' ? 1 : -1)+tabs.length)%tabs.length;
          selectTab(tabs[next],true);
        }
      });
    });
  });

  const decimal = new Intl.NumberFormat(hr ? 'hr-HR' : 'en-GB', {minimumFractionDigits:1, maximumFractionDigits:1});
  const quarterSelect = document.querySelector('#quarter-select');
  function showQuarter() {
    const index = Number(quarterSelect.value);
    const row = data.quarters[index];
    document.querySelector('#quarter-label').textContent = quarterSelect.selectedOptions[0].textContent;
    for (const key of ['inflation','credit']) {
      document.querySelector(`#${key}-share`).textContent = decimal.format(100*row[key]/row.denominator)+'%';
      document.querySelector(`#${key}-count`).textContent = hr
        ? `${format.format(row[key])} / ${format.format(row.denominator)} tekstova`
        : `${format.format(row[key])} of ${format.format(row.denominator)} texts`;
    }
    const difference = 100*(row.inflation-row.credit)/row.denominator;
    const leader = difference > 0 ? (hr ? 'Inflacija' : 'Inflation') : (hr ? 'Kredit' : 'Credit');
    document.querySelector('#quarter-gap').textContent = difference === 0
      ? (hr ? 'Obje riječi imaju jednak udio.' : 'Both words have the same share.')
      : `${leader} ${hr ? 'ima veći udio za' : 'has a larger share by'} ${decimal.format(Math.abs(difference))} ${hr ? 'postotnih bodova.' : 'percentage points.'}`;
    const guide = document.querySelector('.quarter-guide');
    guide.setAttribute('x1',42+index*540/(data.quarters.length-1));
    guide.setAttribute('x2',42+index*540/(data.quarters.length-1));
    document.querySelectorAll('.word-dot').forEach(dot => dot.setAttribute('r', Number(dot.dataset.quarter)===index ? '6' : '4'));
  }
  document.querySelector('.quarter-control').hidden = false;
  quarterSelect.addEventListener('change',showQuarter);
  showQuarter();
  document.querySelector('.language').addEventListener('click', event => {
    const link = new URL(event.currentTarget.href);
    link.hash = location.hash;
    event.currentTarget.href = link.href;
  });
})();
