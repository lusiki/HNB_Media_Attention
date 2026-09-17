"""Pure SVG figures with explicit discontinuities and their own scales."""
from html import escape

# Shared by the interactive chart, no-JavaScript SVG and printed figures.
# Every observed value is retained. The later inflation axis intentionally omits zero.
CHART_SCALES = {
    'all': {'share': [0,16,[0,4,8,12,16]], 'gap': [-12,4,[-12,-8,-4,0,4]],
            'inflation': [0,14,[0,2,4,6,8,10,12,14]]},
    'new': {'share': [0,5,[0,1,2,3,4,5]], 'gap': [-1,4,[-1,0,1,2,3,4]],
            'inflation': [2.5,5.5,[2.5,3,3.5,4,4.5,5,5.5]]},
}

def chart(rows, metric, width=1120, height=350, baseline=0):
    left, right, top, bottom = 42, 15, 36, 33
    plotw, ploth = width-left-right, height-top-bottom
    gap=metric=='gap'; share=metric=='share'; later=len(rows)<35
    lo,hi,ticks=CHART_SCALES['new' if later else 'all'][metric]
    color='#9bc4ff' if gap or share else '#ffb17f'
    value=lambda r:100*(baseline-r['gap']) if share else r[metric]*(100 if gap else 1)
    x=lambda i:left+plotw*i/max(1,len(rows)-1)
    y=lambda v:top+(hi-v)/(hi-lo)*ploth
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" aria-hidden="true">']
    missing=[i for i,r in enumerate(rows) if r['gap'] is None]
    if missing:
        a=max(left,x(min(missing)) - plotw/(len(rows)-1)/2); b=x(max(missing)) + plotw/(len(rows)-1)/2
        s.append(f'<rect x="{a:.2f}" y="{top}" width="{b-a:.2f}" height="{ploth}" fill="#ffffff" opacity=".07"/>')
    for tick in ticks:
        yy=y(tick)
        s.append(f'<line x1="{left}" x2="{width-right}" y1="{yy:.2f}" y2="{yy:.2f}" stroke="#6c8393" opacity="{.8 if tick==0 else .3}" stroke-dasharray="{4 if tick==0 else 0}"/><text x="{left-12}" y="{yy+4:.2f}" fill="#cedbe5" text-anchor="end" font-size="12" font-family="Segoe UI,Arial">{tick}</text>')
    paths=[]; points=[]; last=None
    for i,r in enumerate(rows):
        if r['gap'] is None:
            if points: paths.append(points)
            points=[];last=None;continue
        if last and r['source']!=last:
            if points: paths.append(points)
            points=[]
        points.append(f'{x(i):.2f},{y(value(r)):.2f}');last=r['source']
    if points:paths.append(points)
    for points in paths:s.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.4" stroke-linejoin="round" points="{" ".join(points)}"/>')
    for i,r in enumerate(rows):
        if r['period']=='2024-04' and not later:
            xx=x(i)
            s.append(f'<line x1="{xx:.2f}" x2="{xx:.2f}" y1="{top-4}" y2="{height-bottom}" stroke="#d5dfe6" stroke-dasharray="4 4" opacity=".7"/><text x="{min(xx+8,width-145):.2f}" y="21" fill="#d5dfe6" font-size="12" font-family="Segoe UI,Arial">Apr 2024 · source change</text>')
    indices=[0]+[i for i,r in enumerate(rows) if r['period'].endswith('-01') and 3<i<len(rows)-5]+[len(rows)-1]
    if width<500:indices=[0,len(rows)//2 if later else 24,len(rows)-1]
    for i in indices:
        label=rows[i]['period'] if later or i in [0,len(rows)-1] else rows[i]['period'][:4]
        anchor='start' if i==0 else 'end' if i==len(rows)-1 else 'middle'
        s.append(f'<text x="{x(i):.2f}" y="{height-9}" fill="#cedbe5" text-anchor="{anchor}" font-size="12" font-family="Segoe UI,Arial">{escape(label)}</text>')
    s.append('</svg>');return ''.join(s)

def model_svg(row):
    lo,hi,b=[row[k]*100 for k in ['lo','hi','estimate']]
    x=lambda v:30+(v+.1)/.6*355
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 85" aria-hidden="true"><line x1="30" x2="385" y1="34" y2="34" stroke="#a9bac6"/><line x1="{x(0)}" x2="{x(0)}" y1="13" y2="49" stroke="#4f6470" stroke-dasharray="3 3"/><line x1="{x(lo):.2f}" x2="{x(hi):.2f}" y1="34" y2="34" stroke="#165ce0" stroke-width="4"/><circle cx="{x(b):.2f}" cy="34" r="5" fill="#165ce0"/><text x="30" y="70" font-size="13" fill="#4f6470">−0.1</text><text x="{x(0)}" y="70" text-anchor="middle" font-size="13" fill="#4f6470">0</text><text x="385" y="70" text-anchor="end" font-size="13" fill="#4f6470">0.5 pp</text></svg>'

def sensitivity_svg(rows, narrow=False):
    x=(lambda v:25+(v*100+.1)/.6*290) if narrow else (lambda v:165+(v*100+.1)/.6*285)
    names={'none':'Primary','trend':'Segment trends','year':'Year effects'}
    s=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 '+('340 450' if narrow else '480 310')+'" aria-hidden="true">']
    for tick in [-.1,0,.1,.2,.3,.4,.5]:
        xx=x(tick/100)
        s.append(f'<line x1="{xx}" x2="{xx}" y1="20" y2="{400 if narrow else 265}" stroke="{"#4f6470" if tick==0 else "#d6dfe6"}" stroke-dasharray="3 3"/><text x="{xx}" y="{422 if narrow else 289}" text-anchor="middle" font-size="12" fill="#4f6470">{tick:g}</text>')
    for i,r in enumerate(rows):
        y=(48+i*65) if narrow else (38+i*40); label=('Monthly' if r['frequency']=='monthly' else 'Weekly')+' · '+names[r['adjustment']]
        s.append(f'<text x="{25 if narrow else 0}" y="{y-15 if narrow else y+4}" font-size="{14 if narrow else 12}" font-family="Segoe UI,Arial" fill="#112838">{label}</text><line x1="{x(r["lo"])}" x2="{x(r["hi"])}" y1="{y}" y2="{y}" stroke="#165ce0" stroke-width="3"/><circle cx="{x(r["estimate"])}" cy="{y}" r="4" fill="#165ce0"/>')
    s.append(f'<text x="{170 if narrow else 300}" y="{447 if narrow else 308}" text-anchor="middle" font-size="12" fill="#4f6470">Gap pp per +1 pp inflation · 95% intervals</text></svg>')
    return ''.join(s)
