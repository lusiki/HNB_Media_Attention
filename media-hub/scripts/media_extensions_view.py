"""Shared A1 scope, caption and publication records; no analytical input access."""
from html import escape
from media_chart import number, chart

FILES=['extensions.json','extensions-manifest.json','media-stable-panel.csv','media-indicators-monthly.csv',
       'media-source-rates.csv','media-source-concentration.csv','media-fixed-weight-components.csv',
       'media-latest-edition.json','media-event-screen.csv','media-events.json','media-figure-registry.json']

def brief_text(data,lang):
    n=lambda v,d=0:number(v,lang,d)
    p=next(r for r in data['extensions']['concentration'] if r['period_id']=='pooled' and r['scope']=='all')
    eligible=sum(r['eligible'] for r in data['extensions']['source_rates'] if r['period_id']=='pooled')
    if lang=='hr':return f'Nove stope po izvorima zahtijevaju najmanje 5.000 prihvatljivih pozadinskih objava i 50 objava o HNB-u ({eligible} domena zadovoljava uvjet). Efektivni broj domena iznosi {n(p["effective_domains"],2)}. Brojeve sada prate mjesečni udjeli naslova, obuhvat izvora i usporedbe s jednakim ponderima; to su opisne mjere arhiva.'
    return f'New source rates require at least 5,000 eligible background publications and 50 HNB publications ({eligible} domains qualify). The effective number of domains is {n(p["effective_domains"],2)}. Monthly title shares, source breadth and equal-weight comparisons now accompany counts; these remain descriptive archive measures.'

def narratives(data,lang):
    t=lambda en,hr:hr if lang=='hr' else en
    n=lambda v,d=0:number(v,lang,d)
    ex=data['extensions'];p=next(r for r in ex['concentration'] if r['period_id']=='pooled' and r['scope']=='all')
    current=ex['latest']['current'];prior=ex['latest']['comparisons'][0]
    return [
        ('V5',t('Concentration across domains','Koncentracija među domenama'),t(
            f'The effective number of contributing domains is {n(p["effective_domains"],1)}; the ten largest supply {n(p["top_ten_share"]*100,1)}% of publications. All {p["hnb_domains"]} contributing domains enter this calculation. It measures domain concentration, not ownership or viewpoint diversity.',
            f'Efektivni broj domena koje doprinose iznosi {n(p["effective_domains"],1)}; deset najvećih donosi {n(p["top_ten_share"]*100,1)}% objava. Izračun obuhvaća svih {p["hnb_domains"]} domena s objavama o HNB-u. Mjeri koncentraciju domena, a ne vlasništva ili raznolikosti stavova.')),
        ('V6',t('How widely sources carry HNB','Koliko je izvora objavljivalo o HNB-u'),t(
            f'{p["hnb_domains"]} of {p["background_domains"]} observed background domains carry HNB publications in the full window ({n(p["breadth_share"]*100,1)}%). Annual values use unions of domains; monthly counts cannot be added to obtain annual breadth.',
            f'U cijelom razdoblju {p["hnb_domains"]} od {p["background_domains"]} opaženih pozadinskih domena objavljuje o HNB-u ({n(p["breadth_share"]*100,1)}%). Godišnje vrijednosti koriste uniju domena; zbrajanje mjesečnih brojeva ne daje godišnji obuhvat.')),
        ('V7',t('Title mentions through time','Spominjanja u naslovu kroz vrijeme'),t(
            f'{n(p["title_mention_count"])} of {n(p["hnb_count"])} publications name HNB in the title ({n(p["title_share"]*100,1)}%). Annual shares divide annual title matches by annual publications. A title match is mechanical evidence, not validated prominence or proof of a trend.',
            f'{n(p["title_mention_count"])} od {n(p["hnb_count"])} objava navodi HNB u naslovu ({n(p["title_share"]*100,1)}%). Godišnji udjeli dijele godišnji broj podudarnih naslova godišnjim brojem objava. Podudaranje je mehaničko obilježje, a ne validirana istaknutost ni dokaz trenda.')),
        ('A05',t('Composition sensitivity','Osjetljivost na sastav izvora'),t(
            'Compare three monthly archive rates: all eligible sources, the pooled frozen 128-source panel, and that panel with each domain weighted 1/128. A missing or zero panel denominator makes the fixed-weight rate unavailable. The January 2024 boundary remains; fixed weights do not repair capture changes.',
            'Usporedite tri mjesečne arhivske stope: sve prihvatljive izvore, objedinjeni stalni skup od 128 izvora i isti skup s ponderom 1/128 za svaku domenu. Nedostupan ili nulti nazivnik bilo kojeg člana znači nedostupnu stopu sa stalnim ponderima. Granica u siječnju 2024. ostaje; stalni ponderi ne uklanjaju promjene prikupljanja.')),
        ('A06',t('Latest complete month','Posljednji potpuni mjesec'),t(
            f'August 2026 contains {n(current["hnb_count"])} HNB publications, versus {n(prior["hnb_count"])} in August 2025. Its archive rate is {n(current["rate_per_10000"],2)} per 10,000, compared with {n(prior["rate_per_10000"],2)} a year earlier. The additional baseline is the arithmetic mean of August 2025–July 2026, excluding the current month.',
            f'Kolovoz 2026. sadrži {n(current["hnb_count"])} objava o HNB-u, a kolovoz 2025. {n(prior["hnb_count"])}. Arhivska stopa iznosi {n(current["rate_per_10000"],2)} na 10.000, prema {n(prior["rate_per_10000"],2)} godinu prije. Dodatna osnova jest aritmetička sredina mjeseci od kolovoza 2025. do srpnja 2026., bez tekućeg mjeseca.'))]

