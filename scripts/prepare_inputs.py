"""Explicit research refresh: only small, saved aggregates; never source databases."""
from pathlib import Path
import argparse, csv, json, hashlib, shutil

SITE = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--research-root', required=True, type=Path,
                    help='Local extended research folder containing results/ and paper/. Never uploaded.')
ROOT = parser.parse_args().research_root.resolve()
if not (ROOT/'results').is_dir() or not (ROOT/'paper/PAPER_EXT.qmd').is_file():
    parser.error('The selected research folder must contain results/ and paper/PAPER_EXT.qmd.')
INPUTS = ['primary_coefficients.csv', 'primary_magnitude.csv', 'samples_coverage.csv',
          'regimes_trend.csv', 'regimes_common_network.csv',
          'regimes_common_slope_sensitivity.csv', 'expectations_irf.csv', 'data_quality_series.csv']

def read(name):
    with (ROOT / 'results' / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def select(rows, **where):
    return [r for r in rows if all(r[k] == str(v) for k,v in where.items())]

def number(x):
    return None if x in ('', 'NA', 'NaN') else float(x)

def estimate(row):
    return {k: number(row[k]) for k in ['estimate', 'se', 'lo', 'hi', 'p', 'N']}

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')

magnitude = read('primary_magnitude.csv')
baseline = {f: number(select(magnitude, sample='S1', frequency=f)[0]['baseline']) for f in ['monthly','weekly']}
observations = []
for row in read('data_quality_series.csv'):
    if row['frequency'] != 'monthly' or not '2021-01-01' <= row['date'] < '2026-06-01':
        continue
    usable = row['flag_usable'] == 'TRUE'
    observations.append({
        'period': row['date'][:7],
        'gap': number(row['IAG_primary']) if usable else None,
        'inflation': number(row['pi_t']) if usable else None,
        'source': 'new' if row['BATCH_NEW'] == '1' else 'original',
        'status': 'included' if usable else 'excluded_text_coverage'
    })
assert len(observations) == 65
assert sum(r['gap'] is not None for r in observations) == 62
assert [r['period'] for r in observations if r['gap'] is None] == ['2024-01','2024-02','2024-03']
models = []
for f in ['weekly','monthly']:
    for spec in ['9b','9a']:
        row = select(read('primary_coefficients.csv'), sample='S1', frequency=f, spec=spec, outcome='IAG_primary', term='pi_t')[0]
        models.append({'frequency': f, 'specification': spec, **estimate(row)})
trend = estimate(select(read('regimes_trend.csv'), sample='S3', frequency='monthly', outcome='IAG_primary')[0])
common = estimate(select(read('regimes_common_network.csv'), sample='S3', frequency='monthly', outcome='IAG_common')[0])
lp = []
for freq, outcome, label in [('weekly','exp_linear','Weekly · linear'),('weekly','exp_step','Weekly · step'),('monthly','exp_balance','Monthly · original survey')]:
    rows = [r for r in select(read('expectations_irf.csv'), sample='S1', frequency=freq, outcome=outcome, exposure='IAG_ext', specification='continuity') if int(r['horizon']) > 0]
    assert len(rows) == 12
    lp.append({'label':label,'frequency':freq,'significant_horizons':[int(r['horizon']) for r in rows if float(r['p_bonf']) < .05],
               'tested_future_horizons':len(rows),'correction_family_size':13,'minimum_adjusted_p':min(float(r['p_bonf']) for r in rows)})
evidence = {
    'edition':'extended-2026-09-17', 'verification':'matched_to_output',
    'sample':'S1', 'frequency':'monthly', 'baseline':baseline,
    'series_metadata':[
        {'id':'gap','label':'HNB attention gap','definition':'Fixed Jan–Jun 2021 mean weighted share (after baseline outlier exclusion) minus current weighted share',
         'canonical_units':'share units','display_units':'percentage points','display_multiplier':100,'time_basis':'calendar month of record date; publication timestamp not established',
         'scope':'extended manuscript primary sample; original platform universe','missing_rule':'null for excluded months; no interpolation or bridging source boundary'},
        {'id':'inflation','label':'HICP inflation','definition':'Croatian all-items HICP, year-on-year rate','canonical_units':'percent','display_units':'percent','display_multiplier':1,
         'time_basis':'reference month','scope':'primary-sample months','missing_rule':'suppressed with excluded media months for aligned comparison; not a claim of missing HICP'}],
    'observations':observations, 'models':models, 'trend':trend, 'common_source_trend':common, 'expectations':lp,
    'coverage':[{k:(int(r[k]) if k in ['eligible','complete_baseline','segments'] else r[k]) for k in ['frequency','sample','eligible','complete_baseline','start','end','segments']}
                for r in read('samples_coverage.csv') if r['sample'] in ['S1','S3']],
    'time_sensitivity':[{**{'frequency':r['frequency'],'adjustment':r['adjustment']},**estimate(r)} for r in read('regimes_common_slope_sensitivity.csv')],
    'source_note':'Saved results underlying the 17 September 2026 extended manuscript. Selected values were matched, not re-estimated for this publication.'
}
save(SITE/'public/data/evidence.json', evidence)
with (SITE/'public/data/monthly-series.csv').open('w', encoding='utf-8', newline='') as f:
    writer=csv.DictWriter(f, fieldnames=['period','gap','inflation','source','status']); writer.writeheader(); writer.writerows(observations)
inputs={name:hashlib.sha256((ROOT/'results'/name).read_bytes()).hexdigest() for name in INPUTS}
save(SITE/'content/research-input-hashes.json', {'inputs':inputs})
paper=ROOT/'results/qa/PAPER_EXT.pdf'
assert hashlib.sha256(paper.read_bytes()).hexdigest() == '00aa9a875226ee39d39049d975621a367aa7aa9adeea994e01d12c11469477d1'
(SITE/'public/downloads').mkdir(parents=True,exist_ok=True)
shutil.copyfile(paper, SITE/'public/downloads/hnb-attention-gap-paper.pdf')
save(SITE/'private/input-provenance.json', {'source_commit':'76d9b66','inputs':inputs,'paper_source':str(paper), 'paper_sha256':hashlib.sha256(paper.read_bytes()).hexdigest()})
register=[]
study=json.loads((SITE/'content/study.json').read_text(encoding='utf-8'))
locators=['paper/PAPER_EXT.qmd:250; tbl-primary; Eq8/9b','paper/PAPER_EXT.qmd:340; regimes paragraph; PDF page 13','paper/PAPER_EXT.qmd:310–328; tbl-lp; fig-lp; Appendix A12']
files=[['primary_coefficients.csv','regimes_common_slope_sensitivity.csv'],['regimes_trend.csv','regimes_common_network.csv'],['expectations_irf.csv']]
scripts=['analysis/02_primary.R; analysis/06_regimes.R','analysis/06_regimes.R','analysis/05_expectations.R']
for i,finding in enumerate(study['findings']):
    register.append({**finding,'exact_manuscript_locator':locators[i], 'supporting_files':[str(ROOT/'results'/p) for p in files[i]],
        'producing_script':scripts[i], 'type':'conditional association' if i<2 else 'predictive specification comparison',
        'decision':'include with qualification','identification':'No causal identification asserted; shared media shocks, endogeneity and source composition remain.',
        'sample':'S1 January 2021–May 2026' if i != 1 else 'S3 April 2024–May 2026',
        'estimate':models[0] if i==0 else {'main':trend,'common_sources':common} if i==1 else lp,
        'definition_reference':'Eq8 for gap; Eq9b for main model; Eq10 for forward projections. See evidence metadata for canonical units and baseline.',
        'scope':'Saved extended-paper aggregates, original platform universe, quality-filtered. Vendor selection is not a representative census.'})
save(SITE/'private/claim-register.json', register)
save(SITE/'private/figure-register.json', [{
    'id':'FIG1','paper_locator':'Figure 1 / fig-overview / paper/PAPER_EXT.qmd:259',
    'type':'faithful selected-series adaptation','source':str(ROOT/'results/data_quality_series.csv'),
    'producer':'analysis/10_data_quality.R; analysis/12_exhibits.R',
    'series':['IAG_primary','pi_t'],'transforms':{'IAG_primary':'multiply by 100 to express percentage points','pi_t':'unchanged'},
    'sample':'2021-01 to 2026-05; S1 monthly','missing':'Jan–Mar 2024 null; paths break at missing months and April 2024 source boundary',
    'edition':'extended-2026-09-17','uncertainty':'descriptive observed series, no interval invented',
    'baseline':baseline['monthly'],'time_basis':'calendar record month; HICP reference month',
    'caption':'Selected series from Figure 1; primary sample only. Values before and after April 2024 are not harmonised.'}, {
    'id':'FIG2','type':'exact weighted-share transformation; later collection only',
    'source':str(ROOT/'results/data_quality_series.csv'),
    'transforms':{'share':'100 * (monthly baseline - IAG_primary)','pi_t':'unchanged'},
    'sample':'2024-04 to 2026-05; 26 observed months',
    'edition':'extended-2026-09-17','uncertainty':'observed series, not fitted trend; coverage composition may vary',
    'baseline':baseline['monthly'],'exports':['visibility-later.png','visibility-later-hr.png']
}])
print('Prepared 65 monthly periods (62 included), 4 model estimates, 3 expectation comparisons, and unchanged 32-page paper.')
