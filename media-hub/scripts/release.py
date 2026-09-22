"""Exact public allowlist, deterministic rendering source ZIP and publication bundle."""
from pathlib import Path
import json,hashlib,zipfile,os

def sha(blob):return hashlib.sha256(blob).hexdigest()
def writezip(path,files):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,blob in sorted(files.items()):
            info=zipfile.ZipInfo(name,(2026,9,21,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,blob)

def finalize(site,dist,allowlist):
    allow=set(allowlist);assert len(allow)==len(allowlist),'Duplicate allowlist entries'
    registry=json.loads((site/'content/releases.json').read_text(encoding='utf-8'))
    scripts=['build.py','charts.py','inspection_components.py','media_page.py','media_chart.py','media_content.py','media_extensions_view.py','legacy_context.py','release.py','report_cards.py','lexical_view.py','event_view.py']
    src=['index.html','hr.html','styles.css','charts.js','app.js','media.css','media.js','legacy-links.js','lexical.js','studies/inflation/index.html','studies/inflation/hr.html']
    inputs={}
    for name in scripts:inputs['scripts/'+name]=(site/'scripts'/name).read_bytes()
    for name in src:inputs['src/'+name]=(site/'src'/name).read_bytes()
    for name in ['study.json','releases.json','rebuild-info.json']:inputs['content/'+name]=(site/'content'/name).read_bytes()
    for name in sorted(allow):
        p=site/'public'/name
        if p.is_file():inputs['public/'+name]=p.read_bytes()
    readme='''# Public rendering package

Requires Python 3.10+ standard library only. Run `python scripts/build.py` from this directory. It creates `dist/`, an exact public ZIP, and QA build hashes without network access or a database.

This package rebuilds the static site from fixed aggregate tables and already rendered publication assets. It does not regenerate the PDFs or article-level analysis. Those require authoring dependencies or authorized access to the restricted source respectively. It includes no vendor article text, identifiers, private paths, manuscript PDF, or keys.

Data and method editions differ between the broad HNB_MEDIA corpus and the frozen inflation study. See content/releases.json. The source snapshot is identified by the hashes in the release manifest; the originating working tree was dirty and is not reproducible from its base commit alone.

With SITE_URL unset, output is a local candidate. For a separately authorized deployment, set SITE_URL to the real HTTPS directory and rebuild. Host the contents of dist, preserving directories. No deployment occurs in this script.

The public URL is recorded in content/releases.json. No DOI, author sign-off or open redistribution license is asserted. See public/downloads/media-reuse.txt. Do not infer rights to underlying articles from the presence of aggregates.
'''
    inputs['README.md']=readme.encode('utf-8')
    package='downloads/hnb-media-rendering-source.zip';writezip(dist/package,inputs);allow.add(package)
    fingerprint=sha(json.dumps({k:sha(v) for k,v in sorted(inputs.items())},sort_keys=True).encode())
    payload={name:sha((dist/name).read_bytes()) for name in sorted(allow)}
    manifest={'schema_version':'1.0','presentation_version':registry['presentation_version'],'status':registry['status'],'date':registry['presentation_version'][:10],'canonical_url':registry['canonical_url'],'doi':registry['doi'],'contact':registry['contact'],'studies':registry['studies'],'source_identity':{'kind':'sha256 of exact rendering-input map','sha256':fingerprint,'base_commit':'621d509e62aabfffb3eb7c63ec8b9639422f3764','working_tree_was_dirty':True,'base_commit_alone_reproduces_release':False},'rebuild_boundary':'offline static rendering from aggregates and pre-rendered publications; restricted analysis and PDF authoring not reproduced','hash_scope':'payload files; manifest and checksums omitted to prevent circular hashes','files':payload}
    manifest['canonical_url']=(os.environ.get('SITE_URL') or registry['canonical_url'] or '').rstrip('/') or None
    manifest['build_parameters']={'SITE_URL':manifest['canonical_url']}
    manifest['source_package']={'file':package,'format':'zip','bytes':(dist/package).stat().st_size,'sha256':payload[package]}
    (dist/'release-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');allow.add('release-manifest.json')
    sums={name:sha((dist/name).read_bytes()) for name in sorted(allow)}
    (dist/'checksums.sha256').write_text(''.join(f'{v}  {k}\n' for k,v in sums.items()),encoding='utf-8');allow.add('checksums.sha256')
    actual={p.relative_to(dist).as_posix() for p in dist.rglob('*') if p.is_file()}
    if actual!=allow:raise ValueError(f'Public allowlist mismatch: extra {actual-allow}; missing {allow-actual}')
    final={name:sha((dist/name).read_bytes()) for name in sorted(allow)}
    (site/'qa').mkdir(exist_ok=True)
    (site/'qa/build-manifest.json').write_text(json.dumps({'files':final,'source_identity':fingerprint,'status':registry['status']},indent=2)+'\n',encoding='utf-8')
    bundle=site/'hnb-media-publication.zip';writezip(bundle,{name:(dist/name).read_bytes() for name in sorted(allow)})
    (site/'hnb-media-publication.zip.sha256').write_text(sha(bundle.read_bytes())+'  hnb-media-publication.zip\n',encoding='utf-8')
    print(f'Built {len(allow)} exactly allowlisted files; public bundle and offline rendering source package ready.')
