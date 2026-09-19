"""Targeted publication checks, including PDF integrity and bundle privacy."""
from pathlib import Path
from html.parser import HTMLParser
import argparse, csv, json, hashlib, re, zipfile
from urllib.parse import urlsplit,unquote
from pypdf import PdfReader
from charts import chart

SITE=Path(__file__).resolve().parents[1]; DIST=SITE/'dist'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--research-root',type=Path,help='Optional saved research inputs for upstream comparisons.')
ROOT=parser.parse_args().research_root
if ROOT is not None:ROOT=ROOT.resolve()
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
    if document.name in ['index.html','hr.html']:
        check(label+'_removed_pilot_and_logo',not re.search(r'pilot|H<span> / </span>AG|communication-path',html,re.I))
        check(label+'_scenario_present','scenario-figure' in html)
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

for name,count in [('brief',2),('brief-hr',2)]:
    html=(DIST/f'read/{name}.html').read_text(encoding='utf-8')
    check(name+'_reader_page_count',html.count('class="page-image"')==count)
    check(name+'_reader_has_selectable_text',html.count('class="transcription"')==count)
    check(name+'_reader_no_pdf_plugin',not any(tag in html for tag in ['<iframe','<embed','<object']))

e=json.loads((DIST/'data/evidence.json').read_text(encoding='utf-8'))
check('observation_fields_allowlisted',all(set(r)=={'period','gap','inflation'} for r in e['observations']))
check('published_observations_numeric',len(e['observations'])==62 and all(isinstance(r['gap'],float) and isinstance(r['inflation'],(float,int)) for r in e['observations']))
check('primary_cutoff',e['observations'][-1]['period']=='2026-05')
with (DIST/'data/monthly-series.csv').open(encoding='utf-8-sig',newline='') as stream:
    exported=list(csv.DictReader(stream))
check('csv_matches_json',len(exported)==len(e['observations']) and all(a['period']==b['period'] and float(a['gap'])==b['gap'] and float(a['inflation'])==b['inflation'] for a,b in zip(exported,e['observations'])))
fingerprints=json.loads((SITE/'content/publication-input-hashes.json').read_text(encoding='utf-8'))
def publication_hash(path):
    data=path.read_bytes()
    if path.suffix in {'.json','.csv','.txt'}:data=data.replace(b'\r\n',b'\n')
    return hashlib.sha256(data).hexdigest()
check('committed_publication_inputs',all(publication_hash(SITE/'public'/name)==digest for name,digest in fingerprints['files'].items()))

