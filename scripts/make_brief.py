"""Two-page research-magazine briefs with full-sample, vector evidence figures."""
from pathlib import Path
import json
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from pypdf import PdfReader,PdfWriter,Transformation
from artifact_style import SITE,PAPER,INK,BLUE,MUTED,RULE,PALE,register_pdf_fonts

register_pdf_fonts()
E=json.loads((SITE/'public/data/evidence.json').read_text(encoding='utf-8'))
PAGE_W,PAGE_H=595.276,841.89
M=38;W=PAGE_W-2*M;GUTTER=20;COL=(W-2*GUTTER)/3
WORK=SITE/'.runtime/brief-figures'
layout=[]

def make(lang):
    hr=lang=='hr';t=lambda en,cr:cr if hr else en
    def num(value,digits=2):return f'{value:.{digits}f}'.replace('.',',' if hr else '.')
    r=E['models'][0];trend=E['trend'];common=E['common_source_trend'];net=E['centrality_trend']
    stream=BytesIO();c=canvas.Canvas(stream,pagesize=(PAGE_W,PAGE_H),pageCompression=1)
    charts=[];page_number=1
    def text(value,x,y,width,size=11,font='Sans',color=INK,leading=None,key=''):
        p=Paragraph(value,ParagraphStyle('text',fontName=font,fontSize=size,leading=leading or size*1.28,textColor=HexColor(color)))
        _,height=p.wrap(width,PAGE_H)
        if y-height<51:raise ValueError(f'{lang} page {page_number}: {key} below content boundary: {y-height:.1f}')
        p.drawOn(c,x,y-height)
        layout.append({'language':lang,'page':page_number,'key':key,'box':[x,y-height,x+width,y],'text':value})
        return y-height
    def line(y,x=M,width=W,color=RULE,weight=.65):
        c.setStrokeColor(HexColor(color));c.setLineWidth(weight);c.line(x,y,x+width,y)
    def small(value,x,y,width=W):return text(value,x,y,width,8.4,'Sans-Bold',BLUE,leading=10.4,key='label')
    def furniture(number):
        c.setFillColor(HexColor(PAPER));c.rect(0,0,PAGE_W,PAGE_H,fill=1,stroke=0)
        c.setFont('Sans-Bold',8.7);c.setFillColor(HexColor(INK));c.drawString(M,806,t('MONETARY COMMUNICATION / RESEARCH BRIEF','MONETARNA KOMUNIKACIJA / ISTRAŽIVAČKI SAŽETAK'))
        c.setFont('Sans',8.5);c.drawRightString(PAGE_W-M,806,f'{number} / 2');line(791)
        line(44)
        c.setFillColor(HexColor(MUTED));c.setFont('Sans',7.6)
        c.drawString(M,30,t('Palić & Sikić | 17 September 2026 | Independent research; author review pending','Palić i Sikić | 17. rujna 2026. | Neovisno istraživanje; čeka autorsku provjeru'))
        c.drawRightString(PAGE_W-M,30,'2026-09-19.3')
    def figure(name,top):
        file=WORK/(name+'.pdf')
        source=PdfReader(file).pages[0]
        height=W*float(source.mediabox.height)/float(source.mediabox.width)
        charts.append((page_number-1,file,M,top-height,W))
        layout.append({'language':lang,'page':page_number,'key':name,'box':[M,top-height,M+W,top],'figure':True})
        return top-height

    furniture(1)
    small(t('CROATIA / JANUARY 2021 - MAY 2026','HRVATSKA / SIJEČANJ 2021. - SVIBANJ 2026.'),M,773)
    text(t('HNB in a crowded<br/>inflation debate.','HNB u širokoj<br/>raspravi o inflaciji.'),M,751,W,38,'Display',leading=40.5,key='headline')
    text(t('Higher inflation accompanies a smaller institutional share<br/>in the primary models. Time controls qualify that finding.','Viša inflacija u primarnim modelima prati manji institucionalni<br/>udio. Vremenske kontrole ograničavaju taj zaključak.'),M,653,W,14,'Serif',leading=18,key='deck')
    text(t('Petra Palić & Luka Sikić  /  Hrvatsko katoličko sveučilište','Petra Palić i Luka Sikić  /  Hrvatsko katoličko sveučilište'),M,601,W,9.1,'Sans',MUTED,key='authors')
    line(581)
    text('-'+num(r['estimate']*100),M,565,210,54,'Display',BLUE,leading=57,key='main-estimate')
    text(t('percentage points of weighted share<br/>per +1 percentage point of inflation','postotnih bodova ponderiranog udjela<br/>uz inflaciju višu za 1 postotni bod'),M,500,207,10.2,'Sans',leading=13,key='estimate-unit')
    text(t(f'<b>Primary weekly model.</b> The 95% interval is {num(r["lo"]*100)} to {num(r["hi"]*100)} percentage points lower. The full-sample models contain 268 fitted weeks or 60 months. This is a conditional association, not a causal effect.',f'<b>Primarni tjedni model.</b> 95%-tni interval odgovara udjelu manjem za {num(r["lo"]*100)} do {num(r["hi"]*100)} postotnih bodova. Modeli cijelog uzorka imaju 268 tjednih ili 60 mjesečnih opažanja. To je uvjetna povezanost, a ne uzročni učinak.'),M+233,562,W-233,10.9,'Sans',leading=14.1,key='principal-qualification')
    line(449)
    text(t('An inflation comparison: 2% to 10%','Usporedba inflacije: s 2% na 10%'),M,433,W,19,'Display',leading=23,key='scenario-title')
    text(t(f'Primary difference: -{num(r["estimate"]*800)} pp. Other variables held fixed; all models include media volume.',f'Primarna razlika: -{num(r["estimate"]*800)} pb. Ostale varijable nepromijenjene; svi modeli uključuju medijski obujam.'),M,405,W,9.6,'Sans',MUTED,leading=12.2,key='scenario-description')
    figure('brief-scenario-'+lang,387)
    text(t('Points show estimates; lines show 95% intervals. With year effects, the interval includes zero: the association is sensitive to time controls.','Točke označavaju procjene, a crte 95%-tne intervale. Uz godišnje učinke interval obuhvaća nulu: povezanost je osjetljiva na vremenske kontrole.'),M,190,W,10.1,'Sans',leading=12.6,key='scenario-qualification')
    line(149)
    half=(W-GUTTER)/2
    text(t('What is being measured?','Što se zapravo mjeri?'),M,135,half,15,'Display',leading=18,key='measure-title')
    text(t('Inflation relevance selects the items; prominence and potential reach determine their weights. The gap is the baseline share minus the current share. The baseline is a reference, not a target.','Relevantnost za inflaciju izdvaja objave; istaknutost i potencijalni doseg određuju pondere. Jaz je referentni udio minus tekući udio. Referenca nije komunikacijski cilj.'),M,111,half,9.6,'Sans',leading=12,key='measure-definition')
    x=M+half+GUTTER
    text(t('Same numerator, smaller share.','Isti brojnik, manji udio.'),x,135,half,14.2,'Display',leading=18,key='example-title')
    text('4 / 100 = 4%<font color="'+MUTED+'"> &nbsp; | &nbsp; </font>4 / 200 = 2%',x,109,half,16,'Display',BLUE,leading=20,key='example-arithmetic')
    text(t('Illustrative units: unchanged numerator, doubled denominator. The example does not establish an observed cause.','Ilustrativne jedinice: isti brojnik, dvostruki nazivnik. Primjer ne utvrđuje uzrok opaženih promjena.'),x,84,half,9.1,'Sans',MUTED,leading=11.3,key='example-limit')
    c.showPage();page_number=2;furniture(2)
    small(t('THE FULL SAMPLE / PRIMARY CORPUS','CIJELI UZORAK / PRIMARNI KORPUS'),M,773)
    text(t('The whole timeline, in view.','Cijelo razdoblje u jednom pogledu.'),M,750,W,28,'Display',leading=33,key='timeline-title')
    text(t('January 2021 - May 2026. Monthly weighted visibility and inflation.<br/>Separate scales; observed series, not fitted trends.','Siječanj 2021. - svibanj 2026. Mjesečna ponderirana vidljivost i inflacija.<br/>Zasebne skale; opažene serije, a ne procijenjeni trendovi.'),M,707,W,10.5,'Sans',MUTED,leading=13.2,key='timeline-scope')
    figure('brief-timeline-'+lang,673)
    text(t('Weighted visibility relates institutional prominence and potential reach to the inflation corpus. Potential reach is not observed readership or understanding.','Ponderirana vidljivost povezuje institucionalnu istaknutost i potencijalni doseg s inflacijskim korpusom. Potencijalni doseg nije opažena čitanost ni razumijevanje.'),M,435,W,9.6,'Sans',MUTED,leading=12,key='timeline-meaning')
    line(401)
    # Three findings share a baseline and column grid, with scope next to each claim.
    for index,label in enumerate([t('01 / VISIBILITY TREND','01 / TREND VIDLJIVOSTI'),t('02 / NETWORK POSITION','02 / MREŽNI POLOŽAJ'),t('03 / EXPECTATIONS','03 / OČEKIVANJA')]):small(label,M+index*(COL+GUTTER),384,COL)
    text('-'+num(trend['estimate']*100,3),M,365,COL,31,'Display',BLUE,leading=35,key='trend-number')
    text(t('pp per month','pb mjesečno'),M,326,COL,10,'Sans-Bold',leading=12,key='trend-unit')
    text(t('April 2024 - May 2026','Travanj 2024. - svibanj 2026.'),M,302,COL,8.8,'Sans',MUTED,leading=11,key='trend-scope')
    text(t(f'Controlled share trend: 95% interval -{num(trend["hi"]*100,3)} to -{num(trend["lo"]*100,3)} pp per month (25 months). Common sources also give a negative trend: -{num(common["estimate"]*100,3)} pp per month. This is a result for the stated period.',f'Kontrolirani trend udjela: 95%-tni interval od -{num(trend["hi"]*100,3)} do -{num(trend["lo"]*100,3)} pb mjesečno (25 mjeseci). I trend zajedničkih izvora je negativan: -{num(common["estimate"]*100,3)} pb mjesečno. Nalaz vrijedi za navedeno razdoblje.'),M,281,COL,9.5,'Sans',leading=12.2,key='trend-qualification')
    x=M+COL+GUTTER
    text(t('Direction<br/>uncertain','Neizvjestan<br/>smjer'),x,362,COL,23,'Display',leading=25,key='network-verdict')
    text(t('April 2024 - May 2026','Travanj 2024. - svibanj 2026.'),x,302,COL,8.8,'Sans',MUTED,leading=11,key='network-scope')
    text(t(f'The common-source centrality trend is {num(net["estimate"],4)} index units per month. Its 95% interval ({num(net["lo"],4)} to {num(net["hi"],4)}) includes zero. Lasting network decline is not established. Centrality is not trust.',f'Trend centralnosti zajedničkih izvora iznosi {num(net["estimate"],4)} indeksnih jedinica mjesečno. 95%-tni interval ({num(net["lo"],4)} do {num(net["hi"],4)}) obuhvaća nulu. Trajni pad mrežnog položaja nije utvrđen. Centralnost nije povjerenje.'),x,281,COL,9.5,'Sans',leading=12.2,key='network-qualification')
    x=M+2*(COL+GUTTER)
    text(t('No stable<br/>predictive link','Nema stabilne<br/>prediktivne veze'),x,362,COL,22,'Display',leading=25,key='expectations-verdict')
    text(t('January 2021 - May 2026','Siječanj 2021. - svibanj 2026.'),x,302,COL,8.8,'Sans',MUTED,leading=11,key='expectations-scope')
    text(t('Article-share projections: no significant future horizons with linear weekly assignment; weeks 1-2 with step assignment; month 12 in monthly data, after correction. Controls also matter. Understanding and anchoring are not established by this pattern.','Projekcije udjela objava: linearno tjedno pridruživanje bez značajnih budućih horizonata; stepenasto pridruživanje: 1. i 2. tjedan; mjesečni podatci: 12. mjesec, nakon korekcije. Kontrole također utječu. Obrazac ne utvrđuje razumijevanje ni usidrenost.'),x,281,COL,9.5,'Sans',leading=12.2,key='expectations-qualification')
    line(165)
    for index,label in enumerate([t('PUBLICATION','VLASTITE OBJAVE'),t('REPRESENTATION','ZASTUPLJENOST'),t('UNDERSTANDING','RAZUMIJEVANJE')]):
        text(label,M+index*(COL+GUTTER),151,COL,10.1,'Sans-Bold',BLUE if index==1 else MUTED,leading=13,key='communication-dimension')
    text(t('For HNB: read publication activity, media representation and audience understanding together. This study measures representation; it complements communication records and audience research.','Za HNB: vlastite objave, medijsku zastupljenost i razumijevanje javnosti pratiti zajedno. Istraživanje mjeri zastupljenost i dopunjuje evidenciju komunikacije i istraživanja publike.'),M,127,W,11.2,'Serif',leading=14,key='implication')
    text(t('Scope: selected media corpus, not a representative audience sample. Generic references can include the ECB. Earlier-paper numerical discrepancies remain unresolved.','Obuhvat: odabrani medijski korpus, a ne reprezentativan uzorak publike. Generičke reference mogu uključiti ESB. Numerička odstupanja ranijeg rada ostaju neriješena.'),M,80,W,8.2,'Sans',MUTED,leading=10.2,key='scope')
    # Small source strip remains above the footer and links to the companion evidence.
    c.setFont('Sans',7.6);c.setFillColor(HexColor(MUTED))
    c.drawString(M,51,t('Sources: Sections 4.2-4.7; Appendices A12, A23, B2.','Izvori: odjeljci 4.2-4.7; dodatci A12, A23, B2.'))
    c.setFillColor(HexColor(BLUE));link=t('Interactive evidence','Interaktivni nalazi');c.drawRightString(PAGE_W-M,51,link)
    c.linkURL('../'+('hr.html' if hr else 'index.html'),(PAGE_W-M-100,48,PAGE_W-M,60),relative=0,thickness=0)
    c.save();stream.seek(0)
    base=PdfReader(stream)
    for page,file,x,y,width in charts:
        graphic=PdfReader(file).pages[0];scale=width/float(graphic.mediabox.width)
        base.pages[page].merge_transformed_page(graphic,Transformation().scale(scale).translate(x,y),over=True)
    writer=PdfWriter();writer.append(base)
    writer.add_metadata({'/Title':t('HNB in Croatia\'s inflation debate - full-sample research brief','HNB u hrvatskoj raspravi o inflaciji - cijeli uzorak'),'/Author':'Petra Palić and Luka Sikić','/Subject':'January 2021 - May 2026 | Manuscript 17 September 2026 | Author review pending | Presentation 2026-09-19.3','/Keywords':'HNB, Croatia, inflation, media visibility, 2021-2026'})
    path=SITE/'public/downloads'/('hnb-attention-gap-brief'+('-hr' if hr else '')+'.pdf')
    with path.open('wb') as output:writer.write(output)
    print(f'Created {path.name}: two pages, embedded Source fonts and full-sample vector timeline.')

for language in ['en','hr']:make(language)
(SITE/'qa/brief-layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
