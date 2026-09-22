"""Bilingual descriptions of the two Croatian long reports."""
from html import escape

def report_cards(artifacts,lang):
    hr=lang=='hr';t=lambda en,cr:cr if hr else en
    specs=[
      ('hnb-u-medijskom-prostoru','HNB u medijskom prostoru',
       t('A map of media presence','Pregled medijskog prostora'),
       t('How often HNB appears, which outlets cover it and which topics accompany it. Each indicator includes a clear explanation and a concrete result.',
         'Koliko se HNB pojavljuje, koji ga izvori prate i uz koje teme. Svaki pokazatelj ima jasno objašnjenje i konkretan nalaz.'),
       t('33,235 publications','33.235 objava')),
      ('hnb-od-rijeci-do-javnih-pitanja','HNB: od riječi do javnih pitanja',
       t('Language and public questions','Jezik i javna pitanja'),
       t('Words and phrases around HNB, the topics they describe and their changes over time. Tables and examples explain how to read each result.',
         'Riječi i izrazi uz HNB, teme koje opisuju i njihov raspored kroz vrijeme. Tablice i primjeri pokazuju kako pročitati svaki rezultat.'),
       t('33,100 distinct texts','33.100 različitih tekstova')),
    ]
    cards=[]
    for stem,title,kicker,desc,unit in specs:
        a=next(a for a in artifacts if a['file']==stem+'.pdf')
        cards.append(f'''<article class="report-card"><a class="report-cover" href="downloads/{stem}.html"><img src="downloads/{stem}.webp" width="420" height="594" loading="lazy" alt="{escape(t('Cover: ','Naslovnica: ')+title)}"></a><div><p class="eyebrow">{kicker}</p><h3>{title}</h3><p>{desc}</p><p class="source-note">{unit} · {a['pages']} {t('pages','stranica')} · PDF, {round(a['bytes']/1024)} kB · 22. 9. 2026. · {t('Croatian','hrvatski')}</p><div class="actions"><a class="button" href="downloads/{stem}.pdf">{t('Download PDF','Preuzmi PDF')}</a><a href="downloads/{stem}.html">{t('Read online (Croatian)','Čitaj na mreži')}</a></div></div></article>''')
    return f'''<section class="section" id="izvjestaj"><p class="eyebrow">{t('Publications','Publikacije')}</p><h2>{t('Two reports, two complementary views','Dva izvještaja, dva povezana pogleda')}</h2><p class="intro">{t('Two reports for a clear view of HNB’s media presence: key findings, explained indicators and concrete comparisons. Both cover January 2021-August 2026.',
    'Dva izvještaja za jasan pregled medijske prisutnosti HNB-a: ključni nalazi, objašnjeni pokazatelji i konkretne usporedbe. Oba obuhvaćaju siječanj 2021. - kolovoz 2026.')}</p><div class="reports-grid">{''.join(cards)}</div><p class="note">{t('The overview follows 33,235 online publications. The language report describes the words and phrases around HNB in 33,100 distinct texts.',
    'Medijski pregled prati 33.235 internetskih objava. Jezični izvještaj opisuje riječi i izraze uz HNB u 33.100 različitih tekstova.')}</p><p><a href="data/media/report-language.csv">{t('Vocabulary counts · CSV','Frekvencije riječi · CSV')}</a> · <a href="data/media/report-language.json">{t('Dictionary and data · JSON','Rječnik i podaci · JSON')}</a></p></section>'''
