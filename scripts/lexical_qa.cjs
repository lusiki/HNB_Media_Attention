const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'));
const root=path.resolve(__dirname,'..'),base=process.env.BASE_URL||'http://127.0.0.1:8765/',d=JSON.parse(fs.readFileSync(path.join(root,'media-hub/public/data/media/lexical-extensions.json'),'utf8'));
(async()=>{const browser=await chromium.launch({executablePath:process.env.BROWSER_EXECUTABLE||'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});try{
 const context=await browser.newContext({acceptDownloads:true}),page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 for(const lang of ['en','hr'])for(const width of [1440,768,360]){
  await page.setViewportSize({width,height:1000});await page.goto(base+(lang==='hr'?'hr.html':'index.html'));
  assert.equal(await page.locator('#lexical-term option').count(),64);assert.equal(await page.locator('#lexical-quarter-rows tr').count(),23);
  assert.equal(await page.locator('#V9 tbody tr').count(),8);
  for(const term of ['term:statistika','phrase:uvođenje eura']){
   await page.selectOption('#lexical-term',term);const [kind,label]=term.split(':');const fixture=d.quarterly.filter(r=>r.kind===kind&&r.term===label);
   const actual=await page.locator('#lexical-quarter-rows tr').allTextContents();assert.equal(actual.length,fixture.length);
   const reported=await page.locator('#lexical-quarter-rows tr').evaluateAll(rows=>rows.map(r=>[...r.children].map(x=>x.textContent)));
   for(let i=0;i<fixture.length;i++){assert.equal(Number(reported[i][1].replace(/[.,]/g,'')),fixture[i].count);assert.equal(Number(reported[i][2].replace(/[.,]/g,'')),fixture[i].denominator);if(fixture[i].frequency===null)assert.match(reported[i][3],lang==='hr'?/praga/:/threshold/);}
   assert.equal(new URL(page.url()).searchParams.get('lexical'),term);
  }
  await page.goBack();assert.equal(await page.locator('#lexical-term').inputValue(),'term:statistika');await page.goForward();
  await page.locator('#jezik').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(root,'media-hub/qa',`lexical-${lang}-${width}.png`)});
  await page.evaluate(()=>{document.documentElement.style.fontSize='200%';document.querySelectorAll('body *').forEach(e=>{const s=getComputedStyle(e);if(parseFloat(s.fontSize)<32)e.style.fontSize=parseFloat(s.fontSize)*2+'px';});});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 }
 await page.goto(base+'hr.html?lexical=term%3Akredit&m_metric=title');await Promise.all([page.waitForNavigation(),page.locator('#media-language').click()]);assert.equal(await page.locator('#lexical-term').inputValue(),'term:kredit');assert.equal(await page.locator('#media-metric').inputValue(),'title');
 await page.goto(base+'?lexical=invalid');assert.equal(await page.locator('#lexical-term').inputValue(),'term:banka');assert.match(await page.locator('#lexical-selection').innerText(),/Invalid/);
 const nojs=await browser.newContext({javaScriptEnabled:false}),staticPage=await nojs.newPage();await staticPage.goto(base+'hr.html');assert.equal(await staticPage.locator('#lexical-quarter-rows tr').count(),23);assert.equal(await staticPage.locator('#V9 tbody tr').count(),8);
 assert.deepEqual(errors,[]);console.log('Lexical browser QA passed: 64 selections, aggregate cells, thresholds, partial quarter, history, language, invalid state, responsive/zoom and no-JS tables.');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exit(1);});
