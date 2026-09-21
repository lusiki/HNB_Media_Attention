"""Optional read-only lexical analysis of the already reviewed HNB_MEDIA cache.

Requires duckdb. Raw text is never written by this script. The public output
contains document frequencies and the exact, deliberately limited dictionary.
The publication build consumes the saved output and needs no database access.
"""
from pathlib import Path
from collections import Counter
import argparse, hashlib, json, re
import duckdb

ap = argparse.ArgumentParser()
ap.add_argument('--database', required=True)
ap.add_argument('--output', required=True)
args = ap.parse_args()
site = Path(__file__).resolve().parents[1]
definitions = json.loads((site/'public/data/media/subject-definitions.json').read_text(encoding='utf-8'))
terms = {
 'banka': r'ban(?:k|c)[a-zčćšđž]*', 'kredit': r'kredit[a-zčćšđž]*',
 'euro': r'eur(?:o|a|u|om|ima)?', 'kuna': r'kun(?:a|e|i|u|om|ama)',
 'inflacija': r'(?:inflacij|inflatorn)[a-zčćšđž]*', 'cijena': r'cijen[a-zčćšđž]*',
 'kamata': r'kamat[a-zčćšđž]*', 'rast': r'rast[a-zčćšđž]*',
 'guverner': r'guverner[a-zčćšđž]*', 'ESB / ECB': r'(?:esb|ecb)(?:-[a-z]+)?',
 'gospodarstvo': r'gospodarstv[a-zčćšđž]*', 'potrošač': r'potrošač[a-zčćšđž]*',
 'građanin': r'građan[a-zčćšđž]*', 'plaćanje': r'plaćanj[a-zčćšđž]*',
 'gotovina': r'gotovin[a-zčćšđž]*', 'depozit': r'depozit[a-zčćšđž]*',
 'nekretnina': r'nekretnin[a-zčćšđž]*', 'stabilnost': r'stabilno(?:st|sti|šću)',
 'rizik': r'rizi(?:k|c)[a-zčćšđž]*', 'nadzor': r'nadzor[a-zčćšđž]*',
 'prognoza': r'prognoz[a-zčćšđž]*', 'projekcija': r'projekcij[a-zčćšđž]*',
 'statistika': r'statisti(?:k|c|č)[a-zčćšđž]*', 'tečaj': r'tečaj[a-zčćšđž]*',
 'štednja': r'štednj[a-zčćšđž]*', 'dug': r'dug(?:a|u|om|ovi|ova|ove|ovima)?',
 'dohodak': r'doh(?:odak|otk[a-zčćšđž]*)', 'plaća': r'plać(?:a|e|i|u|om|ama)',
 'kućanstvo': r'kućanstv[a-zčćšđž]*', 'monetarna politika': r'monetarn[a-zčćšđž]*\s+politik[a-zčćšđž]*',
 'europodručje': r'(?:europodruč|eurozon)[a-zčćšđž]*',
 'novčanica': r'novčanic[a-zčćšđž]*', 'kovanica': r'kovanic[a-zčćšđž]*',
 'zaduživanje': r'zaduživ[a-zčćšđž]*', 'mjera': r'mjer(?:a|e|i|u|om|ama)',
 'tržište': r'tržišt[a-zčćšđž]*', 'likvidnost': r'likvidno(?:st|sti|šću)',
 'kapital': r'kapital[a-zčćšđž]*', 'odgovornost': r'odgovorno(?:st|sti|šću)',
 'mandat': r'mandat[a-zčćšđž]*', 'savjet': r'savjet[a-zčćšđž]*',
 'dionica': r'dionic[a-zčćšđž]*', 'obveznica': r'obveznic[a-zčćšđž]*',
 'Vlada': r'vlad(?:a|e|i|u|om)', 'Sabor': r'sabor[a-zčćšđž]*',
 'BDP': r'bdp(?:-[a-z]+)?', 'investicija': r'investicij[a-zčćšđž]*',
 'izvoz': r'izvoz[a-zčćšđž]*', 'uvoz': r'uvoz[a-zčćšđž]*',
 'naknada': r'naknad[a-zčćšđž]*', 'sanacija': r'sanacij[a-zčćšđž]*',
 'digitalni euro': r'digitaln[a-zčćšđž]*\s+eur[a-zčćšđž]*',
}
phrases = {
 'kamatna stopa': r'kamatn[a-zčćšđž]*\s+stop[a-zčćšđž]*',
 'financijska stabilnost': r'financijsk[a-zčćšđž]*\s+stabilno(?:st|sti|šću)',
 'uvođenje eura': r'uvođen[a-zčćšđž]*\s+eur[a-zčćšđž]*',
 'stambeni kredit': r'stamben[a-zčćšđž]*\s+kredit[a-zčćšđž]*',
 'gotovinski kredit': r'gotovinsk[a-zčćšđž]*\s+kredit[a-zčćšđž]*',
 'kupovna moć': r'kupovn[a-zčćšđž]*\s+mo[ćć][a-zčćšđž]*',
 'sukob interesa': r'sukob[a-zčćšđž]*\s+interes[a-zčćšđž]*',
 'zaštita potrošača': r'zaštit[a-zčćšđž]*\s+potrošač[a-zčćšđž]*',
 'platni promet': r'platn[a-zčćšđž]*\s+promet[a-zčćšđž]*',
 'monetarna politika': terms['monetarna politika'],
 'digitalni euro': terms['digitalni euro'],
 'kreditna sposobnost': r'kreditn[a-zčćšđž]*\s+sposobno(?:st|sti|šću)',
}
bounded = lambda p: re.compile(r'(?<!\w)(?:'+p+r')(?!\w)', re.I)
tp = {k:bounded(v) for k,v in terms.items()}
pp = {k:bounded(v) for k,v in phrases.items()}
mention = bounded(r'hnb(?:[-‑–](?:a|u|om|e)|[au])?|hrvatsk[a-zčćšđž]*\s+narodn[a-zčćšđž]*\s+ban[kc][a-zčćšđž]*|croatian\s+national\s+bank')
subjects = {d['id']:re.compile(d['pattern'],re.I) for d in definitions}
con = duckdb.connect(args.database,read_only=True)
records = con.execute("SELECT TITLE,FULL_TEXT,period,source_label FROM media WHERE explicit_any AND period BETWEEN '2021-01' AND '2026-08' ORDER BY first_date,source_label,normalized_url").fetchall()
assert len(records)==33235
unique = {}; empty=0
for title,body,period,source in records:
    # Match the existing RE2/SQL whitespace convention, including for NBSP.
    normalized = re.sub(r'[ \t\n\r\f\v]+',' ',(body or '').strip(' \t\n\r\f\v')).lower()
    if not normalized: empty+=1;continue
    key=hashlib.sha256(normalized.encode()).hexdigest()
    if key not in unique:unique[key]=(title or '',body)
