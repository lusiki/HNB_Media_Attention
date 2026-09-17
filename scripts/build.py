"""Offline, allowlisted bilingual publication build. No database access."""
from pathlib import Path
from datetime import date
from html import escape
from urllib.parse import quote
import json, shutil, hashlib, zipfile
from charts import chart, model_svg, sensitivity_svg
from readers import build_readers

SITE=Path(__file__).resolve().parents[1]
STUDY=json.loads((SITE/'content/study.json').read_text(encoding='utf-8'))
E=json.loads((SITE/'public/data/evidence.json').read_text(encoding='utf-8'))
DIST=SITE/'dist'; DIST.mkdir(exist_ok=True)
assets=['downloads/hnb-attention-gap-paper.pdf','downloads/hnb-attention-gap-brief.pdf','downloads/hnb-attention-gap-brief-hr.pdf','downloads/pilot-outline.txt','downloads/citation.txt','figures/attention-gap.png','figures/visibility-later.png','figures/visibility-later-hr.png','data/evidence.json','data/monthly-series.csv']
for name in assets:
    src=SITE/'public'/name
    if not src.is_file():raise FileNotFoundError(f'Required asset missing: {name}')
    dst=DIST/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
def fmt(v,k=2):return f'{v:.{k}f}'
def pp(v,k=2):return fmt(v*100,k)
def hr(v,k=2):return pp(v,k).replace('.',',')
def share(r):return pp(E['baseline']['monthly']-r['gap'])
def pvalue(v):return '< 0.001' if v<.001 else '= '+fmt(v,3)
def contact(language):
    c=STUDY.get('contact')
    if not c:return ''
    label='Discuss an applied research pilot' if language=='en' else 'Razgovarajmo o primijenjenom istraživanju'
    return f'<a class="button" href="mailto:{quote(c,safe="@.")}?subject=HNB%20media%20research%20pilot">{label} ↗</a>'

primary=E['models'][0];last=E['observations'][-1];later=[r for r in E['observations'] if r['period']>='2024-04']
targets=['inflation-evidence','trend-evidence','expectations-evidence']
stats=[(pp(primary['estimate']),'pp wider gap per +1 pp inflation<br>95% CI '+pp(primary['lo'])+' to '+pp(primary['hi'])),(pp(E['trend']['estimate'],3),'pp per month in the later collection period<br>95% CI '+pp(E['trend']['lo'],3)+' to '+pp(E['trend']['hi'],3)),('Survey timing matters','Results depend on monthly-to-weekly<br>assignment and the selected controls')]
findings=[]
for i,f in enumerate(STUDY['findings']):
    findings.append(f'<article class="finding" id="{f["id"]}"><span class="finding-index">0{i+1}</span><h3>{escape(f["headline"])}</h3><p class="stat">{stats[i][0]}</p><p class="stat-label">{stats[i][1]}</p><p>{escape(f["text"])}</p><p class="caveat">{escape(f["caveat"])}</p><p class="implication">{escape(f["implication"])}</p><a class="text-link" data-evidence href="#{targets[i]}">Inspect this finding ↗</a><p class="source">{escape(f["locator"])}</p></article>')
time_names={'none':'Primary','trend':'Segment trends','year':'Year effects'}
lp=[]
for r in E['expectations']:
    unit='weeks' if r['frequency']=='weekly' else 'months'
    sig=', '.join(map(str,r['significant_horizons']))
    explanation=f'horizons {sig} {unit} ahead pass correction' if sig else f'none of the 1–12 {unit}-ahead horizons pass correction'
    lp.append(f'<li><b>{escape(r["label"])}</b>: {explanation}.</li>')
