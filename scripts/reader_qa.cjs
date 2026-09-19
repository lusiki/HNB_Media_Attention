// Exercise the actual Read links with all PDF requests blocked.
const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const site=path.resolve(__dirname,'..');
const base=(process.env.BASE_URL||'http://127.0.0.1:8766/').replace(/\/?$/,'/');
fs.mkdirSync(path.join(site,'qa'),{recursive:true});

(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.BROWSER_EXECUTABLE?{executablePath:process.env.BROWSER_EXECUTABLE}:{})});
 const results=[];
 try{
  for(const javaScriptEnabled of [true,false]){
   const context=await browser.newContext({javaScriptEnabled});
   await context.route('**/*.pdf',route=>route.abort());
   const page=await context.newPage();
   const errors=[];
   page.on('pageerror',error=>errors.push(error.message));
   for(const width of [1440,360]){
    await page.setViewportSize({width,height:1000});
    for(const [name,count] of [['brief',2],['brief-hr',2]]){
     await page.goto(base);
     await page.locator(`a[href="read/${name}.html"]`).first().click();
     await page.waitForURL(`**/read/${name}.html`);
     if(await page.locator('.page-image').count()!==count)throw new Error('Missing document pages');
     const first=page.locator('.page-image').first();
     await first.evaluate(image=>image.decode());
     if(!await first.evaluate(image=>image.naturalWidth>1000&&image.naturalHeight>1000))throw new Error('Blank first page');
     if(await page.locator('iframe,embed,object').count())throw new Error('Reader still depends on PDF viewer');
     if(context.pages().length!==1)throw new Error('Read link opened another tab');
     if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw new Error('Reader overflows viewport');
     if(javaScriptEnabled)await page.screenshot({path:path.join(site,'qa',`reader-${name}-${width}.png`)});
     await page.getByText('Go to page',{exact:true}).click();
     await page.locator(`.page-links a[href="#page-${count}"]`).first().click();
     const last=page.locator(`#page-${count} .page-image`);
     await last.evaluate(image=>image.decode());
     if(!await last.evaluate(image=>image.naturalWidth>1000))throw new Error('Last page not rendered');
     await page.locator(`#page-${count} .page-text summary`).first().click();
     const transcript=page.locator(`#page-${count} .transcription`);
     if(!await transcript.isVisible()||(await transcript.innerText()).length<100)throw new Error('Page text unavailable');
     // Decode every lazy image, not just the first and last pages.
     for(const image of await page.locator('.page-image').all()){
      await image.evaluate(async image=>{image.loading='eager';await image.decode();});
     }
     results.push({name,width,javaScriptEnabled,pages:count,all_images_decoded:true,text_available:true,pdf_requests_blocked:true});
    }
   }
   if(errors.length)throw new Error(errors.join('\n'));
   await context.close();
  }
  fs.writeFileSync(path.join(site,'qa/reader-checks.json'),JSON.stringify({base,results},null,2));
  console.log(JSON.stringify({base,results},null,2));
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
