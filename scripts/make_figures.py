"""Scientific export figures from frozen aggregates; no model fitting."""
from pathlib import Path
import json, os
from datetime import datetime
from charts import CHART_SCALES
SITE=Path(__file__).resolve().parents[1]
os.environ['MPLCONFIGDIR']=str(SITE/'.runtime/matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
E=json.loads((SITE/'public/data/evidence.json').read_text(encoding='utf-8'))
OUT=SITE/'public/figures';OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.spines.bottom':False})

def draw(scope='all',metric='share',lang='en'):
    later=scope=='new';hr=lang=='hr'
    rows=[r for r in E['observations'] if not later or r['period']>='2024-04']
    dates=[datetime.fromisoformat(r['period']+'-01') for r in rows]
    fig,axes=plt.subplots(2,1,figsize=(10.5,4.9 if later else 6.6),sharex=True,gridspec_kw={'hspace':.52})
    titles=['Ponderirani institucionalni udio (%) - više znači veću vidljivost','Inflacija u Hrvatskoj - HICP, godišnja stopa (%)'] if hr else ['Weighted institutional share (%) - higher means more visibility','Inflation in Croatia - HICP, year-on-year (%)']
    if metric=='gap':titles[0]='HNB attention gap (pp) - higher means less relative visibility'
    for ax,color,m,title in zip(axes,['#165ce0','#b95a22'],[metric,'inflation'],titles):
        values=np.array([np.nan if r['gap'] is None else (100*(E['baseline']['monthly']-r['gap']) if m=='share' else r[m]*(100 if m=='gap' else 1)) for r in rows])
        selected=np.flatnonzero(np.isfinite(values))
        ax.plot([dates[i] for i in selected],values[selected],color=color,lw=1.9)
        lo,hi,ticks=CHART_SCALES[scope][m]
        if lo<=0<=hi:ax.axhline(0,color='#627789',ls='--',lw=.6)
        ax.grid(axis='y',color='#dce3e9',lw=.5)
        ax.tick_params(length=0,labelsize=10);ax.set_title(title,loc='left',fontsize=12,color='#112838',pad=10)
        ax.set_ylim(lo,hi);ax.set_yticks(ticks);ax.set_xlim(dates[0],dates[-1])
    if later:
        axes[1].set_xticks([dates[0],datetime(2025,1,1),datetime(2026,1,1),dates[-1]],labels=['04/2024','01/2025','01/2026','05/2026'])
        note=('Travanj 2024. - svibanj 2026. | Opažene vrijednosti; sastav korpusa može varirati.\nSkala inflacije: 2,5-5,5%; ne počinje od nule. Izvor: nacrt od 17. 9. 2026.' if hr else 'April 2024-May 2026 | Observed values; coverage composition may vary.\nInflation scale: 2.5-5.5%; does not start at zero. Source: extended draft, 17 September 2026.')
        name='visibility-later'+('-hr' if hr else '')+'.png'
    else:
        axes[1].set_xticks([dates[0]]+[datetime(y,1,1) for y in range(2022,2026)]+[dates[-1]],labels=['01/2021','2022','2023','2024','2025','05/2026'])
        note=('Siječanj 2021. - svibanj 2026. | Linije povezuju dostupna opažanja; siječanj-ožujak 2024. nema procjene.\nRazine preko promjene izvora u travnju 2024. nisu usklađene. Izvor: nacrt od 17. 9. 2026.' if hr else 'January 2021-May 2026 | Lines join available observations; January-March 2024 has no estimates.\nLevels across the April 2024 source change are not harmonised. Source: draft, 17 September 2026.')
        name='attention-gap.png' if metric=='gap' else 'visibility-full'+('-hr' if hr else '')+'.png'
    axes[1].get_xticklabels()[0].set_horizontalalignment('left')
    axes[1].get_xticklabels()[-1].set_horizontalalignment('right')
    fig.subplots_adjust(left=.065,right=.98,top=.93,bottom=.15)
    fig.text(.065,.035,note,fontsize=9,color='#4f6470',linespacing=1.5)
    fig.savefig(OUT/name,dpi=180,facecolor='white');plt.close(fig)

def scenario(lang='en'):
    hr=lang=='hr'
    rows=[r for r in E['time_sensitivity'] if r['frequency']=='weekly']
    fig,ax=plt.subplots(figsize=(9,4))
    fig.subplots_adjust(left=.31,right=.96,top=.87,bottom=.26)
    names=['Primarni model','Uz trendove razdoblja','Uz godišnje učinke'] if hr else ['Primary model','With period trends','With year effects']
    ax.axvline(0,color='#6b7c88',ls='--',lw=1)
    for i,r in enumerate(rows):
        b,lo,hi=[r[k]*800 for k in ['estimate','lo','hi']]
        y=2-i
        ax.plot([lo,hi],[y,y],color='#165ce0',lw=3,solid_capstyle='round')
        ax.scatter([b],[y],s=42,color='#165ce0',zorder=3)
        label=f'{b:.2f} ({lo:.2f} to {hi:.2f})'
        if hr:label=label.replace('.',',').replace(' to ',' do ')
        ax.text(b,y+.2,label,ha='center',fontsize=11,color='#112838')
    ax.set_yticks([2,1,0],names,fontsize=11)
    ax.set_ylim(-.4,2.6);ax.set_xlim(-.65,3.65)
    ax.set_xticks([0,1,2,3]);ax.tick_params(length=0,pad=9)
    ax.grid(axis='x',color='#e2e7ed',lw=.5);ax.set_axisbelow(True)
    ax.set_xlabel('Razlika jaza (postotni bodovi)' if hr else 'Difference in the attention gap (percentage points)',labelpad=12,color='#4f6470',fontsize=11)
    fig.text(.04,.94,'Inflacija: 2% → 10%' if hr else 'Inflation: 2% → 10%',fontsize=15,color='#112838',weight='bold')
    fig.text(.04,.025,'Uvjetne razlike uz ostalo nepromijenjeno · 95%-tni intervali · 268 tjedana' if hr else 'Conditional differences, other variables held fixed · 95% intervals · 268 weeks',fontsize=10,color='#4f6470')
    fig.savefig(OUT/('inflation-scenario'+('-hr' if hr else '')+'.png'),dpi=180,facecolor='white');plt.close(fig)

draw(metric='gap')
for lang in ['en','hr']:
    draw(lang=lang);draw(scope='new',lang=lang);scenario(lang)
print('Created connected timelines and bilingual conditional inflation comparisons.')