assert len(unique)==33100 and empty==99
counts=Counter();phrase_counts=Counter();groups={k:Counter() for k in subjects};sizes=Counter()
assessable=0
for title,body in unique.values():
    pieces=re.split(r'(?<=[.!?])\s+(?=[A-ZČĆŠĐŽ0-9])|\n+',body)
    spans=([title] if mention.search(title) else [])+[s for s in pieces if mention.search(s)]
    context=' '.join(spans)
    if not context:continue
    assessable+=1
    lexical_context=mention.sub(' ',context)
    found={k for k,p in tp.items() if p.search(lexical_context)}
    counts.update(found);phrase_counts.update(k for k,p in pp.items() if p.search(lexical_context))
    # These sets are local-context screens, not the full-title/body tags in the overview.
    for k,p in subjects.items():
        if p.search(context):sizes[k]+=1;groups[k].update(found)
out={
 'edition':'2026-09-21.1','analysis_id':'HNB_MEDIA_LEXICAL_1.0',
 'period':'2021-01/2026-08','publications':len(records),'without_body':empty,
 'body_publications':len(records)-empty,'distinct_normalized_bodies':len(unique),
 'assessable_contexts':assessable,'context_missing':len(unique)-assessable,
 'method':{'unit':'one distinct lowercased whitespace-normalized cleaned body; earliest publication supplies title',
 'context':'explicit-HNB title and sentence-like body segments containing an explicit HNB mention; no neighbouring sentences',
 'sentence_split':r'(?<=[.!?])\s+(?=[A-ZČĆŠĐŽ0-9])|\n+',
 'count':'each selected dictionary entry at most once per distinct body',
 'dictionary':'curated inflection patterns; explicit HNB names removed before term counting; not full lemmatization or unrestricted vocabulary discovery',
 'groups':'overlapping subject patterns applied only to extracted mention context',
 'validation':'development checks only; independent human validation pending',
 'limitations':'sentence segmentation, inflection ambiguity, retained navigation, truncation and near-duplicate wording remain'},
 'term_patterns':terms,'phrase_patterns':phrases,
 'terms':dict(sorted(counts.items(),key=lambda x:(-x[1],x[0]))),'phrases':dict(sorted(phrase_counts.items(),key=lambda x:(-x[1],x[0]))),
 'groups':{k:{'n':sizes[k],'terms':dict(sorted(v.items(),key=lambda x:(-x[1],x[0])))} for k,v in groups.items()},
 'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
}
path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:out[k] for k in ['publications','distinct_normalized_bodies','assessable_contexts','context_missing','terms','phrases']},ensure_ascii=False,indent=2))
