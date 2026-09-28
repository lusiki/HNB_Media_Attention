"""Presentation components using only the reports' existing aggregate indicators."""
from html import escape as esc


def annual_subjects(data):
    rows = []
    for definition in data['subject_definitions']:
        if definition['id'] not in ['lending', 'currency', 'payments', 'prices', 'rates']:
            continue
        values = []
        for year in ['2024', '2025', '2026']:
            denominator = sum(r['hnb_count'] for r in data['monthly'] if r['period'].startswith(year) and r['period'] <= '2026-08')
            count = sum(r['lexical_count'] for r in data['subjects'] if r['subject_id'] == definition['id'] and r['period'].startswith(year) and r['period'] <= '2026-08')
            values.append(dict(year=year, count=count, denominator=denominator, share=100*count/denominator))
        rows.append(dict(id=definition['id'], label_hr=definition['label_hr'], label_en=definition['label_en'], values=values))
    order = ['lending', 'currency', 'payments', 'prices', 'rates']
    return sorted(rows, key=lambda r: order.index(r['id']))


def quarterly_words(lexical):
    index = {(r['quarter'], r['term']): r for r in lexical['quarterly'] if r['kind'] == 'term'}
    quarters = sorted({q for q, _ in index if '2024-Q1' <= q <= '2026-Q2'})
    return [dict(quarter=q, denominator=index[q, 'inflacija']['denominator'],
                 inflation=index[q, 'inflacija']['count'], credit=index[q, 'kredit']['count']) for q in quarters]


