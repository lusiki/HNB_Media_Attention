// Real browser checks against approved aggregate intersections and exported files.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'));
const site=path.resolve(__dirname,'..'),base='http://127.0.0.1:8765/',data=JSON.parse(fs.readFileSync(path.join(site,'dist/data/media/media.json'),'utf8'));
let browser;
(async()=>{
 browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const ctx=await browser.newContext({acceptDownloads:true}),page=await ctx.newPage(),errors=[],external=[],report={};
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(!r.url().startsWith(base)&&!r.url().startsWith('data:'))external.push(r.url());});
 await ctx.grantPermissions(['clipboard-read','clipboard-write'],{origin:base});
 for(const lang of ['en','hr'])for(const width of [1440,768,360]){
  await page.setViewportSize({width,height:1000});await page.goto(base+(lang==='hr'?'hr.html':'index.html'));
  assert.equal(await page.locator('html').getAttribute('lang'),lang);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,`${lang} ${width} overflow`);
  assert.equal(await page.locator('#media-to').inputValue(),'2026-08');assert.equal(await page.locator('#media-source').inputValue(),'all');
  assert.equal(await page.locator('#media-chart .media-observed-series').count(),1);assert.equal(await page.locator('#media-numeric-rows tr').count(),68);
  assert.match(await page.locator('#media-view-status').innerText(),new RegExp(lang==='hr'?'33.235':'33,235'));
  await page.screenshot({path:path.join(site,'qa',`media-${lang}-${width}-top.png`)});
  await page.locator('#vidljivost').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(site,'qa',`media-${lang}-${width}-chart.png`)});
  await page.selectOption('#media-metric','rate');await page.selectOption('#media-source','stable');
  const first=await page.locator('#media-numeric-rows tr').first().textContent();assert.ok(first.includes(String(data.monthly[0].stable_hnb_count)));
  await page.locator('#media-definition-open').click();assert.equal(await page.locator('#media-definition').evaluate(e=>e.open),true);
  for(let i=0;i<12;i++)await page.keyboard.press('Tab');assert.equal(await page.evaluate(()=>!!document.activeElement.closest('dialog')),true);
  await page.keyboard.press('Escape');assert.equal(await page.evaluate(()=>document.activeElement.id),'media-definition-open');
  await page.locator('#media-reset').click();await page.selectOption('#media-to','2026-09');assert.equal(await page.locator('.partial-period').count(),1);
  await page.evaluate(()=>document.body.style.zoom='2');assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true,`200% ${lang} ${width} `+JSON.stringify(await page.evaluate(()=>[...document.querySelectorAll("body *")].filter(e=>e.getBoundingClientRect().right>innerWidth+1&&!e.closest(".table-wrap")&&!e.closest(".contents")).map(e=>({tag:e.tagName,cls:String(e.className),width:e.getBoundingClientRect().width,right:e.getBoundingClientRect().right,text:e.textContent.slice(0,70)})).slice(0,15))));
  await page.evaluate(()=>document.body.style.zoom='');
  report[lang+'-'+width]={default_counts:true,stable_rate:true,modal_keyboard:true,partial_endpoint:true,zoom_200:true};
 }
 await page.setViewportSize({width:1440,height:1000});
 await page.goto(base+'?m_from=2024-02&m_to=2025-03&m_source=index.hr&m_metric=rate&m_sort=name#vidljivost');
 const expected=data.source_monthly.filter(r=>r.source_id==='index.hr'&&r.period>='2024-02'&&r.period<='2025-03');
 assert.equal(await page.locator('#media-numeric-rows tr').count(),expected.length);
 const [download]=await Promise.all([page.waitForEvent('download'),page.locator('#media-export-csv').click()]);await download.saveAs(path.join(site,'qa/media-selected.csv'));
 const csv=fs.readFileSync(path.join(site,'qa/media-selected.csv'),'utf8').trim().split(/\r?\n/).map(l=>l.slice(1,-1).split('\",\"'));
 assert.equal(csv.length,expected.length+1);for(let i=0;i<expected.length;i++){assert.equal(csv[i+1][0],expected[i].period);assert.equal(Number(csv[i+1][2]),expected[i].hnb_count);assert.equal(Number(csv[i+1][4]),expected[i].background_i);assert.equal(Number(csv[i+1][5]),expected[i].hnb_i/expected[i].background_i*10000);}
 const [svgdl]=await Promise.all([page.waitForEvent('download'),page.locator('#media-export-svg').click()]);await svgdl.saveAs(path.join(site,'qa/media-selected.svg'));const svg=fs.readFileSync(path.join(site,'qa/media-selected.svg'),'utf8');assert.match(svg,/index.hr/);assert.match(svg,/2024-02/);assert.match(svg,/per 10,000/i);assert.match(svg,/AEM_web_query_i_publications_v1/);
 await page.locator('#media-copy').click();const copied=await page.evaluate(()=>navigator.clipboard.readText());assert.equal(new URL(copied).searchParams.get('m_source'),'index.hr');
 await Promise.all([page.waitForNavigation({waitUntil:'load'}),page.locator('#media-language').click()]);assert.equal(await page.locator('html').getAttribute('lang'),'hr');assert.equal(await page.locator('#media-source').inputValue(),'index.hr');assert.equal(new URL(page.url()).hash,'#vidljivost');
 await page.reload();assert.equal(await page.locator('#media-from').inputValue(),'2024-02');await page.selectOption('#media-source','all');await page.goBack();await page.waitForFunction(()=>document.querySelector('#media-source').value==='index.hr');assert.equal(await page.locator('#media-source').inputValue(),'index.hr');await page.goForward();await page.waitForFunction(()=>document.querySelector('#media-source').value==='all');assert.equal(await page.locator('#media-source').inputValue(),'all');
 const names=await page.locator('#media-source-rows th').allTextContents();assert.deepEqual(names,[...names].sort((a,b)=>a.localeCompare(b)));
 await page.evaluate(()=>{navigator.clipboard.writeText=async()=>{throw new Error('disabled');};});await page.locator('#media-copy').click();assert.equal(await page.locator('#media-copy-fallback').isVisible(),true);
 // Observed zero and absent-source month must be distinct, and exports must preserve null.
 const zero=data.source_monthly.find(r=>r.hnb_count===0&&r.background_i>0),allPeriods=data.monthly.map(r=>r.period);
 let absent;for(const id of data.selector_sources){const available=new Set(data.source_monthly.filter(r=>r.source_id===id).map(r=>r.period));const period=allPeriods.find(p=>!available.has(p));if(period){absent={id,period};break;}}
 for(const [source,period,phrase] of [[zero.source_id,zero.period,'Nema objava'],[absent.id,absent.period,'Podaci nisu dostupni']]){
  await page.goto(base+`hr.html?m_source=${source}&m_from=${period}&m_to=${period}`);assert.match(await page.locator('#media-empty').innerText(),new RegExp(phrase));
  if(phrase.startsWith('Podaci')){const [dl]=await Promise.all([page.waitForEvent('download'),page.locator('#media-export-csv').click()]);await dl.saveAs(path.join(site,'qa/media-unavailable.csv'));const text=fs.readFileSync(path.join(site,'qa/media-unavailable.csv'),'utf8');assert.match(text,/,"","","","","unavailable"/);assert.equal(await page.locator('.media-observed-series').count(),0);}
 }
 await page.goto(base+'?m_source=bad&m_metric=bad&m_from=bad&m_to=bad&m_sort=bad');assert.equal(await page.locator('#media-source').inputValue(),'all');assert.equal(await page.locator('#media-metric').inputValue(),'count');
 await page.goto(base+'?m_from=2026-08&m_to=2021-01');assert.equal(await page.locator('#media-from').inputValue(),'2021-01');
 await page.locator('#media-reset').click();assert.equal(await page.locator('#media-to').inputValue(),'2026-08');
 await page.goto(base+'?window=new&metric=gap&period=2024-04#overview');assert.match(page.url(),/studies\/inflation/);assert.equal(await page.locator('#period').inputValue(),'2024-04');
 await page.goto(base+'hr.html#pregled');assert.equal(new URL(page.url()).pathname,'/studies/inflation/hr.html');assert.equal(new URL(page.url()).hash,'#pregled');
 for(const name of ['index.html','hr.html','downloads/hnb-media-overview-hr.html','downloads/hnb-media-brief-en.html','downloads/hnb-media-brief-hr.html','downloads/hnb-media-slides-hr.html']){
  await page.goto(base+name);const refs=await page.locator('a[href],script[src],link[href]').evaluateAll(es=>es.map(e=>e.href||e.src));for(const ref of new Set(refs)){if(!ref.startsWith(base))continue;const res=await page.request.get(ref.split('#')[0]);assert.equal(res.status(),200,'Broken '+ref);}
 }
 await page.goto(base+'downloads/hnb-media-slides-hr.html');await page.locator('#slide-mode').click();assert.equal(await page.locator('.slide.active').count(),1);await page.keyboard.press('ArrowRight');assert.equal(await page.locator('.slide.active').getAttribute('id'),'slide-2');await page.keyboard.press('Escape');assert.equal(await page.locator('body').evaluate(e=>e.classList.contains('presenting')),false);
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:360,height:1000}}),fallback=await nojs.newPage();await fallback.goto(base+'hr.html');assert.equal(await fallback.locator('#media-numeric-rows tr').count(),68);assert.equal(await fallback.locator('.media-observed-series').count(),1);assert.equal(await fallback.locator('#media-from').isVisible(),false);await nojs.close();
 await page.goto(base+'hr.html');await page.emulateMedia({media:'print',reducedMotion:'reduce'});assert.equal(await page.locator('#media-from').isVisible(),false);await page.screenshot({path:path.join(site,'qa/media-print.png'),fullPage:true});
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);fs.writeFileSync(path.join(site,'qa/media-browser-checks.json'),JSON.stringify({viewports:report,source_date_intersections:true,denominator_export_arithmetic:true,svg_export:true,clipboard_and_fallback:true,history_language_restore:true,invalid_reverse_reset:true,zero_vs_unavailable:true,legacy_redirects:true,local_links:true,slide_mode:true,no_js:true,print_reduced_motion:true,console_errors:errors,external_requests:external},null,2));
 console.log('Broad-media browser checks passed.');await browser.close();
})().catch(async e=>{console.error(e);await browser?.close();process.exitCode=1;});
