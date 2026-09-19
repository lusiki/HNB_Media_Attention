"""Two-page governor briefs, using only the archived paper's saved evidence."""
from pathlib import Path
import json, os
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

def make(lang):
    hr=lang=='hr'
    def num(v,k=2):return f'{v:.{k}f}'.replace('.',',' if hr else '.')
    def pp(v,k=2):return num(100*v,k)
    def choose(en,cr):return cr if hr else en
    r=E['models'][0];t=E['trend'];common=E['common_source_trend'];net=E['centrality_trend']
    path=SITE/'public/downloads'/('hnb-attention-gap-brief'+('-hr' if hr else '')+'.pdf')
    c=canvas.Canvas(str(path),pagesize=(595.276,841.89),pageCompression=1)
    c.setTitle(choose('HNB in Croatia’s inflation debate - executive brief','HNB u raspravi o inflaciji - sažetak za guvernera'))
    c.setAuthor('Research summary of the draft by Petra Palić and Luka Sikić')
    c.setSubject('Evidence and implications for HNB; extended draft, 17 September 2026; author review pending')
    def text(value,y,size=10.3,font='Body',color=INK,leading=None):
        p=Paragraph(value,ParagraphStyle('block',fontName=font,fontSize=size,leading=leading or size*1.32,textColor=HexColor(color)))
        _,h=p.wrap(W,780)
        if y-h<46:raise ValueError(f'{lang}: text below footer at {y-h:.1f}: {value[:80]}')
        p.drawOn(c,M,y-h);return y-h
    def header(page):
        text(choose('RESEARCH BRIEF / IMPLICATIONS FOR HNB','ISTRAŽIVAČKI SAŽETAK / ZNAČENJE ZA HNB'),811,8.5,color=BLUE)
        c.setStrokeColor(HexColor('#cbd6de'));c.line(M,789,M+W,789)
        c.setFillColor(HexColor(MUTED));c.setFont('Body',8)
        c.drawString(M,25,choose('Draft: 17 September 2026 | Author review pending','Nacrt: 17. 9. 2026. | Čeka autorsku provjeru'))
        c.drawRightString(M+W,25,f'{page} / 2')
    def label(value,y):return text(value,y,9,font='Body-Bold',color=BLUE)-7
    def figure(name,y,height):
        c.drawImage(str(SITE/'public/figures'/name),M,y-height,width=W,height=height,mask='auto')
        return y-height-10
    header(1)
    y=text(choose('HNB in Croatia’s inflation debate','HNB u raspravi o inflaciji'),769,25,font='Display',leading=30)-12
    y=text(choose('More attention to prices need not mean more attention to the central bank.','Veća pozornost prema cijenama ne znači nužno veću pozornost prema središnjoj banci.'),y,16,font='Display',leading=21)-13
    y=text(choose('The paper asks whether the Croatian National Bank’s (HNB) relative media visibility keeps pace when inflation dominates the news. Its contribution is to separate what the institution publishes from its place in the wider debate. Higher inflation accompanies a smaller institutional share in the primary models; visibility declines during April 2024-May 2026.','Rad ispituje prati li relativna medijska vidljivost Hrvatske narodne banke (HNB) širenje vijesti o inflaciji. Njegov je doprinos razlikovanje onoga što institucija objavljuje od njezina mjesta u široj raspravi. U primarnim modelima viša inflacija prati manji institucionalni udio; vidljivost pada od travnja 2024. do svibnja 2026.'),y)-13
    y=label(choose('READING THE INDICATOR','KAKO ČITATI POKAZATELJ'),y)
    y=text(choose('<b>Relevance</b> selects items about inflation. <b>Prominence</b> reflects the institution’s presence in the title, position and frequency of mentions, and cues that it acts or speaks. The measure combines prominence with potential reach and compares this with reach across inflation coverage. The <b>attention gap = baseline share minus current weighted share</b>. A larger gap means less relative visibility.','<b>Relevantnost</b> izdvaja objave o inflaciji. <b>Istaknutost</b> obuhvaća prisutnost institucije u naslovu, položaj i učestalost spominjanja te naznake njezina djelovanja ili govora. Mjera spaja istaknutost s potencijalnim dosegom i uspoređuje ih s dosegom objava o inflaciji. <b>Jaz u pažnji = početni udio minus tekući ponderirani udio</b>. Veći jaz znači manju relativnu vidljivost.'),y,10)-8
    y=text(choose('Example: a 4% baseline and a 3% current share give a +1 percentage-point gap. These are illustrative values. The baseline is a historical reference, not a communication target; the share is neither readership nor a simple percentage of articles.','Primjer: početni udio od 4% i tekući udio od 3% daju jaz od +1 postotnog boda. Vrijednosti su ilustrativne. Baza je povijesna referenca, a ne komunikacijski cilj; udio ne mjeri čitatelje niti jednostavan postotak članaka.'),y,9.4,color=MUTED)-14
    y=label(choose('THE SCALE OF THE INFLATION ASSOCIATION','VELIČINA POVEZANOSTI S INFLACIJOM'),y)
    y=text(choose(f'<b>Inflation from 2% to 10%: a {pp(r["estimate"]*8)} percentage-point lower weighted share.</b> Holding the other variables fixed, the primary weekly model implies a weighted share lower by the same amount (95% interval: {pp(r["lo"]*8)} to {pp(r["hi"]*8)}). This is the paper’s conditional comparison, not a forecast or a policy effect.',f'<b>Inflacija s 2% na 10%: ponderirani udio manji za {pp(r["estimate"]*8)} postotnih bodova.</b> Uz ostale varijable nepromijenjene, primarni tjedni model podrazumijeva ponderirani udio manji za isti iznos (95%-tni interval: {pp(r["lo"]*8)} do {pp(r["hi"]*8)}). To je uvjetna usporedba iz rada, a ne prognoza ni učinak politike.'),y,10.3)-6
    y=figure('inflation-scenario'+('-hr' if hr else '')+'.png',y,W*4/9)
    y=text(choose(f'<b>How robust?</b> Per 1 percentage point higher inflation, the primary gap estimate is {pp(r["estimate"])} pp (95% interval {pp(r["lo"])} to {pp(r["hi"])}; 268 fitted weeks). All three chart models include media volume. With year effects, the interval includes zero; the association is not independent of every choice of time controls. The monthly trend-control model is also inconclusive.',f'<b>Koliko je nalaz robustan?</b> Uz inflaciju višu za 1 postotni bod primarna procjena jaza raste za {pp(r["estimate"])} pb (95%-tni interval {pp(r["lo"])} do {pp(r["hi"])}; 268 tjedana u regresiji). Sva tri modela na slici uključuju medijski obujam. Uz godišnje učinke interval obuhvaća nulu. Nalaz nije neovisan o svim vremenskim kontrolama; ni mjesečni model s trendovima ne odbacuje nulti nagib.'),y,9.8)-8
    y=text(choose('Source: paper Section 4.2 and Appendix A23. HICP is the Harmonised Index of Consumer Prices; inflation is the year-on-year rate.','Izvor: odjeljak 4.2 i dodatak A23 rada. HICP je harmonizirani indeks potrošačkih cijena; inflacija je godišnja stopa promjene.'),y,8.5,color=MUTED)
    print(lang,'page 1 content ends at',round(y,1))
    c.showPage();header(2)
    y=text(choose('What the findings mean for HNB','Što nalazi znače za HNB'),769,25,font='Display',leading=30)-12
    y=text(choose(f'<b>1. Assess visibility after the inflation surge as well.</b> Within April 2024-May 2026, the controlled gap trend is +{pp(t["estimate"],3)} pp per month (95% interval {pp(t["lo"],3)} to {pp(t["hi"],3)}; 25 fitted months). Keeping only common sources still gives +{pp(common["estimate"],3)} pp per month (p = {num(common["p"],3)}). This is evidence of declining relative visibility within that period, not proof that disinflation caused the decline.',f'<b>1. Pratiti vidljivost i nakon inflacijskog vala.</b> Od travnja 2024. do svibnja 2026. kontrolirani trend jaza iznosi +{pp(t["estimate"],3)} pb mjesečno (95%-tni interval {pp(t["lo"],3)} do {pp(t["hi"],3)}; 25 mjeseci u procjeni). Među zajedničkim izvorima iznosi +{pp(common["estimate"],3)} pb mjesečno (p = {num(common["p"],3)}). To je nalaz pada relativne vidljivosti unutar razdoblja, a ne dokaz da ga uzrokuje dezinflacija.'),y,10.2)-6
    y=figure('visibility-later'+('-hr' if hr else '')+'.png',y,W*4.9/10.5)
    y=text(choose(f'<b>2. Distinguish visibility from network position.</b> A share describes how much of the debate the institution occupies. Centrality describes its position among actors linked through media sources, weighting connections to well-connected actors more heavily. The common-source monthly trend is {num(net["estimate"],4)} index units (95% interval {num(net["lo"],4)} to {num(net["hi"],4)}; p = {num(net["p"],3)}). The interval includes zero: lasting structural erosion is not established.',f'<b>2. Razlikovati vidljivost od mrežnog položaja.</b> Udio opisuje zastupljenost u raspravi. Centralnost opisuje položaj među akterima koje povezuju medijski izvori, uz veću težinu veza s dobro povezanim akterima. Mjesečni trend među zajedničkim izvorima iznosi {num(net["estimate"],4)} indeksnih jedinica (95%-tni interval {num(net["lo"],4)} do {num(net["hi"],4)}; p = {num(net["p"],3)}). Interval obuhvaća nulu: trajna strukturna erozija nije utvrđena.'),y,10)-12
    y=text(choose('<b>3. Read media evidence alongside expectations surveys.</b> For the article-share measure, baseline weekly projections find no significant future horizons with linear survey interpolation, but weeks 1-2 with step assignment; the monthly comparison finds month 12, after correction for multiple tests. Controls change the pattern too. These results do not establish a stable predictive channel, or show that a media gap causes expectations to become unanchored.','<b>3. Medijske nalaze čitati uz ankete o očekivanjima.</b> Za udio članaka osnovne tjedne projekcije uz linearnu interpolaciju ankete ne nalaze značajne buduće horizonte. Uz stepenasto pridruživanje značajni su 1. i 2. tjedan, a u mjesečnim podatcima 12. mjesec, nakon korekcije za višestruko testiranje. Kontrole također mijenjaju obrazac. Stabilan prediktivni kanal nije utvrđen, kao ni tvrdnja da medijski jaz uzrokuje gubitak usidrenosti očekivanja.'),y,10)-12
    y=text(choose('<b>Implication for the governor.</b> Consider institutional output, relative media representation and public understanding as separate dimensions. More publications need not produce a larger share of a growing debate. The gap adds a diagnostic of representation; it does not score message quality, credibility or policy success.','<b>Značenje za guvernera.</b> Vlastite objave, relativnu medijsku zastupljenost i razumijevanje javnosti treba razmatrati odvojeno. Više objava ne jamči veći udio u rastućoj raspravi. Jaz dopunjuje uvid u zastupljenost; ne ocjenjuje kvalitetu poruke, vjerodostojnost ni uspjeh politike.'),y,10)-12
    y=label(choose('SCOPE AND SOURCE','OBUHVAT I IZVOR'),y)
    y=text(choose('January 2021-May 2026: 60 monthly / 268 weekly observations in the main regressions. Generic central-bank terms may include the ECB or others; potential reach is not observed exposure. The selected corpus is not a representative audience sample. Earlier-paper numerical discrepancies remain unresolved.','Siječanj 2021.-svibanj 2026.: 60 mjesečnih / 268 tjednih opažanja u glavnim regresijama. Generički izrazi mogu uključiti ESB ili druge banke; potencijalni doseg nije opažena izloženost. Korpus nije reprezentativan uzorak publike. Numerička odstupanja ranijeg rada ostaju neriješena.'),y,8.5,leading=11.1)-9
    y=text(choose('<b>Petra Palić and Luka Sikić</b> | Hrvatsko katoličko sveučilište. Independent draft, 17 September 2026; not an HNB publication. Sections 4.2-4.7, discussion, Appendices A12, A23 and B2. Figures and numbers use saved results; models were not re-estimated.','<b>Petra Palić i Luka Sikić</b> | Hrvatsko katoličko sveučilište. Neovisni nacrt, 17. rujna 2026.; nije publikacija HNB-a. Odjeljci 4.2-4.7, rasprava, dodatci A12, A23 i B2. Slike i brojke koriste spremljene rezultate; modeli nisu ponovno procijenjeni.'),y,8.3)-7
    y=text('<link href="../'+choose('index.html','hr.html')+'" color="'+BLUE+'">'+choose('Research page and interactive evidence','Istraživačka stranica i dodatni nalazi')+'</link>',y,9)
    c.save();print(lang,'page 2 content ends at',round(y,1),';',path.name)

for lang in ['en','hr']:make(lang)
(SITE/'public/downloads/citation.txt').write_text(S['citation']+'\n',encoding='utf-8')
