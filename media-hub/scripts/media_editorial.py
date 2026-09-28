"""Presentation helpers for the observatory; read only the published aggregates."""
from html import escape as e
from media_chart import number


def briefing(data, lang):
    t = lambda en, hr: hr if lang == 'hr' else en
    n = lambda v, d=0: number(v, lang, d)
    latest = data['extensions']['latest']
    current = latest['current']
    prior = next(r for r in latest['comparisons'] if r['comparison'] == 'year_ago')
    s = data['summary']
    items = [
        (t('Latest reading · August 2026', 'Najnoviji pregled · kolovoz 2026.'),
         t(f'{n(current["hnb_count"])} publications, compared with {n(prior["hnb_count"])} in August 2025 ({n(prior["hnb_count_change"],1)}%).',
           f'{n(current["hnb_count"])} objava, prema {n(prior["hnb_count"])} u kolovozu 2025. ({n(prior["hnb_count_change"],1)}%).'),
         t(f'The archive rate also fell: {n(current["rate_per_10000"],2)} versus {n(prior["rate_per_10000"],2)} per 10,000 eligible publications.',
           f'Pala je i arhivska stopa: {n(current["rate_per_10000"],2)} prema {n(prior["rate_per_10000"],2)} na 10.000 prihvatljivih objava.'), '#latest-edition'),
        (t('Coverage is uneven', 'Objave su neravnomjerno raspoređene'),
         t(f'Five outlets contribute {n(s["top_five_share"]*100,1)}% of HNB publications.',
           f'Pet izvora donosi {n(s["top_five_share"]*100,1)}% objava o HNB-u.'),
         t('Compare volume with archive rate to see both the number of articles and HNB’s share of an outlet’s captured output.',
           'Usporedite broj objava i arhivsku stopu: prvi pokazuje količinu, a druga udio HNB-a u zabilježenim objavama izvora.'), '#izvori'),
        (t('HNB in the headline', 'HNB u naslovu'),
         t(f'{n(100*s["title_mentions"]/s["hnb_publications"],1)}% of HNB publications also name the bank in the title.',
           f'{n(100*s["title_mentions"]/s["hnb_publications"],1)}% objava o HNB-u navodi banku i u naslovu.'),
         t('Headline presence is a visible editorial choice; it does not establish the bank’s role or the article’s stance.',
           'Spominjanje u naslovu vidljiv je urednički odabir; ne određuje ulogu banke ni stav članka.'), '#media-indicators')]
    cards = ''.join(f'<article><p class="eyebrow">{title}</p><h3>{body}</h3><p>{note}</p><a href="{href}">{t("Explore this finding", "Istražite nalaz")} →</a></article>' for title, body, note, href in items)
    return f'<div class="briefing-grid">{cards}</div><p class="briefing-limit">{t("The latest comparison uses the same calendar month a year earlier. All figures describe the monitored archive; they do not measure audience reach or national attention. Concentration and title figures cover January 2021–August 2026.", "Najnovija usporedba odnosi se na isti kalendarski mjesec prethodne godine. Sve vrijednosti opisuju praćeni arhiv; ne mjere doseg publike ni nacionalnu pozornost. Koncentracija i udio naslova odnose se na siječanj 2021. – kolovoz 2026.")}</p>'


def identity(lang):
    t = lambda en, hr: hr if lang == 'hr' else en
    return f'''<div class="identity"><p><strong><a href="https://www.lukasikic.info/">Luka Sikić</a></strong> · {t('Research and analysis', 'Istraživanje i analiza')}</p><p><a href="mailto:luka.sikic@unicath.hr">{t('Contact', 'Kontakt')}</a> · <a href="downloads/media-citation.txt">{t('Cite this project', 'Citirajte projekt')}</a> · <a href="#updates">{t('Updates and corrections', 'Izmjene i ispravci')}</a></p><p class="source-note">{t('Independent research; no HNB affiliation or endorsement is implied.', 'Neovisno istraživanje; ne podrazumijeva pripadnost HNB-u ni njegovo odobrenje.')}</p></div>'''


def filter_note(lang):
    t = lambda en, hr: hr if lang == 'hr' else en
    return '<p class="filter-guide">'+t('Dates and source selection control the main chart and the three indicators below. Dates also control the source table and the fixed-panel comparison. The briefing, subjects, language, peak-month cards and publications retain their stated periods.', 'Datumi i odabir izvora upravljaju glavnim grafikonom i trima pokazateljima ispod njega. Datumi upravljaju i tablicom izvora te usporedbom stalnog skupa. Sažetak, teme, jezik, kartice vršnih mjeseci i publikacije zadržavaju navedena razdoblja.')+'</p>'