values={
 'QUESTION':escape(STUDY['question']),'ANSWER':escape(STUDY['answer']),
 'PAPER_TITLE':escape(STUDY['paper_title']),'PAPER_SUBTITLE':escape(STUDY['paper_subtitle']),
 'CITATION':escape(STUDY['citation']),'BUILD_DATE':date.today().isoformat(),
 'CONTACT_EN':contact('en'),'CONTACT_HR':contact('hr'),
 'PRIMARY_HR':hr(primary['estimate']),'PRIMARY_CI_HR':hr(primary['lo'])+'–'+hr(primary['hi']),
 'TREND_HR':hr(E['trend']['estimate'],3),'TREND_CI_HR':hr(E['trend']['lo'],3)+'–'+hr(E['trend']['hi'],3),
 'SHARE_SVG':chart(later,'share',baseline=E['baseline']['monthly']),'INFLATION_SVG':chart(later,'inflation'),
 'MODEL_SVG':model_svg(primary),'MODEL_ESTIMATE':pp(primary['estimate']),
 'MODEL_CI':f'95% confidence interval: {pp(primary["lo"])} to {pp(primary["hi"])} percentage points',
 'MODEL_NOTE':f'{int(primary["N"])} fitted weeks · January 2021–May 2026, with exclusions',
 'MODEL_TECHNICAL':f'Sample S1 · equation 9b · segment-aware Newey–West intervals · p {escape(pvalue(primary["p"]))}',
 'SENSITIVITY_SVG':'<div class="sensitivity-wide">'+sensitivity_svg(E['time_sensitivity'])+'</div><div class="sensitivity-narrow">'+sensitivity_svg(E['time_sensitivity'],narrow=True)+'</div>',
 'SENSITIVITY_ROWS':''.join(f'<tr><th scope="row">{r["frequency"].title()}</th><td>{time_names[r["adjustment"]]}</td><td>{pp(r["estimate"],3)}</td><td>{pp(r["lo"],3)} to {pp(r["hi"],3)}</td></tr>' for r in E['time_sensitivity']),
 'FINDINGS':''.join(findings),
 'PERIOD_OPTIONS':''.join(f'<option value="{r["period"]}" {"selected" if r==last else ""}>{r["period"]}</option>' for r in later if r['gap'] is not None),
 'INITIAL_PERIOD':f'{last["period"]} · share {share(last)}% · gap {pp(last["gap"])} pp · inflation {fmt(last["inflation"],1)}%',
 'MONTHLY_ROWS':''.join(f'<tr><th scope="row">{r["period"]}</th><td>{share(r) if r["gap"] is not None else "Excluded"}</td><td>{pp(r["gap"]) if r["gap"] is not None else "Excluded"}</td><td>{fmt(r["inflation"],1) if r["inflation"] is not None else "Excluded"}</td><td>{"Later collection" if r["source"]=="new" else "Original collection"}{" · text coverage excluded" if r["status"]!="included" else ""}</td></tr>' for r in E['observations']),
 'TREND':pp(E['trend']['estimate'],3),'TREND_CI':pp(E['trend']['lo'],3)+' to '+pp(E['trend']['hi'],3),
 'COMMON_TREND':pp(E['common_source_trend']['estimate'],3),'COMMON_P':fmt(E['common_source_trend']['p'],3),
 'BASELINE':pp(E['baseline']['monthly'],3),'LP_LIST':''.join(lp),
 'EVIDENCE_JSON':json.dumps(E,ensure_ascii=False,allow_nan=False).replace('<','\\u003c')
}
for name in ['index.html','hr.html']:
    html=(SITE/'src'/name).read_text(encoding='utf-8')
    for k,v in values.items():html=html.replace('@@'+k+'@@',v)
    assert '@@' not in html, f'Unexpanded template token in {name}'
    (DIST/name).write_text(html,encoding='utf-8')
for name in ['styles.css','app.js']:shutil.copyfile(SITE/'src'/name,DIST/name)
allowlist=['index.html','hr.html','styles.css','app.js']+assets+build_readers(SITE,DIST)
actual=[str(p.relative_to(DIST)).replace('\\','/') for p in DIST.rglob('*') if p.is_file()]
assert sorted(actual)==sorted(allowlist), f'Unexpected public files: {set(actual)-set(allowlist)}'
manifest={p:hashlib.sha256((DIST/p).read_bytes()).hexdigest() for p in allowlist}
(SITE/'qa').mkdir(exist_ok=True)
(SITE/'qa/build-manifest.json').write_text(json.dumps({'build_date':date.today().isoformat(),'files':manifest},indent=2),encoding='utf-8')
with zipfile.ZipFile(SITE/'hnb-attention-gap-publication.zip','w',zipfile.ZIP_DEFLATED) as z:
    for name in allowlist:z.write(DIST/name,name)
print(f'Built {len(allowlist)} allowlisted public files and publication ZIP.')