def figure_registry(data):
    spec=[('media-composition','A05','media-indicators-monthly.csv','monthly archive rates','matching-filter background'),
          ('media-concentration','V5','media-source-concentration.csv','effective domains','all HNB publications'),
          ('media-breadth','V6','media-indicators-monthly.csv','domain share','observed background domains'),
          ('media-titles','V7','media-indicators-monthly.csv','publication share','HNB publications')]
    text={lang:{r[0]:r[2] for r in narratives(data,lang)} for lang in ['en','hr']}
    return [dict(figure_id=id,finding_id=fid,data_file=file,selection='2021-01/2026-08; all eligible sources or declared frozen panel',
        unit=unit,denominator=den,caption_hr=text['hr'][fid],caption_en=text['en'][fid],
        limitation='Descriptive archive; January 2024 collection boundary; no independent validation',
        version=data['extensions']['indicator_version']) for id,fid,file,unit,den in spec]

def scope(data,lang,unit,denominator,fixed=False):
    t=lambda en,hr:hr if lang=='hr' else en
    return '<p class="scope-badge">'+escape(t('Fixed edition · ','Stalno izdanje · ') if fixed else t('Selected dates and sources · ','Odabrani datumi i izvori · '))+escape(
        f'HNB_MEDIA {data["release"]["data_version"]} · '+t('method ','metoda ')+data['release']['method_version']+' · '+data['extensions']['indicator_version']+f' · {unit} · '+t('denominator: ','nazivnik: ')+denominator+' · '+
        t('01/2024 collection boundary · descriptive, no independent validation','01/2024 promjena prikupljanja · opisno, bez neovisne validacije'))+'</p>'

def latest_panel(data,lang,table):
    t=lambda en,hr:hr if lang=='hr' else en;n=lambda v,d=0:number(v,lang,d)
    ex=data['extensions'];latest=ex['latest'];r=latest['current']
    rows=[(t('August 2026','Kolovoz 2026.'),n(r['hnb_count']),n(r['rate_per_10000'],2),'—','—')]
    for c in latest['comparisons']:
        label=t('August 2025','Kolovoz 2025.') if c['comparison']=='year_ago' else t('Previous 12-month mean','Prosjek prethodnih 12 mjeseci')
        rows.append((label,n(c['hnb_count'],1),n(c['rate_per_10000'],2),n(c['hnb_count_change'],1)+'%',n(c['rate_per_10000_change'],1)+'%'))
    return ('<aside class="latest-panel" id="latest-edition"><p class="eyebrow">'+t('Latest complete month · August 2026','Posljednji potpuni mjesec · kolovoz 2026.')+'</p><h3>'+t('Count and archive rate, side by side','Broj objava i arhivska stopa usporedno')+'</h3>'+scope(data,lang,t('publications','objave'),t('matching-filter archive publications','arhivske objave s istim filtrom'),True)+table(
        [t('Observation / baseline','Opažanje / osnova'),t('Publications','Objave'),t('Per 10,000','Na 10.000'),t('Count change','Promjena broja'),t('Rate change','Promjena stope')],rows)+
        '<p class="source-note">'+t('All eligible sources. Changes compare August 2026 with each baseline. Twelve preceding complete months exclude August 2026; rates are averaged monthly. September is partial and excluded.','Svi prihvatljivi izvori. Promjene uspoređuju kolovoz 2026. sa svakom osnovom. Prethodnih 12 potpunih mjeseci isključuje kolovoz 2026.; stope su mjesečno usrednjene. Djelomičan rujan je isključen.')+' <a href="data/media/media-latest-edition.json">JSON</a></p></aside>')

