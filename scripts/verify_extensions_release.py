"""Release gates for aggregate extensions: exact files, arithmetic and public boundaries."""
from pathlib import Path
import csv,hashlib,json,sys,zipfile
ROOT=Path(__file__).resolve().parents[1];HUB=ROOT/'media-hub';DATA=HUB/'public/data/media'
sys.path.insert(0,str(HUB/'scripts'))
from verify_media_extensions import verify
from prepare_lexical_extensions import normalized,contexts,status
checks=verify(HUB,DATA)
d=json.loads((DATA/'lexical-extensions.json').read_text(encoding='utf-8'))
assert d['body_population']==d['pairable_n']==33100 and d['unavailable_context_n']==0
assert d['baseline_1_0_all_cells_reproduced'] and len(d['linkage'])==8
assert normalized(' A\n B ')==normalized('a b') and normalized('a\u00a0b')!='a b'
assert contexts('HNB objava','Cijene rastu. Druga rečenica.')[0]==''
assert 'Cijene' not in contexts('Drugi naslov','HNB govori. Cijene rastu.')[0]
assert [status(n,100) for n in [0,1,29,30]]==['zero','below_reporting_threshold','below_reporting_threshold','reported']
assert status(0,29)=='unavailable'
for r in d['linkage']:
    assert sum(r[k] for k in ['both_yes','whole_only','local_only','neither'])==r['pairable_n']
    assert r['local_only']==0 and r['whole_yes']==r['both_yes']+r['whole_only']
    assert abs(r['linkage']-r['both_yes']/r['whole_yes'])<1e-14
rows=list(csv.DictReader((DATA/'media-lexical-quarterly.csv').open(encoding='utf-8')))
assert len(rows)==len(d['quarterly'])==1472
assert len({(r['quarter'],r['kind'],r['term']) for r in rows})==1472
assert len({(r['kind'],r['term']) for r in rows})==64
for r,q in zip(rows,d['quarterly']):
    assert r['quarter']==q['quarter'] and int(r['count'])==q['count'] and int(r['denominator'])==q['denominator']
    assert 0<=q['count']<=q['denominator'] and q['status']==status(q['count'],q['denominator'])
    assert q['regime']==('legacy' if q['quarter']<'2024-Q1' else 'api')
    assert (q['coverage_state']=='complete')==(q['quarter']!='2026-Q3')
    if q['status'] in ['zero','reported']:assert abs(float(r['frequency'])-q['count']/q['denominator'])<1e-14
    else:assert r['frequency']=='' and q['frequency'] is None
m=json.loads((DATA/'lexical-extensions-manifest.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for k,v in m['files'].items():assert sha(DATA/k)==v,k
for k,v in m['inputs'].items():assert sha(DATA/k)==v,k
assert sha(HUB/'scripts/prepare_lexical_extensions.py')==m['script_sha256']
manifest=json.loads((HUB/'dist/release-manifest.json').read_text(encoding='utf-8'))
registry=json.loads((HUB/'content/releases.json').read_text(encoding='utf-8'))
assert manifest['presentation_version']==registry['presentation_version']
for name,h in manifest['files'].items():assert sha(HUB/'dist'/name)==h,name
with zipfile.ZipFile(HUB/'dist/downloads/hnb-media-rendering-source.zip') as z:
    assert all(not any(part in name.lower() for part in ['private/','qa/','.duckdb','.rds','.env','prepare_lexical']) for name in z.namelist())
    for name in z.namelist():
        if name.endswith(('.json','.csv','.html','.js','.py','.md','.txt')):
            text=z.read(name).decode('utf-8')
            assert 'C:/Users/' not in text and 'C:\\Users\\' not in text,name
artifacts=json.loads((HUB/'public/downloads/artifacts.json').read_text(encoding='utf-8'))
for a in artifacts:
    p=HUB/'public/downloads'/a['file'];assert p.stat().st_size==a['bytes'] and sha(p)==a['sha256'],a['file']
print(f'Extensions passed: {len(checks)} indicator checks, 8 four-cell bridges, 1,472 quarterly cells, missing/suppression fixtures, provenance, artifact hashes and rendering-source privacy.')
