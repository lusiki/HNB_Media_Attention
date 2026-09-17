"""Editable two-page publication brief; all estimates from the public data contract."""
from pathlib import Path
import json, os
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

SITE=Path(__file__).resolve().parents[1]
S=json.loads((SITE/'content/study.json').read_text(encoding='utf-8'))
E=json.loads((SITE/'public/data/evidence.json').read_text(encoding='utf-8'))
font_sets=[
    (Path(os.environ.get('OBS_FONT_DIR','C:/Windows/Fonts')),('arial.ttf','arialbd.ttf','georgia.ttf')),
    (Path('/usr/share/fonts/truetype/dejavu'),('DejaVuSans.ttf','DejaVuSans-Bold.ttf','DejaVuSerif.ttf')),
]
for directory,names in font_sets:
    if all((directory/name).is_file() for name in names):
        for label,name in zip(['Body','Body-Bold','Display'],names):
            pdfmetrics.registerFont(TTFont(label,str(directory/name)))
        break
else:
    raise SystemExit('Install DejaVu fonts or set OBS_FONT_DIR to a folder containing arial.ttf, arialbd.ttf and georgia.ttf. Existing PDF can still be built/deployed unchanged.')
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Body-Bold',italic='Body',boldItalic='Body-Bold')
OUT=SITE/'public/downloads/hnb-attention-gap-brief.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True)
c=canvas.Canvas(str(OUT),pagesize=(595.276,841.89),pageCompression=1)
c.setTitle('The HNB Attention Gap - Two-page research briefing')
c.setAuthor('Research summary of the draft by Petra Palić and Luka Sikić')
c.setSubject('Extended research draft, 17 September 2026; author review pending')
INK='#112838'; BLUE='#165ce0'; MUTED='#4f6470'; M=42; W=511.276

def text(value,x,y,size=10.5,width=W,font='Body',color=INK,leading=None):
    p=Paragraph(value,ParagraphStyle('block',fontName=font,fontSize=size,leading=leading or size*1.38,textColor=HexColor(color),spaceAfter=0))
    _,h=p.wrap(width,780)
    if y-h<39:raise ValueError(f'Text below footer: {value[:65]} at {y-h}')
    p.drawOn(c,x,y-h);return y-h

def header(page):
    text('MONETARY COMMUNICATION / RESEARCH EDITION 01',M,809,8.5,color=MUTED)
    c.setStrokeColor(HexColor('#cbd6de'));c.line(M,787,M+W,787)
    c.setFillColor(HexColor(MUTED));c.setFont('Body',8)
    c.drawString(M,25,'Extended draft · 17 September 2026 · Author review pending')
    c.drawRightString(M+W,25,f'{page} / 2')

def pp(value,k=2):return f'{100*value:.{k}f}'

