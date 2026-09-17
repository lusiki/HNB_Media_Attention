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
        for source in ['original','new']:
            selected=[i for i,r in enumerate(rows) if r['source']==source]
            ax.plot([dates[i] for i in selected],values[selected],color=color,lw=1.7)
        if not later:
            ax.axvspan(datetime(2024,1,1),datetime(2024,4,1),color='#e6ebef',zorder=-1)
            ax.axvline(datetime(2024,4,1),color='#708797',ls='--',lw=.8)
        ax.axhline(0,color='#627789',ls='--',lw=.6);ax.grid(axis='y',color='#dce3e9',lw=.5)
        ax.tick_params(length=0,labelsize=10);ax.set_title(titles[n],loc='left',fontsize=12,color='#112838',pad=8)
        ax.set_ylim((0,6) if n==0 and later else ((-12.5,5) if n==0 else (-.7,14.5)))
        ax.set_yticks([0,2,4,6] if n==0 and later else ([-12,-8,-4,0,4] if n==0 else [0,4,8,12]))
        ax.set_xlim(dates[0],dates[-1])
    if later:
        axes[1].set_xticks([dates[0],datetime(2025,1,1),datetime(2026,1,1),dates[-1]],labels=['04/2024','01/2025','01/2026','05/2026'])
        axes[1].get_xticklabels()[0].set_horizontalalignment('left')
        axes[1].get_xticklabels()[-1].set_horizontalalignment('right')
        note=('Travanj 2024. – svibanj 2026. | Opažene vrijednosti, ne procijenjeni trend. Sastav korpusa može varirati.\nUdio = početna referenca − jaz. Potencijalni doseg nije stvarna izloženost. Izvor: nacrt od 17. 9. 2026.' if lang=='hr' else 'April 2024–May 2026 | Observed values, not a fitted trend. Coverage composition may vary.\nShare = baseline − gap. Potential reach is not actual exposure. Source: extended draft, 17 September 2026.')
        name='visibility-later'+('-hr' if lang=='hr' else '')+'.png'
    else:
        axes[1].set_xticks([datetime(y,1,1) for y in range(2021,2027)],labels=[str(y) for y in range(2021,2027)])
        note='Jan 2021–May 2026 | Gap = baseline − share; zero is a historical reference, not a target.\nJan–Mar 2024 excluded. Levels across the Apr 2024 source change are not harmonised. Draft: 17 Sep 2026.'
        axes[0].text(.58,.05,'Apr 2024: source break',transform=axes[0].transAxes,fontsize=9,color='#4f6470')
        name='attention-gap.png'
    fig.subplots_adjust(left=.065,right=.98,top=.92,bottom=.19)
    fig.text(.065,.05,note,fontsize=9,color='#4f6470',linespacing=1.5)
    fig.savefig(OUT/name,dpi=180,facecolor='white');plt.close(fig)
draw(False);draw(True);draw(True,'hr')
print('Created full-history gap and bilingual later-period share figures; all observed points preserved.')
