"""Validate new report outputs against the fixed public measurement contracts."""
from pathlib import Path
import csv,hashlib,json,re
from html.parser import HTMLParser
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1];HUB=ROOT/'media-hub';DATA=HUB/'public/data/media';OUT=HUB/'public/downloads'
D=json.loads((DATA/'media.json').read_text(encoding='utf-8'))
L=json.loads((DATA/'report-language.json').read_text(encoding='utf-8'))
assert sum(r['hnb_count'] for r in D['monthly'] if r['period']<='2026-08')==L['publications']==33235
assert L['body_publications']+L['without_body']==L['publications']
assert L['body_publications']-L['distinct_normalized_bodies']==36
assert L['distinct_normalized_bodies']==L['assessable_contexts']==33100
assert L['context_missing']==0
assert len(L['term_patterns'])==52 and len(L['phrase_patterns'])==12
assert set(L['groups'])=={d['id'] for d in D['subject_definitions']}
assert L['script_sha256']==hashlib.sha256((HUB/'scripts/prepare_report_language.py').read_bytes()).hexdigest()
rows=list(csv.DictReader((DATA/'report-language.csv').open(encoding='utf-8')))
for r in rows:
    scope=r['scope'];n=int(r['text_count']);denom=int(r['denominator'])
    expected=L[scope] if scope in ['terms','phrases'] else L['groups'][scope]['terms']
    assert n==expected[r['term']] and 0<=n<=denom
    assert denom==(33100 if scope in ['terms','phrases'] else L['groups'][scope]['n'])
class Reader(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.figures=0;self.alternatives=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        if tag=='figure':self.figures+=1
        if tag=='details':self.alternatives+=1
artifacts=json.loads((OUT/'artifacts.json').read_text(encoding='utf-8'))
for stem,pages,figures in [('hnb-u-medijskom-prostoru',16,5),('hnb-od-rijeci-do-javnih-pitanja',14,6)]:
    pdf=PdfReader(OUT/(stem+'.pdf'));assert len(pdf.pages)==pages
    for i,page in enumerate(pdf.pages):
        text=page.extract_text();assert len(text)>300 and '\ufffd' not in text
        assert abs(float(page.mediabox.width)-595.276)<.1
        if i:assert f'{i+1} / {pages}' in text
    assert 'Autorska provjera u tijeku' in pdf.pages[0].extract_text()
    html=(OUT/(stem+'.html')).read_text(encoding='utf-8');p=Reader();p.feed(html)
    assert all('stranica-'+str(i) in p.ids for i in range(1,pages+1))
    assert len(p.ids)==len(set(p.ids)), 'Duplicate SVG ids would clip later figures'
    assert p.figures==p.alternatives==figures
    assert '\ufffd' not in html and not re.search(r'C:[/\\]|ITEM_ID|publication_key',html)
    for ext in ['pdf','html']:
        file=stem+'.'+ext;a=next(a for a in artifacts if a['file']==file);b=(OUT/file).read_bytes()
        assert a['bytes']==len(b) and a['sha256']==hashlib.sha256(b).hexdigest()
        assert a['review']=='author_review_pending' and a['language']=='hr'
    for lang in ['hr.html','index.html']:
        home=(HUB/'dist'/lang).read_text(encoding='utf-8')
        assert 'id="izvjestaj"' in home and 'href="#izvjestaj"' in home
        assert f'href="downloads/{stem}.pdf"' in home and f'href="downloads/{stem}.html"' in home
print('Report checks passed: 30 PDF pages, 11 figures with numeric HTML alternatives, lexical denominators, CSV, status, hashes and bilingual links.')