def components(data, lexical, lang, fmt):
    t = lambda hr, en: hr if lang == 'hr' else en
    n = lambda value, decimals=0: fmt(value, lang, decimals)
    now = data['extensions']['latest']['current']
    comparisons = data['extensions']['latest']['comparisons']
    yearago = next(r for r in comparisons if r['comparison'] == 'year_ago')
    mean = next(r for r in comparisons if r['comparison'] == 'preceding_12_month_mean')
    headline = f'''<div class="reading-grid">
<article class="reading-card"><p class="eyebrow">{t('Mjesto HNB-a u naslovu','HNB in the headline')}</p><h3>{t('Manje objava, više naslova s HNB-om.','Fewer publications, more HNB headlines.')}</h3><p>{t('Broj objava pao je s 208 na 200, ali broj naslova koji spominju HNB porastao je s 35 na 41.','Publications fell from 208 to 200, while headlines naming HNB rose from 35 to 41.')}</p><div class="comparison-pair"><div><span>{t('Kolovoz 2025.','August 2025')}</span><strong>{n(100*yearago['title_share'],1)}<small>%</small></strong></div><span aria-hidden="true">→</span><div><span>{t('Kolovoz 2026.','August 2026')}</span><strong>{n(100*now['title_share'],1)}<small>%</small></strong></div></div><p class="reading-conclusion">+{n(yearago['title_share_change'],1)} {t('postotnih bodova u udjelu naslova.','percentage points in headline share.')}</p></article>
<article class="reading-card"><p class="eyebrow">{t('Dva pogleda na isti mjesec','Two comparisons for the same month')}</p><h3>{t('Blizu prošlog kolovoza, ispod godišnjeg prosjeka.','Near last August, below the recent average.')}</h3><p>{t('Dvjesto objava samo je osam manje nego godinu prije. Razmak je veći prema prosjeku prethodnih dvanaest mjeseci.','Two hundred publications is just eight fewer than a year earlier. The gap is larger against the preceding twelve-month average.')}</p><div class="comparison-pair"><div><span>{t('Prethodnih 12 mjeseci','Previous 12 months')}</span><strong>{n(mean['hnb_count'],1)}</strong></div><span aria-hidden="true">→</span><div><span>{t('Kolovoz 2026.','August 2026')}</span><strong>{n(now['hnb_count'])}</strong></div></div><p class="reading-conclusion">{n(mean['hnb_count_change'],1)}% {t('prema mjesečnom prosjeku VIII. 2025. – VII. 2026.','versus the monthly average, Aug 2025 – Jul 2026.')}</p></article></div>'''

    annual = annual_subjects(data)
    cells = ''
    for row in annual:
        values = ''.join(f'<td style="--heat:{v["share"]/65:.3f}"><span>{n(v["share"],1)}<small>%</small></span></td>' for v in row['values'])
        cells += f'<tr><th scope="row">{esc(row["label_"+lang])}</th>{values}</tr>'
    themes = f'''<div class="theme-history"><div class="theme-reading"><p class="eyebrow">{t('Kako se mijenjaju teme','How the subject mix changes')}</p><h3>{t('U 2025. jači naglasak na cijenama i plaćanjima.','Prices and payments gained ground in 2025.')}</h3><p>{t('Riječi o cijenama i inflaciji pojavljuju se u 42,9% objava u 2025., prema 29,2% u 2024. Plaćanja i gotovina rastu s 31,3% na 40,5%.','Words about prices and inflation appear in 42.9% of publications in 2025, up from 29.2% in 2024. Payments and cash rise from 31.3% to 40.5%.')}</p><p>{t('U prvih osam mjeseci 2026. oba su udjela niža, dok kreditiranje ostaje vodeće među ovih pet područja.','Both shares are lower in the first eight months of 2026, while lending remains the largest of these five subjects.')}</p><a class="report-source" href="downloads/hnb-u-medijskom-prostoru.html#stranica-7">{t('Medijski pregled','Media presence report')} <span>· {t('str. 7','p. 7')} ↗</span></a></div><div class="heatmap-wrap"><table class="theme-heatmap"><caption>{t('Udio u objavama o HNB-u u svakom razdoblju','Share of HNB publications in each period')}</caption><thead><tr><th scope="col">{t('Tema','Subject')}</th><th scope="col">2024</th><th scope="col">2025</th><th scope="col">2026*</th></tr></thead><tbody>{cells}</tbody></table><p class="small">{t('*2026.: siječanj – kolovoz. Tamnije polje označava veći udio. Teme se mogu preklapati.','*2026: January–August. Darker cells indicate a larger share. Subjects can overlap.')}</p></div></div>'''

    quarters = quarterly_words(lexical)
    width, height = 660, 310
    x = lambda i: 42 + i * 540/(len(quarters)-1)
    y = lambda v: 258 - v*7
    svg = f'<svg class="word-chart" viewBox="0 0 {width} {height}" role="img" aria-labelledby="word-chart-title"><title id="word-chart-title">{t("Inflacija i kredit: udio tekstova po tromjesečju, 2024. – 2026.","Inflation and credit: share of texts by quarter, 2024–2026")}</title>'
    for value in [0, 10, 20, 30]:
        svg += f'<line x1="42" x2="582" y1="{y(value)}" y2="{y(value)}" class="gridline"/><text x="31" y="{y(value)+5}" text-anchor="end" class="word-axis">{value}%</text>'
    for i, q in enumerate(quarters):
        if q['quarter'].endswith('Q1'):
            svg += f'<text x="{x(i)}" y="295" class="word-axis">{q["quarter"][:4]}</text>'
    for key, label in [('inflation', t('Inflacija','Inflation')), ('credit',t('Kredit','Credit'))]:
        points = ' '.join(f'{x(i):.2f},{y(100*q[key]/q["denominator"]):.2f}' for i,q in enumerate(quarters))
        svg += f'<polyline points="{points}" class="word-line {key}"/>'
        for i,q in enumerate(quarters):
            share=100*q[key]/q['denominator']
            svg += f'<circle cx="{x(i)}" cy="{y(share)}" r="4" class="word-dot {key}" data-quarter="{i}"><title>{q["quarter"]} · {label}: {n(share,1)}%</title></circle>'
        latest=100*quarters[-1][key]/quarters[-1]['denominator']
        svg += f'<text x="597" y="{y(latest)+6}" class="word-end {key}">{n(latest,1)}%</text>'
    svg += '<line class="quarter-guide" x1="582" x2="582" y1="38" y2="258" aria-hidden="true"/></svg>'
    options=''.join(f'<option value="{i}" {"selected" if i==len(quarters)-1 else ""}>{q["quarter"][:4]} · {q["quarter"][-1]}. {t("tromjesečje","quarter")}</option>' for i,q in enumerate(quarters))
    table=''.join(f'<tr><th scope="row">{q["quarter"]}</th><td>{n(100*q["inflation"]/q["denominator"],1)}%</td><td>{n(100*q["credit"]/q["denominator"],1)}%</td></tr>' for q in quarters)
    last = quarters[-1]
    inflation_share = 100*last['inflation']/last['denominator']
    credit_share = 100*last['credit']/last['denominator']
    language = f'''<section class="section wrap word-section" id="rijeci-kroz-vrijeme" aria-labelledby="words-heading"><div class="section-heading"><div><p class="eyebrow">03 <span>—</span> {t('Riječi kroz vrijeme','Words over time')}</p><h2 id="words-heading">{t('Inflacija ponovno ispred kredita.','Inflation moves ahead of credit again.')}</h2></div><p class="section-intro">{t('Udio tekstova koji sadrže pojedinu riječ uz HNB, po tromjesečju.','Share of texts containing each word around HNB, by quarter.')}</p></div><div class="word-layout"><figure class="word-figure"><figcaption class="word-legend"><span><i></i>{t('Inflacija','Inflation')}</span><span><i></i>{t('Kredit','Credit')}</span><small>2024–2026</small></figcaption>{svg}<p class="small">{t('Od prvog tromjesečja 2024. do drugog tromjesečja 2026.','From the first quarter of 2024 to the second quarter of 2026.')}</p><div class="sr-only"><table><caption>{t('Tromjesečni udjeli','Quarterly shares')}</caption><thead><tr><th scope="col">{t('Tromjesečje','Quarter')}</th><th scope="col">{t('Inflacija','Inflation')}</th><th scope="col">{t('Kredit','Credit')}</th></tr></thead><tbody>{table}</tbody></table></div></figure><aside class="quarter-card"><div class="quarter-control" hidden><label for="quarter-select">{t('Istražite tromjesečje','Explore a quarter')}</label><select id="quarter-select">{options}</select></div><div id="quarter-reading" aria-live="polite"><p class="eyebrow" id="quarter-label">2026 · 2. {t('tromjesečje','quarter')}</p><div class="quarter-values"><div><span>{t('Inflacija','Inflation')}</span><strong id="inflation-share">{n(inflation_share,1)}%</strong><small id="inflation-count">{n(last['inflation'])} / {n(last['denominator'])} {t('tekstova','texts')}</small></div><div><span>{t('Kredit','Credit')}</span><strong id="credit-share">{n(credit_share,1)}%</strong><small id="credit-count">{n(last['credit'])} / {n(last['denominator'])} {t('tekstova','texts')}</small></div></div><p class="quarter-gap" id="quarter-gap">{t('Inflacija je zastupljenija za 7,0 postotnih bodova.','Inflation is more frequent by 7.0 percentage points.')}</p></div></aside></div><div class="word-reading"><p>{t('Kredit je zastupljeniji od inflacije u prva tri tromjesečja 2024. i sredinom 2025. Od posljednjeg tromjesečja 2025. inflacija ponovno ima veći udio.','Credit is more frequent than inflation in the first three quarters of 2024 and in mid-2025. From the final quarter of 2025, inflation has the larger share again.')}</p><a class="report-source" href="downloads/hnb-od-rijeci-do-javnih-pitanja.html#stranica-13">{t('Od riječi do javnih pitanja','Language and public questions')} <span>· {t('str. 13','p. 13')} ↗</span></a></div></section>'''
    return dict(headline=headline, themes=themes, language=language, quarters=quarters, annual=annual)


