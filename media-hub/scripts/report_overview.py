"""Sixteen-page executive overview derived from the published aggregates."""
from report_layout import *


def overview(out, D):
    S = D['summary']; N = S['hnb_publications']; E = D['extensions']
    full = [r for r in D['monthly'] if r['period'] <= '2026-08']
    recent = [r for r in full if r['period'] >= '2024-01']
    defs = D['subject_definitions']; labels = {d['id']: d['label_hr'] for d in defs}
    sc = S['subject_counts']
    pooled = next(r for r in E['concentration'] if r['period_id'] == 'pooled' and r['scope'] == 'all')
    annual = [r for r in E['concentration'] if r['scope'] == 'all' and len(r['period_id']) == 4]
    year_label = lambda y: '2026. I.-VIII.' if str(y) == '2026' else str(y) + '.'
    source = lambda name: R.note('Podaci: <a href="https://lusiki.github.io/HNB_Media_Attention/media/data/media/' + name + '">HNB u hrvatskim medijima</a> · siječanj 2021. - kolovoz 2026.')
    R = Report(out/'hnb-u-medijskom-prostoru.pdf', 'HNB u medijskom prostoru', 'Pregled medijskog prostora', 16, 'pregled medijske prisutnosti')
    R.cover(['HNB', 'u medijskom prostoru'], 'Koliko se HNB spominje, gdje se pojavljuje i uz koje teme',
            [(number(N), 'praćenih internetskih objava koje spominju HNB'), (number(S['outlets']), 'medijskih izvora s objavama o HNB-u'), ('68', 'mjeseci u pregledu')],
            'Pregled medijske prisutnosti kroz ključne pokazatelje, jasne usporedbe i glavne nalaze.')

    R.new('Sažetak za rukovodstvo', 'Pet nalaza za brz pregled', 'HNB se u praćenim internetskim objavama pojavljuje uz svakodnevna financijska pitanja i rad institucija. Ovi nalazi sažimaju opseg, sadržaj i raspored te prisutnosti.')
    R.sub('1. Krediti su najzastupljenije tematsko područje', f'Riječi o kreditiranju i potrošačima pojavljuju se u {pct(sc["lending"], N)} objava. Slijede euro i valute ({pct(sc["currency"], N)}) te plaćanja i gotovina ({pct(sc["payments"], N)}).')
    R.sub('2. HNB se pojavljuje u širokom krugu izvora', f'Objave o HNB-u ima {pooled["hnb_domains"]} od {pooled["background_domains"]} izvora zastupljenih u praćenim objavama cijelog razdoblja, odnosno {pct(pooled["breadth_share"], 1)}.')
    R.sub('3. Deset izvora donosi približno dvije petine objava', f'Njihov zajednički udio iznosi {pct(pooled["top_ten_share"], 1)}. Preostalih {S["outlets"]-10} izvora zajedno donosi {pct(1-pooled["top_ten_share"], 1)} objava o HNB-u.')
    R.sub('4. HNB je naveden u približno svakom šestom naslovu', f'Institucija se spominje u naslovu {number(S["title_mentions"])} objave, odnosno u {pct(S["title_mentions"], N)} svih objava o HNB-u.')
    R.sub('5. Kolovoz 2026. donosi 200 objava', 'To je osam objava manje nego u kolovozu 2025. Istodobno je udio naslova koji spominju HNB veći: 20,5% prema 16,8%.')
    R.callout('Medijsku prisutnost najjasnije opisuju zajedno: broj objava, zastupljenost među izvorima, naslov i tema.')

    R.new('Vodič kroz pokazatelje', 'Koje pitanje rješava pojedina stranica?', 'Svaki pokazatelj osvjetljava jedan dio medijske prisutnosti. Tablica povezuje poslovno pitanje s prikazom koji na njega odgovara.')
    R.table(['Pitanje', 'Što pokazuje', 'Str.'], [
        ['Koliko se HNB pojavljuje?', 'Broj objava po mjesecu i udio HNB-a u praćenim objavama.', '4-5'],
        ['O čemu se piše uz HNB?', 'Zastupljenost riječi o osam tematskih područja i njihov raspored po godinama.', '6-11'],
        ['Gdje ima najviše objava?', 'Medijski izvori poredani prema broju objava o HNB-u.', '12'],
        ['Koliki prostor pojedini izvor daje HNB-u?', 'Broj objava o HNB-u na 10.000 praćenih objava tog izvora.', '13'],
        ['Koliko je prisutnost raširena?', 'Broj izvora koji spominju HNB i raspodjela objava među njima.', '14'],
        ['Koliko je HNB vidljiv u naslovima?', 'Udio objava u kojima se HNB spominje već u naslovu.', '15'],
        ['Kako izgleda prisutnost u istom krugu izvora?', 'Usporedba svih izvora s istih 128 izvora, uz jednaku važnost svakog izvora.', '16'],
    ], [160, CW-210, 50], size=10)
    R.sub('Dva izvještaja povezuju opseg i sadržaj', 'Ovaj izvještaj prikazuje gdje i koliko se HNB pojavljuje. Izvještaj <i>HNB: od riječi do javnih pitanja</i> pokazuje koje se riječi i izrazi pojavljuju uz HNB te koliko su pojedine teme tekstualno blizu njegovu spominjanju.')

    R.new('Mjesečna prisutnost', 'Broj objava i mjesto HNB-a u ukupnoj produkciji', 'Gornji grafikon pokazuje broj praćenih objava koje spominju HNB. Donji pokazuje koliko takvih objava dolazi na 10.000 praćenih objava svih izvora. Prikaz obuhvaća siječanj 2024. - kolovoz 2026.')
    R.sub('Koliko je objava spomenulo HNB?')
    R.figure(timeline(recent, height=154), 'Mjesečni broj objava. Viša točka znači više objava koje spominju HNB.', [[r['period'], number(r['hnb_count'])] for r in recent], ['Mjesec', 'Objave o HNB-u'])
    R.sub('Koliko često se HNB pojavljuje među praćenim objavama?')
    R.figure(timeline(recent, 'rate_per_10000', height=154), 'Objave o HNB-u na 10.000 praćenih objava. Vrijednost 20 znači 20 objava o HNB-u na svakih 10.000.', [[r['period'], number(r['rate_per_10000'], 2)] for r in recent], ['Mjesec', 'Na 10.000 objava'])
    peak = max(recent, key=lambda r: r['hnb_count'])
    R.text(f'Najviše objava u ovom prikazu ima mjesec {peak["period"]}: {number(peak["hnb_count"])}. Dva grafikona povezuju količinu objava o HNB-u s njegovom zastupljenošću u ukupnoj praćenoj produkciji.')

    latest = E['latest']; now = latest['current']; yearago, prior = latest['comparisons']
    R.new('Posljednji mjesec', 'Kolovoz 2026. na jednoj stranici', 'Mjesečni pregled uspoređuje posljednji raspoloživi mjesec s istim mjesecom prethodne godine i prosjekom prethodnih dvanaest mjeseci.')
    R.table(['Pokazatelj', 'VIII. 2026.', 'VIII. 2025.', 'Prethodnih 12 mj.'], [
        ['Objave o HNB-u', number(now['hnb_count']), number(yearago['hnb_count']), number(prior['hnb_count'], 1)],
        ['HNB na 10.000 objava', number(now['rate_per_10000'], 2), number(yearago['rate_per_10000'], 2), number(prior['rate_per_10000'], 2)],
        ['HNB u naslovu', pct(now['title_share'], 1), pct(yearago['title_share'], 1), pct(prior['title_share'], 1)],
        ['Izvori koji spominju HNB', pct(now['breadth_share'], 1), pct(yearago['breadth_share'], 1), pct(prior['breadth_share'], 1)],
    ], [CW-240, 75, 75, 90], size=10)
    R.sub('Količina objava bliska je prošlogodišnjem kolovozu', f'Zabilježeno je {number(now["hnb_count"])} objava prema {number(yearago["hnb_count"])} godinu prije. HNB se pojavljuje u {number(now["rate_per_10000"], 2)} od svakih 10.000 praćenih objava.')
    R.sub('Spominjanje u naslovu češće je nego godinu prije', f'HNB je naveden u naslovu {now["title_mention_count"]} objave. Udio od {pct(now["title_share"], 1)} znači da približno svaka peta objava o HNB-u imenuje instituciju već u naslovu.')
    R.sub('Objave dolaze iz 59 izvora', f'HNB spominje {now["hnb_domains"]} od {now["background_domains"]} izvora s praćenim objavama u mjesecu. Taj podatak pokazuje širinu njegove mjesečne medijske prisutnosti.')
    R.note('Prethodnih 12 mjeseci: kolovoz 2025. - srpanj 2026.; u posljednjem stupcu prikazan je prosjek mjesečnih vrijednosti.')

    R.new('Tematska karta', 'Krediti, euro i plaćanja najčešće prate HNB', 'Stupci pokazuju koliko objava o HNB-u sadrži riječi povezane s pojedinim tematskim područjem. Postotak pokazuje njihov udio među 33.235 objava.')
    items = sorted([(labels[k], v) for k, v in sc.items()], key=lambda r: -r[1])
    R.figure(bars(items, denominator=N, height=282), 'Broj objava i udio po tematskom području. Jedna objava može povezivati više tema.', [(k, number(v), pct(v, N)) for k, v in items], ['Tematsko područje', 'Objave', 'Udio'])
    R.sub('Svakodnevne financije čine velik dio sadržaja', f'Kreditiranje i potrošači pojavljuju se u {number(sc["lending"])} objave. Euro i valute te plaćanja i gotovina također su među najzastupljenijim područjima.')
    R.callout(f'U {pct(S["multiple_tags"], N)} objava pojavljuju se riječi iz više od jednog tematskog područja.')

    R.new('Teme po godinama', 'Kako je raspoređen sadržaj pojedine godine?', 'Svako polje pokazuje postotak objava o HNB-u iz te godine koje sadrže riječi pojedinog tematskog područja. Tamnije polje znači veći udio.')
    years = [str(y) for y in range(2021, 2027)]
    totals = {y: sum(r['hnb_count'] for r in full if r['period'].startswith(y)) for y in years}
    vals = [[100*sum(r['lexical_count'] for r in D['subjects'] if r['subject_id'] == d['id'] and r['period'].startswith(y) and r['period'] <= '2026-08')/totals[y] for y in years] for d in defs]
    R.figure(heatmap([d['label_hr'] for d in defs], [*years[:-1], '2026*'], vals), 'Udio u godišnjim objavama o HNB-u, u %. *2026.: siječanj - kolovoz. Ista objava može biti zastupljena u više redaka.', [[d['label_hr']]+[number(v, 1)+'%' for v in row] for d, row in zip(defs, vals)], ['Područje']+years)
    for k in ['currency', 'prices', 'lending']:
        row = vals[[d['id'] for d in defs].index(k)]; j = max(range(6), key=lambda j: row[j])
        R.sub(labels[k], f'Najveći udio u prikazanim godišnjim objavama iznosi {number(row[j], 1)}% za razdoblje {year_label(years[j])}')

    topic_pages = [
        ('Krediti i kamate', 'Financiranje i trošak novca', ['lending', 'rates'],
         'Ova dva područja povezuju spominjanje HNB-a s kreditima, potrošačima, kamatama i monetarnom politikom.',
         [('Kreditiranje i potrošači', 'Pokazatelj okuplja objave koje uz HNB sadrže rječnik zaduživanja i potrošača. Daje pregled zastupljenosti pitanja povezanih s financiranjem i korisnicima financijskih usluga.'),
          ('Monetarna politika i kamate', 'Ovaj pokazatelj prati rječnik kamata i monetarne politike. U istom pregledu povezuje šire uvjete financiranja s pojmovima koje čitatelj susreće pri razgovoru o trošku kredita.')],
         'Kreditiranje je najzastupljenije od osam prikazanih tematskih područja.'),
        ('Euro i plaćanja', 'Valuta i svakodnevno korištenje novca', ['currency', 'payments'],
         'Valuta, gotovina i plaćanja povezuju HNB s novcem koji građani i poduzeća koriste u svakodnevnom poslovanju.',
         [('Euro i valute', 'Pokazatelj obuhvaća riječi o euru, valuti i tečaju. Njegova vrijednost pokazuje koliko je taj rječnik prisutan u objavama koje spominju HNB.'),
          ('Plaćanja i gotovina', 'Drugi pokazatelj prati riječi o gotovini i platnom prometu. Time prikazuje zastupljenost praktične strane novca: novčanica, kovanica i plaćanja.')],
         'Euro i valute te plaćanja i gotovina nalaze se među tri najzastupljenija područja.'),
        ('Cijene i gospodarska kretanja', 'Od cijena do prognoza', ['prices', 'forecasts'],
         'Ova stranica povezuje svakodnevno pitanje cijena s rječnikom gospodarskih procjena i statistike.',
         [('Cijene i inflacija', 'Pokazatelj prikazuje objave koje spominju HNB i sadrže riječi o cijenama i inflaciji. Pokazuje koliko je taj dio gospodarske rasprave zastupljen u medijskoj prisutnosti HNB-a.'),
          ('Prognoze i statistika', 'Pokazatelj prati riječi povezane s prognozama, projekcijama i statističkim podacima. Uz cijene daje pregled prostora koji u objavama zauzimaju gospodarska tumačenja.')],
         f'Riječi o cijenama i inflaciji pojavljuju se u približno svakoj trećoj objavi o HNB-u ({pct(sc["prices"], N)}).'),
        ('Institucije i odgovornost', 'Stabilnost sustava i rad institucija', ['stability', 'governance'],
         'Dva pokazatelja prikazuju rječnik financijske stabilnosti, nadzora, upravljanja i odgovornosti u objavama koje spominju HNB.',
         [('Stabilnost i nadzor', 'Pokazatelj okuplja riječi povezane sa stabilnošću bankovnog sustava i nadzorom. Prikazuje zastupljenost tog institucionalnog područja u praćenim objavama.'),
          ('Upravljanje i odgovornost', 'Pokazatelj prati rječnik rada i upravljanja institucijama, uključujući imenovanja, mandate i odgovornost. Daje pregled prisutnosti tih pojmova u sadržaju o HNB-u.')],
         f'Rječnik upravljanja i odgovornosti nalazi se u {pct(sc["governance"], N)} objava, a stabilnosti i nadzora u {pct(sc["stability"], N)}.'),
    ]
    for kicker, title, keys, lead, sections, takeaway in topic_pages:
        R.new(kicker, title, lead)
        R.table(['Tematsko područje', 'Objave', 'Udio'], [[labels[k], number(sc[k]), pct(sc[k], N)] for k in keys], [CW-155, 75, 80])
        for heading, text in sections: R.sub(heading, text)
        R.callout(takeaway)
        source('media-subjects.csv')

    R.new('Medijski izvori', 'Gdje je objavljeno najviše sadržaja o HNB-u?', 'Poredak pokazuje deset internetskih izvora s najvećim brojem praćenih objava koje spominju HNB. Svaka objava pridonosi ukupnom broju tog izvora.')
    rows = [(r['source_id'], r['hnb_count']) for r in D['sources'][:10]]
    R.figure(bars(rows, height=308, label_width=146, denominator=N), 'Broj objava i udio u svim praćenim objavama o HNB-u.', [(k, number(v), pct(v, N)) for k, v in rows], ['Izvor', 'Objave', 'Udio'])
    R.sub('Vodeći izvor ima 5,1% svih objava', f'{rows[0][0]} objavio je {number(rows[0][1])} objave o HNB-u. Prikazanih deset izvora zajedno ima {number(sum(v for _, v in rows))} objavu, odnosno {pct(pooled["top_ten_share"], 1)} ukupnog broja.')
    R.text('Ovaj poredak odgovara na pitanje gdje se nalazi najveći broj objava. Sljedeća stranica prikazuje koliki dio vlastite praćene produkcije pojedini izvor posvećuje HNB-u.')

    rates = sorted([r for r in E['source_rates'] if r['period_id'] == 'pooled' and r['eligible']], key=lambda r: r['rank'])[:10]
    R.new('Pozornost pojedinog izvora', 'Koliki prostor izvor daje HNB-u?', 'Intenzitet pozornosti pokazuje koliko objava o HNB-u dolazi na 10.000 praćenih objava istog izvora. Viša vrijednost znači veći udio HNB-a u njegovoj produkciji. Prikazano je prvih deset izvora iz usporednog poretka.')
    R.table(['Izvor', 'Objave o HNB-u', 'Na 10.000 objava'], [[r['source_id'], number(r['hnb_count']), number(r['rate_per_10000'], 1)] for r in rates], [CW-220, 105, 115])
    r = rates[0]
    R.sub('Kako pročitati prvi redak', f'Za {r["source_id"]} vrijednost {number(r["rate_per_10000"], 1)} znači približno {number(r["rate_per_10000"])} objava o HNB-u na svakih 10.000 praćenih objava tog izvora.')
    R.callout('Broj objava pokazuje količinu. Intenzitet pokazuje koliki udio vlastitog prostora izvor daje HNB-u.')

    R.new('Širina i raspodjela', 'Prisutnost je široka, a objave neravnomjerno raspoređene', f'Tijekom cijelog razdoblja HNB se pojavljuje u {pooled["hnb_domains"]} od {pooled["background_domains"]} izvora s praćenim objavama. Tablica pokazuje širinu prisutnosti u svakoj godini.')
    R.table(['Razdoblje', 'Izvori s HNB-om', 'Praćeni izvori', 'Udio'], [[year_label(r['period_id']), number(r['hnb_domains']), number(r['background_domains']), pct(r['breadth_share'], 1)] for r in annual], [CW-245, 90, 85, 70])
    stable = next(r for r in E['concentration'] if r['period_id'] == 'pooled' and r['scope'] == 'stable')
    R.sub('Širina: u koliko se izvora HNB pojavljuje?', f'U cijelom razdoblju udio iznosi {pct(pooled["breadth_share"], 1)}. U stalnoj skupini od 128 izvora HNB se pojavljuje u njih {stable["hnb_domains"]}, odnosno {pct(stable["breadth_share"], 1)}.')
    R.sub('Koncentracija: gdje je smještena većina objava?', f'Pet izvora s najviše objava zajedno ima {pct(pooled["top_five_share"], 1)}, a deset najvećih {pct(pooled["top_ten_share"], 1)} svih objava o HNB-u.')
    R.sub('Efektivni broj izvora: raspodjela izražena jednim brojem', f'Vrijednost {number(pooled["effective_domains"], 1)} znači da zabilježena raspodjela ima jednaku koncentraciju kao približno 38 jednako zastupljenih izvora. Veća vrijednost označava ravnomjerniju raspodjelu objava.')

    title_rows = [dict(r, title_percent=100*r['title_mention_count']/r['hnb_count']) for r in recent]
    R.new('HNB u naslovima', 'Institucija je u naslovu približno svake šeste objave', f'HNB je naveden u naslovu {number(S["title_mentions"])} od {number(N)} objava, odnosno {pct(S["title_mentions"], N)}. Pokazatelj izravno opisuje koliko često čitatelj susreće naziv institucije već u naslovu.')
    R.figure(timeline(title_rows, 'title_percent', height=175), 'Mjesečni udio objava o HNB-u koje spominju HNB u naslovu, u %. Siječanj 2024. - kolovoz 2026.', [[r['period'], pct(r['title_mention_count'], r['hnb_count'])] for r in recent], ['Mjesec', 'HNB u naslovu'])
    R.table(['Razdoblje', 'Naslovi s HNB-om', 'Udio objava'], [[year_label(r['period_id']), number(r['title_mention_count']), pct(r['title_share'], 1)] for r in annual], [CW-235, 125, 110])
    R.text('U kolovozu 2026. udio iznosi 20,5%. To znači da je naziv HNB-a prisutan u naslovu približno svake pete objave koja ga spominje.')

    stable_months = {r['period']: r for r in E['monthly'] if r['scope'] == 'stable'}
    comparison = [dict(r, fixed_weight_rate=stable_months[r['period']]['fixed_weight_rate']) for r in recent]
    last = comparison[-1]
    R.new('Usporediv krug izvora', 'Tri pogleda na medijsku pozornost', 'Ukupna pozornost opisuje sve praćene izvore. Stalna skupina prati istih 128 izvora kroz vrijeme. Indeks s jednakom težinom izvora daje svakom članu te skupine jednak udio u rezultatu.')
    R.figure(timeline(comparison, 'rate_per_10000', height=186, series=[('stable_rate_per_10000', COPPER), ('fixed_weight_rate', '#59734A')]), 'Objave o HNB-u na 10.000 praćenih objava. Plavo: svi izvori. Narančasto: stalna skupina. Zeleno: ista skupina, jednaka težina svakog izvora. Siječanj 2024. - kolovoz 2026.', [[r['period'], number(r['rate_per_10000'], 2), number(r['stable_rate_per_10000'], 2), number(r['fixed_weight_rate'], 2)] for r in comparison], ['Mjesec', 'Svi izvori', 'Stalna skupina', 'Jednake težine'])
    R.table(['Kolovoz 2026.', 'Na 10.000 objava'], [['Svi praćeni izvori', number(last['rate_per_10000'], 2)], ['Stalna skupina od 128 izvora', number(last['stable_rate_per_10000'], 2)], ['Stalna skupina, jednaka težina svakog izvora', number(last['fixed_weight_rate'], 2)]], [CW-120, 120])
    R.text('Usporedba pokazuje kako se slika pozornosti mijenja kada pratimo isti krug izvora i kada veći i manji izvori imaju jednaku važnost. Sva tri prikaza koriste istu mjeru: objave o HNB-u na 10.000 praćenih objava.')
    R.note('Povezani izvještaj: <a href="hnb-od-rijeci-do-javnih-pitanja.html">HNB: od riječi do javnih pitanja</a>. Podaci i izvještaji: <a href="https://lusiki.github.io/HNB_Media_Attention/media/hr.html">HNB u hrvatskim medijima</a>.')
    return R.save()
