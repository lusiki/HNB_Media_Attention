// Test the local publication in an isolated headless browser, not the user's session.
const fs=require('node:fs');
const path=require('node:path');
const site=path.resolve(__dirname,'..');
const runtime=path.join(site,'.runtime');
fs.mkdirSync(path.join(runtime,'tmp'),{recursive:true});
process.env.TEMP=path.join(runtime,'tmp');process.env.TMP=path.join(runtime,'tmp');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const baseUrl=(process.env.BASE_URL||'http://127.0.0.1:8765/').replace(/\/?$/,'/');
fs.mkdirSync(path.join(site,'qa'),{recursive:true});

(async()=>{
 const context=await chromium.launchPersistentContext(path.join(runtime,'browser-profile'),{
   ...(process.env.BROWSER_EXECUTABLE?{executablePath:process.env.BROWSER_EXECUTABLE}:{}),headless:true,
   viewport:{width:1440,height:1000},acceptDownloads:true,
   args:['--disable-background-networking','--disable-component-update','--no-first-run']
 });
 const page=context.pages()[0]||await context.newPage();
 const errors=[],requests=[];
 page.on('pageerror',e=>errors.push(e.message));
 page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 page.on('request',r=>requests.push(r.url()));
 const results=[];
 for(const width of [1440,768,360]){
   await page.setViewportSize({width,height:1000});
   await page.goto(baseUrl,{waitUntil:'networkidle'});
   await page.screenshot({path:path.join(site,'qa',`site-${width}-top.png`)});
   await page.screenshot({path:path.join(site,'qa',`site-${width}-full.png`),fullPage:true});
   const overflow=await page.evaluate(()=>({document:document.documentElement.scrollWidth,viewport:window.innerWidth,
      overflowing:[...document.querySelectorAll('main *')].filter(e=>e.getBoundingClientRect().right>window.innerWidth+1).map(e=>e.tagName+'.'+e.className).slice(0,12)}));
   if(overflow.document>width)throw new Error('Horizontal overflow '+JSON.stringify(overflow));
   await page.locator('#overview').scrollIntoViewIfNeeded();
   await page.screenshot({path:path.join(site,'qa',`site-${width}-chart.png`)});
   await page.selectOption('#window','new');
   if(await page.locator('#period option').count()!==26)throw new Error('New-source period count');
   await page.selectOption('#period','2024-04');
   const april=await page.locator('#period-values').innerText();
   if(!april.startsWith('2024-04'))throw new Error('Period inspector failed');
   await page.selectOption('#window','all');
   if(await page.locator('#period option').count()!==62)throw new Error('Full-sample period count');
   await page.locator('#evidence').scrollIntoViewIfNeeded();
   await page.selectOption('#frequency','monthly');await page.selectOption('#specification','9a');
   const estimate=await page.locator('#model-estimate').innerText();
   if(!estimate.startsWith('0.13'))throw new Error('Model selector failed: '+estimate);
   if(!(await page.locator('#model-note').innerText()).includes('60 fitted months'))throw new Error('N failed');
   await page.selectOption('#frequency','weekly');await page.selectOption('#specification','9b');
   await page.screenshot({path:path.join(site,'qa',`site-${width}-evidence.png`)});
   await page.getByText('What changes for consumer expectations?',{exact:true}).click();
   if(!await page.locator('.lp-list').isVisible())throw new Error('Details failed');
   await page.locator('nav a[href="#paper"]').click();
   if(new URL(page.url()).hash!=='#paper')throw new Error('Navigation failed');
   await page.locator('#paper').scrollIntoViewIfNeeded();
   await page.screenshot({path:path.join(site,'qa',`site-${width}-paper.png`)});
   results.push({width,overflow,period_count:62,new_source_period_count:26,model_switch:estimate,details:true,anchor_navigation:true});
 }
 await page.setViewportSize({width:1440,height:1000});await page.goto(baseUrl);
 await page.keyboard.press('Tab');
 const firstFocus=await page.evaluate(()=>document.activeElement.textContent);
 if(firstFocus!=='Skip to research')throw new Error('Skip link not first');
 await page.keyboard.press('Enter');
 if(new URL(page.url()).hash!=='#main')throw new Error('Skip link failed');
 const links=await page.locator('a[href]').evaluateAll(els=>[...new Set(els.map(e=>e.getAttribute('href')))]);
 for(const href of links){if(href.startsWith('#'))continue;const response=await page.request.get(new URL(href,baseUrl).href.split('#')[0]);if(response.status()!==200)throw new Error('Broken link '+href);}
 const zoom=[];
 for(const width of [1440,360]){
   await page.setViewportSize({width,height:1000});
   await page.evaluate(()=>document.documentElement.style.fontSize='200%');
   const enlarged=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,body_font_px:getComputedStyle(document.body).fontSize}));
   if(enlarged.scroll>width)throw new Error('Text enlargement overflow '+JSON.stringify(enlarged));
   zoom.push(enlarged);
   await page.screenshot({path:path.join(site,'qa',`site-${width}-text-200.png`)});
 }
 const report={base_url:baseUrl,results,firstFocus,link_count:links.length,console_errors:errors,external_requests:requests.filter(u=>!u.startsWith(baseUrl)),font_enlargement:zoom};
 fs.writeFileSync(path.join(site,'qa/browser-checks.json'),JSON.stringify(report,null,2));
 if(errors.length)throw new Error(errors.join('\n'));
 console.log(JSON.stringify(report,null,2));
 await context.close();
})().catch(e=>{console.error(e);process.exitCode=1;});
