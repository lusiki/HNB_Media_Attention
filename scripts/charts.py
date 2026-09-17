"""Pure SVG figures connecting available observations on their own scales."""
from html import escape

def chart(rows, metric, width=1120, height=210):
    left, right, top, bottom = 42, 15, 36, 33
    plotw, ploth = width-left-right, height-top-bottom
    gap=metric=='gap'; factor=100 if gap else 1
    ticks=[-12,-8,-4,0,4] if gap else [0,4,8,12]
    lo,hi=(-12.5,5) if gap else (-.7,14.5)
    color='#9bc4ff' if gap else '#ffb17f'
    x=lambda i:left+plotw*i/max(1,len(rows)-1)
    y=lambda v:top+(hi-v)/(hi-lo)*ploth
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" aria-hidden="true">']
    for tick in ticks:
        yy=y(tick)
        s.append(f'<line x1="{left}" x2="{width-right}" y1="{yy:.2f}" y2="{yy:.2f}" stroke="#6c8393" opacity="{.8 if tick==0 else .3}" stroke-dasharray="{4 if tick==0 else 0}"/><text x="{left-12}" y="{yy+4:.2f}" fill="#cedbe5" text-anchor="end" font-size="12" font-family="Segoe UI,Arial">{tick}</text>')
    points=[]
    for i,r in enumerate(rows):
        if r[metric] is None:
            continue
        points.append(f'{x(i):.2f},{y(r[metric]*factor):.2f}')
    s.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.4" stroke-linejoin="round" points="{" ".join(points)}"/>')
    for i,r in enumerate(rows):
        if r['period']=='2024-04':
            xx=x(i)
            s.append(f'<line x1="{xx:.2f}" x2="{xx:.2f}" y1="{top-4}" y2="{height-bottom}" stroke="#d5dfe6" stroke-dasharray="4 4" opacity=".7"/><text x="{min(xx+8,width-145):.2f}" y="21" fill="#d5dfe6" font-size="12" font-family="Segoe UI,Arial">Apr 2024 · source change</text>')
    indices=[i for i,r in enumerate(rows) if r['period'].endswith('-01')]
    if len(rows)<35:indices=[0]+[i for i in indices if i>3]+[len(rows)-1]
    for i in indices:
        label=rows[i]['period'][:4] if len(rows)>35 else rows[i]['period']
        s.append(f'<text x="{x(i):.2f}" y="{height-9}" fill="#cedbe5" text-anchor="middle" font-size="12" font-family="Segoe UI,Arial">{escape(label)}</text>')
    s.append('</svg>');return ''.join(s)

def model_svg(row):
    lo,hi,b=[row[k]*100 for k in ['lo','hi','estimate']]
    width=420;x=lambda v:25+v/.5*360
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 80" aria-hidden="true"><line x1="25" x2="385" y1="34" y2="34" stroke="#a9bac6"/><line x1="{x(lo):.2f}" x2="{x(hi):.2f}" y1="34" y2="34" stroke="#165ce0" stroke-width="4"/><circle cx="{x(b):.2f}" cy="34" r="5" fill="#165ce0"/><text x="25" y="65" font-size="13" fill="#4f6470">0</text><text x="385" y="65" text-anchor="end" font-size="13" fill="#4f6470">0.5 pp</text></svg>'
