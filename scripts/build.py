"""Offline, allowlisted bilingual publication build. No database access."""
from pathlib import Path
from datetime import date
from html import escape
from urllib.parse import quote
import json, shutil, hashlib, zipfile, os
from charts import chart, model_svg, sensitivity_svg, scenario_svg
from readers import build_readers
from inspection_components import explorer, media_context, finding_records

SITE=Path(__file__).resolve().parents[1]
STUDY=json.loads((SITE/'content/study.json').read_text(encoding='utf-8'))
E=json.loads((SITE/'public/data/evidence.json').read_text(encoding='utf-8'))
I=json.loads((SITE/'public/data/inspection.json').read_text(encoding='utf-8'))
DIST=SITE/'dist'; DIST.mkdir(exist_ok=True)
assets=['data/inspection.json','data/findings.json','figures/social-preview.png','downloads/hnb-attention-gap-brief.pdf','downloads/hnb-attention-gap-brief-hr.pdf','downloads/citation.txt','figures/attention-gap.png','figures/inflation-scenario.png','figures/inflation-scenario-hr.png','figures/visibility-later.png','figures/visibility-later-hr.png','data/evidence.json','data/monthly-series.csv']
for name in assets:
    src=SITE/'public'/name
    if not src.is_file():raise FileNotFoundError(f'Required asset missing: {name}')
    dst=DIST/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
def fmt(v,k=2):return f'{v:.{k}f}'
def pp(v,k=2):return fmt(v*100,k)
def hr(v,k=2):return pp(v,k).replace('.',',')
def share(r):return pp(E['baseline']['monthly']-r['gap'])
def pvalue(v):return '< 0.001' if v<.001 else '= '+fmt(v,3)
primary=E['models'][0];last=E['observations'][-1];later=[r for r in E['observations'] if r['period']>='2024-04']
targets=['inflation-evidence','trend-evidence','expectations-evidence']
stats=[('−'+pp(primary['estimate']),'percentage points of weighted share<br>per +1 percentage point of inflation'),('−'+pp(E['trend']['estimate'],3),'percentage points of weighted share per month<br>April 2024–May 2026'),('No stable link','Consumer expectations · separate outcome')]
findings=[]
for i,f in enumerate(STUDY['findings']):
    interval=('95% interval for the decline: '+pp(primary['lo'])+' to '+pp(primary['hi'])+' percentage points per +1 percentage point of inflation.') if i==0 else ('95% interval for the decline: '+pp(E['trend']['lo'],3)+' to '+pp(E['trend']['hi'],3)+' percentage points per month.') if i==1 else 'Survey timing and model controls change the comparisons.'
    findings.append(f'<article class="finding" id="{f["id"]}"><span class="finding-index">0{i+1}</span><h3>{escape(f["headline"])}</h3><p class="stat">{stats[i][0]}</p><p class="stat-label">{stats[i][1]}</p><p class="caveat">{escape(f["caveat"])}</p><details class="finding-more"><summary>Read the estimate and interpretation</summary><p>{escape(f["text"])}</p><p>{interval}</p><p>{escape(f["implication"])}</p><p class="source">{escape(f["locator"])}</p></details><div class="finding-actions"><a class="text-link" data-evidence href="#{targets[i]}">Inspect evidence ↗</a><button type="button" data-copy="{f["id"]}" hidden data-js>Copy finding link</button></div></article>')

time_names={'none':'Primary','trend':'Period trends','year':'Year effects'}
lp=[]
for r in E['expectations']:
    unit='weeks' if r['frequency']=='weekly' else 'months'
    sig=', '.join(map(str,r['significant_horizons']))
    explanation=f'horizons {sig} {unit} ahead pass correction' if sig else f'none of the 1–12 {unit}-ahead horizons pass correction'
    lp.append(f'<li><b>{escape(r["label"])}</b>: {explanation}.</li>')
