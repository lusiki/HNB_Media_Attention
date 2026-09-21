"""A4 editorial report layout with vector charts and a matching HTML edition."""
from pathlib import Path
from html import escape
import math, random, re
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, Line, String, PolyLine
from reportlab.graphics import renderPDF, renderSVG

ROOT=Path(__file__).resolve().parents[2]
for name,file in [('Sans','SourceSans3-Regular.ttf'),('Bold','SourceSans3-Semibold.ttf'),('Serif','SourceSerif4-Regular.ttf'),('Display','SourceSerif4Display-Regular.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(ROOT/'assets/fonts'/file)))
pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='Bold',italic='Sans',boldItalic='Bold')
INK='#172A32';NAVY='#153641';BLUE='#2454CF';COPPER='#A95836';GOLD='#E7B880';MUTED='#53636A';PAPER='#FAF9F4';RULE='#D5D7CF';PALE='#E9EDF6'
W,H=595.276,841.89;M=46;CW=W-2*M

def number(v,d=0):return f'{v:,.{d}f}'.replace(',','@').replace('.',',').replace('@','.')
def pct(v,n):return number(100*v/n,1)+'%'
def style(size=11.5,font='Sans',color=INK,leading=None):
    return ParagraphStyle('p',fontName=font,fontSize=size,leading=leading or size*1.37,textColor=HexColor(color))

class Report:
    def __init__(self,path,title,short,total,subtitle):
        self.path=path;self.title=title;self.short=short;self.total=total;self.page=0;self.html=[];self.lowest=[];self.figure_serial=0
        self.c=canvas.Canvas(str(path),pagesize=(W,H),pageCompression=1,invariant=1)
        self.c.setTitle(title);self.c.setAuthor('HNB media research project');self.c.setSubject('Javni istraživački nacrt; autorska provjera u tijeku. HNB_MEDIA, 2021-01/2026-08.');self.subtitle=subtitle
    def finish_page(self):
        if not self.page:return
        if self.y<67:raise ValueError(f'{self.short} page {self.page} overflows: y={self.y:.1f}')
        self.lowest.append(round(self.y,1));self.html.append('</section>');self.c.showPage()
    def new(self,kicker,title,lead=None):
        self.finish_page();self.page+=1;c=self.c;c.setFillColor(HexColor(PAPER));c.rect(0,0,W,H,fill=1,stroke=0)
        c.setFillColor(HexColor(COPPER));c.setFont('Bold',8.6);c.drawString(M,H-38,f'{self.page:02d} / {kicker.upper()}')
        c.setStrokeColor(HexColor(RULE));c.line(M,45,W-M,45)
        c.setFont('Sans',7);c.setFillColor(HexColor(MUTED));c.drawString(M,31,'HNB U MEDIJIMA / '+self.short.upper()+' / NACRT · 21. 9. 2026.');c.drawRightString(W-M,31,f'{self.page} / {self.total}')
        self.y=H-70;self.html.append(f'<section id="stranica-{self.page}"><p class="eyebrow">{self.page:02d} / {escape(kicker)}</p>')
        self.text(title,26,'Display',after=15,tag='h2',leading=30)
        if lead:self.text(lead,12.3,after=16)
    def text(self,txt,size=11.5,font='Sans',color=INK,after=11,tag='p',leading=None):
        para=Paragraph(txt,style(size,font,color,leading));_,height=para.wrap(CW,1000)
        para.drawOn(self.c,M,self.y-height);self.y-=height+after
        self.html.append(f'<{tag}>{txt}</{tag}>')
    def sub(self,title,txt=None):
        self.text(title,13,'Bold',after=6,tag='h3')
        if txt:self.text(txt)
    def note(self,txt):self.text(txt,9,'Sans',MUTED,after=12)
    def callout(self,txt):
        p=Paragraph(txt,style(17,'Serif',NAVY,22));_,h=p.wrap(CW-28,1000)
        self.c.setFillColor(HexColor(PALE));self.c.rect(M,self.y-h-24,CW,h+24,fill=1,stroke=0)
        self.c.setFillColor(HexColor(BLUE));self.c.rect(M,self.y-h-24,3,h+24,fill=1,stroke=0)
        p.drawOn(self.c,M+14,self.y-h-12);self.y-=h+40;self.html.append('<blockquote>'+txt+'</blockquote>')
    def table(self,headers,rows,widths=None,size=10.1):
        widths=widths or [CW/len(headers)]*len(headers)
        values=[[Paragraph(str(x),style(size,'Bold' if i==0 else 'Sans',INK,size*1.25)) for x in row] for i,row in enumerate([headers]+rows)]
        t=Table(values,colWidths=widths);t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),HexColor(PALE)),('LINEBELOW',(0,0),(-1,-1),.5,HexColor(RULE)),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
        _,h=t.wrap(CW,1000);t.drawOn(self.c,M,self.y-h);self.y-=h+15
        self.html.append('<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+str(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>')
    def figure(self,drawing,caption,rows=None,headers=None):
        renderPDF.draw(drawing,self.c,M,self.y-drawing.height);self.y-=drawing.height+8
        svg=renderSVG.drawToString(drawing)
        svg=re.sub(r'<\?xml.*?\?>|<!DOCTYPE.*?\]?>','',svg,flags=re.S)
        # Inline SVG ids share a document namespace: each figure needs its own clip.
        self.figure_serial+=1
        for id in re.findall(r'\bid="([^"]+)"',svg):
            unique=f'figure-{self.figure_serial}-{id}'
            svg=svg.replace(f'id="{id}"',f'id="{unique}"').replace(f'url(#{id})',f'url(#{unique})')
        svg=svg.replace('font-family: Bold;', 'font-family: ReportSans; font-weight: 600;').replace('font-family: Sans;', 'font-family: ReportSans; font-weight: 400;')
        svg=svg.replace('<title>...</title>','<title>'+escape(re.sub('<[^>]+>','',caption))+'</title>').replace('<desc>...</desc>','<desc>Brojčani podaci dostupni su u tablici ispod grafikona.</desc>')
        self.html.append('<figure>'+svg+'<figcaption>'+caption+'</figcaption></figure>')
        # Figure captions are included once in HTML.
        old=len(self.html);self.note(caption);self.html=self.html[:old]
        if rows:
            self.html.append('<details><summary>Brojčani podaci uz grafikon</summary><div class="table-wrap"><table><thead><tr>'+''.join('<th>'+str(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div></details>')
    def cover(self,lines,deck,stats,closing):
        self.page=1;c=self.c;c.setFillColor(HexColor(PAPER));c.rect(0,0,W,H,fill=1,stroke=0)
        c.setFillColor(HexColor(NAVY));c.rect(0,275,W,H-275,fill=1,stroke=0)
        c.setFillColor(HexColor(GOLD));c.setFont('Bold',9);c.drawString(M,H-55,'HNB U HRVATSKIM MEDIJIMA / ISTRAŽIVAČKI IZVJEŠTAJ')
        yy=H-143
        for line in lines:
            c.setFont('Display',34);c.setFillColor(HexColor('#FFFFFF'));c.drawString(M,yy,line);yy-=42
        p=Paragraph(deck,style(15,'Sans','#E2EBEA',20));_,h=p.wrap(CW,200);p.drawOn(c,M,yy-h-5)
        c.setStrokeColor(HexColor(GOLD));c.setLineWidth(2);c.line(M,yy-h-32,M+82,yy-h-32)
        c.setFont('Sans',11);c.setFillColor(HexColor('#E2EBEA'));c.drawString(M,yy-h-64,'Siječanj 2021. - kolovoz 2026.');c.drawString(M,yy-h-85,'21. rujna 2026.')
        c.setFont('Bold',10);c.drawString(M,yy-h-117,'Javni istraživački nacrt');c.setFont('Sans',10);c.drawString(M,yy-h-135,'Autorska provjera u tijeku')
        for i,(value,label) in enumerate(stats):
            x=M+i*(CW/3);c.setFont('Serif',24);c.setFillColor(HexColor(GOLD));c.drawString(x,338,value)
            pp=Paragraph(label,style(9,'Sans','#FFFFFF',12));_,hh=pp.wrap(CW/3-14,100);pp.drawOn(c,x,321-hh)
        self.y=H;self.html.append('<section id="stranica-1" class="cover"><p class="eyebrow">HNB u hrvatskim medijima / Istraživački izvještaj</p><h1>'+escape(self.title)+'</h1><p class="lead">'+deck+'</p><p>Siječanj 2021. - kolovoz 2026. · 21. rujna 2026.</p><p>Javni istraživački nacrt. Autorska provjera u tijeku.</p><div class="stats">'+''.join('<p><b>'+v+'</b><br>'+l+'</p>' for v,l in stats)+'</div>')
        self.y=235;self.text(closing,22,'Display',leading=28,after=15)
        self.note('Neovisno istraživanje. Publikacija ne podrazumijeva pripadnost HNB-u ni njegovo odobrenje.')
        c.setFont('Sans',8);c.setFillColor(HexColor(MUTED));c.drawString(M,32,'HNB_MEDIA · podaci 2026-09-21.1 · '+self.subtitle)
    def save(self):
        self.finish_page();assert self.page==self.total,(self.page,self.total);self.c.save()
        nav='<nav><a href="../hr.html#izvjestaj">HNB u hrvatskim medijima</a><a href="'+self.path.name+'">Preuzmi PDF · '+str(self.total)+' stranica</a></nav>'
        html='<!doctype html><html lang="hr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escape(self.title)+'</title><link rel="stylesheet" href="hnb-reports.css"></head><body>'+nav+'<main>'+''.join(self.html)+'</main><footer>HNB_MEDIA · 21. 9. 2026. · Autorska provjera u tijeku</footer></body></html>'
        self.path.with_suffix('.html').write_text(html,encoding='utf-8',newline='\n')
        return self.lowest

def bars(items,width=CW,height=None,label_width=203,color=BLUE,denominator=None):
    height=height or len(items)*31+22;d=Drawing(width,height);row=(height-18)/len(items);maxv=max(v for _,v in items);bw=width-label_width-96
    for i,(label,v) in enumerate(items):
        y=height-18-i*row;d.add(String(0,y-1,label,fontName='Sans',fontSize=10.3,fillColor=HexColor(INK)))
        d.add(Rect(label_width,y-3,bw*v/maxv,11,fillColor=HexColor(color),strokeColor=None))
        text=number(v)+((' | '+pct(v,denominator)) if denominator else '')
        d.add(String(width,y-1,text,textAnchor='end',fontName='Bold',fontSize=10,fillColor=HexColor(INK)))
    return d

def timeline(monthly,metric='hnb_count',height=180,stable=None):
    width=CW;d=Drawing(width,height);l=40;right=10;b=27;t=23;vals=[x[metric] for x in monthly];maximum=max(vals)*1.05
    x=lambda i:l+i*(width-l-right)/(len(vals)-1);y=lambda v:b+(height-t-b)*v/maximum
    for j in range(5):
        v=maximum*j/4;d.add(Line(l,y(v),width-right,y(v),strokeColor=HexColor(RULE),strokeWidth=.5));d.add(String(l-6,y(v)-3,number(v),textAnchor='end',fontName='Sans',fontSize=8,fillColor=HexColor(MUTED)))
    boundary=next(i for i,r in enumerate(monthly) if r['period']=='2024-01')
    d.add(Line(x(boundary),b,x(boundary),height-17,strokeColor=HexColor(COPPER),strokeWidth=.8,strokeDashArray=[3,3]));d.add(String(x(boundary)+5,height-12,'01/2024: promjena prikupljanja',fontName='Sans',fontSize=8,fillColor=HexColor(COPPER)))
    for key,col in [(metric,BLUE)]+([(stable,COPPER)] if stable else []):
        points=[]
        for i,r in enumerate(monthly):points.extend([x(i),y(r[key])])
        d.add(PolyLine(points,strokeColor=HexColor(col),strokeWidth=1.7,fillColor=None))
    for i,r in enumerate(monthly):
        if r['period'].endswith('-01'):d.add(String(x(i),8,r['period'][:4],textAnchor='middle',fontName='Sans',fontSize=9,fillColor=HexColor(MUTED)))
    return d

def heatmap(labels,columns,values,width=CW,height=310):
    d=Drawing(width,height);left=203;cw=(width-left)/len(columns);rh=(height-30)/len(labels);maximum=max(max(r) for r in values)
    for j,label in enumerate(columns):d.add(String(left+(j+.5)*cw,height-12,label,textAnchor='middle',fontName='Bold',fontSize=10,fillColor=HexColor(INK)))
    for i,label in enumerate(labels):
        yy=height-29-(i+1)*rh;d.add(String(0,yy+rh/2-3,label,fontName='Sans',fontSize=10,fillColor=HexColor(INK)))
        for j,val in enumerate(values[i]):
            alpha=val/maximum;col=Color(.92-.78*alpha,.94-.61*alpha,.98-.2*alpha)
            d.add(Rect(left+j*cw,yy,cw-2,rh-2,fillColor=col,strokeColor=None));d.add(String(left+(j+.5)*cw,yy+rh/2-3,number(val,1),textAnchor='middle',fontName='Bold',fontSize=10,fillColor=HexColor('#FFFFFF' if alpha>.55 else INK)))
    return d

def cloud(items,width=CW,height=240,max_words=30):
    """Deterministic horizontal packing, with exact frequencies supplied separately."""
    items=sorted(items,key=lambda x:(-x[1],x[0]))[:max_words];d=Drawing(width,height);occupied=[];rng=random.Random(20260921)
    for index,(label,v) in enumerate(items):
        size=11+32*math.sqrt(v/items[0][1]);size*=min(1,width/430)
        for shrink in range(12):
            tw=pdfmetrics.stringWidth(label,'Bold',size);th=size*1.15
            if tw>width-8:size*=.9;continue
            chosen=None
            for trial in range(1800):
                spread=min(1,(trial+15)/500)
                xx=width/2-tw/2+rng.uniform(-1,1)*(width-tw-6)*spread/2
                yy=height/2-th/2+rng.uniform(-1,1)*(height-th-6)*spread/2
                rect=(xx-3,yy-3,xx+tw+3,yy+th+3)
                if all(rect[2]<a or rect[0]>c or rect[3]<b or rect[1]>e for a,b,c,e in occupied):chosen=(xx,yy,rect);break
            if chosen:
                xx,yy,rect=chosen;occupied.append(rect);d.add(String(xx,yy+size*.23,label,fontName='Bold',fontSize=size,fillColor=HexColor([NAVY,COPPER,MUTED,BLUE][index%4])));break
            size*=.9
        else:raise ValueError('Cloud did not fit: '+label)
    return d
