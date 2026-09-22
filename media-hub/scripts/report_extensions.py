"""Shared extension pages for the established report pair."""
import json
from pathlib import Path
from report_layout import number,pct,CW
DATA=Path(__file__).resolve().parents[1]/'public/data/media'
def language_pages(R):
    d=json.loads((DATA/'lexical-extensions.json').read_text(encoding='utf-8'))
    R.new('Dodatak 1.1 / ista jedinica','Koliko se tema zadržava uz HNB?','Usporedba primjenjuje istih osam obrazaca na cijeli tekst i na njegove odsječke koji izričito spominju HNB. Jedinica je isti različiti tekst, a naslovi su isključeni iz oba pogleda.')
    R.table(['Skup','Cijeli tekst','I uz HNB','Udio'],[[r['label_hr'],number(r['whole_yes']),number(r['both_yes']),pct(r['both_yes'],r['whole_yes'])] for r in d['linkage']],[CW-205,75,65,65],size=9.5)
    R.text(f'Svih {number(d["body_population"])} tekstova ima prihvatljiv lokalni kontekst u tijelu. Broj podudaranja samo lokalno, bez podudaranja u cijelom tekstu, jednak je nuli u svih osam skupova. Izostavljeno je 99 objava bez tijela prije uklanjanja jednakih tekstova.')
    R.text('Povezanost je udio podudaranja iz cijeloga teksta koja se nalaze i uz HNB. Skupovi se preklapaju. Lokalno podudaranje nije dokaz da je HNB autor iskaza, da je tema glavna ili da tekst objašnjava politiku.')
    R.note('Izvor: media-subject-linkage.csv i lexical-extensions.json. Četiri ćelije, nazivnici i obuhvat dostupni su na mreži. HNB_MEDIA_LEXICAL_1.1; podaci 2026-09-21.1. Neovisna ljudska validacija nije dovršena.')
    R.new('Dodatak 1.1 / tromjesečni rječnik','Riječi kroz vrijeme, s jasnim nazivnikom','U 23 prikazana tromjesečja spremljene su frekvencije 52 pojma i 12 izraza: ukupno 1.472 ćelije. Posljednje potpuno tromjesečje jest drugo tromjesečje 2026.; treće sadrži samo srpanj i kolovoz.')
    selected=['banka','kredit','euro','inflacija','kamata','građanin','guverner','statistika']
    rows=[next(r for r in d['quarterly'] if r['quarter']=='2026-Q2' and r['kind']=='term' and r['term']==term) for term in selected]
    R.table(['Pojam · 2026 Q2','Tekstovi','Nazivnik','Udio'],[[r['term'],number(r['count']),number(r['denominator']),'ispod praga' if r['frequency'] is None else pct(r['count'],r['denominator'])] for r in rows],[CW-205,65,70,70],size=10)
    R.text('Odabranih osam pojmova ilustrira čitanje tablice; to nije rang promjena. Mrežni prikaz omogućuje izbor svakog pojma i izraza. Izričito spominjanje u naslovu i rečenični odsječci slijede izvorni kontekst metode 1.0; ta se definicija razlikuje od usporedbe tijela na prethodnoj stranici.')
    R.text('Svaki različiti tekst ulazi najviše jednom u tromjesečje. Isti tekst u dvama tromjesečjima ulazi u oba; zato se tromjesečni nazivnici ne zbrajaju u 33.100 različitih tekstova cijelog razdoblja. Promjena prikupljanja u siječnju 2024. ostaje granica usporedbe.')
    R.note('Pozitivni brojevi manji od 30 nemaju prikazani udio; stvarna nula ostaje nula. Nazivnik manji od 30 nema stopu. Izvor: media-lexical-quarterly.csv. Sve frekvencije metode 1.0 ponovno su reproducirane. Audit 200 objava bez tematskog podudaranja priprema se za kodiranje; nije dovršena klasifikacija.')
def overview_pages(R,D):
    ext=D['extensions'];p=next(r for r in ext['concentration'] if r['period_id']=='pooled' and r['scope']=='all')
    R.new('Dodatak / pokazatelji arhiva','Broj, širina i koncentracija odgovaraju na različita pitanja','Nova pokazateljska specifikacija zadržava korpus 2026-09-21.1. Mijenja dostupne usporedbe, a ne broj uključenih objava.')
    R.table(['Pokazatelj','Vrijednost · 2021-01/2026-08'],[
      ['Efektivni broj domena',number(p['effective_domains'],2)],['Udio deset najvećih domena',pct(p['top_ten_share'],1)],['Domene s HNB objavama / pozadinske domene',f'{p["hnb_domains"]} / {p["background_domains"]}'],['Spominjanje u naslovu',f'{number(p["title_mention_count"])} / {number(p["hnb_count"])}'],['Domene iznad oba praga za rang stope','78']],[CW*.58,CW*.42])
    R.text('Efektivni broj jest inverz zbroja kvadrata udjela objava po domeni. To je koncentracija domena, bez tvrdnje o vlasništvu ili raznolikosti stajališta. Godišnji obuhvat koristi uniju domena, a godišnji udio naslova omjer zbrojeva.')
    R.text('Rang stope na 10.000 objava zahtijeva najmanje 5.000 pozadinskih objava i 50 objava o HNB-u s istim filtrom. Mrežna tablica nudi cijelo razdoblje, 2021.-2023. i 2024.-kolovoz 2026. Izvori ispod praga ostaju izvan ranga stope.')
    R.note('V5-V7; HNB_MEDIA_INDICATORS_1.0. Izvori: media-source-concentration.csv, media-source-rates.csv i media-indicators-monthly.csv. Naslov je mehanička oznaka, bez neovisno potvrđene istaknutosti institucije.')
    R.new('Dodatak / usporedbe i jezik','Što mijenjaju sastav izvora i lokalni kontekst?','Usporedba triju mjesečnih stopa razdvaja cjelokupni opaženi skup, stalni panel od 128 izvora i isti panel s jednakim stalnim ponderom 1/128.')
    R.text('Stalni ponderi sprječavaju da promjena udjela pojedinog izvora sama određuje panelnu stopu. Ako nedostaje nazivnik bilo kojeg člana ili je nula, rezultat nije dostupan; nema preponderiranja ni imputacije nule. Granica prikupljanja iz siječnja 2024. i dalje vrijedi.')
    R.sub('Posljednji potpuni mjesec','Kolovoz 2026. sadrži 200 HNB objava prema 208 u kolovozu 2025. Stopa je 13,65 prema 15,34 na 10.000. Dodatna usporedba koristi aritmetički prosjek dvanaest prethodnih mjesečnih stopa, bez tekućeg mjeseca. To nije sezonska prilagodba.')
    R.sub('Veza s jezičnim izvještajem','Usporedba na istih 33.100 različitih tekstova nalazi da se, ovisno o skupini, 36,4%-54,5% podudaranja iz cijelog tijela nalazi i u odsječcima uz HNB. Jezični izvještaj donosi svih osam rezultata i tromjesečne frekvencije 52 pojma i 12 izraza. Lokalna prisutnost riječi ne potvrđuje autorstvo ni funkciju poruke.')
    R.note('Izvori: media-fixed-weight-components.csv, media-latest-edition.json, media-subject-linkage.csv. Izdanje prikaza 2026-09-22.1. Novi pokazatelji ostaju opisni; plan neovisnog kodiranja, klastera i službenih poruka ima zasebne uvjete objave.')