values={
 'HR_SHARE_WIDE':chart(later,'share',width=1120,height=220,baseline=E['baseline']['monthly']),
 'HR_SHARE_NARROW':chart(later,'share',width=320,height=225,baseline=E['baseline']['monthly']),
 'HR_INFLATION_WIDE':chart(later,'inflation',width=1120,height=220),
 'HR_INFLATION_NARROW':chart(later,'inflation',width=320,height=225),
 'SCENARIO_SVG':scenario_svg(E['time_sensitivity']),'SCENARIO_SVG_HR':scenario_svg(E['time_sensitivity'],hr=True),
 'SCENARIO':pp(primary['estimate']*8),'SCENARIO_CI':pp(primary['lo']*8)+' to '+pp(primary['hi']*8),
 'SCENARIO_HR':hr(primary['estimate']*8),'SCENARIO_CI_HR':hr(primary['lo']*8)+'–'+hr(primary['hi']*8),
 'CENTRALITY':fmt(E['centrality_trend']['estimate'],4),'CENTRALITY_CI':fmt(E['centrality_trend']['lo'],4)+' to '+fmt(E['centrality_trend']['hi'],4),'CENTRALITY_P':fmt(E['centrality_trend']['p'],3),
 'CENTRALITY_HR':fmt(E['centrality_trend']['estimate'],4).replace('.',','),'CENTRALITY_CI_HR':fmt(E['centrality_trend']['lo'],4).replace('.',',')+' do '+fmt(E['centrality_trend']['hi'],4).replace('.',','),'CENTRALITY_P_HR':fmt(E['centrality_trend']['p'],3).replace('.',','),
 'QUESTION':escape(STUDY['question']),'ANSWER':escape(STUDY['answer']),
 'PAPER_TITLE':escape(STUDY['paper_title']),'PAPER_SUBTITLE':escape(STUDY['paper_subtitle']),
 'CITATION':escape(STUDY['citation']),'BUILD_DATE':date.today().isoformat(),
 'PRIMARY_HR':hr(primary['estimate']),'PRIMARY_CI_HR':hr(primary['lo'])+'–'+hr(primary['hi']),
 'TREND_HR':hr(E['trend']['estimate'],3),'TREND_CI_HR':hr(E['trend']['lo'],3)+'–'+hr(E['trend']['hi'],3),
 'SHARE_SVG':chart(E['observations'],'share',baseline=E['baseline']['monthly']),'INFLATION_SVG':chart(E['observations'],'inflation'),
 'MODEL_SVG':model_svg(primary),'MODEL_ESTIMATE':pp(primary['estimate']),
 'MODEL_CI':f'95% confidence interval: {pp(primary["lo"])} to {pp(primary["hi"])} percentage points',
 'MODEL_NOTE':f'{int(primary["N"])} fitted weeks · January 2021–May 2026',
 'MODEL_TECHNICAL':f'Sample S1 · equation 9b · Newey–West intervals · p {escape(pvalue(primary["p"]))}',
 'SENSITIVITY_SVG':'<div class="sensitivity-wide">'+sensitivity_svg(E['time_sensitivity'])+'</div><div class="sensitivity-narrow">'+sensitivity_svg(E['time_sensitivity'],narrow=True)+'</div>',
 'SENSITIVITY_ROWS':''.join(f'<tr><th scope="row">{r["frequency"].title()}</th><td>{time_names[r["adjustment"]]}</td><td>{pp(r["estimate"],3)}</td><td>{pp(r["lo"],3)} to {pp(r["hi"],3)}</td></tr>' for r in E['time_sensitivity']),
 'FINDINGS':''.join(findings),
 'PERIOD_OPTIONS':''.join(f'<option value="{r["period"]}" {"selected" if r==last else ""}>{r["period"]}</option>' for r in E['observations'] if r['gap'] is not None),
 'INITIAL_PERIOD':f'{last["period"]} · share {share(last)}% · gap {pp(last["gap"])} pp · inflation {fmt(last["inflation"],1)}%',
 'MONTHLY_ROWS':''.join(f'<tr><th scope="row">{r["period"]}</th><td>{share(r)}</td><td>{pp(r["gap"])}</td><td>{fmt(r["inflation"],1)}</td></tr>' for r in E['observations']),
 'TREND':pp(E['trend']['estimate'],3),'TREND_CI':pp(E['trend']['lo'],3)+' to '+pp(E['trend']['hi'],3),
 'COMMON_TREND':pp(E['common_source_trend']['estimate'],3),'COMMON_P':fmt(E['common_source_trend']['p'],3),
 'BASELINE':pp(E['baseline']['monthly'],3),'LP_LIST':''.join(lp),
 'INSPECTION_JSON':json.dumps(I,ensure_ascii=False,allow_nan=False).replace('<','\\u003c'),
 'EVIDENCE_JSON':json.dumps(E,ensure_ascii=False,allow_nan=False).replace('<','\\u003c')
}
for name in ['index.html','hr.html']:
    html=(SITE/'src'/name).read_text(encoding='utf-8')
    lang='hr' if name=='hr.html' else 'en'
    html=html.replace('@@EXPLORER@@',explorer(lang,E,I)).replace('@@MEDIA_CONTEXT@@',media_context(lang,E,I)).replace('@@FINDING_RECORDS@@',finding_records(lang,E,I))
    for k,v in values.items():html=html.replace('@@'+k+'@@',v)
    assert '@@' not in html, f'Unexpanded template token in {name}'
    base_url=os.environ.get('SITE_URL','').rstrip('/')
    if base_url:
        assert base_url.startswith('https://'), 'SITE_URL must use HTTPS'
        html=html.replace('content="figures/social-preview.png"','content="'+base_url+'/figures/social-preview.png"')
        html=html.replace('</head>','<meta property="og:url" content="'+base_url+'/'+('' if name=='index.html' else name)+'"></head>')
    (DIST/name).write_text(html,encoding='utf-8')
for name in ['styles.css','charts.js','app.js']:shutil.copyfile(SITE/'src'/name,DIST/name)
allowlist=['index.html','hr.html','styles.css','charts.js','app.js']+assets+build_readers(SITE,DIST)
actual=[str(p.relative_to(DIST)).replace('\\','/') for p in DIST.rglob('*') if p.is_file()]
assert sorted(actual)==sorted(allowlist), f'Unexpected public files: {set(actual)-set(allowlist)}'
manifest={p:hashlib.sha256((DIST/p).read_bytes()).hexdigest() for p in allowlist}
(SITE/'qa').mkdir(exist_ok=True)
(SITE/'qa/build-manifest.json').write_text(json.dumps({'build_date':date.today().isoformat(),'files':manifest},indent=2),encoding='utf-8')
with zipfile.ZipFile(SITE/'hnb-attention-gap-publication.zip','w',zipfile.ZIP_DEFLATED) as z:
    for name in allowlist:z.write(DIST/name,name)
print(f'Built {len(allowlist)} allowlisted public files and publication ZIP.')
