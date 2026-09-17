"""Render committed PDFs into browser-readable pages; run after replacing a PDF."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from PIL import Image
from pypdf import PdfReader

SITE = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--pdftoppm', default=shutil.which('pdftoppm'), help='Path to the Poppler pdftoppm executable')
args = parser.parse_args()
if not args.pdftoppm:
    parser.error('Install Poppler or supply --pdftoppm PATH')

for name in ['brief', 'paper']:
    pdf = SITE / 'public/downloads' / f'hnb-attention-gap-{name}.pdf'
    output = SITE / 'public/read' / name
    output.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(pdf)
    pages = []
    with tempfile.TemporaryDirectory(prefix='hnb-reader-') as scratch:
        prefix = Path(scratch) / 'page'
        subprocess.run([args.pdftoppm, '-scale-to', '2200', '-png', str(pdf), str(prefix)], check=True)
        images = sorted(Path(scratch).glob('page-*.png'), key=lambda p: int(p.stem.split('-')[-1]))
        if len(images) != len(reader.pages):
            raise ValueError(f'Incomplete rendering: {name}')
        for i, (image, page) in enumerate(zip(images, reader.pages), 1):
            filename = f'page-{i:02}.webp'
            with Image.open(image) as rendered:
                rendered.convert('RGB').save(output / filename, 'WEBP', quality=88, method=6)
                width, height = rendered.size
            pages.append({'image': filename, 'width': width, 'height': height,
                          'text': page.extract_text() or ''})
    manifest = {'pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(), 'pages': pages}
    (output / 'pages.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Rendered {len(pages)} {name} pages for the on-site reader.')