def source_comparison(data, lang, fmt):
    t = lambda hr, en: hr if lang == 'hr' else en
    n = lambda v, decimals=0: fmt(v, lang, decimals)
    counts = data['sources'][:5]
    rates = sorted([r for r in data['extensions']['source_rates'] if r['period_id']=='pooled' and r['eligible']],key=lambda r:r['rank'])[:5]
    panels=''
    for key, rows, field, title, unit, note in [
        ('volume', counts, 'hnb_count', t('Prvih pet prema broju objava','Top five by publication count'), t('Objave','Publications'), t('Tportal.hr ima najviše objava: 1.694, odnosno 5,1% svih objava o HNB-u.','Tportal.hr has the most publications: 1,694, or 5.1% of all HNB publications.')),
        ('intensity', rates, 'rate_per_10000', t('Prvih pet prema udjelu u vlastitoj produkciji','Top five by share of their own output'), t('Na 10.000','Per 10,000'), t('Tockanai.hr vodi prema udjelu: 216 objava o HNB-u među 7.821 praćenom objavom tog izvora.','Tockanai.hr leads by share: 216 HNB publications among the outlet’s 7,821 monitored publications.')),
    ]:
        items=''.join(f'<li><span class="source-rank">0{i+1}</span><strong>{esc(r["source_id"])}</strong><span class="source-meter" aria-hidden="true"><span style="width:{100*r[field]/rows[0][field]:.3f}%"></span></span><span class="source-count">{n(r[field],1 if key=="intensity" else 0)}</span></li>' for i,r in enumerate(rows))
        eligibility=f'<p class="small ranking-note">{t("Usporedni poredak: najmanje 5.000 praćenih objava i 50 objava o HNB-u po izvoru.","Comparison ranking: at least 5,000 monitored publications and 50 HNB publications per outlet.")}</p>' if key=='intensity' else ''
        panels += f'<div id="{key}-panel" role="tabpanel" aria-labelledby="{key}-tab" tabindex="0"><div class="ranking-heading"><h3>{title}</h3><span>{unit}</span></div><ol class="sources-list">{items}</ol><p class="source-insight">{note}</p>{eligibility}</div>'
    result=f'''<div class="source-controls" hidden role="tablist" aria-label="{t('Usporedite izvore','Compare sources')}"><button id="volume-tab" role="tab" aria-controls="volume-panel" aria-selected="true">{t('Broj objava','Publication count')}</button><button id="intensity-tab" role="tab" aria-controls="intensity-panel" aria-selected="false" tabindex="-1">{t('Udio kod izvora','Share of outlet output')}</button></div>{panels}<a class="report-source" href="downloads/hnb-u-medijskom-prostoru.html#stranica-12">{t('Medijski pregled','Media presence report')} <span>· {t('str. 12–14','pp. 12–14')} ↗</span></a>'''
    return result, rates
