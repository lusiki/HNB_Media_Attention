"""Read-only author tools. Restricted outputs must be outside synchronized folders.

audit: weighted 200-publication development sample of unmatched screens.
concordance: bounded HTML reading file; no public or rendering-build dependency.
"""
from pathlib import Path
from collections import defaultdict,Counter
from html import escape
import argparse,csv,hashlib,json,random,re
SEED=20260922
def private_path(raw):
    p=Path(raw).resolve()
    if any(x.lower() in ['dropbox','onedrive','google drive','hnb_media_attention_release'] for x in p.parts):raise ValueError('Restricted outputs must remain outside synchronized/public directories')
    p.mkdir(parents=True,exist_ok=True);return p
def writecsv(path,rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def audit(con,out):
    query="""SELECT publication_key,body_hash,source_label,period,first_date,TITLE,FULL_TEXT,normalized_url
    FROM tagged WHERE period BETWEEN '2021-01' AND '2026-08' AND NOT
    (tag_prices OR tag_rates OR tag_currency OR tag_stability OR tag_lending OR tag_forecasts OR tag_governance OR tag_payments)
    ORDER BY publication_key"""
    records=con.execute(query).fetchall();assert len(records)==4118
    volumes=dict(con.execute("SELECT source_label,count(*) FROM media WHERE explicit_any AND period BETWEEN '2021-01' AND '2026-08' GROUP BY source_label").fetchall())
    strata=defaultdict(list)
    for r in records:
        volume='500plus' if volumes[r[2]]>=500 else '100to499' if volumes[r[2]]>=100 else 'under100'
        strata[('legacy' if r[3]<'2024-01' else 'api')+'|'+volume+'|'+('body' if (r[6] or '').strip() else 'no_body')].append(r)
    # Largest-remainder allocation after guaranteeing two or a census in tiny strata.
    allocation={k:min(2,len(v)) for k,v in strata.items()}
    remaining=200-sum(allocation.values());capacity={k:len(v)-allocation[k] for k,v in strata.items()};cap=sum(capacity.values())
    quotas={k:remaining*v/cap for k,v in capacity.items()}
    for k in strata:allocation[k]+=int(quotas[k])
    for k in sorted(strata,key=lambda k:(-(quotas[k]%1),k))[:200-sum(allocation.values())]:allocation[k]+=1
    rng=random.Random(SEED);sample=[];metadata=[]
    for k,frame in sorted(strata.items()):
        n=allocation[k];N=len(frame);metadata.append(dict(stratum=k,population=N,sample=n,inclusion_probability=n/N,weight=N/n))
        for r in sorted(rng.sample(frame,n),key=lambda r:r[0]):
            sample.append(dict(audit_id=f'U{len(sample)+1:03d}',stratum=k,stratum_N=N,stratum_n=n,inclusion_probability=n/N,weight=N/n,publication_key=r[0],exact_body_group=r[1],source=r[2],period=r[3],first_date=str(r[4]),title=r[5],body=r[6],url=r[7],reason='',candidate_theme='',reviewer='',note=''))
    assert len(sample)==200 and len({r['publication_key'] for r in sample})==200
    assert abs(sum(r['weight'] for r in sample)-4118)<1e-8
    writecsv(out/'unmatched-audit-200-private.csv',sample)
    manifest=dict(seed=SEED,population=4118,sample=200,strata=metadata,allocation='minimum two per nonempty stratum, then proportional largest remainder',source_group_substitution='full-window source volume: under100 / 100to499 / 500plus HNB publications',reason_codes=['missing_subject_family','incidental_HNB','foreign_bank_ambiguity','text_navigation_problem','insufficient_text','other_explained'],status='sample drawn; no labels assigned; development audit, not independent validation',weight_sum=sum(r['weight'] for r in sample),exact_body_groups_in_sample=len({r['exact_body_group'] for r in sample if r['body']}),uncertainty='Design-stratified estimates require completed labels; repeated exact bodies must not be treated as independent themes; report cluster-aware sensitivity.')
    (out/'audit-design.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:manifest[k] for k in ['population','sample','status','weight_sum','exact_body_groups_in_sample']}))
def concordance(con,out,args):
    if not args.term:raise ValueError('--term is required')
    from prepare_lexical_extensions import contexts
    cur=con.execute("""SELECT first_date,source_label,TITLE,FULL_TEXT FROM media WHERE explicit_any AND period BETWEEN ? AND ? AND (?='' OR source_label=?) AND (contains(lower(FULL_TEXT),lower(?)) OR contains(lower(TITLE),lower(?))) ORDER BY first_date,source_label LIMIT ?""",[args.start,args.end,args.source,args.source,args.term,args.term,args.limit])
    rows=cur.fetchall();html=['<!doctype html><html lang="hr"><meta charset="utf-8"><title>Privatna konkordancija</title><style>body{max-width:900px;margin:40px auto;font:17px/1.6 sans-serif}article{border-top:1px solid #ccc;padding:20px 0}p{white-space:pre-wrap}</style><h1>Privatna konkordancija</h1><p>Ograničen prikaz; nije slučajan uzorak. Ne objavljivati.</p>']
    for date,source,title,body in rows:
        text=contexts(title or '',body or '')[1] if args.context=='hnb' else body or ''
        if args.term.casefold() not in text.casefold():continue
        html.append('<article><h2>'+escape(title or '')+'</h2><small>'+escape(str(date)+' · '+source)+'</small><p>'+escape(text)+'</p></article>')
    html.append('</html>');(out/'concordance-private.html').write_text(''.join(html),encoding='utf-8');print('Private bounded concordance written; no text emitted to console.')
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--database',required=True);ap.add_argument('--output',required=True);ap.add_argument('--stage',choices=['audit','concordance'],required=True);ap.add_argument('--term');ap.add_argument('--start',default='2021-01');ap.add_argument('--end',default='2026-08');ap.add_argument('--source',default='');ap.add_argument('--context',choices=['hnb','whole'],default='hnb');ap.add_argument('--limit',type=int,default=50);args=ap.parse_args()
    if not 1<=args.limit<=200:ap.error('limit must be 1-200')
    import duckdb
    output=private_path(args.output);p=Path(args.database);before=(p.stat().st_size,p.stat().st_mtime_ns)
    with duckdb.connect(str(p),read_only=True) as con:
        if args.stage=='audit':audit(con,output)
        else:concordance(con,output,args)
    assert before==(p.stat().st_size,p.stat().st_mtime_ns)
if __name__=='__main__':main()