def panels(data,lang,table):
    t=lambda en,hr:hr if lang=='hr' else en;n=lambda v,d=0:number(v,lang,d)
    ex=data['extensions'];stories=narratives(data,lang)
    annual=[r for r in ex['concentration'] if r['period_id'].isdigit() and r['scope']=='all']
    rows=[(r['period_id']+(' *' if r['period_end'].endswith('-08') else ''),n(r['hnb_domains']),n(r['background_domains']),n(r['breadth_share']*100,1)+'%',n(r['title_mention_count']),n(r['hnb_count']),n(r['title_share']*100,1)+'%') for r in annual]
    out='<section class="section extension-evidence" id="media-indicators"><p class="eyebrow">'+t('Breadth, titles and composition','Obuhvat, naslovi i sastav')+'</p><h2>'+t('Read the denominator with the count','Čitajte nazivnik zajedno s brojem')+'</h2>'
    out+=scope(data,lang,t('domains / publications','domene / objave'),t('background domains / HNB publications','pozadinske domene / objave o HNB-u'))
    out+='<p id="extension-scope" class="source-note">2021-01–2026-08 · '+t('All eligible sources; no rate-ranking threshold','Svi prihvatljivi izvori; bez praga za poredak stopa')+'</p><div class="indicator-cards" id="extension-cards">'+''.join('<article id="'+id+'"><span class="claim-id">'+id+'</span><h3>'+escape(title)+'</h3><p>'+escape(text)+'</p></article>' for id,title,text in stories[:3])+'</div>'
    out+='<p><a href="data/media/media-source-concentration.csv">'+t('Annual and window indicators · CSV','Godišnji pokazatelji i razdoblja · CSV')+'</a> · <a href="data/media/media-indicators-monthly.csv">'+t('Monthly indicators · CSV','Mjesečni pokazatelji · CSV')+'</a></p>'
    out+='<details><summary>'+t('Annual reference table · fixed full edition','Godišnja referentna tablica · stalno cijelo izdanje')+'</summary><p class="source-note">'+t('All eligible sources; annual domain unions and ratios of annual counts. * 2026: January–August. This reference table does not follow the controls.','Svi prihvatljivi izvori; godišnje unije domena i omjeri godišnjih brojeva. * 2026.: siječanj–kolovoz. Ova referentna tablica ne prati kontrole.')+'</p>'+table([t('Year','Godina'),t('HNB domains','HNB domene'),t('Background domains','Pozadinske domene'),t('Breadth','Obuhvat'),t('Titles','Naslovi'),t('Publications','Objave'),t('Title share','Udio naslova')],rows)+'</details>'
    out+='<h3>'+stories[3][1]+'</h3><p>'+stories[3][2]+'</p><p class="scope-badge">'+t('Selected complete months · fixed populations: all sources and frozen 128-source panel. Source selector does not change this comparison.','Odabrani potpuni mjeseci · stalni skupovi: svi izvori i stalni skup od 128 izvora. Odabir izvora ne mijenja ovu usporedbu.')+'</p><div class="chart-legend"><span class="series-all">'+t('All sources','Svi izvori')+'</span><span class="series-stable">'+t('128 sources · pooled','128 izvora · objedinjeno')+'</span><span class="series-fixed">'+t('128 sources · equal weights','128 izvora · jednaki ponderi')+'</span></div><div class="figure" id="composition-chart"></div><details><summary>'+t('Numeric composition comparison','Brojčana usporedba sastava')+'</summary>'+table([t('Month','Mjesec'),t('All sources','Svi izvori'),t('Panel pooled','Objedinjeni skup'),t('Equal weights','Jednaki ponderi')],[(r['period'],n(next(x['rate_per_10000'] for x in ex['monthly'] if x['period']==r['period'] and x['scope']=='all'),2),n(r['rate_per_10000'],2),n(r['fixed_weight_rate'],2)) for r in ex['monthly'] if r['scope']=='stable'],'composition-rows')+'</details><p><a href="data/media/media-fixed-weight-components.csv">'+t('Components and weights · CSV','Sastavnice i ponderi · CSV')+'</a> · <a href="data/media/media-stable-panel.csv">'+t('Frozen panel · CSV','Stalni skup · CSV')+'</a></p></section>'
    return out

def context(lang):
    t=lambda en,hr:hr if lang=='hr' else en
    return '<aside class="external-context"><p class="eyebrow">'+t('External survey context · 2026','Vanjski anketni kontekst · 2026.')+'</p><h3>'+t('News use is a separate measurement','Praćenje vijesti zasebno je mjerenje')+'</h3><p>'+t('The Reuters Institute Croatia profile reports 29% trust in news overall and 63% avoiding news sometimes or often. YouGov collected online answers from mid-January to late February 2026, using demographic quotas and weighting. The results describe the online population. They do not measure trust in HNB or exposure to these articles and supply no readership weights for this archive.','Profil Hrvatske Reutersova instituta navodi 29% povjerenja u vijesti općenito te 63% onih koji ponekad ili često izbjegavaju vijesti. YouGov je prikupljao internetske odgovore od sredine siječnja do kraja veljače 2026., uz demografske kvote i ponderiranje. Rezultati opisuju internetsku populaciju. Ne mjere povjerenje u HNB ni izloženost ovim člancima i ne daju pondere čitanosti za arhiv.')+'</p><p><a href="https://reutersinstitute.politics.ox.ac.uk/digital-news-report/2026/croatia">'+t('Croatia profile','Profil Hrvatske')+'</a> · <a href="https://reutersinstitute.politics.ox.ac.uk/digital-news-report/2026/methodology">'+t('Survey methodology','Metodologija ankete')+'</a> · '+t('Checked 22 September 2026','Provjereno 22. rujna 2026.')+'</p></aside>'