if ROOT is not None:
    with (ROOT/'results/data_quality_series.csv').open(encoding='utf-8-sig',newline='') as f:
        source={r['date'][:7]:r for r in csv.DictReader(f) if r['frequency']=='monthly'}
    check('all_included_monthly_values_match_saved_outputs',all(r['gap'] is None or (r['gap']==float(source[r['period']]['IAG_primary']) and r['inflation']==float(source[r['period']]['pi_t'])) for r in e['observations']))
    def saved(name):
        with (ROOT/'results'/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
    def exact(row,source):return all(row[k]==float(source[k]) for k in ['estimate','se','lo','hi','p','N'])
    for r in e['models']:
        src=next(s for s in saved('primary_coefficients.csv') if s['frequency']==r['frequency'] and s['spec']==r['specification'] and s['sample']=='S1' and s['outcome']=='IAG_primary' and s['term']=='pi_t')
        check('model_matches_'+r['frequency']+'_'+r['specification'],exact(r,src))
    for r in e['time_sensitivity']:
        src=next(s for s in saved('regimes_common_slope_sensitivity.csv') if s['frequency']==r['frequency'] and s['adjustment']==r['adjustment'])
        check('time_controls_match_'+r['frequency']+'_'+r['adjustment'],exact(r,src))
    for key,file,outcome in [('trend','regimes_trend.csv','IAG_primary'),('common_source_trend','regimes_common_network.csv','IAG_common')]:
        src=next(s for s in saved(file) if s['frequency']=='monthly' and s['sample']=='S3' and s['outcome']==outcome)
        check(key+'_matches',exact(e[key],src))
    for r,outcome in zip(e['expectations'],['exp_linear','exp_step','exp_balance']):
        rows=[s for s in saved('expectations_irf.csv') if s['sample']=='S1' and s['frequency']==r['frequency'] and s['outcome']==outcome and s['exposure']=='IAG_ext' and s['specification']=='continuity' and int(s['horizon'])>0]
        check('expectations_match_'+outcome,r['significant_horizons']==[int(s['horizon']) for s in rows if float(s['p_bonf'])<.05] and len(rows)==12)
check('signature_gap_axis_contains_every_point',all(r['gap'] is None or -12.5<=100*r['gap']<=5 for r in e['observations']))
check('signature_inflation_axis_contains_every_point',all(r['inflation'] is None or -.7<=r['inflation']<=14.5 for r in e['observations']))
check('full_share_axis_contains_every_point',all(r['gap'] is None or 0<=100*(e['baseline']['monthly']-r['gap'])<=18 for r in e['observations']))
check('later_share_axis_contains_every_point',all(0<=100*(e['baseline']['monthly']-r['gap'])<=6 for r in e['observations'] if r['period']>='2024-04'))
check('later_gap_axis_contains_every_point',all(-2<=100*r['gap']<=5 for r in e['observations'] if r['period']>='2024-04'))
check('sensitivity_axis_contains_every_interval',all(-.1<=r['lo']*100<=r['hi']*100<=.5 for r in e['time_sensitivity']))
for metric in ['share','gap','inflation']:
    svg=chart(e['observations'],metric,baseline=e['baseline']['monthly'])
    check(metric+'_single_continuous_path',svg.count('<polyline')==1)
    check(metric+'_no_source_marker','source change' not in svg and '<rect' not in svg)
    points=re.search(r'points="([^"]+)"',svg)[1].split()
    check(metric+'_only_observed_points',len(points)==62)
if ROOT is not None:
    with (ROOT/'results/regimes_common_network.csv').open(encoding='utf-8-sig',newline='') as f:
        network=next(r for r in csv.DictReader(f) if r['sample']=='S3' and r['frequency']=='monthly' and r['outcome']=='C_EV_common')
    check('centrality_estimate_and_uncertainty_match',all(e['centrality_trend'][k]==float(network[k]) for k in e['centrality_trend']))
    with (ROOT/'results/primary_magnitude.csv').open(encoding='utf-8-sig',newline='') as f:
        magnitude=next(r for r in csv.DictReader(f) if r['sample']=='S1' and r['frequency']=='weekly')
    check('scenario_matches_paper_magnitude',abs(e['models'][0]['estimate']*8-float(magnitude['delta_8pp']))<1e-14)
    for r in e['time_sensitivity']:
        check('scenario_interval_'+r['frequency']+'_'+r['adjustment'],-.65<r['lo']*800<r['hi']*800<3.65)

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
for name,count in [('hnb-attention-gap-brief.pdf',2),('hnb-attention-gap-brief-hr.pdf',2)]:
    path=DIST/'downloads'/name;reader=PdfReader(path)
    check(name+'_page_count',len(reader.pages)==count)
    pages=[p.extract_text() or '' for p in reader.pages]
    check(name+'_selectable_text',all(len(t)>100 for t in pages))
    check(name+'_no_private_paths',not private_pattern.search('\n'.join(pages)))
    check(name+'_no_unresolved_tokens',not any(t in '\n'.join(pages) for t in ['Error!','Reference source not found','`r ','@@']))
    pdf_results[name]={'pages':len(pages),'selectable_text':True,'links':[str(a.get_object().get('/A',{}).get('/URI','')) for p in reader.pages for a in p.get('/Annots',[]) if a.get_object().get('/A',{}).get('/URI')]}
if ROOT is not None:check('paper_unchanged',hashlib.sha256((ROOT/'results/qa/PAPER_EXT.pdf').read_bytes()).hexdigest()=='00aa9a875226ee39d39049d975621a367aa7aa9adeea994e01d12c11469477d1')
for lang in ['en','hr']:
    name='hnb-attention-gap-brief'+('-hr' if lang=='hr' else '')+'.pdf'
    check(lang+'_brief_has_companion_links',set(pdf_results[name]['links'])=={'../'+('hr.html' if lang=='hr' else 'index.html')})
    body='\n'.join(p.extract_text() for p in PdfReader(DIST/'downloads'/name).pages)
    check(lang+'_trend_has_monthly_unit',('pb mjesečno' if lang=='hr' else 'pp per month') in body)
    check(lang+'_brief_has_no_pilot','pilot' not in body.lower())
    check(lang+'_brief_has_scenario',('1,68' if lang=='hr' else '1.68') in body)
    check(lang+'_brief_has_centrality',('centralnost' if lang=='hr' else 'centrality') in body.lower())
editorial_pattern=re.compile(r'missing(?: values| data| months| monthly)|excluded(?: media| months| monthly)|with exclusions|collection (?:change|phase|regime|break)|text.coverage gap|levels.{0,40}harmon|nedostatka teksta|promjen[ae] prikupljanja|faze prikupljanja|isključen.{0,25}uzor',re.I)
for path in DIST.rglob('*'):
    if not path.is_file():continue
    if path.suffix in ['.html','.js','.json','.csv','.txt']:
        check('editorial_scope_'+path.name,not editorial_pattern.search(path.read_text(encoding='utf-8')))
    elif path.suffix=='.pdf':
        check('editorial_scope_'+path.name,not editorial_pattern.search(' '.join(p.extract_text() for p in PdfReader(path).pages)))
check('manuscript_not_in_public_bundle',not (DIST/'downloads/hnb-attention-gap-paper.pdf').exists())
check('no_public_collection_fields','coverage' not in e and all('missing_rule' not in row for row in e['series_metadata']))
if ROOT is not None:
    provenance=json.loads((SITE/'content/research-input-hashes.json').read_text(encoding='utf-8'))
    check('research_input_hashes_unchanged',all(hashlib.sha256((ROOT/'results'/name).read_bytes()).hexdigest()==sha for name,sha in provenance['inputs'].items()))
(SITE/'qa/publication-checks.json').write_text(json.dumps({'checks':checks,'pdfs':pdf_results,'passed':sum(checks.values())},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{sum(checks.values())} publication checks passed. Bilingual briefs and readers: two pages each.')

if ROOT is None:print('Standalone checks complete. Optional upstream checks use --research-root.')
