"""Scientific export figures from frozen aggregates; no model fitting."""
from pathlib import Path
import json, os
from datetime import datetime
SITE=Path(__file__).resolve().parents[1]
os.environ['MPLCONFIGDIR']=str(SITE/'.runtime/matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
E=json.loads((SITE/'public/data/evidence.json').read_text(encoding='utf-8'))
OUT=SITE/'public/figures';OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.spines.bottom':False})
def draw(later,lang='en'):
    rows=[r for r in E['observations'] if not later or r['period']>='2024-04']
    dates=[datetime.fromisoformat(r['period']+'-01') for r in rows]
    fig,axes=plt.subplots(2,1,figsize=(10.5,4.9),sharex=True,gridspec_kw={'hspace':.65})
    titles=['Ponderirani institucionalni udio (%) · više znači veću vidljivost','Inflacija u Hrvatskoj · HICP, godišnja stopa (%)'] if lang=='hr' else ['Weighted institutional share (%) · higher means more visibility','Inflation in Croatia · HICP, year-on-year (%)']
    if not later:titles[0]='HNB attention gap (pp) · higher means less relative visibility'
    for n,(ax,color) in enumerate(zip(axes,['#165ce0','#b95a22'])):
        values=np.array([np.nan if r['gap'] is None else ((E['baseline']['monthly']-r['gap'])*100 if later else r['gap']*100) for r in rows]) if n==0 else np.array([np.nan if r['inflation'] is None else r['inflation'] for r in rows])
        selected=np.flatnonzero(np.isfinite(values))
        ax.plot([dates[i] for i in selected],values[selected],color=color,lw=1.7)
        ax.axhline(0,color='#627789',ls='--',lw=.6);ax.grid(axis='y',color='#dce3e9',lw=.5)
        ax.tick_params(length=0,labelsize=10);ax.set_title(titles[n],loc='left',fontsize=12,color='#112838',pad=8)
        ax.set_ylim((0,6) if n==0 and later else ((-12.5,5) if n==0 else (-.7,14.5)))
        ax.set_yticks([0,2,4,6] if n==0 and later else ([-12,-8,-4,0,4] if n==0 else [0,4,8,12]))
        ax.set_xlim(dates[0],dates[-1])
    if later:
        axes[1].set_xticks([dates[0],datetime(2025,1,1),datetime(2026,1,1),dates[-1]],labels=['04/2024','01/2025','01/2026','05/2026'])
        axes[1].get_xticklabels()[0].set_horizontalalignment('left')
        axes[1].get_xticklabels()[-1].set_horizontalalignment('right')
        note=('Travanj 2024. – svibanj 2026. | Opažene vrijednosti, ne procijenjeni trend.\nUdio = početna referenca − jaz. Potencijalni doseg nije stvarna izloženost. Izvor: nacrt od 17. 9. 2026.' if lang=='hr' else 'April 2024–May 2026 | Observed values, not a fitted trend.\nShare = baseline − gap. Potential reach is not actual exposure. Source: extended draft, 17 September 2026.')
        name='visibility-later'+('-hr' if lang=='hr' else '')+'.png'
    else:
        axes[1].set_xticks([datetime(y,1,1) for y in range(2021,2027)],labels=[str(y) for y in range(2021,2027)])
        note='Jan 2021–May 2026 | Gap = baseline − weighted share. Higher gap means lower relative visibility.\nPotential reach is not observed readership. Source: extended draft, 17 September 2026.'
        name='attention-gap.png'
    fig.subplots_adjust(left=.065,right=.98,top=.92,bottom=.19)
    fig.text(.065,.05,note,fontsize=9,color='#4f6470',linespacing=1.5)
    fig.savefig(OUT/name,dpi=180,facecolor='white');plt.close(fig)
def scenario(lang='en'):
    hr=lang=='hr'
    rows=[r for r in E['time_sensitivity'] if r['frequency']=='weekly']
    fig,ax=plt.subplots(figsize=(9,4))
    fig.subplots_adjust(left=.31,right=.96,top=.87,bottom=.26)
    names=['Primarni model','Uz trendove razdoblja','Uz godišnje učinke'] if hr else ['Primary model','With period trends','With year effects']
    ax.axvline(0,color='#6b7c88',ls='--',lw=1)
    for i,r in enumerate(rows):
        b,lo,hi=[-r[k]*800 for k in ['estimate','hi','lo']]
        y=2-i
        ax.plot([lo,hi],[y,y],color='#165ce0',lw=3,solid_capstyle='round')
        ax.scatter([b],[y],s=42,color='#165ce0',zorder=3)
        label=f'{b:.2f} ({lo:.2f} to {hi:.2f})'
        if hr:label=label.replace('.',',').replace(' to ',' do ')
        ax.text(b,y+.2,label,ha='center',fontsize=11,color='#112838')
    ax.set_yticks([2,1,0],names,fontsize=11)
    ax.set_ylim(-.4,2.6);ax.set_xlim(-3.65,.65)
    ax.set_xticks([-3,-2,-1,0]);ax.tick_params(length=0,pad=9)
    ax.grid(axis='x',color='#e2e7ed',lw=.5);ax.set_axisbelow(True)
    ax.set_xlabel('Promjena ponderiranog udjela (postotni bodovi)' if hr else 'Change in weighted share (percentage points)',labelpad=12,color='#4f6470',fontsize=11)
    fig.text(.04,.94,'Inflacija: 2% → 10%' if hr else 'Inflation: 2% → 10%',fontsize=15,color='#112838',weight='bold')
    fig.text(.04,.025,'Uvjetne razlike uz ostalo nepromijenjeno · 95%-tni intervali · 268 tjedana' if hr else 'Conditional differences, other variables held fixed · 95% intervals · 268 weeks',fontsize=10,color='#4f6470')
    fig.savefig(OUT/('inflation-scenario'+('-hr' if hr else '')+'.png'),dpi=180,facecolor='white');plt.close(fig)

draw(False);draw(True);draw(True,'hr');scenario();scenario('hr')
# A share card is a research graphic with a single, qualified estimate.
fig=plt.figure(figsize=(12,6.3),dpi=100,facecolor='#112838')
fig.text(.065,.87,'MONETARY COMMUNICATION / RESEARCH',fontsize=15,color='#a6caff')
fig.text(.065,.70,'HNB in Croatia’s inflation debate',fontsize=31,color='white',fontfamily='DejaVu Serif')
fig.text(.065,.47,'−0.21',fontsize=75,color='#a6caff')
fig.text(.38,.52,'percentage points of weighted visibility',fontsize=19,color='white')
fig.text(.38,.45,'per +1 percentage point of inflation',fontsize=19,color='white')
ax=fig.add_axes([.08,.24,.35,.12],facecolor='#112838')
r=E['models'][0];ax.axvline(0,color='#b0c1cc',ls='--',lw=1)
ax.plot([-r['hi']*100,-r['lo']*100],[0,0],lw=4,color='#a6caff');ax.scatter([-r['estimate']*100],[0],s=65,color='#a6caff')
ax.set_xlim(-.36,.05);ax.set_ylim(-1,1);ax.set_yticks([]);ax.set_xticks([-.3,-.2,-.1,0]);ax.tick_params(colors='#dce5eb',labelsize=12,length=0)
fig.text(.49,.30,'Primary weekly model · 95% interval',fontsize=15,color='white')
fig.text(.49,.24,'Sensitive to time controls; not a causal effect.',fontsize=14,color='#cedbe5')
fig.text(.065,.08,'Palić & Sikić · Manuscript 17 September 2026 · Author review pending',fontsize=14,color='#cedbe5')
fig.savefig(OUT/'social-preview.png',dpi=100,facecolor=fig.get_facecolor());plt.close(fig)
print('Created six research figures from saved observations and estimates.')
