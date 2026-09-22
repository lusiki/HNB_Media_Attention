"""Render every released PDF page with Poppler; create manageable QA contact sheets."""
from pathlib import Path
import subprocess,json,re
from PIL import Image,ImageOps,ImageDraw
from pypdf import PdfReader
SITE=Path(__file__).resolve().parents[1];OUT=SITE/'qa/pdf-review';OUT.mkdir(parents=True,exist_ok=True)
POPPLER=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe'
report=[]
for pdf in sorted((SITE/'dist/downloads').glob('*.pdf')):
    reader=PdfReader(pdf);prefix=OUT/pdf.stem
    subprocess.run([str(POPPLER),'-scale-to','1250','-png',str(pdf),str(prefix)],check=True,capture_output=True)
    pages=sorted(p for p in OUT.glob(pdf.stem+'-*.png') if re.fullmatch(re.escape(pdf.stem)+r'-[0-9]+\.png',p.name));assert len(pages)==len(reader.pages)
    for start in range(0,len(pages),4):
        tiles=[]
        for p in pages[start:start+4]:
            im=Image.open(p).convert('RGB');im.thumbnail((620,830));tile=Image.new('RGB',(650,865),'#dde4ea');tile.paste(im,((650-im.width)//2,25));ImageDraw.Draw(tile).text((12,840),p.name,fill='black');tiles.append(tile)
        sheet=Image.new('RGB',(1300,865*((len(tiles)+1)//2)),'white')
        for i,tile in enumerate(tiles):sheet.paste(tile,((i%2)*650,(i//2)*865))
        sheet.save(OUT/(pdf.stem+f'-sheet-{start//4+1}.jpg'),quality=90)
    report.append({'file':pdf.name,'pages':len(pages),'rendered':True,'renderer':'Poppler','manual_visual_review':'pending'})
(OUT/'render-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(report)
