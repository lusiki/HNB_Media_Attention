"""Compose the independently verified inflation page and media hub for Pages."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / 'media-hub'
OUT = ROOT / 'site-dist'
base = os.environ.get('SITE_URL', 'https://lusiki.github.io/HNB_Media_Attention').rstrip('/')
subprocess.run([sys.executable, str(HUB / 'scripts/build.py')], cwd=HUB,
               env={**os.environ, 'SITE_URL': base + '/media'}, check=True)

expected = {}
for source, prefix in [(ROOT, ''), (HUB, 'media/')]:
    files = json.loads((source / 'qa/build-manifest.json').read_text(encoding='utf-8'))['files']
    actual = {p.relative_to(source / 'dist').as_posix() for p in (source / 'dist').rglob('*') if p.is_file()}
    assert actual == set(files), f'Unexpected public files in {source.name}'
    for name, digest in files.items():
        data = (source / 'dist' / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == digest, name
        expected[prefix + name] = digest
        dest = OUT / (prefix + name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / 'dist' / name, dest)

actual = {p.relative_to(OUT).as_posix() for p in OUT.rglob('*') if p.is_file()}
assert actual == set(expected), 'Unexpected files in composed site'
for name, digest in expected.items():
    assert hashlib.sha256((OUT / name).read_bytes()).hexdigest() == digest, name
print(f'Verified {len(expected)} public files: existing site at /; media hub at /media/.')
