"""SVG figures connecting available observations, with separate scales. Missing values stay null."""
from html import escape

# Shared by the interactive chart, no-JavaScript SVG and printed figures.
# Every observed value is retained. The later inflation axis intentionally omits zero.
CHART_SCALES = {
    'all': {'share': [0,16,[0,4,8,12,16]], 'gap': [-12,4,[-12,-8,-4,0,4]],
            'inflation': [0,14,[0,2,4,6,8,10,12,14]]},
    'new': {'share': [0,5,[0,1,2,3,4,5]], 'gap': [-1,4,[-1,0,1,2,3,4]],
            'inflation': [2.5,5.5,[2.5,3,3.5,4,4.5,5,5.5]]},
}

def scenario_svg(rows, hr=False):
    rows=[r for r in rows if r['frequency']=='weekly']
    names=['Primarni model','Uz trendove razdoblja','Uz godišnje učinke'] if hr else ['Primary model','With period trends','With year effects']
    x=lambda v:28+(v+.65)/4.3*374
    n=lambda v:f'{v:.2f}'.replace('.',',' if hr else '.')
    s=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 430 365" aria-hidden="true">']
    for tick in [0,1,2,3]:
        s.append(f'<line x1="{x(tick)}" x2="{x(tick)}" y1="40" y2="299" stroke="{"#6b7c88" if tick==0 else "#dce3e9"}" stroke-dasharray="3 3"/><text x="{x(tick)}" y="325" text-anchor="middle" font-family="Arial" font-size="16" fill="#4f6470">{tick}</text>')
    for i,r in enumerate(rows):
        y=60+i*94;b,lo,hi=[r[k]*800 for k in ['estimate','lo','hi']]
        s.append(f'<text x="28" y="{y-34}" font-family="Arial" font-size="16" font-weight="bold" fill="#112838">{names[i]}</text><line x1="{x(lo)}" x2="{x(hi)}" y1="{y}" y2="{y}" stroke="#165ce0" stroke-width="4"/><circle cx="{x(b)}" cy="{y}" r="5" fill="#165ce0"/><text x="28" y="{y+28}" font-family="Arial" font-size="15" fill="#4f6470">{n(b)} ({n(lo)} {"do" if hr else "to"} {n(hi)})</text>')
    s.append('<text x="215" y="355" text-anchor="middle" font-family="Arial" font-size="16" fill="#4f6470">'+('Razlika jaza (postotni bodovi)' if hr else 'Gap difference (percentage points)')+'</text></svg>')
    return ''.join(s)

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
    for tick in ticks:
        yy=y(tick)
        s.append(f'<line x1="{left}" x2="{width-right}" y1="{yy:.2f}" y2="{yy:.2f}" stroke="#6c8393" opacity="{.8 if tick==0 else .3}" stroke-dasharray="{4 if tick==0 else 0}"/><text x="{left-12}" y="{yy+4:.2f}" fill="#cedbe5" text-anchor="end" font-size="12" font-family="Segoe UI,Arial">{tick}</text>')
    points=[f'{x(i):.2f},{y(value(r)):.2f}' for i,r in enumerate(rows) if r['gap'] is not None]
    s.append(f'<polyline class="observed-series" fill="none" stroke="{color}" stroke-width="2.4" stroke-linejoin="round" points="{" ".join(points)}"/>')
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
