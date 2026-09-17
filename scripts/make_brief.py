"""Bilingual two-page executive briefs; numeric claims use the frozen evidence."""
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
INK='#112838';BLUE='#165ce0';MUTED='#4f6470';M=42;W=511.276
def number(v,k=2,hr=False):return f'{100*v:.{k}f}'.replace('.',',' if hr else '.')

def make(lang):
    hr=lang=='hr';n=lambda v,k=2:number(v,k,hr);r=E['models'][0];t=E['trend']
    path=SITE/'public/downloads'/('hnb-attention-gap-brief'+('-hr' if hr else '')+'.pdf')
    c=canvas.Canvas(str(path),pagesize=(595.276,841.89),pageCompression=1)
    c.setTitle('HNB u raspravi o inflaciji - sažetak' if hr else 'HNB in Croatia’s inflation debate - executive brief')
    c.setAuthor('Research summary of the draft by Petra Palić and Luka Sikić')
    c.setSubject('Extended draft, 17 September 2026; author review pending')
    def text(value,y,size=10.2,font='Body',color=INK,leading=None):
        p=Paragraph(value,ParagraphStyle('block',fontName=font,fontSize=size,leading=leading or size*1.36,textColor=HexColor(color)))
        _,h=p.wrap(W,780)
        if y-h<42:raise ValueError(f'{lang}: text below footer at {y-h:.1f}: {value[:65]}')
        p.drawOn(c,M,y-h);return y-h
    def header(page):
        text('MONETARNA KOMUNIKACIJA / ISTRAŽIVAČKA STUDIJA' if hr else 'MONETARY COMMUNICATION / RESEARCH CASE STUDY',810,8.5,color=MUTED)
        c.setStrokeColor(HexColor('#cbd6de'));c.line(M,787,M+W,787)
        c.setFillColor(HexColor(MUTED));c.setFont('Body',8)
        c.drawString(M,25,'Nacrt · 17. 9. 2026. · Čeka autorsku provjeru' if hr else 'Draft · 17 September 2026 · Author review pending')
        c.drawRightString(M+W,25,f'{page} / 2')
    header(1)
    y=text('HNB u raspravi o inflaciji' if hr else 'HNB in Croatia’s inflation debate',764,25,font='Display',leading=29)-16
    y=text('Koliko je središnja banka vidljiva kada inflacija dominira vijestima?' if hr else S['question'],y,16,font='Display',leading=21)-14
    y=text('Broj institucionalnih objava pokazuje što je objavljeno. Analiza medija dodaje podatke o zastupljenosti institucije u široj raspravi. Ciljano proširenje moglo bi ispitati koja se objašnjenja prenose, kroz koje kanale i s kakvom točnošću.' if hr else 'Counting institutional publications tells us what was issued. Media analysis adds evidence about representation in the wider debate. A focused extension could examine which explanations are carried, through which channels, and how accurately.',y,10.2)-12
    image_height=300
    c.drawImage(str(SITE/'public/figures'/('visibility-full-hr.png' if hr else 'visibility-full.png')),M,y-image_height,width=W,height=image_height,mask='auto')
    y-=image_height+12
    findings=[
        ('<b>1. Viša inflacija prati manju vidljivost.</b> Inflacija viša za 1 pb povezana je s jazom većim za '+n(r['estimate'])+' pb (95%-tni interval '+n(r['lo'])+' do '+n(r['hi'])+'; 268 tjedana). Primarni model uključuje medijski obujam. Preciznost ovisi o vremenskim kontrolama.') if hr else ('<b>1. Higher inflation accompanies lower visibility.</b> A 1 pp higher inflation rate is associated with a '+n(r['estimate'])+' pp wider gap (95% CI '+n(r['lo'])+' to '+n(r['hi'])+'; 268 weeks). The primary model includes media volume. Precision depends on time controls.'),
        ('<b>2. Vidljivost pada unutar kasnijeg razdoblja.</b> Kontrolirani trend jaza iznosi +'+n(t['estimate'],3)+' pb mjesečno (95%-tni interval '+n(t['lo'],3)+' do '+n(t['hi'],3)+'; 25 mjeseci). Trend je pozitivan i među zajedničkim izvorima. Sastav objava može se mijenjati.') if hr else ('<b>2. Visibility declines within the later period.</b> The controlled gap trend is +'+n(t['estimate'],3)+' pp per month (95% CI '+n(t['lo'],3)+' to '+n(t['hi'],3)+'; 25 months). A positive trend also appears among common sources. Coverage composition may change.'),
        '<b>3. Stabilna veza s očekivanjima nije utvrđena.</b> Rezultati ovise o pridruživanju mjesečne ankete tjednima i izboru kontrola. Pojedini horizonti jesu značajni; vidljivost nije mjera razumijevanja ni povjerenja.' if hr else '<b>3. A stable expectations link is not established.</b> Results depend on how the monthly survey is assigned to weeks and which controls are used. Some horizons are significant; visibility does not measure understanding or trust.'
    ]
    for f in findings:y=text(f,y,10.5,leading=14.3)-13
    c.showPage();header(2)
    y=text('Od nalaza do primjene' if hr else 'From evidence to an applied pilot',764,25,font='Display',leading=30)-18
    y=text('Institucionalno objašnjenje → medijska zastupljenost → izloženost i razumijevanje → očekivanja i odluke.' if hr else 'Institutional explanation → media representation → exposure and understanding → expectations and decisions.',y,11,font='Body-Bold')-9
    y=text('To je konceptualni slijed, a ne procijenjeni uzročni lanac. Ovaj rad mjeri medijsku zastupljenost. Cilj je razumjeti prijenos informacija, a ne maksimizirati spominjanje institucije.' if hr else 'This is a conceptual pathway, not an estimated causal chain. The current study measures media representation. The objective is understanding how information travels, not maximising institutional mentions.',y,10.2)-20
    y=text('<b>Pokazatelj, intuitivno.</b> Ponderirani udio uzima u obzir istaknutost institucije i potencijalni doseg objava. Hipotetski: početni udio 4% minus tekući udio 3% daje jaz od +1 postotnog boda. Veći jaz znači manji udio. To nije udio ljudi ni jednostavan postotak članaka.' if hr else '<b>The measure, intuitively.</b> The weighted share accounts for institutional prominence and potential reach. Hypothetically: a 4% baseline minus a 3% current share gives a +1 percentage point gap. A larger gap means a smaller share. This is not a share of people or a simple percentage of articles.',y,9.7)-10
    y=text('PREDLOŽENO ISTRAŽIVANJE' if hr else 'PROPOSED RESEARCH',y,9,font='Body-Bold',color=BLUE)-10
    y=text('Kako se odabrana monetarna objašnjenja prenose u hrvatskim medijima? Dogovoriti mali skup komunikacija, razdoblje i odluku kojoj analiza treba pridonijeti.' if hr else 'How are selected monetary-policy explanations represented in Croatian media? Agree a small set of communications, a time window and the decision the analysis should inform.',y,10.2)-12
    tasks=[
      '<b>1. Provjera mjerenja.</b> Razlikovati HNB, ESB/Eurosustav, druge i nejasne navode. Isporuka: izvještaj o atribuciji, obuhvatu i pouzdanosti.' if hr else '<b>1. Validate measurement.</b> Distinguish HNB, ECB/Eurosystem, other and ambiguous references. Output: an attribution, coverage and reliability audit.',
      '<b>2. Praćenje objašnjenja.</b> Uz ručnu provjeru usporediti komunikacije i medijske objave. Isporuka: studije prijenosa poruka po kanalima i validirani analitički skup podataka.' if hr else '<b>2. Trace explanations.</b> Compare source communications with media items, using human validation. Output: message-uptake case studies by channel and a validated analytical dataset.',
      '<b>3. Podloga za odluku.</b> Isporuka: sažetak za rukovodstvo i preporuka opravdavaju li rezultati redovito praćenje ili zasebno istraživanje publike.' if hr else '<b>3. Inform the next decision.</b> Output: an executive assessment and a recommendation on whether recurring monitoring or separate audience research is justified.'
    ]
    for t in tasks:y=text(t,y,10.2)-10
    y=text('Ovo je prijedlog proširenja, a ne provedena analiza. Točnost prijenosa i validirana atribucija nisu još izmjerene. Opseg, pristup podatcima, rad i cijena dogovaraju se zasebno. Predstavljanje postojećih nalaza može biti početni angažman.' if hr else 'This is a proposed extension, not completed analysis. Message fidelity and validated attribution have not yet been measured. Scope, data access, effort and price would be agreed separately. A briefing of existing findings can be an initial engagement.',y,9.5)-17
    y=text('GRANICE ZA TUMAČENJE' if hr else 'ESSENTIAL INTERPRETATION LIMITS',y,9,font='Body-Bold',color=BLUE)-10
    y=text('Primarni uzorak: siječanj 2021. - svibanj 2026.; 62 uporabljiva mjeseca / 270 tjedana, odnosno 60 / 268 opažanja u glavnim regresijama. Siječanj-ožujak 2024. isključen je mjesečno; potpuni tjedan od 1. siječnja ostaje uključen. Razine preko promjene prikupljanja u travnju 2024. nisu usklađene.' if hr else 'Primary sample: January 2021-May 2026; 62 usable months / 270 weeks, with 60 / 268 observations in the main regressions. January-March 2024 is excluded monthly; the complete week from 1 January remains included. Levels across the April 2024 collection change are not harmonised.',y,9.3)-9
    y=text('Odabrani korpus nije reprezentativan uzorak publike. Generički nazivi mogu uključiti druge središnje banke. Potencijalni doseg nije izloženost; sentiment nije neovisno validiran. Nije utvrđen uzročni učinak na uvjerenja. Raniji i ponovno izračunani koeficijenti nisu potpuno usklađeni; točna replikacija ranijeg rada ostaje neriješena.' if hr else 'The selected corpus is not a representative audience sample. Generic terms can capture other central banks. Potential reach is not exposure; sentiment lacks independent validation. No causal effect on beliefs is established. Earlier reported and recalculated coefficients do not fully agree; exact earlier-paper replication remains unresolved.',y,9.3)-16
    y=text('AUTORI I IZVOR' if hr else 'AUTHORS AND SOURCE',y,9,font='Body-Bold',color=BLUE)-9
    y=text('<b>Petra Palić i Luka Sikić</b> · Hrvatsko katoličko sveučilište.' if hr else '<b>Petra Palić and Luka Sikić</b> · Hrvatsko katoličko sveučilište.',y,9.4)-7
    y=text('Neovisni istraživački nacrt od 17. rujna 2026.; nije publikacija HNB-a. Nalazi su uspoređeni sa spremljenim izlazima; modeli nisu ponovno procijenjeni. Izvor: odjeljci 4.2, 4.5, 4.6 i dodatak A23.' if hr else 'Independent draft of 17 September 2026; not an HNB publication. Findings were matched to saved outputs; models were not re-estimated. Source: sections 4.2, 4.5, 4.6 and Appendix A23.',y,8.7)-9
    if S.get('contact'):y=text(escape(S['contact']),y,9.4)-7
    links=('<link href="https://lusiki.github.io/HNB_Media_Attention/read/paper.html" color="'+BLUE+'">'+('Cjeloviti rad' if hr else 'Full paper')+'</link> · <link href="https://lusiki.github.io/HNB_Media_Attention/'+('hr.html' if hr else 'index.html')+'" color="'+BLUE+'">'+('Istraživačka stranica' if hr else 'Research page')+'</link> · <link href="https://lusiki.github.io/HNB_Media_Attention/downloads/pilot-outline.txt" color="'+BLUE+'">'+('Prijedlog pilota' if hr else 'Pilot outline')+'</link>')
    y=text(links,y,9.4);c.save();print(f'{path.name}: two pages; final content ends at {y:.1f} pt.')
for lang in ['en','hr']:make(lang)
(SITE/'public/downloads/citation.txt').write_text(S['citation']+'\n',encoding='utf-8')
