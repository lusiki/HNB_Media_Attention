"""Five concise findings, using the same populations as the two reports."""
from html import escape as esc


def finding_carousel(data, language, lang, fmt):
    t = lambda hr, en: hr if lang == 'hr' else en
    n = lambda value, decimals=0: fmt(value, lang, decimals)
    total = data['summary']['hnb_publications']
    texts = language['distinct_normalized_bodies']
    top_ten = sum(r['hnb_count'] for r in data['sources'][:10])
    findings = [
        (t('HNB već u naslovu', 'HNB in the headline'),
         data['summary']['title_mentions'], total,
         t('Približno svaka šesta objava navodi HNB i u naslovu.', 'Roughly one in six publications also names HNB in the headline.'), 'publications'),
        (t('Krediti u prvom planu', 'Lending in focus'),
         data['summary']['subject_counts']['lending'], total,
         t('Gotovo polovica objava sadrži riječi o kreditiranju i potrošačima.', 'Almost half of publications contain words about lending and consumers.'), 'publications'),
        (t('Deset vodećih izvora', 'Ten leading sources'),
         top_ten, total,
         t('Dvije petine svih objava dolaze iz samo deset izvora.', 'Two fifths of all publications come from just ten sources.'), 'publications'),
        (t('Guverner uz HNB', 'The governor and HNB'),
         language['terms']['guverner'], texts,
         t('Približno svaki četvrti tekst sadrži riječ „guverner” uz HNB.', 'Roughly one in four texts contains the word “governor” around HNB.'), 'texts'),
        (t('Uvođenje eura', 'Euro adoption'),
         language['phrases']['uvođenje eura'], texts,
         t('Najčešći praćeni izraz uz HNB je „uvođenje eura”.', '“Euro adoption” is the most frequent tracked phrase around HNB.'), 'texts'),
    ]
    cards, selectors = [], []
    for index, (title, count, denominator, description, unit) in enumerate(findings):
        share = 100 * count / denominator
        dots = ''.join(f'<span style="--fill:{min(100,max(0,(share-i)*100)):.4f}%"></span>' for i in range(100))
        caption = f'{n(count)} {t("od", "of")} {n(denominator)} {t("objava", "publications") if unit == "publications" else t("tekstova", "texts")}'
        position = f'{index+1} {t("od", "of")} {len(findings)}'
        cards.append(f'''<article class="finding-card" id="finding-{index+1}" role="group" aria-roledescription="{t('nalaz','slide')}" aria-label="{position}: {esc(title)}"><h2 class="eyebrow finding-title">{esc(title)}</h2><div class="headline-number">{n(share,1)}<span>%</span></div><p class="finding-copy">{esc(description)}</p><div class="dot-grid" aria-hidden="true">{dots}</div><p class="small finding-denominator">{caption}</p></article>''')
        selectors.append(f'<button class="finding-selector" type="button" data-finding="{index}" aria-controls="findings-track" aria-label="{t("Prikaži nalaz", "Show finding")} {index+1}: {esc(title)}" aria-pressed="{str(index == 0).lower()}"><span></span></button>')
    return f'''<aside class="headline-carousel" aria-label="{t('Pet izdvojenih nalaza','Five selected findings')}" aria-roledescription="{t('galerija','carousel')}"><div class="finding-track" id="findings-track" tabindex="0" aria-label="{t('Nalazi iz izvještaja','Report findings')}" aria-describedby="finding-help">{''.join(cards)}</div><p id="finding-help" class="sr-only">{t('Listajte vodoravno ili koristite tipke sa strelicama lijevo i desno za pregled pet nalaza.', 'Scroll horizontally or use the left and right arrow keys to explore five findings.')}</p><div class="finding-controls" hidden><button class="finding-prev" type="button" aria-label="{t('Prethodni nalaz','Previous finding')}" aria-controls="findings-track" aria-disabled="true">←</button><div class="finding-selectors" role="group" aria-label="{t('Odaberite nalaz','Choose a finding')}">{''.join(selectors)}</div><button class="finding-next" type="button" aria-label="{t('Sljedeći nalaz','Next finding')}" aria-controls="findings-track">→</button></div><p class="finding-status sr-only" role="status" aria-atomic="true"></p></aside>'''
