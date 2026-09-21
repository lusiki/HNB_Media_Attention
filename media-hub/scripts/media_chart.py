"""Count/rate figures with actual calendar coordinates and explicit availability."""
from html import escape
import math

def number(v,lang='en',digits=0):
    if v is None:return '—'
    s=f'{v:,.{digits}f}'
    return s.translate(str.maketrans({',':'.','.':','})) if lang=='hr' else s

def chart(rows,lang='en',metric='hnb_count',width=1000,height=340):
    hr=lang=='hr';left,right,top,bottom=62,22,38,48
    ordinal=lambda p:int(p[:4])*12+int(p[5:7])
    start,end=ordinal(rows[0]['period']),ordinal(rows[-1]['period'])
    vals=[r.get(metric) for r in rows if r.get(metric) is not None]
    maximum=max(vals,default=1) or 1;step=10**math.floor(math.log10(maximum));upper=math.ceil(maximum/step)*step
    x=lambda p:left+(width-left-right)*(ordinal(p)-start)/max(1,end-start)
    y=lambda v:top+(height-top-bottom)*(1-v/upper)
    title='Broj objava sa spominjanjem HNB-a' if hr else 'Publications containing HNB mentions'
    if metric=='rate_per_10000':title='Spominjanja HNB-a na 10.000 praćenih objava koje prolaze filtar' if hr else 'HNB mentions per 10,000 monitored query-eligible publications'
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}"><title>{escape(title)}</title><rect width="100%" height="100%" fill="white"/>']
    for j in range(5):
        v=upper*j/4;yy=y(v)
        s.append(f'<line x1="{left}" x2="{width-right}" y1="{yy}" y2="{yy}" stroke="#dce4ea"/><text x="{left-9}" y="{yy+5}" text-anchor="end" font-family="Arial" font-size="14" fill="#4f6470">{number(v,lang,0)}</text>')
    segments=[];points=[];previous=None
    for r in rows:
        v=r.get(metric);o=ordinal(r['period'])
        if v is None or (previous is not None and o-previous>1):
            if points:segments.append(points);points=[]
        if v is not None:points.append(f'{x(r["period"]):.2f},{y(v):.2f}')
        previous=o
    if points:segments.append(points)
    for points in segments:s.append(f'<polyline class="media-observed-series" points="{" ".join(points)}" fill="none" stroke="#165ce0" stroke-width="3" stroke-linejoin="round"/>')
    if start<ordinal('2024-01')<end:
        xx=x('2024-01');label='Promjena prikupljanja' if hr else 'Collection change'
        s.append(f'<line class="media-boundary" x1="{xx}" x2="{xx}" y1="{top}" y2="{height-bottom}" stroke="#4f6470" stroke-dasharray="5 5"/><text x="{xx+7}" y="22" font-family="Arial" font-size="13" fill="#4f6470">01/2024 · {label}</text>')
    if rows[-1].get('coverage_state')=='partial':
        xx=x(rows[-1]['period']);s.append(f'<circle cx="{xx}" cy="{y(rows[-1][metric])}" r="5" fill="white" stroke="#165ce0" stroke-width="2"/>')
    for yr in range(int(rows[0]['period'][:4]),int(rows[-1]['period'][:4])+1):
        p=f'{yr}-01'
        if start<=ordinal(p)<=end:s.append(f'<text x="{x(p)}" y="{height-15}" text-anchor="middle" font-family="Arial" font-size="14" fill="#4f6470">{yr}</text>')
    s.append('</svg>');return ''.join(s)