def explorer_extras(lang):
    t = lambda en, hr: hr if lang == 'hr' else en
    buttons = ''.join(f'<button type="button" data-chart-window="{key}">{label}</button>' for key, label in [('latest', t('Latest 12 months', 'Posljednjih 12 mjeseci')), ('api', t('Since January 2024', 'Od siječnja 2024.')), ('all', t('Full history', 'Cijelo razdoblje'))])
    return f'<div class="actions presets" hidden data-media-js aria-label="{t("Time presets", "Odabir razdoblja")}">{buttons}</div>'


def month_inspector(lang):
    t = lambda en, hr: hr if lang == 'hr' else en
    return f'''<div class="month-inspector" hidden data-media-js><div class="month-controls"><label for="media-inspect">{t('Inspect a month', 'Pregledajte mjesec')}<select id="media-inspect"></select></label><button id="media-month-prev" aria-label="{t('Previous month', 'Prethodni mjesec')}">←</button><button id="media-month-next" aria-label="{t('Next month', 'Sljedeći mjesec')}">→</button></div><p id="media-month-reading" role="status"></p></div>'''


def source_tools(lang):
    t = lambda en, hr: hr if lang == 'hr' else en
    return f'''<div class="source-tools" hidden data-media-js><label for="media-search">{t('Find an outlet domain', 'Pronađite domenu izvora')}<input type="search" id="media-search" placeholder="{t('e.g. tportal.hr', 'npr. tportal.hr')}" autocomplete="off"></label><button id="media-search-clear">{t('Clear search', 'Očisti pretragu')}</button></div>'''


def source_pager(lang):
    t = lambda en, hr: hr if lang == 'hr' else en
    return f'''<div class="source-pager" hidden data-media-js><button id="media-source-prev">← {t('Previous', 'Prethodna')}</button><p id="media-source-page" role="status"></p><button id="media-source-next">{t('Next', 'Sljedeća')} →</button></div>'''


def source_example(data, lang):
    t = lambda en, hr: hr if lang == 'hr' else en
    n = lambda v, d=0: number(v, lang, d)
    rates = {r['source_id']: r for r in data['extensions']['source_rates'] if r['period_id'] == 'pooled'}
    a, b = rates['tportal.hr'], rates['poslovni.hr']
    text = t(
        f'tportal.hr has more HNB publications ({n(a["hnb_count"])}) than poslovni.hr ({n(b["hnb_count"])}). Yet poslovni.hr has the higher archive rate: {n(b["rate_per_10000"],2)} per 10,000 eligible publications, compared with {n(a["rate_per_10000"],2)} for tportal.hr. HNB accounts for a larger share of poslovni.hr’s eligible captured output, although tportal.hr contributes more HNB articles.',
        f'tportal.hr ima više objava o HNB-u ({n(a["hnb_count"])}) od izvora poslovni.hr ({n(b["hnb_count"])}). Ipak, poslovni.hr ima višu arhivsku stopu: {n(b["rate_per_10000"],2)} na 10.000 prihvatljivih objava, prema {n(a["rate_per_10000"],2)} za tportal.hr. HNB čini veći udio prihvatljivih zabilježenih objava izvora poslovni.hr, iako tportal.hr donosi više članaka o HNB-u.')
    return '<details class="worked-example"><summary>'+t('Worked example · count and rate tell different stories', 'Primjer · broj objava i stopa pokazuju različite aspekte')+'</summary><p>'+text+'</p><p class="source-note">'+t('Fixed comparison: January 2021–August 2026; all eligible sources. Does not follow the controls.', 'Stalna usporedba: siječanj 2021. – kolovoz 2026.; svi prihvatljivi izvori. Ne prati kontrole.')+' <a href="data/media/media-source-rates.csv">CSV</a></p></details>'


