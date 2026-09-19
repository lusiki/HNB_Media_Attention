"""Publication figures from frozen observations and saved coefficient intervals."""
from pathlib import Path
from datetime import datetime
import json,os
from artifact_style import SITE,PAPER,INK,BLUE,MUTED,RULE,COPPER,configure_matplotlib
os.environ.setdefault('MPLCONFIGDIR',str(SITE/'.runtime/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
configure_matplotlib()
E=json.loads((SITE/'public/data/evidence.json').read_text(encoding='utf-8'))
OUT=SITE/'public/figures';OUT.mkdir(parents=True,exist_ok=True)
WORK=SITE/'.runtime/brief-figures';WORK.mkdir(parents=True,exist_ok=True)
manifest={}

def timeline(lang='en',later=False,gap=False,brief=False):
    hr=lang=='hr';t=lambda en,cr:cr if hr else en
    rows=[r for r in E['observations'] if not later or r['period']>='2024-04']
    dates=[datetime.fromisoformat(r['period']+'-01') for r in rows]
    series=[[100*r['gap'] if gap else 100*(E['baseline']['monthly']-r['gap']) for r in rows],[r['inflation'] for r in rows]]
    fig,axes=plt.subplots(2,1,figsize=(11.4,5.1 if brief else 6.2),sharex=True,gridspec_kw={'hspace':.77})
    fig.subplots_adjust(left=.065,right=.90,top=.90 if brief else .79,bottom=.15 if brief else .20)
    titles=[t('Attention gap (percentage points)','Jaz u pažnji (postotni bodovi)') if gap else t('Weighted institutional share (%)','Ponderirani institucionalni udio (%)'),t('Inflation in Croatia - HICP, year-on-year (%)','Inflacija u Hrvatskoj - HICP, godišnja stopa (%)')]
    for index,(ax,values,color) in enumerate(zip(axes,series,[BLUE,COPPER])):
        ax.plot(dates,values,color=color,lw=2.0,solid_capstyle='round')
        ax.scatter([dates[-1]],[values[-1]],s=30,color=color,zorder=4)
        ax.set_title(titles[index],loc='left',fontsize=16,color=INK,pad=14)
        ax.grid(axis='y',color=RULE,lw=.7);ax.set_axisbelow(True);ax.tick_params(length=0,pad=8,labelsize=13)
        limits=(-12.5,5) if gap else ((0,6) if later else (0,18))
        ticks=[-12,-8,-4,0,4] if gap else ([0,2,4,6] if later else [0,6,12,18])
        ax.set_ylim(limits if index==0 else (-.7,14.5));ax.set_yticks(ticks if index==0 else [0,4,8,12])
        ax.set_xlim(dates[0],dates[-1])
        label=f'{values[-1]:.2f}' if index==0 else f'{values[-1]:.1f}'
        if hr:label=label.replace('.',',')
        ax.annotate(label+('' if gap and index==0 else '%'),(dates[-1],values[-1]),xytext=(8,0),textcoords='offset points',ha='left',va='center',color=color,fontsize=14,fontweight='semibold',annotation_clip=False)
    ticks=[dates[0],datetime(2025,1,1),datetime(2026,1,1),dates[-1]] if later else [dates[0],*[datetime(y,1,1) for y in range(2022,2026)],dates[-1]]
    labels=['04/2024','01/2025','01/2026','05/2026'] if later else ['01/2021','2022','2023','2024','2025','05/2026']
    axes[1].set_xticks(ticks,labels);axes[1].get_xticklabels()[0].set_ha('left');axes[1].get_xticklabels()[-1].set_ha('right')
    if brief:
        name='brief-timeline-'+lang
        fig.savefig(WORK/(name+'.pdf'));fig.savefig(WORK/(name+'.svg'));fig.savefig(WORK/(name+'.png'),dpi=220)
    else:
        name='attention-gap' if gap else 'visibility-'+('later' if later else 'full')+('-hr' if hr else '')
        title=t('Institutional visibility and the inflation debate','Institucionalna vidljivost i rasprava o inflaciji') if not gap else 'Visibility relative to its historical reference'
        scope=t('April 2024 - May 2026','Travanj 2024. - svibanj 2026.') if later else t('January 2021 - May 2026','Siječanj 2021. - svibanj 2026.')
        fig.text(.065,.925,title,fontfamily='Source Serif 4 Display',fontsize=25,color=INK)
        fig.text(.065,.863,scope+'  /  '+t('PRIMARY CORPUS','PRIMARNI KORPUS'),fontsize=12,color=MUTED)
        note=t('Observed monthly series. Separate scales. Potential reach is not observed readership.','Opažene mjesečne serije. Zasebne skale. Potencijalni doseg nije opažena čitanost.')
        fig.text(.065,.073,note,fontsize=12,color=MUTED)
        fig.text(.065,.035,t('Palić & Sikić | Extended manuscript, 17 September 2026','Palić i Sikić | Prošireni rukopis, 17. rujna 2026.'),fontsize=11,color=MUTED)
        fig.savefig(OUT/(name+'.png'),dpi=220)
    manifest[name]={'periods':[r['period'] for r in rows],'primary_metric':'gap_pp' if gap else 'weighted_share_percent','values':series,'sample':'primary'}
    plt.close(fig)

def scenario(lang='en',brief=False):
    hr=lang=='hr';t=lambda en,cr:cr if hr else en
    rows=[r for r in E['time_sensitivity'] if r['frequency']=='weekly']
    fig,ax=plt.subplots(figsize=(11.4,4.15 if brief else 5.0))
    fig.subplots_adjust(left=.33,right=.93,top=.89 if brief else .77,bottom=.19 if brief else .33)
    names=[t('Primary model','Primarni model'),t('Period trends','Trendovi razdoblja'),t('Year effects','Godišnji učinci')]
    ax.axvline(0,color=MUTED,ls=(0,(3,3)),lw=.9)
    values=[]
    for index,r in enumerate(rows):
        b,lo,hi=[-r[k]*800 for k in ['estimate','hi','lo']];y=2-index;values.append({'estimate':b,'lo':lo,'hi':hi})
        color=BLUE if index==0 else MUTED
        ax.plot([lo,hi],[y,y],color=color,lw=3.0,solid_capstyle='round');ax.scatter([b],[y],s=55,color=color,zorder=4)
        label=f'{b:.2f} ({lo:.2f} '+t('to','do')+f' {hi:.2f})'
        if hr:label=label.replace('.',',')
        ax.text(-3.65,y+.27,label,fontsize=14,color=color,ha='left')
    ax.set_yticks([2,1,0],names,fontsize=16);ax.tick_params(length=0,pad=12)
    ax.set_ylim(-.45,2.65);ax.set_xlim(-3.65,.65);ax.set_xticks([-3,-2,-1,0]);ax.grid(axis='x',color=RULE,lw=.6);ax.set_axisbelow(True)
    ax.set_xlabel(t('Weighted-share difference (percentage points)','Razlika ponderiranog udjela (postotni bodovi)'),labelpad=11,fontsize=13,color=MUTED)
    if brief:
        fig.savefig(WORK/('brief-scenario-'+lang+'.pdf'));fig.savefig(WORK/('brief-scenario-'+lang+'.svg'));fig.savefig(WORK/('brief-scenario-'+lang+'.png'),dpi=220)
    else:
        fig.text(.065,.92,t('Inflation from 2% to 10%','Inflacija s 2% na 10%'),fontsize=28,fontfamily='Source Serif 4 Display',color=INK)
        fig.text(.065,.845,t('The estimate changes with the time controls.','Procjena se mijenja s vremenskim kontrolama.'),fontsize=15,color=MUTED)
        fig.text(.065,.095,t('Points: conditional differences. Lines: 95% intervals. All models include media volume.','Točke: uvjetne razlike. Crte: 95%-tni intervali. Svi modeli uključuju medijski obujam.'),fontsize=12,color=MUTED)
        fig.text(.065,.052,t('268 fitted weeks | January 2021 - May 2026 | Palić & Sikić, 17 September 2026','268 tjedana u regresiji | Siječanj 2021. - svibanj 2026. | Palić i Sikić, 17. rujna 2026.'),fontsize=11,color=MUTED)
        fig.savefig(OUT/('inflation-scenario'+('-hr' if hr else '')+'.png'),dpi=220)
    manifest['scenario-'+lang]={'frequency':'weekly','N':268,'inflation_contrast_pp':8,'values':values}
    plt.close(fig)

for lang in ['en','hr']:
    timeline(lang);timeline(lang,later=True);timeline(lang,brief=True);scenario(lang);scenario(lang,brief=True)
timeline(gap=True)
# Keep the site's social preview in the same typographic system.
fig=plt.figure(figsize=(12,6.3),dpi=100)
fig.text(.065,.88,'MONETARY COMMUNICATION / CROATIA / 2021-2026',fontsize=13,color=BLUE)
fig.text(.065,.70,'HNB in the inflation debate',fontfamily='Source Serif 4 Display',fontsize=39,color=INK)
fig.text(.065,.36,'-0.21',fontfamily='Source Serif 4 Display',fontsize=82,color=BLUE)
fig.text(.41,.44,'percentage points of weighted share',fontsize=20,color=INK)
fig.text(.41,.36,'per +1 percentage point of inflation',fontsize=20,color=INK)
fig.text(.065,.20,'Primary weekly model | 95% interval: -0.31 to -0.11 pp',fontsize=16,color=MUTED)
fig.text(.065,.145,'Sensitive to time controls; not a causal effect.',fontsize=16,color=MUTED)
fig.text(.065,.055,'Palić & Sikić | Manuscript 17 September 2026 | Author review pending',fontsize=12,color=MUTED)
fig.savefig(OUT/'social-preview.png',dpi=100);plt.close(fig)
(SITE/'qa').mkdir(exist_ok=True)
(SITE/'qa/figure-data.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print('Created eight publication figures and vector charts for the two full-sample briefs.')
