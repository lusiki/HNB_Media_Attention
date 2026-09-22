"""A1 indicators and B03 peak screen from safe aggregates only (standard library).

No database, article text, or network access. Definitions: HNB_MEDIA_INDICATORS_1.0.
"""
from pathlib import Path
from collections import defaultdict
from statistics import mean, stdev
import csv, hashlib, json

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT/'public/data/media'
ANALYSIS = 'HNB_MEDIA_INDICATORS_1.0'
OUTPUT = ROOT/'qa'/ANALYSIS
META = dict(study_id='hnb-media', corpus_id='HNB_MEDIA', data_version='2026-09-21.1',
            method_version='1.0', indicator_version=ANALYSIS,
            validation_status='descriptive_archive_counts_not_independently_validated')

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rate(h,b):return 10000*h/b if b else None
def regime(period):return 'legacy' if period<'2024-01' else 'api'
def dump(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def write_csv(path,rows):
    assert rows, 'Do not generate empty future-result tables'
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def summarize(rows, start, end, scope, period_id):
    sources=defaultdict(lambda:defaultdict(int))
    for r in rows:
        for k in ['hnb_count','hnb_i','background_count','background_i','title_mention_count']:
            sources[r['source_id']][k]+=r[k]
    h=sum(r['hnb_count'] for r in rows);hi=sum(r['hnb_i'] for r in rows)
    b=sum(r['background_i'] for r in rows);titles=sum(r['title_mention_count'] for r in rows)
    counts=sorted((r['hnb_count'] for r in sources.values() if r['hnb_count']>0),reverse=True)
    hhi=sum((n/h)**2 for n in counts) if h else None
    return dict(period_id=period_id,period_start=start,period_end=end,scope=scope,
        collection_regime=regime(start) if regime(start)==regime(end) else 'mixed_boundary_2024_01',
        hnb_count=h,hnb_i=hi,background_i=b,rate_per_10000=rate(hi,b),
        title_mention_count=titles,title_share=titles/h if h else None,
        hnb_domains=len(counts),background_domains=sum(r['background_count']>0 for r in sources.values()),
        breadth_share=len(counts)/sum(r['background_count']>0 for r in sources.values()) if sources else None,
        breadth_denominator='domains_with_background_count_gt_0_union',
        effective_domains=1/hhi if hhi else None,top_five_share=sum(counts[:5])/h if h else None,
        top_ten_share=sum(counts[:10])/h if h else None,**META)

def fixed_weights(rows,panel):
    by_source={r['source_id']:r for r in rows}
    missing=[s for s in panel if s not in by_source or by_source[s]['background_i']<=0]
    value=None if missing else mean(rate(by_source[s]['hnb_i'],by_source[s]['background_i']) for s in panel)
    return value, 'missing_or_zero_panel_denominator' if missing else 'available',len(missing)

def compare_months(current,obs,label):
    complete=len(obs)==(1 if label=='year_ago' else 12)
    crossing=any(r['collection_regime']!=current['collection_regime'] for r in obs)
    comparison={'comparison':label,'period_start':obs[0]['period'] if obs else None,
        'period_end':obs[-1]['period'] if obs else None,'n_months':len(obs),
        'status':'incomplete' if not complete else 'regime_boundary_withheld' if crossing else 'available',
        'crosses_regime_boundary':crossing}
    for k in ['hnb_count','rate_per_10000','title_share','breadth_share']:
        comparator=mean(r[k] for r in obs) if complete and all(r[k] is not None for r in obs) else None
        comparison[k]=comparator
        comparison[k+'_change']=None if comparator is None or current[k] is None or crossing else ((current[k]-comparator)*100 if k.endswith('share') else 100*(current[k]/comparator-1) if comparator else None)
    return comparison

def produce():
    summary=json.loads((INPUT/'summary.json').read_text(encoding='utf-8'))
    monthly=read_csv(INPUT/'media-monthly.csv')
    start,end=summary['first_period'],summary['last_full_period']
    periods=[r['period'] for r in monthly if start<=r['period']<=end]
    source_rows=read_csv(INPUT/'media-source-monthly.csv')
    source_rows=[{k:v if k in ['source_id','period'] else int(v) for k,v in r.items()}
                 for r in source_rows if start<=r['period']<=end]
    panel=sorted(r['source_id'] for r in read_csv(INPUT/'media-sources.csv') if r['is_stable']=='1')
    OUTPUT.mkdir(parents=True,exist_ok=True)
    panel_file=OUTPUT/'media-stable-panel.csv'
    panel_rows=[dict(source_id=s,weight=1/len(panel),panel_id='S0_2021_01_2026_08',
        period_start=start,period_end=end,selection='background publication observed in every full month',**META) for s in panel]
    if panel_file.exists():
        assert [r['source_id'] for r in read_csv(panel_file)]==panel,'Frozen panel changed: requires a new identity'
    write_csv(panel_file,panel_rows)
    indicators=[];components=[]
    by_period=defaultdict(list)
    for r in source_rows:by_period[r['period']].append(r)
    for period in periods:
        rows=by_period[period]
        value,status,gaps=fixed_weights(rows,panel)
        for scope in ['all','stable']:
            selected=rows if scope=='all' else [r for r in rows if r['source_id'] in panel]
            indicators.append(dict(period=period,**summarize(selected,period,period,scope,period),
                fixed_weight_rate=value if scope=='stable' else None,
                fixed_weight_status=status if scope=='stable' else 'not_applicable',
                missing_panel_denominators=gaps if scope=='stable' else None))
        by_source={r['source_id']:r for r in rows}
        for source in panel:
            r=by_source.get(source)
            components.append(dict(period=period,source_id=source,panel_id='S0_2021_01_2026_08',
                weight=1/len(panel),hnb_i=r['hnb_i'] if r else None,background_i=r['background_i'] if r else None,
                rate_per_10000=rate(r['hnb_i'],r['background_i']) if r else None,
                status='available' if r and r['background_i']>0 else 'missing_or_zero_panel_denominator',**META))
    windows=[('pooled',start,end),('legacy',start,'2023-12'),('api','2024-01',end)]
    windows += [(str(y),max(start,f'{y}-01'),min(end,f'{y}-12')) for y in range(int(start[:4]),int(end[:4])+1)]
    concentration=[];rates=[]
    for label,lo,hi in windows:
        rows=[r for r in source_rows if lo<=r['period']<=hi]
        for scope in ['all','stable']:
            selected=rows if scope=='all' else [r for r in rows if r['source_id'] in panel]
            concentration.append(summarize(selected,lo,hi,scope,label))
        if label not in ['pooled','legacy','api']:continue
        by_source=defaultdict(list)
        for r in rows:by_source[r['source_id']].append(r)
        window_rates=[]
        for source,items in sorted(by_source.items()):
            h=sum(r['hnb_i'] for r in items);b=sum(r['background_i'] for r in items)
            window_rates.append(dict(period_id=label,period_start=lo,period_end=hi,source_id=source,
                hnb_count=sum(r['hnb_count'] for r in items),hnb_i=h,background_i=b,
                rate_per_10000=rate(h,b),eligible=int(b>=5000 and h>=50),
                eligibility='eligible' if b>=5000 and h>=50 else 'below_ranking_threshold',rank=None,
                collection_regime=label if label!='pooled' else 'mixed_boundary_2024_01',**META))
        ranked=sorted((r for r in window_rates if r['eligible']),key=lambda r:(-r['rate_per_10000'],r['source_id']))
        for i,r in enumerate(ranked,1):r['rank']=i
        rates.extend(window_rates)
    current=next(r for r in indicators if r['period']==end and r['scope']=='all')
    year_ago=f'{int(end[:4])-1}{end[4:]}'
    previous=next((r for r in indicators if r['period']==year_ago and r['scope']=='all'),None)
    history=[r for r in indicators if r['period']<end and r['scope']=='all'][-12:]
    comparisons=[]
    for label,obs in [('year_ago',[previous] if previous else []),('preceding_12_month_mean',history)]:
        comparisons.append(compare_months(current,obs,label))
    latest=dict(period=end,current=current,comparisons=comparisons,
        percent_change_fields=['hnb_count_change','rate_per_10000_change'],
        percentage_point_fields=['title_share_change','breadth_share_change'],
        prior_mean_definition='arithmetic mean of previous 12 complete monthly observations, current excluded',**META)
    # B03 screening is possible from A1 inputs. Event interpretation still needs review.
    events=[];all_months=[r for r in indicators if r['scope']=='all']
    stable_months={r['period']:r for r in indicators if r['scope']=='stable'}
    for r in all_months:
        prior=[x for x in all_months if x['period']<r['period'] and x['collection_regime']==r['collection_regime']][-24:]
        eligible=len(prior)==24
        row=dict(period=r['period'],collection_regime=r['collection_regime'],prior_months=len(prior),
            rate_per_10000=r['rate_per_10000'],previous_24_mean=None,previous_24_sd=None,threshold=None,
            status='insufficient_history',candidate=None,hnb_domains=r['hnb_domains'],title_share=r['title_share'],
            stable_rate_per_10000=stable_months[r['period']]['rate_per_10000'],
            fixed_weight_rate=stable_months[r['period']]['fixed_weight_rate'],**META)
        if eligible:
            avg=mean(x['rate_per_10000'] for x in prior);sd=stdev(x['rate_per_10000'] for x in prior)
            row.update(previous_24_mean=avg,previous_24_sd=sd,threshold=avg+2*sd,
                       status='scored' if sd>0 else 'zero_variance',candidate=int(r['rate_per_10000']>avg+2*sd) if sd>0 else None)
        events.append(row)
    files={'media-indicators-monthly.csv':indicators,'media-source-rates.csv':rates,
           'media-source-concentration.csv':concentration,'media-fixed-weight-components.csv':components,
           'media-event-screen.csv':events}
    for name,rows in files.items():write_csv(OUTPUT/name,rows)
    dump(OUTPUT/'media-latest-edition.json',latest)
    dump(OUTPUT/'media-events.json',dict(rule='rate > mean(previous 24 complete same-regime months) + 2 sample SD',
        interpretation='descriptive candidate screen; no causal or independently verified event attribution',
        candidates=[r for r in events if r['candidate']==1],**META))
    dump(OUTPUT/'extensions.json',dict(schema_version='1.1',**META,period_start=start,period_end=end,
        panel_id='S0_2021_01_2026_08',panel=panel,monthly=indicators,source_rates=rates,
        concentration=concentration,latest=latest,events=events,
        definitions={'breadth':'union of domains with H>0 / union with background_count>0; existing active_outlets definition',
        'rate':'10000 * sum(hnb_i) / sum(background_i)',
        'fixed_weight':'10000 * sum_s((1/128) * hnb_i(s,t)/background_i(s,t)); null if any frozen-panel denominator missing/zero',
        'ranking':'background_i >= 5000 AND hnb_i >= 50 in selected window',
        'concentration':'all HNB-carrying domains; no rate-ranking threshold',
        'title':'sum(title_mention_count) / sum(hnb_count); mechanical match only'}))
    manifest=dict(**META,period_start=start,period_end=end,panel_sha256=sha(panel_file),
        inputs={name:sha(INPUT/name) for name in ['summary.json','media-monthly.csv','media-source-monthly.csv','media-sources.csv']},
        outputs={p.name:sha(p) for p in sorted(OUTPUT.iterdir()) if p.is_file() and p.name!='extensions-manifest.json'})
    dump(OUTPUT/'extensions-manifest.json',manifest)
    print(json.dumps({'analysis':ANALYSIS,'monthly_rows':len(indicators),'panel_size':len(panel),
        'pooled':concentration[0],'eligible_rate_domains':sum(r['eligible'] for r in rates if r['period_id']=='pooled'),
        'event_candidate_months':[r['period'] for r in events if r['candidate']==1]},ensure_ascii=False))

if __name__=='__main__':produce()