def method_summary(lang):
    t = lambda en, hr: hr if lang == 'hr' else en
    cards = [
        (t('What is counted?', 'Što se broji?'), t('A captured web publication explicitly naming HNB in its title or body. Repeated captures on the same outlet are merged; copies published by different outlets count separately.', 'Zabilježena internetska objava koja izričito navodi HNB u naslovu ili tekstu. Ponovljeni zapisi istog izvora spajaju se; preneseni tekstovi na različitim izvorima broje se zasebno.')),
        (t('What is the comparison?', 'Što se uspoređuje?'), t('Counts show volume. Rates divide matching HNB publications by all archive publications passing the same filter, within the same sources and months, then multiply by 10,000.', 'Broj objava pokazuje količinu. Stopa dijeli broj podudarnih objava o HNB-u svim arhivskim objavama koje prolaze isti filtar u istim izvorima i mjesecima te ga množi s 10.000.')),
        (t('Which sources and dates?', 'Koji izvori i datumi?'), t('The main view covers January 2021–August 2026 and domains matching the Agency for Electronic Media register. September is available through 10 September in the explorer and is excluded from headline totals.', 'Glavni pregled obuhvaća siječanj 2021. – kolovoz 2026. i domene koje se podudaraju s upisnikom Agencije za elektroničke medije. U interaktivnom prikazu rujan je dostupan do 10. rujna i isključen je iz glavnih ukupnih vrijednosti.'))]
    result = '<div class="method-summary">'+''.join(f'<article><h3>{title}</h3><p>{text}</p></article>' for title, text in cards)+'</div>'
    result += '<aside class="note"><h3>'+t('What these data cannot tell you', 'Što ovi podaci ne mogu pokazati')+'</h3><p>'+t('Publication counts do not measure readership, trust, sentiment, policy effects or communication effectiveness. Outlet domains do not establish ownership. Keyword matches describe words in captured text, not an article’s main topic.', 'Broj objava ne mjeri čitanost, povjerenje, sentiment, učinke politike ni učinkovitost komunikacije. Domene izvora ne utvrđuju vlasništvo. Ključne riječi opisuju riječi u zabilježenom tekstu, a ne glavnu temu članka.')+'</p></aside>'
    return result


def updates(lang, version):
    t = lambda en, hr: hr if lang == 'hr' else en
    return f'''<div id="updates" class="updates"><h3>{t('Updates and corrections', 'Izmjene i ispravci')}</h3><p>{t('This is a dated edition, updated when a new release is published. The headline view uses the latest complete month in that edition.', 'Ovo je datirano izdanje koje se ažurira objavom novog izdanja. Glavni pregled koristi posljednji potpuni mjesec tog izdanja.')}</p><p>{t('Report a correction to', 'Ispravak prijavite na')} <a href="mailto:luka.sikic@unicath.hr">luka.sikic@unicath.hr</a>. {t('Include the section, month or outlet and the page link. Published corrections will identify the affected edition and describe the change here.', 'Navedite odjeljak, mjesec ili izvor te poveznicu stranice. Objavljeni ispravci ovdje će navesti zahvaćeno izdanje i opis promjene.')}</p><details><summary>{t('Change log', 'Povijest izmjena')}</summary><ul><li><strong>{e(version)}</strong> — {t('Clearer bilingual briefing, source search and pagination, month inspection, mobile navigation and a consolidated publications library. Published data and calculation rules unchanged.', 'Jasniji dvojezični sažetak, pretraga i listanje izvora, pregled pojedinačnih mjeseci, mobilna navigacija i objedinjena biblioteka publikacija. Objavljeni podaci i pravila izračuna ostaju isti.')}</li><li><strong>2026-09-28.1</strong> — {t('Updated specialist paper with PDF and HTML editions.', 'Ažurirani specijalistički rad u PDF i HTML izdanju.')}</li><li><strong>2026-09-22.1</strong> — {t('Source rates, composition indicators and language comparisons.', 'Stope po izvorima, pokazatelji sastava i jezične usporedbe.')}</li></ul></details></div>'''


def metadata(base, name, title, description, lang, version):
    url = base+'/'+('' if name == 'index.html' else name)
    image = base+'/figures/media-social-preview.png'
    tags = {'og:type': 'website', 'og:title': title, 'og:description': description,
            'og:url': url, 'og:image': image, 'og:image:width': '1200', 'og:image:height': '630',
            'og:image:alt': 'HNB in Croatian media · Independent observatory · 28 September 2026',
            'og:locale': 'hr_HR' if lang == 'hr' else 'en_GB', 'og:site_name': 'HNB · Media observatory'}
    return ''.join(f'<meta property="{key}" content="{e(value,quote=True)}">' for key,value in tags.items())+f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{e(image)}"><meta name="author" content="Luka Sikić"><meta name="date" content="{version[:10]}"><link rel="canonical" href="{e(url)}"><link rel="alternate" hreflang="en" href="{e(base)}/"><link rel="alternate" hreflang="hr" href="{e(base)}/hr.html">'
