"""Offline, allowlisted static build. No research-source or database access."""
from pathlib import Path
from datetime import date
from html import escape
import json, shutil, hashlib, zipfile
from charts import chart, model_svg

SITE=Path(__file__).resolve().parents[1]
STUDY=json.loads((SITE/'content/study.json').read_text(encoding='utf-8'))
E=json.loads((SITE/'public/data/evidence.json').read_text(encoding='utf-8'))
DIST=SITE/'dist'; DIST.mkdir(exist_ok=True)
paperfiles=['downloads/hnb-attention-gap-paper.pdf','downloads/hnb-attention-gap-brief.pdf','downloads/citation.txt','figures/attention-gap.png','data/evidence.json','data/monthly-series.csv']
for file in paperfiles:
    src=SITE/'public'/file
    if not src.is_file():raise FileNotFoundError(f'Required publication asset missing: {src}')
    dst=DIST/file; dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)

def fmt(v,k=2):return f'{v:.{k}f}'
def pp(v,k=2):return fmt(v*100,k)
def pvalue(v):return '< 0.001' if v<.001 else '= '+fmt(v,3)

primary=E['models'][0]; last=E['observations'][-1]
finding_html=[]
stats=[(pp(primary['estimate']),'pp wider gap per +1 pp inflation<br>95% CI '+pp(primary['lo'])+' to '+pp(primary['hi'])),
       (pp(E['trend']['estimate'],3),'pp per month within the newer source<br>95% CI '+pp(E['trend']['lo'],3)+' to '+pp(E['trend']['hi'],3)),
       ('Timing matters','Forward expectation results change<br>with interpolation and controls')]
for i,f in enumerate(STUDY['findings']):
    finding_html.append(f'<article class="finding" id="{f["id"]}"><span class="finding-index">0{i+1}</span><h3>{escape(f["headline"])}</h3><p class="stat">{stats[i][0]}</p><p class="stat-label">{stats[i][1]}</p><p>{escape(f["text"])}</p><p class="caveat">{escape(f["caveat"])}</p><a class="text-link" href="#evidence">Inspect the evidence ↗</a><p class="source">{escape(f["locator"])}</p></article>')
values={
    'QUESTION':escape(STUDY['question']),'ANSWER':escape(STUDY['answer']),
    'PAPER_TITLE':escape(STUDY['paper_title']),'PAPER_SUBTITLE':escape(STUDY['paper_subtitle']),
    'CITATION':escape(STUDY['citation']),'BUILD_DATE':date.today().isoformat(),
    'GAP_SVG':chart(E['observations'],'gap'),'INFLATION_SVG':chart(E['observations'],'inflation'),
    'MODEL_SVG':model_svg(primary),'MODEL_ESTIMATE':pp(primary['estimate']),
    'MODEL_CI':f'95% confidence interval: {pp(primary["lo"])} to {pp(primary["hi"])} percentage points',
    'MODEL_NOTE':f'S1 · {int(primary["N"])} fitted weeks · segment-aware Newey–West intervals · p {escape(pvalue(primary["p"]))}',
    'FINDINGS':''.join(finding_html),
    'PERIOD_OPTIONS':''.join(f'<option value="{r["period"]}" {"selected" if r==last else ""}>{r["period"]}</option>' for r in E['observations'] if r['gap'] is not None),
    'INITIAL_PERIOD':f'{last["period"]} · gap {pp(last["gap"])} pp · inflation {fmt(last["inflation"],1)}%',
    'MONTHLY_ROWS':''.join(f'<tr><th scope="row">{r["period"]}</th><td>{pp(r["gap"]) if r["gap"] is not None else "Excluded"}</td><td>{fmt(r["inflation"],1) if r["inflation"] is not None else "Excluded"}</td><td>{"Newer source" if r["source"]=="new" else "Original source"}{" · text coverage excluded" if r["status"]!="included" else ""}</td></tr>' for r in E['observations']),
    'TREND':pp(E['trend']['estimate'],3),'TREND_CI':pp(E['trend']['lo'],3)+' to '+pp(E['trend']['hi'],3),
    'COMMON_TREND':pp(E['common_source_trend']['estimate'],3),'COMMON_P':fmt(E['common_source_trend']['p'],3),
    'WEEKLY_YEAR_P':fmt(next(r['p'] for r in E['time_sensitivity'] if r['frequency']=='weekly' and r['adjustment']=='year'),3),
    'MONTHLY_TREND_P':fmt(next(r['p'] for r in E['time_sensitivity'] if r['frequency']=='monthly' and r['adjustment']=='trend'),3),
    'LP_LIST':''.join(f'<li><b>{escape(r["label"])}</b>: {len(r["significant_horizons"])}/{r["tested_future_horizons"]} future horizons pass correction'+(f' (horizons {", ".join(map(str,r["significant_horizons"]))})' if r['significant_horizons'] else '')+'.</li>' for r in E['expectations']),
    'BASELINE':pp(E['baseline']['monthly'],3),
    'EVIDENCE_JSON':json.dumps(E,ensure_ascii=False,allow_nan=False).replace('<','\\u003c')
}
html=(SITE/'src/index.html').read_text(encoding='utf-8')
for k,v in values.items():html=html.replace('@@'+k+'@@',v)
assert '@@' not in html, 'Unexpanded template token'
(DIST/'index.html').write_text(html,encoding='utf-8')
for file in ['styles.css','app.js']:shutil.copyfile(SITE/'src'/file,DIST/file)
allowlist=['index.html','styles.css','app.js']+paperfiles
actual=[str(p.relative_to(DIST)).replace('\\','/') for p in DIST.rglob('*') if p.is_file()]
assert sorted(actual)==sorted(allowlist), f'Unexpected public files: {set(actual)-set(allowlist)}'
manifest={p:hashlib.sha256((DIST/p).read_bytes()).hexdigest() for p in allowlist}
(SITE/'qa').mkdir(exist_ok=True)
(SITE/'qa/build-manifest.json').write_text(json.dumps({'build_date':date.today().isoformat(),'files':manifest},indent=2),encoding='utf-8')
with zipfile.ZipFile(SITE/'hnb-attention-gap-publication.zip','w',zipfile.ZIP_DEFLATED) as z:
    for file in allowlist:z.write(DIST/file,file)
print(f'Built {len(allowlist)} allowlisted public files and publication ZIP; no source data required.')
