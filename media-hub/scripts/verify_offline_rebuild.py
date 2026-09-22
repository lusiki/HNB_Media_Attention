"""Rebuild from the source ZIP in a fresh directory with standard library only."""
from pathlib import Path
import tempfile,subprocess,zipfile,hashlib,json,sys,os
SITE=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='hnb-public-rebuild-') as temp:
    root=Path(temp)
    with zipfile.ZipFile(SITE/'dist/downloads/hnb-media-rendering-source.zip') as z:
        assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist());z.extractall(root)
    runner='''import sys,runpy
from pathlib import Path
root=Path.cwd().resolve()
def audit(event,args):
    if event.startswith('socket.'):raise RuntimeError('Network forbidden during offline rebuild')
    if event=='open' and isinstance(args[0],str):
        p=Path(args[0]).resolve()
        if p.suffix.lower() in {'.duckdb','.rds','.rdata'}:raise RuntimeError('Restricted data forbidden')
sys.addaudithook(audit)
sys.path.insert(0,str(root/'scripts'))
runpy.run_path(str(root/'scripts/build.py'),run_name='__main__')
'''
    (root/'run-isolated.py').write_text(runner,encoding='utf-8')
    env=os.environ.copy();env.pop('SITE_URL',None);env.pop('PYTHONPATH',None)
    result=subprocess.run([sys.executable,'-I','-S','run-isolated.py'],cwd=root,env=env,capture_output=True,text=True,check=True)
    hashes=lambda base:{p.relative_to(base).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in base.rglob('*') if p.is_file()}
    expected=hashes(SITE/'dist');actual=hashes(root/'dist');assert expected==actual,{'different':[k for k in expected if actual.get(k)!=expected[k]],'extra':set(actual)-set(expected)}
    assert (root/'hnb-media-publication.zip').read_bytes()==(SITE/'hnb-media-publication.zip').read_bytes()
    report={'passed':True,'files':len(actual),'byte_identical':True,'publication_zip_identical':True,'standard_library_only':True,'network_blocked_by_audit_hook':True,'restricted_data_types_blocked':True,'fresh_directory':True,'scope':'static site rendering from approved aggregates and pre-rendered assets; not restricted analysis or PDF authoring'}
    production_prefix='https://example.org/research/hnb-media'
    env['SITE_URL']=production_prefix
    subprocess.run([sys.executable,'-I','-S','run-isolated.py'],cwd=root,env=env,capture_output=True,text=True,check=True)
    assert f'href="{production_prefix}/"' in (root/'dist/index.html').read_text(encoding='utf-8')
    assert f'content="{production_prefix}/studies/inflation/"' in (root/'dist/studies/inflation/index.html').read_text(encoding='utf-8')
    assert json.loads((root/'dist/release-manifest.json').read_text(encoding='utf-8'))['build_parameters']['SITE_URL']==production_prefix
    report['simulated_https_path_prefix_metadata']=True
    (SITE/'qa/offline-rebuild-checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(result.stdout.strip());print('Offline rebuild is byte-identical to the candidate; simulated production-prefix metadata passed.')
