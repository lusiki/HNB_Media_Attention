"""Optional read-only lexical 1.1 analysis; emits aggregate tables, never text or record keys.

Reuses the exact 1.0 dictionary/context from the recovered publication source.
The bridge deliberately uses BODY-ONLY contexts to make containment testable.
Quarterly vocabulary retains 1.0's explicit-mention title plus body context.
"""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,csv,hashlib,json,re

ANALYSIS='HNB_MEDIA_LEXICAL_1.1'
MENTION=r'hnb(?:[-‑–](?:a|u|om|e)|[au])?|hrvatsk[a-zčćšđž]*\s+narodn[a-zčćšđž]*\s+ban[kc][a-zčćšđž]*|croatian\s+national\s+bank'
SPLIT=r'(?<=[.!?])\s+(?=[A-ZČĆŠĐŽ0-9])|\n+'
mention=re.compile(r'(?<!\w)(?:'+MENTION+r')(?!\w)',re.I)
def normalized(body):return re.sub(r'[ \t\n\r\f\v]+',' ',(body or '').strip(' \t\n\r\f\v')).lower()
def contexts(title,body):
    local=' '.join(s for s in re.split(SPLIT,body) if mention.search(s))
    return local,' '.join(([title] if mention.search(title) else [])+([local] if local else []))
