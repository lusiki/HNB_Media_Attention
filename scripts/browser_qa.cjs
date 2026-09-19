// Test the local publication in an isolated headless browser, not the user's session.
const fs=require('node:fs');
const path=require('node:path');
const site=path.resolve(__dirname,'..');
const runtime=path.join(site,'.runtime');
fs.mkdirSync(path.join(runtime,'tmp'),{recursive:true});
process.env.TEMP=path.join(runtime,'tmp');process.env.TMP=path.join(runtime,'tmp');
const os=require('node:os');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||(fs.existsSync(path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'))?path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'):'playwright'));

const base=(process.env.BASE_URL||'http://127.0.0.1:8766/').replace(/\/?$/,'/');
let qaContext,qaBrowser;
(async()=>{
 const browser=await chromium.launch({
   executablePath:process.env.BROWSER_EXECUTABLE||process.env.CHROME_PATH||(fs.existsSync('C:/Program Files/Google/Chrome/Application/chrome.exe')?'C:/Program Files/Google/Chrome/Application/chrome.exe':undefined),headless:true,
   args:['--disable-background-networking','--disable-component-update','--no-first-run']
 });
 const context=await browser.newContext({viewport:{width:1440,height:1000},acceptDownloads:true});
 qaBrowser=browser;
 const page=context.pages()[0]||await context.newPage();
 qaContext=context;
 const errors=[],requests=[];
 page.on('pageerror',e=>errors.push(e.message));
 page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 page.on('request',r=>requests.push(r.url()));
 const results=[];
 for(const width of [1440,768,360]){
   await page.setViewportSize({width,height:1000});
   await page.goto(base,{waitUntil:'networkidle'});
   await page.screenshot({path:path.join(site,'qa',`site-${width}-top.png`)});
   await page.screenshot({path:path.join(site,'qa',`site-${width}-full.png`),fullPage:true});
   const overflow=await page.evaluate(()=>({document:document.documentElement.scrollWidth,viewport:window.innerWidth,
      overflowing:[...document.querySelectorAll('main *')].filter(e=>e.getBoundingClientRect().right>window.innerWidth+1).map(e=>e.tagName+'.'+e.className).slice(0,12)}));
   if(overflow.document>width)throw new Error('Horizontal overflow '+JSON.stringify(overflow));
   await page.locator('#overview').scrollIntoViewIfNeeded();
   await page.screenshot({path:path.join(site,'qa',`site-${width}-chart.png`)});
   if(await page.locator('#window').inputValue()!=='all'||await page.locator('#metric').inputValue()!=='share')throw new Error('Executive chart defaults');
   if(await page.locator('#gap-chart polyline').count()!==1||await page.locator('#inflation-chart polyline').count()!==1)throw new Error('Connected full-history series');
   if(await page.locator('#pilot,.mark').count())throw new Error('Removed content remains');
   await page.selectOption('#window','new');
   if(await page.locator('#period option').count()!==26)throw new Error('New-source period count');
   await page.selectOption('#period','2024-04');
   const april=await page.locator('#period-values').innerText();
   if(!april.startsWith('2024-04'))throw new Error('Period inspector failed');
   if(!april.includes('share 2.78%')||await page.locator('.selected-month[data-period="2024-04"]').count()!==2)throw new Error('Share conversion or aligned marker failed');
   await page.selectOption('#metric','gap');
   if(!(await page.locator('#visibility-unit').innerText()).includes('less visible'))throw new Error('Gap direction label');
   await page.selectOption('#window','all');
   if(await page.locator('#period option').count()!==62)throw new Error('Full-sample period count');
   if(/missing|excluded|collection change/i.test(await page.locator('main').innerText()))throw new Error('Editorial scope');
   if((await page.locator('#gap-chart').innerText()).includes('source break'))throw new Error('Source marker remains');
   await page.screenshot({path:path.join(site,'qa',`site-${width}-connected.png`)});
   await page.selectOption('#period','2023-03');
   if(await page.locator('.selected-month[data-period="2023-03"]').count()!==2)throw new Error('Full-history marker failed');
   await page.selectOption('#metric','share');await page.selectOption('#window','new');
   await page.locator('#evidence').scrollIntoViewIfNeeded();
   await page.selectOption('#frequency','monthly');await page.selectOption('#specification','9a');
   const estimate=await page.locator('#model-estimate').innerText();
   if(!(await page.locator('#model-ci').innerText()).includes('-0.00348')||!(await page.locator('#model-interpretation').innerText()).includes('includes zero'))throw new Error('Near-zero interval precision and interpretation');
   if(!estimate.startsWith('0.13'))throw new Error('Model selector failed: '+estimate);
   if(!(await page.locator('#model-note').innerText()).includes('60 fitted months'))throw new Error('N failed');
   await page.selectOption('#frequency','weekly');await page.selectOption('#specification','9b');
   await page.screenshot({path:path.join(site,'qa',`site-${width}-evidence.png`)});
   await page.locator('#F3 a[data-evidence]').click();
   if(!await page.locator('.lp-list').isVisible())throw new Error('Details failed');
   await page.locator('#F2 a[data-evidence]').click();
   if((await page.locator('#trend-evidence').getAttribute('open'))===null)throw new Error('Trend details failed');
   await page.locator('nav a[href="#paper"]').click();
   if(new URL(page.url()).hash!=='#paper')throw new Error('Navigation failed');
   await page.locator('#paper').scrollIntoViewIfNeeded();
   await page.screenshot({path:path.join(site,'qa',`site-${width}-paper.png`)});
   await page.locator('#implications').scrollIntoViewIfNeeded();
   await page.screenshot({path:path.join(site,'qa',`site-${width}-implications.png`)});
   await page.locator('.scenario-figure').scrollIntoViewIfNeeded();
   await page.screenshot({path:path.join(site,'qa',`site-${width}-scenario.png`)});
   results.push({width,overflow,period_count:62,new_source_period_count:26,model_switch:estimate,details:true,anchor_navigation:true});
 }
 await page.setViewportSize({width:1440,height:1000});await page.goto(base);
 await page.keyboard.press('Tab');
 const firstFocus=await page.evaluate(()=>document.activeElement.textContent);
 if(firstFocus!=='Skip to research')throw new Error('Skip link not first');
 await page.keyboard.press('Enter');
 if(new URL(page.url()).hash!=='#main')throw new Error('Skip link failed');
 const links=await page.locator('a[href]').evaluateAll(els=>[...new Set(els.map(e=>e.getAttribute('href')))]);
 for(const href of links){if(href.startsWith('#')||href.startsWith('mailto:')||href.startsWith('https:'))continue;const response=await page.request.get(new URL(href,base).href.split('#')[0]);if(response.status()!==200)throw new Error('Broken link '+href);}
 for(const width of [1440,360]){
   await page.setViewportSize({width,height:1000});await page.goto(base+'hr.html');
   if(await page.locator('html').getAttribute('lang')!=='hr')throw new Error('Croatian language');
   if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw new Error('Croatian overflow');
   await page.screenshot({path:path.join(site,'qa',`hr-${width}-full.png`),fullPage:true});
   await page.locator('#grafikon').scrollIntoViewIfNeeded();
   await page.waitForTimeout(350);
   if(await page.locator('.contents [aria-current="location"]').getAttribute('href')!=='#grafikon')throw new Error('Croatian active contents');
   await page.screenshot({path:path.join(site,'qa',`hr-${width}-chart.png`)});
   await page.evaluate(()=>document.documentElement.style.fontSize='200%');
   if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw new Error('Croatian text enlargement overflow '+JSON.stringify(await page.evaluate(()=>[...document.querySelectorAll('main *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1&&!e.closest('.table-scroll')).map(e=>({tag:e.tagName,cls:e.className,id:e.id,right:e.getBoundingClientRect().right,text:e.textContent.slice(0,80)})).slice(0,12))));
   await page.evaluate(()=>document.documentElement.style.fontSize='');
   await page.locator('#znacenje .scenario-figure').scrollIntoViewIfNeeded();
   await page.screenshot({path:path.join(site,'qa',`hr-${width}-scenario.png`)});
   await page.locator('a[data-original-href="index.html#expectations-evidence"]').first().click();
   if(!await page.locator('.lp-list').isVisible())throw new Error('Cross-language deep link');
 }
 // Restorable selections, invalid parameter handling, reset, sharing and real exports.
 await page.goto(base+'?window=new&metric=gap&period=2024-04&frequency=monthly&specification=9a#overview');
 const state=await page.locator('#period-values').innerText();
 if(!state.startsWith('2024-04')||await page.locator('#frequency').inputValue()!=='monthly')throw new Error('URL restore');
 await page.reload();
 if(await page.locator('#metric').inputValue()!=='gap'||!(await page.locator('#model-interpretation').innerText()).includes('includes zero'))throw new Error('Reload state');
 await page.selectOption('#period','2025-01');
 if(new URL(page.url()).searchParams.get('period')!=='2025-01')throw new Error('URL update');
 await context.grantPermissions(['clipboard-read','clipboard-write'],{origin:new URL(base).origin});
 await page.locator('[data-copy="F1"]').click();
 const copied=await page.evaluate(()=>navigator.clipboard.readText());
 if(!copied.endsWith('#F1')||!copied.includes('frequency=monthly')||!copied.includes('period=2025-01'))throw new Error('Copy finding state');
 for(const [button,ext] of [['export-svg','svg'],['export-csv','csv']]){
   const event=page.waitForEvent('download');await page.locator('#'+button).click();const dl=await event;
   const file=path.join(site,'qa','selected-view.'+ext);await dl.saveAs(file);const text=fs.readFileSync(file,'utf8');
   if(ext==='svg'&&(!text.includes('2025-01')||!text.includes('2024-04–2026-05')||!text.includes('Attention gap')))throw new Error('SVG export state');
   if(ext==='csv'&&(text.trim().split(/\r?\n/).length!==27||!text.includes('weighted_share_percent')))throw new Error('CSV selected period');
 }
 await page.locator('#reset-view').click();
 if(await page.locator('#window').inputValue()!=='all'||await page.locator('#frequency').inputValue()!=='weekly'||await page.locator('#period').inputValue()!=='2026-05')throw new Error('Reset state');
 await page.goto(base+'?window=invalid&metric=invalid&period=invalid&frequency=invalid&specification=invalid');
 if(await page.locator('#period').inputValue()!=='2026-05'||await page.locator('#metric').inputValue()!=='share')throw new Error('Invalid state fallback');
 await page.locator('#measure').scrollIntoViewIfNeeded();
 await page.locator('.indicator-guide summary').first().focus();await page.keyboard.press('Enter');
 if((await page.locator('.indicator-guide details').first().getAttribute('open'))===null)throw new Error('Keyboard disclosure');
 await page.locator('#evidence').scrollIntoViewIfNeeded();
 await page.waitForTimeout(350);
 if(await page.locator('.contents [aria-current="location"]').getAttribute('href')!=='#evidence')throw new Error('Active contents');
 const zoom=[];
 for(const width of [1440,360]){
   await page.setViewportSize({width,height:1000});
   await page.evaluate(()=>document.documentElement.style.fontSize='200%');
   const enlarged=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,body_font_px:getComputedStyle(document.body).fontSize,offenders:[...document.querySelectorAll("main *")].filter(e=>e.getBoundingClientRect().right>innerWidth+1 && !e.closest(".table-scroll")).map(e=>({tag:e.tagName,cls:e.className,id:e.id,width:e.getBoundingClientRect().width,right:e.getBoundingClientRect().right,text:e.textContent.slice(0,60)})).slice(0,10)}));
   if(enlarged.scroll>width)throw new Error('Text enlargement overflow '+JSON.stringify(enlarged));
   zoom.push(enlarged);
   await page.screenshot({path:path.join(site,'qa',`site-${width}-text-200.png`)});
 }
 const report={shareable_state:true,selected_exports:true,reset:true,near_zero_precision:true,keyboard_disclosure:true,results,firstFocus,link_count:links.length,console_errors:errors,external_requests:requests.filter(u=>!u.startsWith(base)),font_enlargement:zoom};
 const fallbackContext=await context.browser().newContext({javaScriptEnabled:false,viewport:{width:1440,height:1000}});
 const fallback=await fallbackContext.newPage();await fallback.goto(base);
 if(await fallback.locator('#gap-chart polyline').count()!==1||await fallback.locator('.scenario-chart svg').count()!==1)throw new Error('Static figures missing without JavaScript');
 await fallbackContext.close();report.static_fallback=true;
 fs.writeFileSync(path.join(site,'qa/browser-checks.json'),JSON.stringify(report,null,2));
 if(errors.length)throw new Error(errors.join('\n'));
 console.log(JSON.stringify(report,null,2));
 await browser.close();
})().catch(async e=>{console.error(e);await qaBrowser?.close();process.exitCode=1;});
