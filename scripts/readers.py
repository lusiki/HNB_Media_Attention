"""Build standalone HTML readers from pre-rendered publication pages."""
from html import escape
import hashlib
import json
import shutil


def build_readers(site, dist):
    files = []
    template = (site / 'src/reader.html').read_text(encoding='utf-8')
    (dist / 'read').mkdir(exist_ok=True)
    shutil.copyfile(site / 'src/reader.css', dist / 'read/reader.css')
    files.append('read/reader.css')
    for name, title, language, lang, other, other_title in [
        ('brief', 'Two-page research brief', 'English', 'en', 'paper', 'Read the full paper'),
        ('paper', 'Full research paper', 'Croatian', 'hr', 'brief', 'Read the two-page brief'),
    ]:
        source = site / 'public/read' / name
        manifest = json.loads((source / 'pages.json').read_text(encoding='utf-8'))
        pdf = site / 'public/downloads' / f'hnb-attention-gap-{name}.pdf'
        if hashlib.sha256(pdf.read_bytes()).hexdigest() != manifest['pdf_sha256']:
            raise ValueError(f'{name} reader is stale. Run scripts/make_readers.py after updating its PDF.')
        sections = []
        count = len(manifest['pages'])
        for i, page in enumerate(manifest['pages'], 1):
            filename = f'page-{i:02}.webp'
            assert page['image'] == filename
            public_path = f'read/{name}/{filename}'
            (dist / public_path).parent.mkdir(exist_ok=True)
            shutil.copyfile(source / filename, dist / public_path)
            files.append(public_path)
            image_path = f'{name}/{filename}'
            loading = 'eager' if i == 1 else 'lazy'
            sections.append(f'''<section class="document-page" id="page-{i}" aria-labelledby="label-{i}">
              <div class="page-heading" lang="en"><h2 id="label-{i}">Page {i} of {count}</h2><a href="{image_path}">Open full-size page ↗</a></div>
              <img class="page-image" src="{image_path}" width="{page['width']}" height="{page['height']}" loading="{loading}" alt="{escape(title)} — page {i}. Selectable text follows below.">
              <details class="page-text"><summary lang="en">Read / copy page text</summary><div class="transcription">{escape(page['text'])}</div></details>
            </section>''')
        values = {'TITLE': title, 'COUNT': str(count), 'LANGUAGE': language, 'LANG': lang,
                  'NAME': name, 'OTHER': other, 'OTHER_TITLE': other_title,
                  'PAGE_LINKS': ''.join(f'<a href="#page-{i}">{i}</a>' for i in range(1, count + 1)),
                  'PAGES': '\n'.join(sections)}
        html = template
        for key, value in values.items():
            html = html.replace('@@' + key + '@@', value)
        assert '@@' not in html
        output = f'read/{name}.html'
        (dist / output).write_text(html, encoding='utf-8')
        files.append(output)
    return files
