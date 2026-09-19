"""Verify the inspection layer against its saved panels and aggregate inputs."""
from pathlib import Path
import argparse,csv,json,hashlib,math,re
P=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--research-root',type=Path)
parser.add_argument('--aggregate-root',type=Path,default=P/'private/inspection-aggregates')
args=parser.parse_args();ROOT=args.research_root.resolve() if args.research_root else None
def rows(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
i=json.loads((P/'dist/data/inspection.json').read_text(encoding='utf-8'))
hashes=json.loads((P/'content/inspection-input-hashes.json').read_text(encoding='utf-8'))
checks={}
def check(key,test):
    checks[key]=bool(test)
    if not test:raise AssertionError(key)
if ROOT is not None:
    check('source_hashes',all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h for f,h in hashes['inputs'].items()))
    main={r['yearmonth'][:7]:r for r in rows(ROOT/'panel_monthly.csv')}
    common={r['yearmonth'][:7]:r for r in rows(ROOT/'panel_monthly_commonsrc.csv')}
    check('aggregate_hashes',all(hashlib.sha256((args.aggregate_root/f).read_bytes()).hexdigest()==h for f,h in hashes['aggregates'].items()))
    stats={(r['period'],r['sample']):r for r in rows(args.aggregate_root/'concentration.csv')}
else:stats={}
e=json.loads((P/'dist/data/evidence.json').read_text(encoding='utf-8'))
check('observation_periods',[r['period'] for r in i['observations']]==[r['period'] for r in e['observations']])
check('primary_matches_published_series',all(math.isclose(a['primary']['share'],100*(e['baseline']['monthly']-b['gap']),rel_tol=1e-12) and a['inflation']==b['inflation'] for a,b in zip(i['observations'],e['observations'])))
for row in i['observations']:
    for sample in ['primary','common']:
        d=row[sample]
        if ROOT is not None:
            p=main[row['period']] if sample=='primary' else common[row['period']];s=stats[row['period'],sample]
            numerator=float(p['A_s_infl' if sample=='primary' else 'A_s_infl_common'])
            denominator=float(p['A_INF_core' if sample=='primary' else 'A_INF_common'])+1
            count=int(p['n_infl_hnb' if sample=='primary' else 'n_hnb_common'])
            count_den=int(p['n_infl_core' if sample=='primary' else 'n_infl_common'])
        else:
            numerator=d['numerator'];denominator=d['denominator'];count=d['relevant_items'];count_den=d['inflation_items']
        tag=row['period']+'_'+sample
        check(tag+'_share',math.isclose(d['share'],100*numerator/denominator,rel_tol=1e-12))
        if ROOT is not None:check(tag+'_gap',d['gap']==100*float(p['IAG_primary' if sample=='primary' else 'IAG_common']))
        check(tag+'_article',math.isclose(d['article'],100*count/(count_den+1),rel_tol=1e-12))
        check(tag+'_reference_constant',math.isclose(d['share']+d['gap'],i['observations'][0][sample]['share']+i['observations'][0][sample]['gap'],rel_tol=1e-12))
        check(tag+'_counts',d['relevant_items']==count and d['inflation_items']==count_den and 0<=count<=d['items'] and 0<=d['weighted_sources']<=d['source_labels'] and count_den>=0 and denominator>0 and all(isinstance(d[k],int) for k in ['items','relevant_items','inflation_items','source_labels','weighted_sources']))
        if ROOT is not None:check(tag+'_concentration',d['hhi']==float(s['weight_hhi']) and d['top5']==100*float(s['top5_source_share']) and d['top10']==100*float(s['top10_item_share']))
        check(tag+'_ranges',0<=d['top5']<=100 and 0<=d['top10']<=100 and 0<=d['hhi']<=1 and 0<=d['centrality']<=1 and d['share']<=18)
        if row['period']>='2024-04':check(tag+'_recent_chart_range',0<=d['share']<=(6 if sample=='primary' else 8) and (-2 if sample=='primary' else -4)<=d['gap']<=5)
        check(tag+'_public_source_labels',all(re.fullmatch(r'[a-z0-9][a-z0-9.-]*\.[a-z]{2,}',r['source']) for r in d['domains']))
        check(tag+'_domain_shares',sum(r['contribution'] for r in d['domains'])<=100.0000001)
for r in i['robustness']:
    check(r['finding']+'_'+r['frequency']+'_'+r['key']+'_valid',all(math.isfinite(r[k]) for k in ['estimate','lo','hi','p','N']) and r['lo']<=r['estimate']<=r['hi'] and 0<=r['p']<=1 and r['N']>0)
    if ROOT is None:continue
    table=rows(ROOT/'results'/r['file'])
    subset=[s for s in table if s['frequency']==r['frequency'] and s['sample']==('S1' if r['finding']=='F1' else 'S3')]
    if r['file']=='primary_coefficients.csv':subset=[s for s in subset if s['spec']==r['key'] and s['term']=='pi_t' and s['outcome']=='IAG_primary']
    elif r['file']=='regimes_common_slope_sensitivity.csv':subset=[s for s in subset if s['adjustment']==r['key']]
    elif r['file']=='spec_curve_curve.csv':subset=[s for s in subset if s['outcome']==('IAG_common' if r['key']=='common' else 'IAG_winsor') and s['controls']=='3' and s['concentration']=='HHI_all']
    else:
        outcome='IAG_primary' if r['finding']=='F2' and r['sample']=='primary' else 'IAG_common' if r['finding']=='F2' else 'C_EV_common' if r['key']=='common' else 'C_EV_reconstructed'
        subset=[s for s in subset if s['outcome']==outcome and s['term']=='trend']
    check(r['finding']+'_'+r['frequency']+'_'+r['key']+'_exact',len(subset)==1 and all(r[k]==float(subset[0][k]) for k in ['estimate','lo','hi','p','N']))
check('fixed_finding_ids',[r['id'] for r in i['findings']]==['F1','F2','F3','F4'])
check('bilingual_indicator_catalog',set(i['indicators']['en'])==set(i['indicators']['hr']) and len(i['indicators']['en'])==9)
check('revision_type',all(r['type']=='editorial' for r in i['revisions']))
check('channel_count',sum(r['items'] for r in i['channels'])==sum(r['primary']['items'] for r in i['observations']))
for lang in ['en','hr']:
    html=(P/'dist'/('index.html' if lang=='en' else 'hr.html')).read_text(encoding='utf-8')
    check(lang+'_inspection_payload',json.loads(re.search(r'<script type="application/json" id="inspection-data">(.*?)</script>',html,re.S)[1])==i)
(P/'qa/inspection-checks.json').write_text(json.dumps({'passed':len(checks),'checks':checks},indent=2),encoding='utf-8')
print(f'{len(checks)} inspection checks passed.'+(' Upstream panels, estimates and aggregates matched.' if ROOT else ' Standalone numerical contracts and metadata verified.'))
