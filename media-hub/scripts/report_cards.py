"""Bilingual descriptions of the two Croatian long reports."""
from html import escape

def report_cards(artifacts,lang):
    hr=lang=='hr';t=lambda en,cr:cr if hr else en
    specs=[
      ('hnb-u-medijskom-prostoru','HNB u medijskom prostoru',
       t('A map of media presence','Pregled medijskog prostora'),
       t('A timeline, eight overlapping subject screens, outlet distribution and three monthly portraits explain where HNB appears in this monitored media sample.',
         'Kretanje kroz vrijeme, osam preklapajućih tematskih skupova, raspodjela izvora i tri mjesečna portreta objašnjavaju gdje se HNB pojavljuje u praćenom medijskom uzorku.'),
       t('33,235 publications','33.235 objava')),
      ('hnb-od-rijeci-do-javnih-pitanja','HNB: od riječi do javnih pitanja',
       t('Language and public questions','Jezik i javna pitanja'),
       t('A word cloud, eight thematic vocabularies and selected phrases lead into three examples: cash exchange, lending criteria and public accountability.',
         'Oblak riječi, osam tematskih rječnika i odabrani izrazi vode do triju primjera: zamjene gotovine, kreditnih kriterija i javne odgovornosti.'),
       t('33,100 distinct texts','33.100 različitih tekstova')),
    ]
    cards=[]
    for stem,title,kicker,desc,unit in specs:
        a=next(a for a in artifacts if a['file']==stem+'.pdf')
        cards.append(f'''<article class="report-card"><a class="report-cover" href="downloads/{stem}.html"><img src="downloads/{stem}.webp" width="420" height="594" loading="lazy" alt="{escape(t('Cover: ','Naslovnica: ')+title)}"></a><div><p class="eyebrow">{kicker}</p><h3>{title}</h3><p>{desc}</p><p class="source-note">{unit} · {a['pages']} {t('pages','stranica')} · PDF, {round(a['bytes']/1024)} kB · 21. 9. 2026. · {t('Croatian','hrvatski')}</p><div class="actions"><a class="button" href="downloads/{stem}.pdf">{t('Download PDF','Preuzmi PDF')}</a><a href="downloads/{stem}.html">{t('Read online (Croatian)','Čitaj na mreži')}</a></div></div></article>''')
    return f'''<section class="section" id="izvjestaj"><p class="eyebrow">{t('Publications','Publikacije')}</p><h2>{t('Two reports, two complementary views','Dva izvještaja, dva povezana pogleda')}</h2><p class="intro">{t('The overview describes HNB’s media presence; the language report examines vocabulary around explicit mentions and reads three public examples in detail. Both cover January 2021-August 2026 and are public research drafts awaiting author review.',
    'Pregled opisuje medijsku prisutnost HNB-a, a jezični izvještaj razrađuje rječnik oko izričitih spominjanja i detaljnije čita tri javna primjera. Oba obuhvaćaju siječanj 2021. - kolovoz 2026. i javni su istraživački nacrti za autorsku provjeru.')}</p><div class="reports-grid">{''.join(cards)}</div><p class="note">{t('The overview counts publications. The language report excludes 99 publications without body text and counts identical normalized bodies once: 33,100 texts. Its vocabulary is measured in sentence-like passages that explicitly mention HNB. The eight keyword groups overlap and have not been independently validated.',
    'Pregled broji objave. Jezični izvještaj izostavlja 99 objava bez tijela teksta, a jednake normalizirane tekstove broji jednom: ukupno 33.100 tekstova. Rječnik mjeri u rečeničnim odsječcima koji izričito spominju HNB. Osam skupova ključnih riječi preklapa se i nije neovisno validirano.')}</p><p><a href="data/media/report-language.csv">{t('Vocabulary counts · CSV','Frekvencije riječi · CSV')}</a> · <a href="data/media/report-language.json">{t('Dictionary, definitions and aggregates · JSON','Rječnik, definicije i agregati · JSON')}</a></p></section>'''
