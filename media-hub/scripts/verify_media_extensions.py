"""Independent arithmetic checks against the frozen source-month audit trail."""
from pathlib import Path
from collections import defaultdict
from statistics import mean,stdev
import csv,json,hashlib,math,sys

def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def verify(root,out):
    checks={}
    def check(k,v):
        checks['extension '+k]=bool(v)
        if not v:raise AssertionError(k)
    def close(a,b):return a is None and b is None or a is not None and b is not None and math.isclose(float(a),float(b),rel_tol=1e-11,abs_tol=1e-10)
    d=json.loads((out/'extensions.json').read_text(encoding='utf-8'))
    src=read(root/'public/data/media/media-source-monthly.csv')
    src=[{k:v if k in ['source_id','period'] else int(v) for k,v in r.items()} for r in src if d['period_start']<=r['period']<=d['period_end']]
    panel=d['panel'];monthly=read(root/'public/data/media/media-monthly.csv')
    expected={r['period']:r for r in monthly if r['period']<=d['period_end']}
    check('frozen panel 128',len(panel)==len(set(panel))==128)
    check('source-month unique',len(src)==len({(r['source_id'],r['period']) for r in src}))
    for row in d['monthly']:
        p=row['period'];scope=row['scope'];rs=[r for r in src if r['period']==p and (scope=='all' or r['source_id'] in panel)]
        h=sum(r['hnb_count'] for r in rs);hi=sum(r['hnb_i'] for r in rs);b=sum(r['background_i'] for r in rs)
        label=p+' '+scope
        check(label+' totals',(h,hi,b)==(row['hnb_count'],row['hnb_i'],row['background_i']))
        check(label+' rate',close(row['rate_per_10000'],10000*hi/b))
        check(label+' title',row['title_mention_count']==sum(r['title_mention_count'] for r in rs) and close(row['title_share'],row['title_mention_count']/h))
        check(label+' breadth',(row['hnb_domains'],row['background_domains'])==(sum(r['hnb_count']>0 for r in rs),sum(r['background_count']>0 for r in rs)))
        if scope=='all':check(label+' legacy breadth',row['hnb_domains']==int(expected[p]['outlet_breadth']) and row['background_domains']==int(expected[p]['active_outlets']))
        else:
            check(label+' fixed denominators',len(rs)==128 and all(r['background_i']>0 for r in rs))
            check(label+' equal weighting',close(row['fixed_weight_rate'],sum(r['hnb_i']/r['background_i'] for r in rs)*10000/128))
    for row in d['concentration']:
        rs=[r for r in src if row['period_start']<=r['period']<=row['period_end'] and (row['scope']=='all' or r['source_id'] in panel)]
        grouped=defaultdict(int)
        for r in rs:grouped[r['source_id']]+=r['hnb_count']
        positive=sorted((n for n in grouped.values() if n),reverse=True);h=sum(positive)
        check(row['period_id']+row['scope']+' effective',close(row['effective_domains'],h*h/sum(n*n for n in positive)))
        check(row['period_id']+row['scope']+' top ten',close(row['top_ten_share'],sum(positive[:10])/h))
        check(row['period_id']+row['scope']+' union breadth',row['hnb_domains']==len(positive) and row['background_domains']==len({r['source_id'] for r in rs if r['background_count']>0}))
    pooled=next(r for r in d['concentration'] if r['period_id']=='pooled' and r['scope']=='all')
    fixtures={'hnb_count':33235,'hnb_i':33235,'background_i':10110869,'title_mention_count':5222,'hnb_domains':281,'background_domains':416,'effective_domains':38.441196429596225,'top_ten_share':0.4197683165337746}
    for k,want in fixtures.items():check('pinned fixture '+k,close(pooled[k],want))
    for period in ['pooled','legacy','api']:
        rows=[r for r in d['source_rates'] if r['period_id']==period]
        check(period+' ranking thresholds',all(bool(r['eligible'])==(r['hnb_i']>=50 and r['background_i']>=5000) for r in rows))
        rank=sorted((r for r in rows if r['eligible']),key=lambda r:(-r['rate_per_10000'],r['source_id']))
        check(period+' order',all(r['rank']==i for i,r in enumerate(rank,1)) and all(r['rank'] is None for r in rows if not r['eligible']))
    check('78 ranked',sum(r['eligible'] for r in d['source_rates'] if r['period_id']=='pooled')==78)
    check('201 typology workload',sum(r['background_i']>=5000 or r['hnb_i']>=50 for r in d['source_rates'] if r['period_id']=='pooled')==201)
    latest=d['latest'];hist=[r for r in d['monthly'] if r['scope']=='all' and r['period']<latest['period']][-12:]
    avg=next(r for r in latest['comparisons'] if r['comparison']=='preceding_12_month_mean')
    check('latest August',latest['period']=='2026-08' and len(hist)==12 and hist[0]['period']=='2025-08' and hist[-1]['period']=='2026-07')
    check('monthly rate arithmetic mean',close(avg['rate_per_10000'],mean(r['rate_per_10000'] for r in hist)))
    for r in d['events']:
        previous=[x for x in d['monthly'] if x['scope']=='all' and x['period']<r['period'] and x['collection_regime']==r['collection_regime']][-24:]
        if len(previous)<24:check(r['period']+' unscored',r['candidate'] is None and r['status']=='insufficient_history')
        else:check(r['period']+' peak rule',close(r['threshold'],mean(x['rate_per_10000'] for x in previous)+2*stdev(x['rate_per_10000'] for x in previous)))
    # Failure behavior, not just the observed happy path.
    sys.path.insert(0,str(root/'scripts'))
    from extensions_aggregates import fixed_weights,compare_months
    mini=[{'source_id':'a','hnb_i':1,'background_i':10}]
    check('missing panel member yields null',fixed_weights(mini,['a','b'])==(None,'missing_or_zero_panel_denominator',1))
    check('zero panel denominator yields null',fixed_weights([{'source_id':'a','hnb_i':0,'background_i':0}],['a'])[0] is None)
    current=dict(period='2024-01',collection_regime='api',hnb_count=2,rate_per_10000=4,title_share=.5,breadth_share=.4)
    past=dict(period='2023-01',collection_regime='legacy',hnb_count=1,rate_per_10000=2,title_share=.25,breadth_share=.2)
    crossing=compare_months(current,[past],'year_ago')
    check('crossing regime withholds changes',crossing['status']=='regime_boundary_withheld' and crossing['hnb_count_change'] is None)
    zero=dict(past,collection_regime='api',hnb_count=0,rate_per_10000=0)
    change=compare_months(current,[zero],'year_ago')
    check('zero comparison yields no percent change',change['hnb_count_change'] is None and change['rate_per_10000_change'] is None)
    check('share changes use percentage points',change['title_share_change']==25 and change['breadth_share_change']==20)
    check('incomplete year comparison unavailable',compare_months(current,[],'year_ago')['hnb_count_change'] is None)
    manifest=json.loads((out/'extensions-manifest.json').read_text(encoding='utf-8'))
    for name,digest in manifest['outputs'].items():check('output hash '+name,hashlib.sha256((out/name).read_bytes()).hexdigest()==digest)
    for name,digest in manifest['inputs'].items():check('input hash '+name,hashlib.sha256((root/'public/data/media'/name).read_bytes()).hexdigest()==digest)
    return checks

if __name__=='__main__':
    site=Path(__file__).resolve().parents[1];root=site
    checks=verify(root,root/'public/data/media')
    (site/'qa/media-extension-checks.json').write_text(json.dumps({'passed':len(checks),'checks':checks},indent=2)+'\n',encoding='utf-8')
    print(len(checks),'extension checks passed')
