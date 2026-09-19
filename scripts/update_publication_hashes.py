"""Refresh reviewed publication-asset fingerprints after deliberate authoring changes."""
from pathlib import Path
import hashlib,json

SITE=Path(__file__).resolve().parents[1]
PUBLIC=SITE/'public'
version=json.loads((PUBLIC/'data/inspection.json').read_text(encoding='utf-8'))['version']
files={}
for path in sorted(PUBLIC.rglob('*')):
    if not path.is_file():continue
    data=path.read_bytes()
    if path.suffix in {'.json','.csv','.txt'}:data=data.replace(b'\r\n',b'\n')
    files[path.relative_to(PUBLIC).as_posix()]=hashlib.sha256(data).hexdigest()
output={'version':version,'text_line_endings':'LF','files':files}
(SITE/'content/publication-input-hashes.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
print(f'Recorded {len(files)} reviewed publication inputs for {version}.')
