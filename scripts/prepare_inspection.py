"""Prepare a frozen inspection layer from existing panels and saved estimates."""
from pathlib import Path
import argparse,csv,json,hashlib,math,re
from html import unescape
P=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--research-root',required=True,type=Path)
ROOT=parser.parse_args().research_root.resolve()
def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def save(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
e=json.loads((P/'public/data/evidence.json').read_text(encoding='utf-8'))
panels={r['yearmonth'][:7]:r for r in read_csv(ROOT/'panel_monthly.csv')}
commons={r['yearmonth'][:7]:r for r in read_csv(ROOT/'panel_monthly_commonsrc.csv')}
private=P/'private/inspection-aggregates'
concentration={(r['period'],r['sample']):r for r in read_csv(private/'concentration.csv')}
domains=read_csv(private/'domains.csv')
observations=[]
for r in e['observations']:
    period=r['period'];p=panels[period];c=commons[period]
    assert abs(float(p['s_infl_core'])-(e['baseline']['monthly']-r['gap']))<1e-13
    row={'period':period,'inflation':r['inflation'],'expectations':float(p['exp_balance'])}
    for sample in ['primary','common']:
        stat=concentration[period,sample]
        numerator=float(p['A_s_infl'] if sample=='primary' else c['A_s_infl_common'])
        denominator=float(p['A_INF_core'] if sample=='primary' else c['A_INF_common'])+1
        relevant=int(p['n_infl_hnb'] if sample=='primary' else c['n_hnb_common'])
        inflation_items=int(p['n_infl_core'] if sample=='primary' else c['n_infl_common'])
        assert math.isclose(float(stat['numerator']),numerator,rel_tol=1e-12)
        assert int(stat['relevant_items'])==relevant
        value={
            'share':100*numerator/denominator,'gap':100*float(p['IAG_primary'] if sample=='primary' else c['IAG_common']),
            'article':100*relevant/(inflation_items+1),'numerator':numerator,'denominator':denominator,
            'relevant_items':relevant,'inflation_items':inflation_items,'items':int(stat['items']),
            'centrality':float(p['C_EV'] if sample=='primary' else c['C_EV_common']),
            'hhi':float(stat['weight_hhi']),'source_labels':int(stat['source_labels']),
            'weighted_sources':int(stat['weighted_sources']),'top5':100*float(stat['top5_source_share']),
            'top10':100*float(stat['top10_item_share'])}
        assert all(math.isfinite(v) for v in value.values())
        value['domains']=[{'source':d['source'],'items':int(d['items']),'relevant_items':int(d['relevant_items']),'contribution':100*float(d['weight'])/numerator} for d in domains if d['period']==period and d['sample']==sample]
        value['domains'].sort(key=lambda d:d['source'])
        assert sum(d['contribution'] for d in value['domains'])<=100.0000001
        row[sample]=value
    observations.append(row)

def est(row,**fields):return {**fields,**{k:float(row[k]) for k in ['estimate','lo','hi','p','N']}}
robustness=[]
curve=read_csv(ROOT/'results/spec_curve_curve.csv')
trend=read_csv(ROOT/'results/regimes_trend.csv')
network=read_csv(ROOT/'results/regimes_common_network.csv')
for freq in ['weekly','monthly']:
    for spec in ['9b','9a']:
        row=next(x for x in e['models'] if x['frequency']==freq and x['specification']==spec)
        robustness.append(est(row,finding='F1',key=spec,frequency=freq,sample='primary',units='share_pp_per_inflation_pp',transform=-100,file='primary_coefficients.csv',selection=f'S1 / {freq} / IAG_primary / pi_t / {spec}'))
    for adj in ['trend','year']:
        row=next(x for x in e['time_sensitivity'] if x['frequency']==freq and x['adjustment']==adj)
        robustness.append(est(row,finding='F1',key=adj,frequency=freq,sample='primary',units='share_pp_per_inflation_pp',transform=-100,file='regimes_common_slope_sensitivity.csv',selection=f'S1 / {freq} / pi_t / {adj}'))
    for outcome,key,sample in [('IAG_common','common','common'),('IAG_winsor','winsor','primary')]:
        row=next(x for x in curve if x['sample']=='S1' and x['frequency']==freq and x['outcome']==outcome and x['concentration']=='HHI_all' and x['controls']=='3')
        robustness.append(est(row,finding='F1',key=key,frequency=freq,sample=sample,units='share_pp_per_inflation_pp',transform=-100,file='spec_curve_curve.csv',selection=f'S1 / {freq} / {outcome} / HHI_all / controls 3 / pi_t'))
    for table,outcome,key,sample,file in [(trend,'IAG_primary','primary','primary','regimes_trend.csv'),(network,'IAG_common','common','common','regimes_common_network.csv')]:
        row=next(x for x in table if x['sample']=='S3' and x['frequency']==freq and x['outcome']==outcome)
        robustness.append(est(row,finding='F2',key=key,frequency=freq,sample=sample,units='share_pp_per_'+('week' if freq=='weekly' else 'month'),transform=-100,file=file,selection=f'S3 / {freq} / {outcome} / trend'))
    for outcome,key,sample in [('C_EV_common','common','common'),('C_EV_reconstructed','reconstructed','primary')]:
        row=next(x for x in network if x['sample']=='S3' and x['frequency']==freq and x['outcome']==outcome)
        robustness.append(est(row,finding='F4',key=key,frequency=freq,sample=sample,units='centrality_units_per_'+('week' if freq=='weekly' else 'month'),transform=1,file='regimes_common_network.csv',selection=f'S3 / {freq} / {outcome} / trend'))

def clean(text):return unescape(re.sub('<[^>]+>','',text)).strip()
catalog={}
keys=['relevance','prominence','reach','share','gap','centrality','expectations']
for lang,filename in [('en','index.html'),('hr','hr.html')]:
    html=(P/'src'/filename).read_text(encoding='utf-8')
    block=html.split('<div class="indicator-guide">',1)[1].split('<div class="worked-example"',1)[0]
    catalog[lang]={}
    for key,detail in zip(keys,re.findall('<details>(.*?)</details>',block,re.S)):
        title=clean(re.search('<summary>(.*?)<span',detail,re.S)[1])
        vals=re.findall('<dd>(.*?)</dd>',detail,re.S)
        catalog[lang][key]={'title':title,'meaning':clean(vals[0])+' '+clean(vals[1]),'construction':clean(vals[2]),'limitations':clean(vals[3])}
    additions={
      'en':{
       'article':{'title':'Article share','meaning':'How many inflation-relevant institutional items appear relative to the inflation corpus?','construction':'100 × relevant institutional item count / (inflation item count + 1). It does not apply prominence or reach weights.','limitations':'Counts publication instances; repeated publication is not independent editorial attention.'},
       'hhi':{'title':'Concentration of institutional weight','meaning':'How concentrated is the visibility numerator across source labels?','construction':'Sum the squared source shares of the salience × reach numerator. A value of 1 means one source carries all weight.','limitations':'Source labels are not necessarily independent brands or owners. This weighted-numerator diagnostic differs from the broad source-reach HHI used as a regression control.'}},
      'hr':{
       'article':{'title':'Udio objava','meaning':'Koliko institucionalnih objava relevantnih za inflaciju ima u odnosu na inflacijski korpus?','construction':'100 × broj relevantnih institucionalnih objava / (broj inflacijskih objava + 1), bez ponderiranja istaknutošću ili dosegom.','limitations':'Broje se pojedinačne objave; prenošenje teksta ne predstavlja neovisnu uredničku pozornost.'},
       'hhi':{'title':'Koncentracija institucionalnog pondera','meaning':'Koliko je brojnik vidljivosti koncentriran među oznakama izvora?','construction':'Zbroj kvadrata udjela izvora u brojniku istaknutost × doseg. Vrijednost 1 znači da jedan izvor nosi sav ponder.','limitations':'Oznake izvora nisu nužno neovisni brendovi ili vlasnici. Ova dijagnostika ponderiranog brojnika razlikuje se od HHI-ja ukupnog dosega korištenog kao kontrola u regresiji.'}}}
    catalog[lang].update(additions[lang])

records=[
 {'id':'F1','model':'Primary weekly model, equation 9b','measure':'Weighted institutional visibility','sample':'S1 · January 2021–May 2026','reference':'Section 4.2 · Table 6 · Appendix A23','finding':'Higher inflation is associated with lower weighted visibility in the primary weekly model; time-control sensitivity qualifies the association.','finding_hr':'U primarnom tjednom modelu viša inflacija povezana je s nižom ponderiranom vidljivošću; osjetljivost na vremenske kontrole ograničava zaključak.','checks':['9b','9a','trend','year','common','winsor']},
 {'id':'F2','model':'Controlled monthly trend','measure':'Weighted institutional visibility','sample':'S3 · April 2024–May 2026','reference':'Section 4.6 · common-source comparison','finding':'Weighted visibility declines within April 2024–May 2026 in the primary and common-source monthly trend models.','finding_hr':'Od travnja 2024. do svibnja 2026. ponderirana vidljivost pada u mjesečnim modelima primarnog uzorka i zajedničkih izvora.','checks':['primary','common']},
 {'id':'F3','model':'Forward projections; article-share exposure; continuity controls','measure':'Consumer expectations survey balance','sample':'S1 · January 2021–May 2026','reference':'Section 4.5 · Table 8 · Appendix A12','finding':'A stable predictive relationship with consumer expectations is not established; survey assignment and model controls affect the results.','finding_hr':'Stabilna prediktivna veza s potrošačkim očekivanjima nije utvrđena; vremensko pridruživanje ankete i kontrole mijenjaju rezultate.','checks':['linear','step','monthly']},
 {'id':'F4','model':'Common-source monthly network trend','measure':'Normalised eigenvector centrality','sample':'S3 · April 2024–May 2026','reference':'Section 4.7 · Appendix B2','finding':'The common-source monthly centrality interval includes zero; a lasting decline in network position is not established.','finding_hr':'Interval mjesečnog trenda centralnosti zajedničkih izvora obuhvaća nulu; trajni pad mrežnog položaja nije utvrđen.','checks':['common','reconstructed']}
]
record_hr={
 'F1':('Primarni tjedni model, jednadžba 9b','Ponderirana institucionalna vidljivost','S1 · siječanj 2021. – svibanj 2026.','Odjeljak 4.2 · tablica 6 · dodatak A23'),
 'F2':('Mjesečni trend uz kontrole','Ponderirana institucionalna vidljivost','S3 · travanj 2024. – svibanj 2026.','Odjeljak 4.6 · usporedba zajedničkih izvora'),
 'F3':('Projekcije budućih ishoda; udio objava; osnovne kontrole','Saldo ankete potrošačkih očekivanja','S1 · siječanj 2021. – svibanj 2026.','Odjeljak 4.5 · tablica 8 · dodatak A12'),
 'F4':('Mjesečni trend mreže zajedničkih izvora','Normalizirana centralnost svojstvenog vektora','S3 · travanj 2024. – svibanj 2026.','Odjeljak 4.7 · dodatak B2')}
for record in records:
    record.update(dict(zip(['model_hr','measure_hr','sample_hr','reference_hr'],record_hr[record['id']])))
    record.update(data_version=e['edition'],method_version='extended-manuscript-2026-09-17',presentation_version='2026-09-19.2',verification='Matched to saved outputs',author_review='pending')
result={'version':'2026-09-19.2','data_version':e['edition'],'method_version':'extended-manuscript-2026-09-17','observations':observations,'robustness':robustness,'indicators':catalog,'findings':records,
 'common_source_definition':{'source_labels':258,'reference_windows':['2023-01–2023-12','2024-07–2024-12'],'rule':'Intersection of source labels with institutional items in both reference windows; restrict both numerator and denominator.'},
 'channels':[{ 'channel':r['channel'],'items':int(r['items'])} for r in read_csv(private/'channels.csv')],
 'revisions':[{'version':'2026-09-19.2','type':'editorial','date':'2026-09-19','description':'Context-preserving inspection, predefined sensitivity comparisons and diagnostics from existing scored records. Published research estimates unchanged.'},{'version':'2026-09-19.1','type':'editorial','date':'2026-09-19','description':'Evidence overview, worked examples, URL selections and selected-view exports. Published research estimates unchanged.'}]}
save(P/'public/data/inspection.json',result)
save(P/'public/data/findings.json',{'version':result['version'],'findings':records,'revisions':result['revisions']})
inputs=['panel_monthly.csv','panel_monthly_commonsrc.csv','results/spec_curve_curve.csv','results/regimes_trend.csv','results/regimes_common_network.csv']
save(P/'content/inspection-input-hashes.json',{'inputs':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in inputs},'aggregates':{f:hashlib.sha256((private/f).read_bytes()).hexdigest() for f in ['concentration.csv','domains.csv','channels.csv']}})
print(f'Prepared {len(observations)} monthly inspection records, {len(robustness)} saved comparisons and four traceable findings.')
