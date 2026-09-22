// Verify the new views against independently prepared aggregate fixtures.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'));
const site=path.resolve(__dirname,'..'),base='http://127.0.0.1:8765/',data=JSON.parse(fs.readFileSync(path.join(site,'dist/data/media/media.json'),'utf8'));
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-9,`${a} != ${b}`);
let browser;
(async()=>{
 browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const context=await browser.newContext({acceptDownloads:true}),page=await context.newPage(),errors=[],checks=[];
 page.on('pageerror',e=>errors.push(e.message));
 const exportCSV=async selector=>{const [d]=await Promise.all([page.waitForEvent('download'),page.locator(selector).click()]);const p=await d.path();const lines=fs.readFileSync(p,'utf8').trim().split(/\r?\n/).map(l=>l.slice(1,-1).split('\",\"'));const header=lines.shift();return lines.map(r=>Object.fromEntries(header.map((h,i)=>[h,r[i]])));};
 for(const lang of ['en','hr'])for(const width of [1440,768,360]){
  await page.setViewportSize({width,height:1000});await page.goto(base+(lang==='hr'?'hr.html':'index.html'));
  assert.equal(await page.locator('#composition-chart polyline').count(),3);
  assert.equal(await page.locator('#composition-rows tr').count(),68);
  assert.match(await page.locator('#V5 .indicator-value').innerText(),lang==='hr'?/38,44/:/38.44/);
  await page.locator('#media-indicators').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(site,'qa',`extensions-${lang}-${width}.png`)});
  await page.locator('#composition-chart').screenshot({path:path.join(site,'qa',`composition-${lang}-${width}.png`)});
  await page.locator('#latest-edition').screenshot({path:path.join(site,'qa',`latest-${lang}-${width}.png`)});
  await page.locator('#izvori').scrollIntoViewIfNeeded();await page.selectOption('#media-sort','rate');
  assert.equal(await page.locator('#media-source-rows th').first().innerText(),'tockanai.hr');
  assert.match(await page.locator('#media-source-scope').innerText(),/78/);
  const sourceExport=await exportCSV('#media-export-sources');
  const fixtures=data.extensions.source_rates.filter(r=>r.period_id==='pooled');
  assert.equal(sourceExport.length,fixtures.length);
  for(const r of sourceExport){const f=fixtures.find(f=>f.source_id===r.source_id);assert.equal(+r.hnb_i,f.hnb_i);assert.equal(+r.background_i,f.background_i);close(+r.rate_per_10000,f.rate_per_10000);assert.equal(r.rank,f.rank===null?'':String(f.rank));}
  for(const window of ['legacy','api']){
   await page.locator(`[data-source-window="${window}"]`).click();
   const exported=await exportCSV('#media-export-sources');
   const expected=data.extensions.source_rates.filter(r=>r.period_id===window);
   assert.equal(exported.length,expected.length);
   for(const r of exported){const f=expected.find(f=>f.source_id===r.source_id);assert.equal(+r.eligible,f.eligible);assert.equal(r.rank,f.rank===null?'':String(f.rank));}
  }
  await page.locator('#media-reset').click();
  for(const metric of ['title','breadth'])for(const scope of ['all','stable']){
   await page.selectOption('#media-source',scope);await page.selectOption('#media-metric',metric);
   const exported=await exportCSV('#media-export-csv');
   for(const r of exported){const f=data.extensions.monthly.find(f=>f.period===r.period&&f.scope===scope);close(+r.title_share,f.title_share);close(+r.breadth_share,f.breadth_share);assert.equal(+r.title_mention_count,f.title_mention_count);assert.equal(+r.background_domains,f.background_domains);assert.equal(r.selected_metric,metric);}
  }
  await page.selectOption('#media-to','2026-09');await page.selectOption('#media-from','2026-09');
  assert.equal(await page.locator('#composition-chart polyline').count(),0);assert.equal(await page.locator('#composition-rows tr').count(),0);
  await page.locator('#media-reset').click();
  await page.evaluate(()=>document.body.style.zoom='2');assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
  await page.evaluate(()=>document.body.style.zoom='');
  checks.push({lang,width,three_rates:true,rate_thresholds:true,all_window_exports:true,title_breadth_export_matches:true,partial_excluded_from_composition:true,zoom_200:true});
 }
 await page.goto(base+'?m_metric=not-a-metric&m_source=missing');assert.equal(await page.locator('#media-state-warning').isVisible(),true);
 await page.goto(base+'?m_metric=title&m_source=stable&m_from=2025-01&m_to=2025-12#media-indicators');
 await Promise.all([page.waitForNavigation({waitUntil:'load'}),page.locator('#media-language').click()]);assert.equal(await page.locator('#media-metric').inputValue(),'title');assert.equal(await page.locator('#media-source').inputValue(),'stable');assert.equal(new URL(page.url()).hash,'#media-indicators');
 const noJS=await browser.newContext({javaScriptEnabled:false}),staticPage=await noJS.newPage();await staticPage.goto(base+'hr.html');
 assert.equal(await staticPage.locator('#composition-rows tr').count(),68);assert.equal(await staticPage.locator('#media-numeric-rows tr').count(),68);assert.equal(await staticPage.locator('#media-source-rows tr').first().locator('th,td').count(),7);assert.equal(await staticPage.locator('#latest-edition').isVisible(),true);
 assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(site,'qa/media-extension-browser-checks.json'),JSON.stringify({passed:true,checks,no_js_tables:true,language_state:true,invalid_state_explained:true,errors},null,2));
 await browser.close();console.log('Extension browser, CSV, language, no-JS and responsive checks passed.');
})().catch(async e=>{console.error(e);await browser?.close();process.exitCode=1;});
