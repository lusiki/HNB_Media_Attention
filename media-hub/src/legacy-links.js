'use strict';
(()=>{const u=new URL(location.href),keys=['window','metric','period','sample','frequency','specification','lens','finding','mode','inspect','sort'];
 const oldAnchors=['F1','F2','F3','F4','record-F1','record-F2','record-F3','record-F4','overview','grafikon','evidence','methods','paper','rad','research-status','inflation-evidence','trend-evidence','expectations-evidence','analysis-desk','indicator-guide','media-context','pregled','mjera','nalazi','znacenje','title','summary','summary-title','measure','measure-title','worked-example','findings','findings-title','implications','implications-title','centrality','evidence-title','methods-title','paper-title','researchers'];
 if(keys.some(k=>u.searchParams.has(k))||oldAnchors.includes(u.hash.slice(1))){const target=new URL('studies/inflation/'+(document.documentElement.lang==='hr'?'hr.html':'index.html'),u);target.search=u.search;target.hash=u.hash;location.replace(target.href);}
})();
