"""Static scientific figure for the page download and the two-page brief."""
from pathlib import Path
import json
import os
SITE=Path(__file__).resolve().parents[1]
os.environ['MPLCONFIGDIR']=str(SITE/'.runtime/matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

E=json.loads((SITE/'public/data/evidence.json').read_text(encoding='utf-8'))
rows=E['observations'];dates=[datetime.fromisoformat(r['period']+'-01') for r in rows]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.spines.bottom':False})
fig,axes=plt.subplots(2,1,figsize=(10.5,4.9),sharex=True,gridspec_kw={'hspace':.7})
for ax,metric,color,title,unit in zip(axes,['gap','inflation'],['#165ce0','#b95a22'],['HNB attention gap','Inflation in Croatia'],['Percentage points relative to baseline','HICP · year-on-year, %']):
    values=np.array([np.nan if r[metric] is None else r[metric]*(100 if metric=='gap' else 1) for r in rows])
    for source in ['original','new']:
        selected=[i for i,r in enumerate(rows) if r['source']==source]
        ax.plot([dates[i] for i in selected],values[selected],color=color,lw=1.7)
    ax.axvspan(datetime(2024,1,1),datetime(2024,4,1),color='#e6ebef',zorder=-1)
    ax.axvline(datetime(2024,4,1),color='#708797',ls='--',lw=.8)
    ax.axhline(0,color='#627789',ls='--',lw=.6)
    ax.grid(axis='y',color='#dce3e9',lw=.5);ax.tick_params(length=0,labelsize=9)
    ax.set_title(title+'  |  '+unit,loc='left',fontsize=11,color='#112838',pad=9)
    ax.set_ylim((-12,4.8) if metric=='gap' else (-.7,14.5))
    ax.set_yticks([-12,-8,-4,0,4] if metric=='gap' else [0,4,8,12])
    ax.set_xlim(dates[0],dates[-1])
axes[0].annotate('Apr 2024: source change',xy=(datetime(2024,4,1),3.5),xytext=(datetime(2024,5,1),-10.5),fontsize=9,color='#4f6470')
axes[1].set_xticks([datetime(y,1,1) for y in range(2021,2027)],labels=[str(y) for y in range(2021,2027)])
fig.subplots_adjust(left=.055,right=.985,top=.94,bottom=.075)
out=SITE/'public/figures';out.mkdir(parents=True,exist_ok=True)
fig.savefig(out/'brief-chart.png',dpi=180,facecolor='white')
fig.savefig(out/'attention-gap.png',dpi=220,facecolor='white')
plt.close(fig)
print('Created two aligned plots from saved monthly aggregates; no fitted or interpolated points.')
