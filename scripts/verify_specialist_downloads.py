"""Check the refreshed paper, bilingual download links and public-file integrity."""
from pathlib import Path
from html.parser import HTMLParser
from pypdf import PdfReader
import hashlib, json, re

ROOT=Path(__file__).resolve().parents[1]
HUB=ROOT/'media-hub'
DIST=ROOT/'site-dist/media'
metadata=json.loads((HUB/'public/downloads/artifacts.json').read_text(encoding='utf-8'))
for name in ['PAPER_EXT.pdf','PAPER_EXT.html']:
    item=next(a for a in metadata if a['file']==name)
    data=(DIST/'downloads'/name).read_bytes()
    assert hashlib.sha256(data).hexdigest()==item['sha256']
    assert item['date']=='2026-09-28' and item['language']=='hr'
    assert item['period']=='2021-01/2026-08'

pdf=PdfReader(DIST/'downloads/PAPER_EXT.pdf')
assert len(pdf.pages)==18
text='\n'.join(p.extract_text() or '' for p in pdf.pages)
assert all(x in text for x in ['0,25','0,27','295','kolovoza 2026.','Sažetak'])
assert not re.search(r'C:[/\\]|/Users/|Invalid Date|<U\+|@[A-Z_]+@',text)
html=(DIST/'downloads/PAPER_EXT.html').read_text(encoding='utf-8')
assert '<math' in html and 'href="PAPER_EXT.pdf"' in html
assert not re.search(r'C:[/\\]|/Users/|Invalid Date|<U\+|@[A-Z_]+@',html)

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a': self.links.append(dict(attrs))

for lang in ['index.html','hr.html']:
    html=(DIST/lang).read_text(encoding='utf-8')
    card=html.split('<article class="study-card">',1)[1].split('</article>',1)[0]
    assert '28. 9. 2026.' in card and '295' in card and '68' in card
    assert not any(x in card for x in ['through May 2026','do svibnja 2026','0.21','0,21','studies/inflation/'])
    p=Links();p.feed(card)
    for ext in ['pdf','html']:
        a=next(a for a in p.links if a.get('href')=='downloads/PAPER_EXT.'+ext and 'download' in a)
        assert (DIST/a['href']).is_file()
    assert any(a.get('href')=='downloads/PAPER_EXT.html' and 'download' not in a for a in p.links)
print('Updated specialist paper verified: identical published assets, 18 PDF pages, native HTML equations, bilingual download links and current study scope.')
