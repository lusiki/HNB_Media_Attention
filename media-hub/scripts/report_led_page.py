"""Build the bilingual, report-led media landing page from published aggregates."""
from pathlib import Path
from html import escape as esc
import argparse
import json
import shutil
from report_led_insights import components, source_comparison, annual_subjects, quarterly_words
from report_led_publications import specialist_study
from report_led_findings import finding_carousel

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PUBLIC = ROOT / 'public'
D = json.loads((PUBLIC / 'data/media/media.json').read_text(encoding='utf-8'))
L = json.loads((PUBLIC / 'data/media/report-language.json').read_text(encoding='utf-8'))
E = json.loads((PUBLIC / 'data/media/lexical-extensions.json').read_text(encoding='utf-8'))
S = D['summary']
TOTAL = S['hnb_publications']
TEXTS = L['distinct_normalized_bodies']
MONTHS = [r for r in D['monthly'] if '2024-01' <= r['period'] <= S['last_full_period']]
POOLED = next(r for r in D['extensions']['concentration'] if r['period_id'] == 'pooled' and r['scope'] == 'all')
MONTH_NAMES = {
    'hr': ['siječanj', 'veljača', 'ožujak', 'travanj', 'svibanj', 'lipanj', 'srpanj', 'kolovoz', 'rujan', 'listopad', 'studeni', 'prosinac'],
    'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
}
TRANSLATIONS = {
    'banka': 'bank', 'euro': 'euro', 'guverner': 'governor', 'rast': 'growth', 'kuna': 'kuna', 'građanin': 'citizen',
    'uvođenje eura': 'euro adoption', 'kamatna stopa': 'interest rate', 'monetarna politika': 'monetary policy',
    'stambeni kredit': 'housing loan', 'financijska stabilnost': 'financial stability', 'zaštita potrošača': 'consumer protection',
}


def fmt(value, lang, decimals=0):
    text = f'{value:,.{decimals}f}'
    return text.translate(str.maketrans({',': '.', '.': ','})) if lang == 'hr' else text


def month(period, lang):
    year, m = period.split('-')
    return MONTH_NAMES[lang][int(m)-1] + ' ' + year + ('.' if lang == 'hr' else '')


def line_chart(lang, narrow=False):
    """A single monthly series, with the peak and latest observation labelled."""
    width, height = (420, 256) if narrow else (1020, 256)
    left, right, top, bottom = (46, 44, 36, 34) if narrow else (46, 70, 36, 34)
    x = lambda i: left + i * (width-left-right) / (len(MONTHS)-1)
    y = lambda v: top + (height-top-bottom)*(1-v/1100)
    points = ' '.join(f'{x(i):.2f},{y(r["hnb_count"]):.2f}' for i, r in enumerate(MONTHS))
    peak = max(range(len(MONTHS)), key=lambda i: MONTHS[i]['hnb_count'])
    peak_text = fmt(MONTHS[peak]['hnb_count'], lang) + ' · ' + month(MONTHS[peak]['period'], lang)
    last_text = fmt(MONTHS[-1]['hnb_count'], lang)
    label = 'Mjesečni broj objava koje spominju HNB, od siječnja 2024. do kolovoza 2026.' if lang == 'hr' else 'Monthly publications mentioning HNB, January 2024 to August 2026.'
    suffix = 'narrow' if narrow else 'wide'
    svg = f'<svg viewBox="0 0 {width} {height}" role="img" aria-labelledby="trend-title-{suffix} trend-description-{suffix}"><title id="trend-title-{suffix}">{label}</title><desc id="trend-description-{suffix}">{esc(peak_text)}; {esc(month(MONTHS[-1]["period"],lang))}: {last_text}.</desc><defs><linearGradient id="area-fill-{suffix}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#2455c7" stop-opacity=".16"/><stop offset="100%" stop-color="#2455c7" stop-opacity=".01"/></linearGradient></defs>'
    for value in [0, 500, 1000]:
        svg += f'<line x1="{left}" x2="{width-right}" y1="{y(value)}" y2="{y(value)}" class="gridline"/><text x="{left-12}" y="{y(value)+4}" text-anchor="end" class="axis">{fmt(value,lang)}</text>'
    svg += f'<polygon points="{left},{y(0)} {points} {width-right},{y(0)}" fill="url(#area-fill-{suffix})"/><polyline points="{points}" class="trend-line"/>'
    for i, r in enumerate(MONTHS):
        if r['period'].endswith('-01'):
            svg += f'<text x="{x(i)}" y="{height-8}" class="axis">{r["period"][:4]}</text>'
        svg += f'<circle class="month-hit" data-month="{i}" cx="{x(i)}" cy="{y(r["hnb_count"])}" r="11"><title>{esc(month(r["period"],lang))} · {r["hnb_count"]}</title></circle>'
    svg += f'<circle cx="{x(peak)}" cy="{y(MONTHS[peak]["hnb_count"])}" r="4" class="peak-point"/><text x="{x(peak)-10}" y="{y(MONTHS[peak]["hnb_count"])-17}" text-anchor="end" class="peak-label">{peak_text}</text>'
    svg += f'<circle cx="{x(len(MONTHS)-1)}" cy="{y(MONTHS[-1]["hnb_count"])}" r="5" class="latest-point"/><text x="{x(len(MONTHS)-1)+13}" y="{y(MONTHS[-1]["hnb_count"])+5}" class="latest-label">{last_text}</text>'
    svg += '<circle r="5" class="inspection-point" visibility="hidden"/></svg>'
    return svg


