"""Targeted publication checks, including PDF integrity and bundle privacy."""
from pathlib import Path
from html.parser import HTMLParser
import argparse, csv, json, hashlib, re, zipfile
from urllib.parse import urlsplit,unquote
from pypdf import PdfReader
from charts import chart, CHART_SCALES

SITE=Path(__file__).resolve().parents[1]; DIST=SITE/'dist'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--research-root',type=Path,help='Optional local research folder for comparisons to original saved outputs.')
research_root=parser.parse_args().research_root
if research_root is not None:research_root=research_root.resolve()
checks={}
def check(name,condition):
    checks[name]=bool(condition)
    if not condition:raise AssertionError(name)

class Page(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.refs=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        for attr in ['href','src']:
            if attr in a:self.refs.append(a[attr])

for document in DIST.rglob('*.html'):
    html=document.read_text(encoding='utf-8');p=Page();p.feed(html)
    label=document.relative_to(DIST).as_posix()
    check(label+'_all_template_fields_expanded','@@' not in html)
    check(label+'_unique_html_ids',len(p.ids)==len(set(p.ids)))
    for ref in p.refs:
        u=urlsplit(ref)
        if u.scheme or u.netloc:continue
        if u.path:
            target=(document.parent/unquote(u.path)).resolve()
            check(label+'_asset_'+u.path,target.is_relative_to(DIST) and target.is_file())
            if u.fragment and target.suffix=='.html':
                linked=Page();linked.feed(target.read_text(encoding='utf-8'))
                check(label+'_linked_anchor_'+u.fragment,u.fragment in linked.ids)
        elif u.fragment:check(label+'_anchor_'+u.fragment,u.fragment in p.ids)

for name,count in [('brief',2),('brief-hr',2),('paper',32)]:
    html=(DIST/f'read/{name}.html').read_text(encoding='utf-8')
    check(name+'_reader_page_count',html.count('class="page-image"')==count)
    check(name+'_reader_has_selectable_text',html.count('class="transcription"')==count)
    check(name+'_reader_no_pdf_plugin',not any(tag in html for tag in ['<iframe','<embed','<object']))

e=json.loads((DIST/'data/evidence.json').read_text(encoding='utf-8'))
check('observation_fields_allowlisted',all(set(r)=={'period','gap','inflation','source','status'} for r in e['observations']))
check('three_missing_months_are_null',[r['period'] for r in e['observations'] if r['gap'] is None]==['2024-01','2024-02','2024-03'])
check('primary_cutoff',e['observations'][-1]['period']=='2026-05')
for metric in ['gap','inflation']:
    svg=chart(e['observations'],metric)
    segments=re.findall(r'<polyline[^>]* points="([^"]+)"',svg)
    check(metric+'_source_and_missing_breaks',len(segments)==2)
    check(metric+'_only_observed_points',sum(len(segment.split()) for segment in segments)==62)
with (DIST/'data/monthly-series.csv').open(encoding='utf-8-sig',newline='') as f:
    exported=list(csv.DictReader(f))
check('csv_and_json_observation_count',len(exported)==len(e['observations']))
check('csv_and_json_values_match',all(
    row['period']==r['period'] and row['source']==r['source'] and row['status']==r['status']
    and (None if row['gap']=='' else float(row['gap']))==r['gap']
    and (None if row['inflation']=='' else float(row['inflation']))==r['inflation']
    for row,r in zip(exported,e['observations'])))
if research_root is not None:
    with (research_root/'results/data_quality_series.csv').open(encoding='utf-8-sig',newline='') as f:
        source={r['date'][:7]:r for r in csv.DictReader(f) if r['frequency']=='monthly'}
    check('all_included_monthly_values_match_saved_outputs',all(r['gap'] is None or (r['gap']==float(source[r['period']]['IAG_primary']) and r['inflation']==float(source[r['period']]['pi_t'])) for r in e['observations']))
for scope,metrics in CHART_SCALES.items():
    for metric,(lo,hi,ticks) in metrics.items():
        values=[100*(e['baseline']['monthly']-r['gap']) if metric=='share' else r[metric]*(100 if metric=='gap' else 1) for r in e['observations'] if r['gap'] is not None and (scope=='all' or r['source']=='new')]
        check(scope+'_'+metric+'_axis_contains_every_point',all(lo<=v<=hi for v in values))
        check(scope+'_'+metric+'_variation_uses_plot_height',(max(values)-min(values))/(hi-lo)>.7)
check('sensitivity_axis_contains_every_interval',all(-.1<=r['lo']*100<=r['hi']*100<=.5 for r in e['time_sensitivity']))

manifest=json.loads((SITE/'qa/build-manifest.json').read_text(encoding='utf-8'))['files']
check('public_files_exactly_allowlisted',set(manifest)=={str(p.relative_to(DIST)).replace('\\','/') for p in DIST.rglob('*') if p.is_file()})
with zipfile.ZipFile(SITE/'hnb-attention-gap-publication.zip') as z:
    check('zip_exact_allowlist',set(z.namelist())==set(manifest))
    check('zip_hashes_match_dist',all(hashlib.sha256(z.read(f)).hexdigest()==manifest[f] for f in manifest))
private_pattern=re.compile(r'C:[\\/]|/Users/|/home/|full_text|item_id|api[_-]?key|BEGIN PRIVATE KEY',re.I)
for path in DIST.rglob('*'):
    if path.is_file() and path.suffix in ['.html','.js','.css','.json','.csv','.txt']:
        check('no_private_tokens_'+path.name,not private_pattern.search(path.read_text(encoding='utf-8')))

pdf_results={}
for name,count in [('hnb-attention-gap-paper.pdf',32),('hnb-attention-gap-brief.pdf',2),('hnb-attention-gap-brief-hr.pdf',2)]:
    path=DIST/'downloads'/name;reader=PdfReader(path)
    check(name+'_page_count',len(reader.pages)==count)
    pages=[p.extract_text() or '' for p in reader.pages]
    check(name+'_selectable_text',all(len(t)>100 for t in pages))
    check(name+'_no_private_paths',not private_pattern.search('\n'.join(pages)))
    check(name+'_no_unresolved_tokens',not any(t in '\n'.join(pages) for t in ['Error!','Reference source not found','`r ','@@']))
    pdf_results[name]={'pages':len(pages),'selectable_text':True,'links':[str(a.get_object().get('/A',{}).get('/URI','')) for p in reader.pages for a in p.get('/Annots',[]) if a.get_object().get('/A',{}).get('/URI')]}
check('paper_unchanged',hashlib.sha256((DIST/'downloads/hnb-attention-gap-paper.pdf').read_bytes()).hexdigest()=='00aa9a875226ee39d39049d975621a367aa7aa9adeea994e01d12c11469477d1')
for lang in ['en','hr']:
    name='hnb-attention-gap-brief'+('-hr' if lang=='hr' else '')+'.pdf'
    check(lang+'_brief_has_companion_links',set(pdf_results[name]['links'])=={'https://lusiki.github.io/HNB_Media_Attention/read/paper.html','https://lusiki.github.io/HNB_Media_Attention/'+('hr.html' if lang=='hr' else 'index.html'),'https://lusiki.github.io/HNB_Media_Attention/downloads/pilot-outline.txt'})
    body='\n'.join(p.extract_text() for p in PdfReader(DIST/'downloads'/name).pages)
    check(lang+'_trend_has_monthly_unit',('pb mjesečno' if lang=='hr' else 'pp per month') in body)
skipped=[]
if research_root is not None:
    provenance=json.loads((SITE/'content/research-input-hashes.json').read_text(encoding='utf-8'))
    check('research_input_hashes_unchanged',all(hashlib.sha256((research_root/'results'/name).read_bytes()).hexdigest()==sha for name,sha in provenance['inputs'].items()))
else:
    skipped=['Upstream saved-output comparison and source hashes require --research-root; not needed for a standalone publication build.']
(SITE/'qa/publication-checks.json').write_text(json.dumps({'checks':checks,'pdfs':pdf_results,'passed':sum(checks.values()),'skipped':skipped},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{sum(checks.values())} publication checks passed. Paper: 32 pages, unchanged; bilingual briefs: 2 pages each, selectable text and companion links.')
for note in skipped:print('Not run: '+note)
