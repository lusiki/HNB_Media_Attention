"""Regenerate both Croatian reports and accessible HTML from saved aggregates.

Run from the publication checkout; requires ReportLab and pypdf. Fonts are
bundled at assets/fonts with their licenses. No database or network is used.
"""
from pathlib import Path
import csv,hashlib,json
from pypdf import PdfReader
from report_overview import overview
from report_language import language

SITE=Path(__file__).resolve().parents[1]
OUT=SITE/'public/downloads';OUT.mkdir(parents=True,exist_ok=True)
D=json.loads((SITE/'public/data/media/media.json').read_text(encoding='utf-8'))
L=json.loads((SITE/'public/data/media/report-language.json').read_text(encoding='utf-8'))
assert L['distinct_normalized_bodies']==33100 and len(L['term_patterns'])==52
assert all(0<=v<=33100 for v in L['terms'].values())
assert all(0<=v<=g['n'] for g in L['groups'].values() for v in g['terms'].values())
layout={'overview':overview(OUT,D),'language':language(OUT,D,L)}
with (SITE/'public/data/media/report-language.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.writer(f);w.writerow(['analysis_id','scope','term','text_count','denominator'])
    for key in ['terms','phrases']:
        for term,count in L[key].items():w.writerow([L['analysis_id'],key,term,count,33100])
    for scope,g in L['groups'].items():
        for term,count in g['terms'].items():w.writerow([L['analysis_id'],scope,term,count,g['n']])
artifacts=json.loads((OUT/'artifacts.json').read_text(encoding='utf-8'))
stems=['hnb-u-medijskom-prostoru','hnb-od-rijeci-do-javnih-pitanja']
artifacts=[a for a in artifacts if not any(a['file'].startswith(stem+'.') for stem in stems)]
for stem,pages in zip(stems,[14,12]):
    assert len(PdfReader(OUT/(stem+'.pdf')).pages)==pages
    for ext in ['pdf','html']:
        path=OUT/(stem+'.'+ext)
        artifacts.append({'file':path.name,'language':'hr','format':ext,'date':'2026-09-21',
          'period':'2021-01/2026-08','data_version':'2026-09-21.1','method_version':'1.0',
          'presentation_version':'2026-09-21.2','source_identity':'HNB_MEDIA / maintained merged snapshot 2026-09-19',
          'analysis_id':'HNB_MEDIA_LEXICAL_1.0' if stem==stems[1] else 'HNB_MEDIA',
          'pages':pages if ext=='pdf' else None,'slides':None,'page_size':'A4' if ext=='pdf' else None,
          'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
          'citation':stem+'.html#stranica-'+str(pages),
          'canonical_url':'https://lusiki.github.io/HNB_Media_Attention/media/downloads/'+path.name,
          'review':'author_review_pending'})
(OUT/'artifacts.json').write_text(json.dumps(artifacts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(SITE/'qa').mkdir(exist_ok=True)
(SITE/'qa/long-reports-layout.json').write_text(json.dumps(layout,indent=2)+'\n',encoding='utf-8')
print('Generated 14-page overview and 12-page language report with matching HTML; layout:',layout)