def bars(rows, denominator, lang, variant=''):
    out = f'<ol class="bars {variant}">'
    maximum = max(v for _, v in rows)
    for label, value in rows:
        out += f'<li><div class="bar-label"><span>{esc(label)}</span><strong>{fmt(value/denominator*100,lang,1)}<small>%</small></strong></div><div class="bar-track" aria-hidden="true"><span style="width:{100*value/maximum:.5f}%"></span></div><span class="sr-only">{fmt(value,lang)} / {fmt(denominator,lang)}</span></li>'
    return out + '</ol>'


def page(lang, production=False, site_url='', presentation_version=''):
    hr = lang == 'hr'
    t = lambda cr, en: cr if hr else en
    n = lambda v, d=0: fmt(v,lang,d)
    home = ('hr.html' if hr else 'index.html') if production else ('index.html' if hr else 'en.html')
    other = ('index.html' if hr else 'hr.html') if production else ('en.html' if hr else 'index.html')
    insight = components(D, E, lang, fmt)
    ranking, _ = source_comparison(D, lang, fmt)
    overview = 'downloads/hnb-u-medijskom-prostoru'
    language = 'downloads/hnb-od-rijeci-do-javnih-pitanja'
    labels = {r['id']:r['label_'+lang] for r in D['subject_definitions']}
    subjects = sorted([(labels[k],v) for k,v in S['subject_counts'].items()],key=lambda x:-x[1])[:5]
    terms = sorted(L['terms'].items(),key=lambda x:-x[1])[:6]
    phrases = sorted(L['phrases'].items(),key=lambda x:-x[1])[:6]
    translated = lambda rows: [(k if hr else TRANSLATIONS.get(k,k),v) for k,v in rows]
    current = D['extensions']['latest']['current']
    prior = next(r for r in D['extensions']['latest']['comparisons'] if r['comparison']=='year_ago')
    trend_table = ''.join(f'<tr><th scope="row">{esc(month(r["period"],lang))}</th><td>{r["hnb_count"]}</td></tr>' for r in MONTHS)
    report_cards = ''
    for number,stem,title,description,pages in [
        ('01','hnb-u-medijskom-prostoru','HNB u medijskom prostoru',t('Koliko se HNB spominje, gdje se pojavljuje i uz koje teme.','How often HNB appears, which outlets cover it and which subjects accompany it.'),16),
        ('02','hnb-od-rijeci-do-javnih-pitanja','HNB: od riječi do javnih pitanja',t('Riječi i izrazi koji povezuju HNB sa svakodnevnim financijama i javnim pitanjima.','The words and phrases connecting HNB with everyday finance and public issues.'),14),
    ]:
        report_cards += f'''<article class="report"><a class="report-cover" href="downloads/{stem}.html" aria-label="{esc(title)}"><img src="downloads/{stem}.webp" width="420" height="594" loading="lazy" alt="{t('Naslovnica','Cover')}: {esc(title)}"></a><div><p class="eyebrow">{t('Izvještaj','Report')} {number} <span>· {pages} {t('stranica','pages')} · {t('hrvatski','Croatian')}</span></p><h3>{title}</h3><p>{description}</p><div class="report-actions"><a class="button" href="downloads/{stem}.pdf" download>PDF ↓</a><a href="downloads/{stem}.html">{t('Čitajte online','Read online')} ↗</a></div></div></article>'''
    payload = json.dumps({'months':[{'period':r['period'],'label':month(r['period'],lang),'count':r['hnb_count']} for r in MONTHS], 'quarters':insight['quarters']},ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    html = f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="author" content="Luka Sikić"><title>{t('HNB u hrvatskim medijima','HNB in Croatian media')} · {t('Novi prikaz','New page preview')}</title><meta name="description" content="{t('Odabrani pokazatelji iz dva izvještaja o medijskoj prisutnosti HNB-a.','Selected findings from two reports on HNB’s media presence.')}"><link rel="stylesheet" href="styles.css"><script src="app.js" defer></script></head>
<body><a class="skip" href="#main">{t('Preskoči na sadržaj','Skip to content')}</a>
<header class="masthead wrap"><a class="brand" href="{home}"><span class="brand-symbol" aria-hidden="true">H</span><span>HNB <span class="brand-divider">/</span> {t('MEDIJSKI PREGLED','MEDIA REVIEW')}</span></a><div class="masthead-right"><span class="preview-label">{t('Pregled prijedloga','Page preview')}</span><a class="language" href="{other}" lang="{t('en','hr')}">{t('English','Hrvatski')} ↗</a></div></header>
<main id="main"><span id="hnb-pregled"></span>
<section class="hero wrap" aria-labelledby="page-title"><div class="hero-copy"><p class="eyebrow"><span class="small-rule"></span>{t('Neovisni pregled · 2021. – 2026.','Independent review · 2021–2026')}</p><h1 id="page-title">{t('HNB u hrvatskim<br>medijima.','HNB in<br>Croatian media.')}</h1><p class="hero-intro">{t('Koliko se spominje. Gdje se pojavljuje.<br>Koje ga riječi prate.','How often it appears. Where it is covered.<br>Which words accompany it.')}</p><p class="hero-description">{t('Odabrani nalazi iz dva izvještaja o medijskoj prisutnosti Hrvatske narodne banke.','Selected findings from two reports on the media presence of the Croatian National Bank.')}</p><div class="author-byline"><span>{t("Autor pregleda", "Author")}</span><a href="https://www.lukasikic.info/" rel="author">Luka Sikić</a><a class="author-contact" href="mailto:luka.sikic@unicath.hr">{t("Kontakt", "Contact")} ↗</a></div><div class="hero-actions"><a class="button" href="#prisutnost">{t('Pogledajte nalaze','Explore the findings')} <span>↓</span></a><a class="text-link" href="#publikacije">{t('Dva izvještaja','The two reports')} ↗</a></div></div>
{finding_carousel(D, L, lang, fmt)}
<div class="scope-facts"><div><strong>{n(TOTAL)}</strong><span>{t('objava koje spominju HNB','publications mentioning HNB')}</span></div><div><strong>{n(S['outlets'])}</strong><span>{t('medijskih izvora','media sources')}</span></div><div><strong>68</strong><span>{t('mjeseci u pregledu','months covered')}</span></div><p>{t('Siječanj 2021. – kolovoz 2026.','January 2021 – August 2026')}</p></div></section>

<span id="vidljivost"></span><section class="section wrap" id="prisutnost" aria-labelledby="trend-heading"><div class="section-heading"><div><p class="eyebrow">01 <span>—</span> {t('Prisutnost kroz vrijeme','Presence over time')}</p><h2 id="trend-heading">{t('Kolovoz:','August:')} {n(current['hnb_count'])} {t('objava.','publications.')}</h2></div><div class="latest-comparison"><strong>{n(prior['hnb_count_change'],1)}%</strong><span>{t('prema kolovozu 2025.','versus August 2025')}<br>{n(prior['hnb_count'])} → {n(current['hnb_count'])} {t('objava','publications')}</span></div></div>
<figure class="trend-panel"><figcaption><span>{t('Mjesečni broj objava koje spominju HNB','Monthly publications mentioning HNB')}</span><span>{t('Siječanj 2024. – kolovoz 2026.','January 2024 – August 2026')}</span></figcaption><div class="chart-container"><div class="chart-wide">{line_chart(lang)}</div><div class="chart-narrow">{line_chart(lang,True)}</div></div><div class="trend-inspector" hidden><label for="month-range">{t('Pregledajte mjesec','Inspect a month')}</label><input id="month-range" type="range" min="0" max="{len(MONTHS)-1}" value="{len(MONTHS)-1}" aria-valuetext="{esc(month(MONTHS[-1]['period'],lang))}: {MONTHS[-1]['hnb_count']}"><output id="month-reading" for="month-range">{esc(month(MONTHS[-1]['period'],lang))} <strong>{n(current['hnb_count'])}</strong></output></div><div class="sr-only"><table><caption>{t('Brojčane vrijednosti grafikona','Chart values')}</caption><thead><tr><th scope="col">{t('Mjesec','Month')}</th><th scope="col">{t('Objave','Publications')}</th></tr></thead><tbody>{trend_table}</tbody></table></div></figure>
{insight['headline']}
<p class="report-source"><a href="{overview}.html#stranica-4">{t('HNB u medijskom prostoru','Media presence report')} <span>· {t('str. 4–5','pp. 4–5')} ↗</span></a></p></section>

<span id="teme"></span><section class="content-section" id="sadrzaj" aria-labelledby="content-heading"><div class="wrap"><div class="section-heading"><div><p class="eyebrow">02 <span>—</span> {t('Sadržaj medijske prisutnosti','The content of coverage')}</p><h2 id="content-heading">{t('Od kredita do javnih pitanja.','From credit to public issues.')}</h2></div><p class="section-intro">{t('Prvi izvještaj pokazuje teme objava.<br>Drugi približava riječi uz HNB.','The first report maps subjects in publications.<br>The second looks at the words around HNB.')}</p></div>
<div class="content-grid"><article class="content-panel"><p class="eyebrow">{t('Teme u objavama','Subjects in publications')}</p><h3>{t('Krediti, euro i plaćanja<br>na vrhu su pregleda.','Lending, the euro and payments<br>lead the subject overview.')}</h3><p class="panel-caption">{t('Pet vodećih tematskih skupova · udio u objavama','Five leading subject screens · share of publications')}</p>{bars(subjects,TOTAL,lang)}<p class="small">{t('Riječi u naslovu i tekstu. Ista objava može povezivati više tema.','Words in titles and bodies. A publication can match several subjects.')}</p><a class="report-source" href="{overview}.html#stranica-6">{t('Medijski pregled','Media presence report')} <span>· {t('str. 6','p. 6')} ↗</span></a></article>
<article class="content-panel language-panel"><p class="eyebrow">{t('Rječnik uz HNB','Vocabulary around HNB')}</p><h3>{t('Banka. Euro. Guverner.<br>Riječi otkrivaju sadržaj.','Bank. Euro. Governor.<br>Words reveal the context.')}</h3><div class="vocabulary-controls" hidden role="tablist" aria-label="{t('Odaberite prikaz rječnika','Choose vocabulary view')}"><button role="tab" id="words-tab" aria-controls="words-panel" aria-selected="true" tabindex="0">{t('Riječi','Words')}</button><button role="tab" id="phrases-tab" aria-controls="phrases-panel" aria-selected="false" tabindex="-1">{t('Izrazi','Phrases')}</button></div><div id="words-panel" class="vocabulary-panel" role="tabpanel" aria-labelledby="words-tab" tabindex="0"><p class="panel-caption">{t('Šest vodećih praćenih riječi · udio u tekstovima','Six leading tracked words · share of texts')}</p>{bars(translated(terms),TEXTS,lang,'copper')}</div><div id="phrases-panel" class="vocabulary-panel" role="tabpanel" aria-labelledby="phrases-tab" tabindex="0"><p class="panel-caption">{t('Šest vodećih praćenih izraza · udio u tekstovima','Six leading tracked phrases · share of texts')}</p>{bars(translated(phrases),TEXTS,lang,'copper')}</div><p class="small">{t('U naslovima i dijelovima teksta koji spominju HNB · 33.100 različitih tekstova.','In titles and text passages mentioning HNB · 33,100 distinct texts. Croatian terms are translated here.')}</p><a class="report-source" href="{language}.html#stranica-3">{t('Od riječi do javnih pitanja','Language and public questions')} <span>· {t('str. 3 i 8','pp. 3, 8')} ↗</span></a></article></div>{insight['themes']}</div></section>

<span id="jezik"></span>{insight['language']}

<section class="section wrap source-section" id="izvori" aria-labelledby="sources-heading"><div class="sources-copy"><p class="eyebrow">04 <span>—</span> {t('Medijski izvori','Media sources')}</p><h2 id="sources-heading">{t('Široka prisutnost.<br>Nejednak raspored.','Broad presence.<br>An uneven distribution.')}</h2><div class="concentration"><strong>{n(100*POOLED['top_ten_share'],1)}<span>%</span></strong><p>{t('svih objava dolazi iz<br>deset vodećih izvora.','of all publications come from<br>the ten leading sources.')}</p></div><div class="concentration-track" aria-hidden="true"><span style="width:{100*POOLED['top_ten_share']:.5f}%"></span></div><div class="concentration-key"><span><i></i>{t('Deset vodećih','Top ten')}</span><span><i></i>{t('Ostali izvori','Other sources')}</span></div><p class="source-context">{t('Vodeći izvor donosi 5,1% objava. Preostalih 271 izvor izvan prvih deset zajedno donosi 58,0%. Prisutnost je raspoređena na velik broj izvora, uz vidljivu koncentraciju pri vrhu.', 'The leading outlet contributes 5.1% of publications. The 271 outlets outside the top ten contribute 58.0% together. Coverage spans many sources, with a substantial concentration at the top.')}</p><p class="source-context small">{t('Broj objava pokazuje količinu; udio kod izvora pokazuje koliko prostora HNB zauzima u njegovoj praćenoj produkciji.', 'Publication count shows volume; share of outlet output shows how much of its monitored coverage mentions HNB.')}</p></div><div class="sources-ranking">{ranking}</div></section>

<section class="publications-section" id="publikacije" aria-labelledby="publications-heading"><span id="izvjestaj"></span><div class="wrap"><div class="section-heading"><div><p class="eyebrow">{t('Biblioteka publikacija','Publications library')}</p><h2 id="publications-heading">{t('Cijela priča u dva izvještaja.','The full picture in two reports.')}</h2></div><p class="section-intro">{t('Grafikoni, nalazi i širi kontekst.<br>Čitajte online ili preuzmite PDF.','Charts, findings and the wider context.<br>Read online or download a PDF.')}</p></div><div class="reports-grid">{report_cards}</div></div></section>

{specialist_study(lang)}

<section class="about wrap" id="analiza"><details><summary>{t('O podacima','About the data')} <span>+</span></summary><div><p>{t('Pregled obuhvaća 33.235 praćenih internetskih objava koje spominju HNB, od siječnja 2021. do kolovoza 2026. Jezični pregled obuhvaća 33.100 različitih tekstova. Prikazani su odabrani pokazatelji iz dvaju izvještaja; objave nisu mjera čitanosti ili povjerenja.','The overview covers 33,235 monitored web publications mentioning HNB, January 2021–August 2026. The language report covers 33,100 distinct texts. This page presents selected indicators from the two reports; publications do not measure readership or trust.')}</p><p><a href="data/selected-indicators.json">{t('Podaci prikaza · JSON','Page data · JSON')}</a> · <a href="downloads/media-citation.txt">{t('Citiranje','Citation')}</a></p></div></details></section>
</main><footer class="wrap footer"><p><a href="https://www.lukasikic.info/">Luka Sikić</a> <span>·</span> <a href="mailto:luka.sikic@unicath.hr">luka.sikic@unicath.hr</a></p><p>{t('Neovisno istraživanje. Nije službena publikacija HNB-a.','Independent research. Not an official HNB publication.')}</p><a href="#page-title">{t('Na vrh','Back to top')} ↑</a></footer><script type="application/json" id="page-data">{payload}</script></body></html>'''
    if production:
        from media_editorial import metadata
        title = t('HNB u hrvatskim medijima', 'HNB in Croatian media')
        description = t('Odabrani nalazi iz dva izvještaja o medijskoj prisutnosti HNB-a.', 'Selected findings from two reports on HNB’s media presence.')
        head = metadata(site_url.rstrip('/'), home, title, description, lang, presentation_version)
        html = html.replace('<meta name="robots" content="noindex,nofollow">', '')
        html = html.replace('<span class="preview-label">'+t('Pregled prijedloga','Page preview')+'</span>', '')
        html = html.replace('href="#publikacije">'+t('Dva izvještaja','The two reports'), 'href="#izvjestaj">'+t('Dva izvještaja','The two reports'))
        html = html.replace('href="styles.css"', 'href="report-led.css"').replace('src="app.js"', 'src="report-led.js"')
        html = html.replace('</head>', head+'</head>')
    return html


def build(out, production=False, site_url='', presentation_version=''):
    out.mkdir(parents=True,exist_ok=True)
    for name in ['report-led.css','report-led.js']:
        shutil.copyfile(ROOT/'src'/name,out/name)
    pages = [('en','index.html'),('hr','hr.html')] if production else [('hr','index.html'),('en','en.html')]
    for lang,name in pages:
        (out/name).write_text(page(lang,production,site_url,presentation_version),encoding='utf-8')
    downloads=out/'downloads';downloads.mkdir(exist_ok=True)
    files=['SourceSans3-Regular.woff2','SourceSans3-Semibold.woff2','SourceSerif4Display-Regular.woff2','source-sans-LICENSE.txt','source-serif-LICENSE.txt','hnb-reports.css','media-citation.txt']
    files += ['PAPER_EXT.pdf', 'PAPER_EXT.html']
    files += [stem+ext for stem in ['hnb-u-medijskom-prostoru','hnb-od-rijeci-do-javnih-pitanja'] for ext in ['.pdf','.html','.webp']]
    if not production:
        for name in files:
            shutil.copyfile(PUBLIC/'downloads'/name,downloads/name)
            if name.startswith('hnb-') and name.endswith('.html'):
                reader = (downloads/name).read_text(encoding='utf-8')
                reader = reader.replace('../hr.html#izvjestaj', '../index.html#publikacije')
                (downloads/name).write_text(reader, encoding='utf-8')
    data={'period':'2021-01/2026-08','summary':{k:S[k] for k in ['hnb_publications','outlets','title_mentions','last_full_period']},
          'monthly':[{'period':r['period'],'hnb_count':r['hnb_count']} for r in MONTHS],
          'subjects':S['subject_counts'],'subject_definitions':D['subject_definitions'],
          'language_population':TEXTS,'terms':L['terms'],'phrases':L['phrases'],
          'leading_sources':[{'source_id':r['source_id'],'hnb_count':r['hnb_count']} for r in D['sources'][:10]],
          'top_ten_share':POOLED['top_ten_share'],
          'annual_subjects':annual_subjects(D), 'quarterly_words':quarterly_words(E),
          'latest_comparisons':{k:D['extensions']['latest'][k] for k in ['period','current','comparisons']},
          'leading_source_rates':[{k:r[k] for k in ['source_id','hnb_count','background_i','rate_per_10000']} for r in sorted([r for r in D['extensions']['source_rates'] if r['period_id']=='pooled' and r['eligible']],key=lambda r:r['rank'])[:5]],
          'source_reports':['hnb-u-medijskom-prostoru.pdf','hnb-od-rijeci-do-javnih-pitanja.pdf']}
    (out/'data').mkdir(exist_ok=True)
    (out/'data/selected-indicators.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if production:
        return ['report-led.css','report-led.js','data/selected-indicators.json']
    print('Local report-led preview: '+str(out))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT.parent/'output/hnb-report-preview');args=parser.parse_args()
    build(args.output.resolve())
