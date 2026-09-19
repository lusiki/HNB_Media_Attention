// Bounded checks for context, dialog behavior, comparison values and data exports.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||(fs.existsSync(path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'))?path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'):'playwright'));
const site=path.resolve(__dirname,'..'),base=(process.env.BASE_URL||'http://127.0.0.1:8766/').replace(/\/?$/,'/'),origin=new URL(base).origin;
const data=JSON.parse(fs.readFileSync(path.join(site,'dist/data/inspection.json'),'utf8'));
let browser;
(async()=>{
 browser=await chromium.launch({executablePath:process.env.BROWSER_EXECUTABLE||process.env.CHROME_PATH||(fs.existsSync('C:/Program Files/Google/Chrome/Application/chrome.exe')?'C:/Program Files/Google/Chrome/Application/chrome.exe':undefined),headless:true});
 const context=await browser.newContext({viewport:{width:1440,height:1000},acceptDownloads:true});
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 const report={};
 await context.grantPermissions(['clipboard-read','clipboard-write'],{origin});
 for(const width of [1440,768,360]){
  await page.setViewportSize({width,height:1000});
  await page.goto(base+'?window=new&metric=share&sample=common&period=2026-01&frequency=monthly&specification=9a&finding=F2&mode=compare&from=2024-04&to=2026-01');
  assert.equal(await page.locator('#sample').inputValue(),'common');
  assert.equal(await page.locator('#period').inputValue(),'2026-01');
  assert.match(await page.locator('#chart-scope').innerText(),/0–8/);
  assert.match(await page.locator('#period-values').innerText(),/6\.52%/);
  // Every displayed point must remain inside the plotted panel, including the common-source peak.
  for(const metric of ['share','gap','article','centrality','hhi']){
   await page.selectOption('#metric',metric);
   const inside=await page.locator('#gap-chart svg').evaluate(svg=>{const h=svg.viewBox.baseVal.height;return svg.querySelector('polyline').getAttribute('points').split(' ').every(p=>{const y=Number(p.split(',')[1]);return y>=37.99&&y<=h-34+.01;});});
   assert.equal(inside,true,`axis clips ${metric} at ${width}`);
  }
  await page.selectOption('#metric','share');
  await page.locator('#inspect-current').scrollIntoViewIfNeeded();
  const before=await page.evaluate(()=>scrollY);
  await page.locator('#inspect-current').click();
  assert.equal(await page.locator('#indicator-dialog').evaluate(e=>e.open),true);
  assert.match(await page.locator('#indicator-context').innerText(),/2026-01.*Common sources/);
  assert.match(await page.locator('#indicator-value').innerText(),/6\.518/);
  for(let n=0;n<15;n++)await page.keyboard.press('Tab');
  assert.equal(await page.evaluate(()=>document.activeElement.closest('#indicator-dialog')!==null),true,'focus leaves modal');
  await page.screenshot({path:path.join(site,'qa',`inspection-${width}-dialog.png`)});
  await page.keyboard.press('Escape');
  assert.equal(await page.locator('#indicator-dialog').evaluate(e=>e.open),false);
  assert.equal(await page.evaluate(()=>document.activeElement.id),'inspect-current');
  assert.ok(Math.abs(await page.evaluate(()=>scrollY)-before)<3,'return position changed');
  assert.equal(await page.locator('#comparison').evaluate(e=>e.open),true,'comparison mode not restored');
  await page.locator('#analysis-desk').scrollIntoViewIfNeeded();
  assert.equal(await page.locator('#robustness-table tbody tr').count(),2);
  await page.selectOption('#compare-finding','F1');
  assert.equal(await page.locator('#robustness-table tbody tr').count(),6);
  assert.match(await page.locator('#robustness-table').innerText(),/Includes zero/);
  await page.screenshot({path:path.join(site,'qa',`inspection-${width}-comparisons.png`)});
  await page.locator('.robustness-desk').scrollIntoViewIfNeeded();
  const forestLayout=await page.locator('#robustness-chart svg').evaluate(svg=>{
   const width=svg.viewBox.baseVal.width,labels=[...svg.querySelectorAll('text')];
   const inside=labels.every(label=>{const b=label.getBBox();return b.x>=0&&b.x+b.width<=width;});
   const ticks=[...svg.querySelectorAll('[data-forest-tick]')].map(e=>e.getBBox()).sort((a,b)=>a.x-b.x);
   return {inside,noOverlap:ticks.every((b,i)=>!i||ticks[i-1].x+ticks[i-1].width+5<b.x)};
  });
  assert.deepEqual(forestLayout,{inside:true,noOverlap:true},`forest labels at ${width}`);
  await page.screenshot({path:path.join(site,'qa',`inspection-${width}-estimates.png`)});
  await page.selectOption('#compare-finding','F4');assert.equal(await page.locator('#robustness-table tbody tr').count(),2);
  await page.selectOption('#compare-finding','F3');assert.equal(await page.locator('#robustness-table tbody tr').count(),3);
  await page.locator('[data-lens="composition"]').click();
  assert.equal(await page.locator('#sample').inputValue(),'common');assert.equal(await page.locator('#window').inputValue(),'new');
  await page.locator('.concentration-desk').scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(site,'qa',`inspection-${width}-diagnostics.png`)});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  await page.evaluate(()=>document.documentElement.style.fontSize='200%');
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'zoom overflow');
  await page.locator('#inspect-current').click();
  assert.equal(await page.locator('#indicator-dialog').evaluate(e=>e.scrollWidth<=e.clientWidth+1),true,'dialog zoom overflow');
  await page.keyboard.press('Escape');await page.evaluate(()=>document.documentElement.style.fontSize='');
  report[width]={modal_focus:true,return_position:true,source_scale:true,comparison_families:true,zoom:true};
 }
 // Language switches from an open inspector preserve every parameter and open the same indicator.
 await page.goto(base+'?window=new&metric=article&sample=common&period=2025-09&frequency=monthly&specification=9a&finding=F2&mode=compare&from=2024-04&to=2025-09');
 await page.locator('#inspect-current').click();await page.selectOption('#indicator-choice','hhi');
 await page.locator('#indicator-dialog a[data-original-href="hr.html"]').click();
 await page.waitForLoadState('load');
 assert.equal(await page.locator('html').getAttribute('lang'),'hr');
 for(const [key,value] of Object.entries({window:'new',metric:'article',sample:'common',period:'2025-09',frequency:'monthly',specification:'9a',finding:'F2',from:'2024-04',to:'2025-09',inspect:'hhi',lang:'hr'}))assert.equal(new URL(page.url()).searchParams.get(key),value,key);
 assert.equal(await page.locator('#indicator-dialog').evaluate(e=>e.open),true);
 assert.match(await page.locator('#indicator-title').innerText(),/Koncentracija/);
 await page.keyboard.press('Escape');
 await page.locator('header a[data-original-href="index.html"]').click();
 await page.waitForLoadState('load');
 assert.equal(await page.locator('#sample').inputValue(),'common');assert.equal(await page.locator('#period').inputValue(),'2025-09');
 // Source ordering is neutral by default, numeric sort is named, and totals match the prepared record.
 await page.locator('.concentration-desk details summary').click();
 const names=await page.locator('#source-table tbody th').allTextContents();assert.deepEqual(names,[...names].sort((a,b)=>a.localeCompare(b)));
 await page.selectOption('#source-sort','weight');
 const expected=data.observations.find(r=>r.period==='2025-09').common;
 const first=await page.locator('#source-table tbody th').first().innerText();assert.equal(first,[...expected.domains].sort((a,b)=>b.contribution-a.contribution)[0].source);
 for(const [button,file] of [['export-csv','inspection-period.csv'],['export-svg','inspection-chart.svg'],['export-sources','inspection-sources.csv'],['export-comparison','inspection-comparison.csv']]){
  if(button==='export-comparison')await page.locator('[data-mode="compare"]').click();
  const [download]=await Promise.all([page.waitForEvent('download'),page.locator('#'+button).click()]);await download.saveAs(path.join(site,'qa',file));
  const text=fs.readFileSync(path.join(site,'qa',file),'utf8');assert.match(text,/common/);assert.match(text,/2025-09/);
 }
 assert.match(fs.readFileSync(path.join(site,'qa/inspection-period.csv'),'utf8'),/selected_value/);
 assert.match(fs.readFileSync(path.join(site,'qa/inspection-chart.svg'),'utf8'),/Article share/);
 const exported=fs.readFileSync(path.join(site,'qa/inspection-comparison.csv'),'utf8').trim().split(/\r?\n/).map(line=>line.slice(1,-1).split('\",\"'));
 const record=Object.fromEntries(exported[0].map((key,i)=>[key,exported[1][i]]));
 const from=data.observations.find(r=>r.period==='2024-04').common.article;
 assert.equal(Number(record.comparison_from_value),from);assert.equal(Number(record.comparison_to_value),expected.article);assert.equal(Number(record.comparison_difference),expected.article-from);
 assert.equal(record.comparison_difference_unit,'percentage_points');
 await page.locator('#record-F2 summary').click();await page.locator('[data-cite="F2"]').click();
 assert.match(await page.evaluate(()=>navigator.clipboard.readText()),/F2:.*extended-2026-09-17/s);
 // Native Back/Forward and a copied inspector URL restore their complete states.
 await page.goto(base+'?sample=primary&period=2026-05');await page.selectOption('#sample','common');await page.goBack();assert.equal(await page.locator('#sample').inputValue(),'primary');await page.goForward();assert.equal(await page.locator('#sample').inputValue(),'common');
 await page.locator('#inspect-current').click();await page.locator('#copy-indicator').click();const shared=await page.evaluate(()=>navigator.clipboard.readText());await page.goto(shared);assert.equal(await page.locator('#indicator-dialog').evaluate(e=>e.open),true);await page.keyboard.press('Escape');
 await page.goto(base+'?sample=bad&finding=bad&metric=bad&period=bad&inspect=bad#%');assert.equal(await page.locator('#sample').inputValue(),'primary');assert.equal(await page.locator('#metric').inputValue(),'share');
 await page.evaluate(()=>{navigator.clipboard.writeText=async()=>{throw new Error('Clipboard disabled for fallback check');};});
 await page.locator('#inspect-current').click();await page.locator('#copy-indicator').click();assert.equal(await page.locator('#copy-fallback').isVisible(),true);assert.equal(await page.locator('#copy-fallback').getAttribute('aria-label'),'Text to copy');await page.keyboard.press('Escape');
 const figure=await context.newPage();await figure.setViewportSize({width:1200,height:760});await figure.goto(require('node:url').pathToFileURL(path.join(site,'qa/inspection-chart.svg')).href);await figure.screenshot({path:path.join(site,'qa/inspection-export.png')});await figure.close();
 assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(site,'qa/inspection-browser-checks.json'),JSON.stringify({viewports:report,language_context:true,source_sort:true,exports:true,record_citations:true,back_forward:true,invalid_context:true,console_errors:errors},null,2));
 console.log('Inspection browser checks passed: modal focus/return, language state, all comparison families, data exports, source order, history and three responsive widths.');
 await browser.close();
})().catch(async error=>{console.error(error);await browser?.close();process.exitCode=1;});