header(1)
text('The HNB Attention Gap',M,768,29,font='Display',leading=34)
text(S['subtitle'],M,727,12,color=MUTED)
text(escape(S['question']),M,694,18,font='Display',leading=24)
text('The extended study separates relative institutional visibility from inflation itself. Its findings support monitoring media representation, while limiting claims about communication effects and public beliefs.',M,633,10.7)
c.drawImage(str(SITE/'public/figures/brief-chart.png'),M,321,width=W,height=238,mask='auto')
text('Figure: selected series from the draft’s Figure 1, January 2021-May 2026. Gap shown in percentage points; inflation on a separate scale. Missing media-text months in early 2024 are left blank. April 2024 changes the data source; levels across it are not harmonised.',M,314,8.7,color=MUTED,leading=11.5)
y=251
r=E['models'][0]
y=text('<b>1. Higher inflation accompanies lower relative visibility.</b> A one percentage point higher HICP inflation rate is associated with a '+pp(r['estimate'])+' pp wider gap in the primary weekly model (95% CI '+pp(r['lo'])+' to '+pp(r['hi'])+'; N = '+str(int(r['N']))+'). This is conditional association; significance is sensitive to time controls.',M,y,10.2,leading=13.7)-11
r=E['trend']
y=text('<b>2. Lower inflation does not guarantee recovery.</b> Within April 2024-May 2026, the controlled monthly trend is +'+pp(r['estimate'],3)+' pp (95% CI '+pp(r['lo'],3)+' to '+pp(r['hi'],3)+'). A positive trend also appears for common sources. This does not establish hysteresis.',M,y,10.2,leading=13.7)-11
y=text('<b>3. A stable expectations channel is not established.</b> Forward projection results depend on survey interpolation and controls. Some horizons are significant; media visibility does not directly measure public understanding or trust.',M,y,10.2,leading=13.7)
c.showPage()
header(2)
text('What HNB readers can take from it',M,766,25,font='Display',leading=30)
y=text('Use relative visibility as a diagnostic alongside the number of institutional messages and the quality of their transmission. The evidence opens a discussion about where HNB appears in inflation coverage; it does not prescribe an optimal share or demonstrate the effect of communication policy.',M,716,10.5)-21
text('THE MEASURE',M,y,9,font='Body-Bold',color=BLUE);y-=23
y=text('<b>Attention gap = baseline weighted share - current weighted share.</b> Positive values mean lower visibility than the reference; negative values mean higher visibility. The numerator combines inflation-relevant institutional items, salience and vendor potential reach. The denominator is reach in the inflation corpus, plus one.',M,y,10.3)-10
y=text('The baseline is the January-June 2021 mean after excluding initial share outliers beyond two standard deviations. It is calculated separately for monthly ('+pp(E['baseline']['monthly'],3)+'%) and weekly ('+pp(E['baseline']['weekly'],3)+'%) data. The reference is not a normative target.',M,y,10.3)-19
text('SAMPLE & METHODS',M,y,9,font='Body-Bold',color=BLUE);y-=23
y=text('Primary sample: January 2021-May 2026, with 62 usable months / 270 weeks and 60 / 268 fitted observations. Monthly January-March 2024 is excluded for text coverage; the complete week starting 1 January remains eligible. Newly added platforms are excluded. The main sample stops before the June 2026 change in vendor sentiment labels.',M,y,10.3)-9
y=text('The primary model controls for inflation changes, euro adoption, reach concentration, vendor sentiment, data source and log HNB-corpus volume. Confidence intervals use segment-aware Newey-West estimates. Weekly macroeconomic series repeat monthly information. Values in this brief match saved outputs; models were not re-estimated for the website.',M,y,10.3)-19
text('LIMITS TO KEEP BESIDE THE FINDINGS',M,y,9,font='Body-Bold',color=BLUE);y-=23
y=text('The vendor query and selection change in April 2024. Keeping common sources cannot rule out changes within their coverage. Reach is potential audience, not actual exposure; some values are imputed. Generic central-bank terms may capture institutions other than HNB. Sentiment lacks independent corpus validation.',M,y,10.3)-9
y=text('The inflation association is not significant in every time-control specification. Forward expectations results vary with interpolation and controls. HANFA comparisons and instruments do not establish a causal mechanism. Earlier reported and recalculated coefficients do not fully agree; exact legacy replication remains unresolved.',M,y,10.3)-18
text('AUTHORS & SOURCE',M,y,9,font='Body-Bold',color=BLUE);y-=22
y=text('<b>Petra Palić and Luka Sikić</b> · Hrvatsko katoličko sveučilište.<br/>Both are named manuscript authors; individual roles and contact details are not supplied.',M,y,9.5)-8
y=text(escape(S['citation']),M,y,9,leading=12)-7
y=text('Sources: section 4.2 / Table 6; section 4.6; section 4.5 / Table 8 / Figure 5; Appendix A23. The Croatian manuscript is a provisional extended draft, not an HNB publication.',M,y,8.5,color=MUTED,leading=11)-8
y=text('<link href="hnb-attention-gap-paper.pdf" color="'+BLUE+'">Read the full paper (companion PDF)</link>  ·  <link href="../index.html" color="'+BLUE+'">Research page (companion website)</link>',M,y,9,leading=12)
c.save()
(SITE/'public/downloads/citation.txt').write_text(S['citation']+'\n',encoding='utf-8')
print(f'Created {OUT.name}; second-page content ends at {y:.1f} pt.')