def status(n,denom):return 'unavailable' if denom<30 else 'zero' if n==0 else 'below_reporting_threshold' if n<30 else 'reported'
def csvwrite(path,rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--database',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
    import duckdb
    site=Path(__file__).resolve().parents[1];data=site/'public/data/media'
    old=json.loads((data/'report-language.json').read_text(encoding='utf-8'))
    definitions=json.loads((data/'subject-definitions.json').read_text(encoding='utf-8'))
    assert old['analysis_id']=='HNB_MEDIA_LEXICAL_1.0' and old['method']['sentence_split']==SPLIT
    terms={kind:{k:re.compile(r'(?<!\w)(?:'+v+r')(?!\w)',re.I) for k,v in old[kind+'_patterns'].items()} for kind in ['term','phrase']}
    subjects={d['id']:re.compile(d['pattern'],re.I) for d in definitions}
    database=Path(args.database);before=(database.stat().st_size,database.stat().st_mtime_ns)
    with duckdb.connect(str(database),read_only=True) as con:
        records=con.execute("SELECT TITLE,FULL_TEXT,period FROM media WHERE explicit_any AND period BETWEEN '2021-01' AND '2026-08' ORDER BY first_date,source_label,normalized_url").fetchall()
    assert len(records)==33235
    unique={};quarterly=defaultdict(dict);empty=0
    for title,body,period in records:
        norm=normalized(body)
        if not norm:empty+=1;continue
        key=hashlib.sha256(norm.encode()).digest();title=title or ''
        unique.setdefault(key,(title,body));quarter=period[:4]+'-Q'+str((int(period[5:])-1)//3+1)
        quarterly[quarter].setdefault(key,(title,body))
    assert len(unique)==33100 and empty==99
    counts={k:Counter() for k in subjects};unavailable=title_only=0;baseline={k:Counter() for k in terms};baseline_groups={k:Counter() for k in subjects};sizes=Counter()
    for title,body in unique.values():
        local,context=contexts(title,body)
        assert context
        found={kind:{k for k,p in pats.items() if p.search(mention.sub(' ',context))} for kind,pats in terms.items()}
        for kind in terms:baseline[kind].update(found[kind])
        for k,p in subjects.items():
            if p.search(context):sizes[k]+=1;baseline_groups[k].update(found['term'])
        if not local:
            unavailable+=1;title_only+=bool(mention.search(title));continue
        for k,p in subjects.items():
            whole=bool(p.search(body));near=bool(p.search(local));counts[k][(whole,near)]+=1
    # Independently reproduce every previously published 1.0 vocabulary cell.
    assert dict(baseline['term'])==old['terms'] and dict(baseline['phrase'])==old['phrases']
    for k in subjects:assert sizes[k]==old['groups'][k]['n'] and dict(baseline_groups[k])==old['groups'][k]['terms']
    rows=[]
    for d in definitions:
        c=counts[d['id']];pairable=sum(c.values());whole=c[(True,True)]+c[(True,False)]
        assert c[(False,True)]==0 and pairable+unavailable==len(unique)
        rows.append(dict(analysis_id=ANALYSIS,subject_id=d['id'],label_hr=d['label_hr'],label_en=d['label_en'],period='2021-01/2026-08',body_population=len(unique),pairable_n=pairable,unavailable_context_n=unavailable,title_only_context_n=title_only,both_yes=c[(True,True)],whole_only=c[(True,False)],local_only=c[(False,True)],neither=c[(False,False)],whole_yes=whole,linkage=c[(True,True)]/whole if whole else None,pairable_coverage=pairable/len(unique),whole_corpus_coverage=whole/len(unique),unit='distinct_body',local_context='body_only_explicit_HNB_segments',validation='exploratory_not_independently_validated'))
    qrows=[]
    for q,bodies in sorted(quarterly.items()):
        den=0;counts_q={k:Counter() for k in terms}
        for title,body in bodies.values():
            _,context=contexts(title,body)
            if not context:continue
            den+=1;text=mention.sub(' ',context)
            for kind,pats in terms.items():counts_q[kind].update(k for k,p in pats.items() if p.search(text))
        for kind,pats in terms.items():
            for term in pats:
                n=counts_q[kind][term];state=status(n,den)
                qrows.append(dict(analysis_id=ANALYSIS,dictionary_id='HNB_MEDIA_LEXICAL_1.0',quarter=q,coverage_state='partial_July_August' if q=='2026-Q3' else 'complete',regime='legacy' if q<'2024-Q1' else 'api',kind=kind,term=term,count=n,denominator=den,frequency=n/den if state in ['reported','zero'] else None,status=state,unit='distinct_body_within_quarter',context='explicit_HNB_title_and_body_segments'))
    output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    csvwrite(output/'media-subject-linkage.csv',rows);csvwrite(output/'media-lexical-quarterly.csv',qrows)
    result=dict(analysis_id=ANALYSIS,data_version=old['edition'],period=old['period'],body_population=len(unique),without_body=empty,body_publications=len(records)-empty,pairable_n=len(unique)-unavailable,unavailable_context_n=unavailable,title_only_context_n=title_only,last_complete_quarter='2026-Q2',baseline_1_0_all_cells_reproduced=True,terms=52,phrases=12,reporting_threshold=30,linkage=rows,quarterly=qrows,method=dict(bridge='Same distinct bodies; body-only whole and local screens, excluding unavailable local-body contexts from both sides. Titles are not part of the bridge.',quarterly='Original 1.0 explicit-HNB title plus body segments; one contribution per distinct body per quarter; earliest within-quarter title. Whole-period counts are separate sets.',normalization='Lowercase and ASCII whitespace as in 1.0',sentence_split=SPLIT,mention_pattern=MENTION,validation='Development checks only; independent human validation and unmatched-screen audit pending.',suppression='N<30: no rate; 0<count<30: no rate; true zero stays zero. Partial 2026 Q3 excluded from complete-quarter comparisons.'))
    (output/'lexical-extensions.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    manifest=dict(analysis_id=ANALYSIS,baseline_script_sha256=old['script_sha256'],script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),inputs={n:hashlib.sha256((data/n).read_bytes()).hexdigest() for n in ['report-language.json','subject-definitions.json']},files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir()) if p.name in ['media-subject-linkage.csv','media-lexical-quarterly.csv','lexical-extensions.json']},cache_opened_read_only=True,cache_size_mtime_unchanged=before==(database.stat().st_size,database.stat().st_mtime_ns))
    assert manifest['cache_size_mtime_unchanged']
    (output/'lexical-extensions-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['linkage','quarterly','method']}));print('Linkage rows:',len(rows),'quarterly cells:',len(qrows))
if __name__=='__main__':main()
