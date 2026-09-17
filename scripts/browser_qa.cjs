// Test the local publication in an isolated headless browser, not the user's session.
const fs=require('node:fs');
const path=require('node:path');
const site=path.resolve(__dirname,'..');
const runtime=path.join(site,'.runtime');
fs.mkdirSync(path.join(runtime,'tmp'),{recursive:true});
process.env.TEMP=path.join(runtime,'tmp');process.env.TMP=path.join(runtime,'tmp');
const baseUrl=(process.env.BASE_URL||'http://127.0.0.1:8765/').replace(/\/?$/,'/');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');

let qaContext;
(async()=>{
 const context=await chromium.launchPersistentContext(fs.mkdtempSync(path.join(runtime,'browser-qa-')),{
   ...(process.env.BROWSER_EXECUTABLE?{executablePath:process.env.BROWSER_EXECUTABLE}:{}),headless:true,
   viewport:{width:1440,height:1000},acceptDownloads:true,
   args:['--disable-background-networking','--disable-component-update','--no-first-run']
 });
 const page=context.pages()[0]||await context.newPage();
 qaContext=context;
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
   if(await page.locator('#window').inputValue()!=='all'||await page.locator('#metric').inputValue()!=='share')throw new Error('Full-history chart defaults');
   if(await page.locator('#period option').count()!==62)throw new Error('Default must include full sample');
   if(await page.locator('#period option').first().getAttribute('value')!=='2021-01')throw new Error('Missing original period');
   for(const scope of ['all','new']){
     await page.selectOption('#window',scope);
     for(const metric of ['share','gap']){
       await page.selectOption('#metric',metric);
       const charts=await page.locator('.timeline .chart svg').evaluateAll(svgs=>svgs.map(svg=>{
         const height=svg.viewBox.baseVal.height,points=[...svg.querySelectorAll('polyline')].flatMap(p=>p.getAttribute('points').trim().split(/\s+/).map(p=>p.split(',').map(Number)));
         const ys=points.map(p=>p[1]);
         return {height,min:svg.dataset.min,max:svg.dataset.max,count:points.length,segments:svg.querySelectorAll('polyline').length,inside:points.every(p=>p[0]>=38&&p[0]<=svg.viewBox.baseVal.width-20&&p[1]>=38&&p[1]<=height-34),span:(Math.max(...ys)-Math.min(...ys))/(height-72)};
       }));
       if(charts.some(c=>!c.inside||c.height<300||c.span<.7||c.count!==(scope==='all'?62:26)||c.segments!==(scope==='all'?2:1)))throw new Error('Clipped, flattened or incomplete chart '+JSON.stringify(charts));
       if(scope==='new'&&(charts[1].min!=='2.5'||charts[1].max!=='5.5'||!(await page.locator('#chart-scope').innerText()).includes('does not start at zero')))throw new Error('Later inflation scale disclosure');
     }
   }
   await page.selectOption('#metric','share');
   await page.selectOption('#window','new');
   await page.locator('.timeline').screenshot({path:path.join(site,'qa',`timeline-${width}-later.png`)});
   if(await page.locator('#period option').count()!==26)throw new Error('New-source period count');
   await page.selectOption('#period','2024-04');
   const april=await page.locator('#period-values').innerText();
   if(!april.startsWith('2024-04'))throw new Error('Period inspector failed');
   if(!april.includes('share 2.78%')||await page.locator('.selected-month[data-period="2024-04"]').count()!==2)throw new Error('Share conversion or aligned marker failed');
   await page.selectOption('#metric','gap');
   if(!(await page.locator('#visibility-unit').innerText()).includes('less visible'))throw new Error('Gap direction label');
   await page.selectOption('#window','all');
   if(await page.locator('#period option').count()!==62)throw new Error('Full-sample period count');
   if(!(await page.locator('#chart-scope').innerText()).includes('not harmonised'))throw new Error('Source boundary context');
   await page.selectOption('#period','2023-03');
   if(await page.locator('.selected-month[data-period="2023-03"]').count()!==2)throw new Error('Full-history marker failed');
   await page.selectOption('#metric','share');
   await page.locator('.timeline').screenshot({path:path.join(site,'qa',`timeline-${width}-full.png`)});
   await page.locator('#evidence').scrollIntoViewIfNeeded();
   await page.selectOption('#frequency','monthly');await page.selectOption('#specification','9a');
   const estimate=await page.locator('#model-estimate').innerText();
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
   results.push({width,overflow,period_count:62,new_source_period_count:26,model_switch:estimate,details:true,anchor_navigation:true});
 }
 await page.setViewportSize({width:1440,height:1000});await page.goto(baseUrl);
 await page.keyboard.press('Tab');
 const firstFocus=await page.evaluate(()=>document.activeElement.textContent);
 if(firstFocus!=='Skip to research')throw new Error('Skip link not first');
 await page.keyboard.press('Enter');
 if(new URL(page.url()).hash!=='#main')throw new Error('Skip link failed');
 const links=await page.locator('a[href]').evaluateAll(els=>[...new Set(els.map(e=>e.getAttribute('href')))]);
 for(const href of links){if(href.startsWith('#')||href.startsWith('mailto:'))continue;const response=await page.request.get(new URL(href,baseUrl).href.split('#')[0]);if(response.status()!==200)throw new Error('Broken link '+href);}
 const downloads=[];
 for(const name of ['brief','brief-hr','paper']){
   const filename=`hnb-attention-gap-${name}.pdf`;
   const [download]=await Promise.all([page.waitForEvent('download'),page.locator(`a[download="${filename}"]`).click()]);
   if(download.suggestedFilename()!==filename)throw new Error('Unexpected download filename');
   const saved=path.join(site,'qa',filename);
   await download.saveAs(saved);
   if(await download.failure())throw new Error('PDF download failed');
   if(!fs.readFileSync(saved).equals(fs.readFileSync(path.join(site,'public','downloads',filename))))throw new Error('Downloaded PDF differs from publication');
   downloads.push(filename);
 }
 for(const width of [1440,360]){
   await page.setViewportSize({width,height:1000});await page.goto(new URL('hr.html',baseUrl).href);
   if(await page.locator('html').getAttribute('lang')!=='hr')throw new Error('Croatian language');
   if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw new Error('Croatian overflow');
   await page.screenshot({path:path.join(site,'qa',`hr-${width}-full.png`),fullPage:true});
   await page.locator('a[href="index.html#expectations-evidence"]').click();
   if(!await page.locator('.lp-list').isVisible())throw new Error('Cross-language deep link');
 }
 const zoom=[];
 for(const width of [1440,360]){
   await page.setViewportSize({width,height:1000});
   await page.evaluate(()=>document.documentElement.style.fontSize='200%');
   const enlarged=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,body_font_px:getComputedStyle(document.body).fontSize}));
   if(enlarged.scroll>width)throw new Error('Text enlargement overflow '+JSON.stringify(enlarged));
   zoom.push(enlarged);
   await page.screenshot({path:path.join(site,'qa',`site-${width}-text-200.png`)});
 }
 const report={base_url:baseUrl,pdf_downloads:downloads,results,firstFocus,link_count:links.length,console_errors:errors,external_requests:requests.filter(u=>!u.startsWith(baseUrl)),font_enlargement:zoom};
 fs.writeFileSync(path.join(site,'qa/browser-checks.json'),JSON.stringify(report,null,2));
 if(errors.length)throw new Error(errors.join('\n'));
 console.log(JSON.stringify(report,null,2));
 await context.close();
})().catch(async e=>{console.error(e);await qaContext?.close();process.exitCode=1;});
