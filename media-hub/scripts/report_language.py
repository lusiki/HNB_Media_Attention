"""Fourteen-page executive reading of the published language indicators."""
import json
from report_layout import *
from reportlab.graphics.shapes import Group


def language(out, D, L):
    N = L['distinct_normalized_bodies']; T = L['terms']; G = L['groups']; P = L['phrases']
    defs = D['subject_definitions']; labels = {d['id']: d['label_hr'] for d in defs}
    E = json.loads((ROOT/'media-hub/public/data/media/lexical-extensions.json').read_text(encoding='utf-8'))
    R = Report(out/'hnb-od-rijeci-do-javnih-pitanja.pdf', 'HNB: od riječi do javnih pitanja', 'Jezik i javna pitanja', 14, 'pregled jezika i javnih pitanja')
    R.cover(['HNB', 'Od riječi do javnih pitanja'], 'Koje riječi prate HNB i što otkrivaju o sadržaju objava',
            [(number(N), 'različitih tekstova u jezičnom pregledu'), ('8', 'tematskih područja'), ('12', 'izdvojenih izraza')],
            'Rječnik medijske prisutnosti: od banaka i eura do kredita, cijena i rada institucija.')

    R.new('Sažetak za rukovodstvo', 'Četiri nalaza o jeziku uz HNB', 'Pokazatelji prate riječi u naslovima koji imenuju HNB i u dijelovima teksta koji ga spominju. Broj uz riječ pokazuje u koliko se različitih tekstova ona pojavljuje u tom kontekstu.')
    R.sub('Banke, euro i guverner vode među praćenim pojmovima', f'Banka se pojavljuje u {number(T["banka"])} tekstova, euro u {number(T["euro"])} i guverner u {number(T["guverner"])}. Ti pojmovi povezuju financijski sustav, valutu i instituciju.')
    R.sub('Svakodnevne financije imaju prepoznatljiv rječnik', f'Građanin se pojavljuje u {number(T["građanin"])} tekstova, kredit u {number(T["kredit"])} i cijena u {number(T["cijena"])}. Ti izrazi pokazuju prisutnost jezika osobnih financija u sadržaju uz HNB.')
    R.sub('Uvođenje eura i kamatna stopa vode među izrazima', f'Izraz uvođenje eura nalazi se u {number(P["uvođenje eura"])} tekstova, a kamatna stopa u {number(P["kamatna stopa"])}. Višerječni izrazi jasnije imenuju konkretno javno pitanje.')
    R.sub('Teme imaju različitu blizinu spominjanju HNB-a', 'Među tekstovima s riječima o plaćanjima i gotovini, 54,5% sadrži te riječi i u dijelovima koji spominju HNB. Za kreditiranje taj udio iznosi 47,5%, a za cijene i inflaciju 45,7%.')
    R.callout('Riječi pokazuju sadržaj. Izrazi ga pobliže određuju. Njihova blizina spominjanju HNB-a pokazuje tekstualnu povezanost.')
    R.note('Vodič: riječi na str. 3; teme na str. 4-7; izrazi na str. 8-11; blizina tema HNB-u na str. 12; kretanje kroz vrijeme na str. 13; sažeti pregled na str. 14.')

    R.new('Rječnik uz HNB', 'Banke, euro i institucije u središtu rječnika', 'Oblak prikazuje najčešće praćene riječi uz HNB. Veća riječ znači da se pojavljuje u većem broju različitih tekstova. Tablica izdvaja tri vodeća pojma.')
    items = list(T.items())[:32]
    R.figure(cloud(items, height=245, max_words=32), 'Najčešća 32 od 52 praćena pojma. Veličina riječi predstavlja broj tekstova u kojima se pojavljuje uz HNB.', [(k, number(v), pct(v, N)) for k, v in items], ['Pojam', 'Tekstovi', 'Udio'])
    R.table(['Pojam', 'Tekstovi', 'Udio od 33.100'], [[k, number(T[k]), pct(T[k], N)] for k in ['banka', 'euro', 'guverner']], [CW-190, 90, 100])
    R.sub('Kako pročitati broj', f'Vrijednost {number(T["euro"])} uz riječ euro znači da se ona pojavljuje uz HNB u toliko različitih tekstova. Udio od {pct(T["euro"], N)} pokazuje njezinu zastupljenost u cijelom jezičnom pregledu.')

    R.new('Teme uz HNB', 'Krediti, plaćanja i valuta vode i u bližem kontekstu', 'Stupci prikazuju broj tekstova u kojima se riječi pojedinog tematskog područja pojavljuju u dijelovima koji spominju HNB, uključujući naslov. Tako se vidi sadržaj neposredno uz naziv institucije.')
    items = sorted([(labels[k], g['n']) for k, g in G.items()], key=lambda r: -r[1])
    R.figure(bars(items, height=280, denominator=N), 'Tekstovi s tematskim riječima uz HNB i njihov udio među 33.100 različitih tekstova. Isti tekst može povezivati više područja.', [(k, number(v), pct(v, N)) for k, v in items], ['Područje', 'Tekstovi', 'Udio'])
    R.sub('Kreditiranje je vodeće područje', f'Riječi o kreditiranju i potrošačima nalaze se uz HNB u {number(G["lending"]["n"])} tekstova. Slijede plaćanja i gotovina s {number(G["payments"]["n"])} te euro i valute s {number(G["currency"]["n"])} tekstom.')
    R.text('Medijski pregled opisuje teme u cijelim objavama. Ovaj prikaz približava pogled dijelovima u kojima se HNB izričito spominje. Na sljedećim stranicama svako je područje prikazano kroz svoj najčešći rječnik.')

    def four_clouds(keys):
        d = Drawing(CW, 420); rows = []
        short = {'prices': 'Cijene i inflacija', 'rates': 'Monetarna politika i kamate', 'lending': 'Kreditiranje i potrošači', 'forecasts': 'Prognoze i statistika', 'currency': 'Euro i valute', 'payments': 'Plaćanja i gotovina', 'stability': 'Stabilnost i nadzor', 'governance': 'Upravljanje i odgovornost'}
        for i, k in enumerate(keys):
            x = (i % 2)*(CW/2+8); yy = 420-(i//2)*210; w = CW/2-12; g = G[k]
            d.add(String(x, yy-12, short[k], fontName='Bold', fontSize=11, fillColor=HexColor(INK)))
            d.add(String(x, yy-29, number(g['n'])+' tekstova', fontName='Sans', fontSize=9, fillColor=HexColor(MUTED)))
            items = list(g['terms'].items())[:15]
            group = Group(); group.add(cloud(items, width=w, height=140, max_words=15)); group.translate(x, yy-174); d.add(group)
            top = ' · '.join(f'{a} {number(b)}' for a, b in items[:2])
            d.add(String(x, yy-196, top, fontName='Sans', fontSize=8.9, fillColor=HexColor(MUTED)))
            rows.extend([[short[k], a, number(b)] for a, b in items])
        return d, rows

    R.new('Kućanstva i gospodarstvo', 'Jezik troškova, kredita i gospodarskih procjena', 'Četiri oblaka izdvajaju riječi uz HNB u području cijena, kamata, kreditiranja i prognoza. Svaki oblak ima vlastiti tematski naglasak.')
    d, rows = four_clouds(['prices', 'rates', 'lending', 'forecasts'])
    R.figure(d, 'Veća riječ znači veću zastupljenost unutar prikazanog područja. Ispod svakog oblaka navedena su dva vodeća pojma i broj tekstova.', rows, ['Područje', 'Pojam', 'Tekstovi'])
    R.text('Cijene i inflacija povezuju se s rječnikom rasta. Kreditiranje okuplja banku, potrošača i kamatu. Prognoze izdvajaju inflaciju, projekciju i BDP. Prikaz tako povezuje osobni trošak s odlukama o financiranju i gospodarskim očekivanjima.')

    R.new('Novac i institucije', 'Od eura i gotovine do stabilnosti i upravljanja', 'Četiri područja prikazuju jezik valute, korištenja novca i rada institucija. Zajedničke riječi povezuju ih u širu sliku sadržaja uz HNB.')
    d, rows = four_clouds(['currency', 'payments', 'stability', 'governance'])
    R.figure(d, 'Najčešći praćeni pojmovi unutar svakog područja. Broj ispod naslova pokazuje koliko tekstova pripada tom tematskom prikazu.', rows, ['Područje', 'Pojam', 'Tekstovi'])
    R.text('Euro, kuna i kovanica izdvajaju jezik valute i gotovine. Stabilnost okuplja rizik, kapital i kredit. Guverner, savjet i Sabor povezuju rječnik s radom institucija. Svaki oblak daje brz uvid u prepoznatljive riječi svojeg područja.')

    R.new('Povezanost rječnika', 'Četiri pojma kroz osam područja', 'Tablica pokazuje koliko se često banka, guverner, građanin i euro pojavljuju uz HNB u tekstovima pojedinog tematskog područja. Tamnije polje znači veći postotak.')
    keys = [d['id'] for d in defs]; words = ['banka', 'guverner', 'građanin', 'euro']
    values = [[100*G[k]['terms'].get(w, 0)/G[k]['n'] for w in words] for k in keys]
    R.figure(heatmap([labels[k] for k in keys], words, values, height=294), 'Postotak tekstova unutar svakog područja koji uz HNB sadrže prikazani pojam.', [[labels[k]]+[number(v, 1)+'%' for v in row] for k, row in zip(keys, values)], ['Područje']+words)
    for word in ['građanin', 'guverner']:
        j = words.index(word); i = max(range(len(keys)), key=lambda i: values[i][j])
        R.sub('Gdje je najzastupljeniji pojam '+word+'?', f'Najveći udio ima područje {labels[keys[i]].lower()}: {number(values[i][j], 1)}% njegovih tekstova sadrži taj pojam uz HNB.')
    R.text('Prikaz povezuje institucionalni rječnik s riječima koje označavaju građane i svakodnevni novac. Svaki redak daje sažet jezični profil jednog područja.')

    R.new('Izrazi', 'Uvođenje eura i kamatna stopa najčešći su izrazi', 'Izrazi od više riječi jasnije imenuju predmet razgovora. Stupci pokazuju njihovu zastupljenost u dijelovima tekstova koji spominju HNB.')
    items = list(P.items())
    R.figure(bars(items, height=333, denominator=N), 'Dvanaest praćenih izraza: broj tekstova i udio među 33.100 različitih tekstova.', [(a, number(b), pct(b, N)) for a, b in items], ['Izraz', 'Tekstovi', 'Udio'])
    R.sub('Od opće riječi prema konkretnom pitanju', 'Euro imenuje valutu, a uvođenje eura proces. Kredit imenuje financijski proizvod, a stambeni kredit njegovu namjenu. Financijska stabilnost imenuje stanje sustava, a zaštita potrošača javni cilj povezan s korisnicima.')
    R.text('Sljedeće tri stranice povezuju ove izraze s javnim pitanjima o novcu, zaduživanju i institucijama.')

    R.new('Valuta i svakodnevni novac', 'Uvođenje eura daje jasan sadržaj općoj riječi euro', 'Rječnik valute obuhvaća i naziv novca i pojmove njegove svakodnevne uporabe. Ovaj prikaz povezuje glavne riječi s izrazima koji određuju konkretniji sadržaj.')
    R.table(['Pojam ili izraz', 'Tekstovi uz HNB', 'Udio'], [[k, number(v), pct(v, N)] for k, v in [('euro', T['euro']), ('kuna', T['kuna']), ('kovanica', T['kovanica']), ('uvođenje eura', P['uvođenje eura']), ('novčanica', T['novčanica']), ('gotovina', T['gotovina']), ('platni promet', P['platni promet']), ('digitalni euro', P['digitalni euro'])]], [CW-195, 115, 80])
    R.sub('Što pokazuje odnos riječi i izraza?', f'Euro se pojavljuje uz HNB u {number(T["euro"])} tekstova, a uvođenje eura u {number(P["uvođenje eura"])}. Prvi broj opisuje širinu prisutnosti valute, a drugi zastupljenost posebno imenovanog procesa.')
    R.callout('Riječi o novčanicama, kovanicama i gotovini čine svakodnevnu stranu rječnika o valuti.')

    R.new('Krediti i potrošači', 'Od kredita do vrste kredita i mogućnosti zaduživanja', 'Kreditni rječnik povezuje proizvod, cijenu financiranja i korisnika. Višerječni izrazi izdvajaju namjenu kredita, kreditnu sposobnost i zaštitu potrošača.')
    R.table(['Pojam ili izraz', 'Tekstovi uz HNB', 'Udio'], [[k, number(v), pct(v, N)] for k, v in [('kredit', T['kredit']), ('kamata', T['kamata']), ('potrošač', T['potrošač']), ('kamatna stopa', P['kamatna stopa']), ('stambeni kredit', P['stambeni kredit']), ('zaštita potrošača', P['zaštita potrošača']), ('gotovinski kredit', P['gotovinski kredit']), ('kreditna sposobnost', P['kreditna sposobnost'])]], [CW-195, 115, 80])
    R.sub('Koji izrazi najjasnije određuju predmet razgovora?', f'Stambeni kredit pojavljuje se u {number(P["stambeni kredit"])} tekstova, gotovinski kredit u {number(P["gotovinski kredit"])}, a kreditna sposobnost u {number(P["kreditna sposobnost"])}. Ti izrazi usmjeravaju čitanje prema vrsti zaduženja i mogućnosti njegova odobravanja.')
    R.callout('Kamatna stopa jedan je od dvaju najčešćih praćenih izraza uz HNB.')

    R.new('Institucionalni rječnik', 'Funkcije, nadzor i stabilnost', 'Ovi pojmovi izdvajaju institucionalnu stranu sadržaja uz HNB: tko se imenuje, koja se tijela spominju i kojim se riječima opisuje financijski sustav.')
    selected = ['guverner', 'Vlada', 'Sabor', 'savjet', 'nadzor', 'rizik', 'stabilnost', 'odgovornost']
    R.table(['Pojam', 'Tekstovi uz HNB', 'Udio'], [[k, number(T[k]), pct(T[k], N)] for k in selected], [CW-195, 115, 80])
    R.sub('Guverner je među vodećim pojmovima cijelog pregleda', f'Pojavljuje se u {number(T["guverner"])} tekstova, odnosno u {pct(T["guverner"], N)}. Vlada, Sabor i savjet dodatno opisuju institucionalni rječnik prisutan uz HNB.')
    R.sub('Višerječni izraz pobliže određuje institucionalno pitanje', f'Financijska stabilnost pojavljuje se u {number(P["financijska stabilnost"])} tekstova. Izraz povezuje opću riječ stabilnost s financijskim sustavom i daje precizniji opis sadržaja.')
    R.note('Broj uz pojam označava tekstove u kojima se on pojavljuje u dijelovima koji spominju HNB.')

    R.new('Blizina teme HNB-u', 'Koliko se tema pojavljuje baš uz spominjanje HNB-a?', 'Tablica uspoređuje prisutnost tematskih riječi u cijelom tekstu s njihovom prisutnošću u rečenicama koje spominju HNB. Uspoređuje iste tekstove, pa udio pokazuje koliko je tema tekstualno blizu instituciji.')
    R.table(['Tematsko područje', 'U tekstu', 'Uz HNB', 'Udio'], [[r['label_hr'], number(r['whole_yes']), number(r['both_yes']), pct(r['both_yes'], r['whole_yes'])] for r in E['linkage']], [CW-205, 75, 65, 65], size=9.5)
    payments = next(r for r in E['linkage'] if r['subject_id'] == 'payments')
    R.sub('Primjer: plaćanja i gotovina', f'Riječi ovog područja pojavljuju se u {number(payments["whole_yes"])} tekstova. U {number(payments["both_yes"])} tih tekstova nalaze se i u rečenicama koje spominju HNB. Zato udio iznosi {pct(payments["linkage"], 1)}.')
    R.callout('Veći udio znači da se riječi određene teme češće pojavljuju u dijelovima teksta koji imenuju HNB.')
    R.note('Ovaj prikaz uspoređuje tekst članaka. Tematski pregled na str. 4 obuhvaća i njihove naslove.')

    R.new('Riječi kroz vrijeme', 'Kako se mijenja zastupljenost pojedine riječi?', 'Udio pokazuje koliko tekstova pojedinog tromjesečja sadrži riječ uz HNB. Grafikon uspoređuje inflaciju i kredit od početka 2024. do drugog tromjesečja 2026.')
    quarters = sorted({r['quarter'] for r in E['quarterly'] if '2024-Q1' <= r['quarter'] <= '2026-Q2'})
    qindex = {(r['quarter'], r['term']): r for r in E['quarterly'] if r['kind'] == 'term'}
    trends = [dict(period=q, inflacija=100*qindex[q, 'inflacija']['frequency'], kredit=100*qindex[q, 'kredit']['frequency']) for q in quarters]
    R.figure(timeline(trends, 'inflacija', height=168, series=[('kredit', COPPER)]), 'Udio tekstova u tromjesečju, u %. Plavo: inflacija. Narančasto: kredit.', [[q['period'], number(q['inflacija'], 1)+'%', number(q['kredit'], 1)+'%'] for q in trends], ['Tromjesečje', 'Inflacija', 'Kredit'])
    selected = ['banka', 'kredit', 'euro', 'inflacija', 'kamata', 'građanin', 'guverner']
    rows = [qindex['2026-Q2', term] for term in selected]
    R.sub('Drugo tromjesečje 2026.: odabrani pojmovi')
    R.table(['Pojam', 'Tekstovi', 'Udio od 1.392'], [[r['term'], number(r['count']), pct(r['count'], r['denominator'])] for r in rows], [CW-180, 80, 100], size=9.6)
    R.text('U drugom tromjesečju 2026. inflacija se pojavljuje uz HNB u 24,2% tekstova, a kredit u 17,2%. Postotak pokazuje mjesto svake riječi u sadržaju tog razdoblja.')

    R.new('Pregled na jednoj stranici', 'Što govori svaki jezični pokazatelj?', 'Zajedno, pokazatelji opisuju rječnik uz HNB, teme kojima taj rječnik pripada i njegov raspored kroz vrijeme.')
    R.table(['Pokazatelj', 'Kako ga pročitati', 'Nalaz iz izvještaja'], [
        ['Učestalost riječi', 'U koliko se tekstova riječ pojavljuje uz HNB?', f'Banka: {number(T["banka"])} tekstova.'],
        ['Tematsko područje', 'Koje se tematske riječi pojavljuju u dijelovima koji spominju HNB?', f'Kreditiranje i potrošači: {number(G["lending"]["n"])} tekstova.'],
        ['Rječnik po područjima', 'Koje riječi prevladavaju unutar pojedinog područja?', 'Oblaci izdvajaju rječnik svih osam područja.'],
        ['Višerječni izraz', 'Koliko je zastupljeno posebno imenovano javno pitanje?', f'Uvođenje eura: {number(P["uvođenje eura"])} tekstova.'],
        ['Blizina teme HNB-u', 'Koliki dio tekstova s temom sadrži njezine riječi baš uz HNB?', 'Plaćanja i gotovina: 54,5%.'],
        ['Tromjesečni udio', 'Koliki dio tekstova razdoblja sadrži riječ uz HNB?', 'Inflacija: 24,2% u drugom tromjesečju 2026.'],
    ], [123, 220, CW-343], size=10)
    R.callout('Medijska prisutnost dobiva sadržaj kada broj objava povežemo s riječima i konkretnim javnim pitanjima.')
    R.note('Povezani izvještaj: <a href="hnb-u-medijskom-prostoru.html">HNB u medijskom prostoru</a>. Podaci i izvještaji: <a href="https://lusiki.github.io/HNB_Media_Attention/media/hr.html">HNB u hrvatskim medijima</a>.')
    return R.save()
