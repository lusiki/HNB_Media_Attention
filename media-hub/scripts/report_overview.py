"""Fourteen-page Croatian descriptive overview, derived from public aggregates."""
from report_layout import *

def overview(out,D):
    S=D['summary'];N=S['hnb_publications'];full=[r for r in D['monthly'] if r['period']<='2026-08']
    defs=D['subject_definitions'];labels={d['id']:d['label_hr'] for d in defs};sc=S['subject_counts']
    link=lambda file,label:f'<a href="https://lusiki.github.io/HNB_Media_Attention/media/{file}" color="#2454CF">{label}</a>'
    src=lambda file:link('data/media/'+file,file)
    R=Report(out/'hnb-u-medijskom-prostoru.pdf','HNB u medijskom prostoru','Pregled medijskog prostora',14,'opisni pregled')
    R.cover(['HNB','u medijskom prostoru'],'Novac, svakodnevne potrebe i javna odgovornost',[(number(N),'objava s izričitim spominjanjem'),(number(S['outlets']),'registrirani medijski izvori'),('68','punih mjeseci praćenja')],'Gdje se pojavljuje Hrvatska narodna banka, koje je teme prate i kako čitati njezinu medijsku prisutnost.')

    R.new('Ključni nalazi','Institucija se pojavljuje kroz više javnih pitanja','Medijska slika HNB-a obuhvaća kreditiranje, valutu, cijene, platne usluge i rasprave o odgovornosti. Pregled povezuje veličinu te prisutnosti s mjestima i temama u kojima je zabilježena.')
    R.sub('Krediti su najrašireniji od osam praćenih tematskih skupova',f'Riječi povezane s kreditiranjem i potrošačima prisutne su u {number(sc["lending"])} objave ({pct(sc["lending"],N)}). Slijede euro i valute s {number(sc["currency"])} te plaćanja i gotovina s {number(sc["payments"])} objava. To su preklapajuće oznake: ista vijest može govoriti o kreditu, kamati i inflaciji.')
    R.sub('Prisutnost je raspoređena preko mnogo izvora',f'Pet izvora s najvećim brojem objava zajedno čini {pct(sum(r["hnb_count"] for r in D["sources"][:5]),N)} uzorka. Nijedan ne prelazi {pct(D["sources"][0]["hnb_count"],N)}. Taj raspored opisuje objavljivanje u arhivu, bez mjerenja publike, čitanosti ili vlasničkih veza.')
    R.sub('Velik broj objava može imati različite povode','U siječnju 2022. među zabilježenim sadržajima nalazimo raspravu o odgovornosti zaposlenika HNB-a. U siječnju 2023. ističu se praktična pitanja zamjene valute. U veljači 2025. HNB se pojavljuje i u raspravi potrošača o cijenama. Odabrani portreti pokazuju raznolikost sadržaja, a ne dokazuju što je prouzročilo mjesečni broj objava.')
    R.callout('Broj spominjanja otvara pitanje o sadržaju. Sam po sebi ne govori je li institucija objašnjavala, bila kritizirana ili samo navedena.')
    R.note('Kako čitati izvještaj: podaci i vrijeme na str. 3-5; teme na str. 6-11; izvori i osjetljivost na str. 12-13; izvori podataka i daljnje čitanje na str. 14.')

    R.new('O podacima','Od arhivskog zapisa do medijske objave','Osnovna jedinica je objava na internetskoj domeni. Ako isti članak sustav zabilježi više puta, ti se zapisi povezuju u jednu objavu. Isti sadržaj objavljen na različitim portalima ostaje više objava.')
    R.table(['Korak','Što je učinjeno'],[
      ['Odabir izvora','Uključene su uredničke web publikacije čija domena točno odgovara aktualnom upisniku Agencije za elektroničke medije, provjerenom 21. 9. 2026.'],
      ['Pronalaženje HNB-a','U naslovu i pohranjenom tekstu traži se kratica HNB ili hrvatski odnosno engleski naziv institucije. Uključeni su odgovarajući gramatički oblici.'],
      ['Povezivanje zapisa','Identitet objave temelji se na domeni i normaliziranoj adresi članka. Zadržava se najdulji pohranjeni tekst, a datum je najraniji zabilježeni datum.'],
      ['Provjera teksta','Nakon dokumentiranog uklanjanja dijela povezanih sadržaja i dodataka ponovno se provjerava postoji li izričito spominjanje u zadržanom tekstu.'],
      ['Opis rezultata','Prikazuju se broj objava, izvori, mjesečni raspored i osam unaprijed definiranih skupova ključnih riječi.']],[114,CW-114])
    R.sub('Što uzorak obuhvaća',f'Glavni pregled sadrži {number(N)} objava od siječnja 2021. do kolovoza 2026. Rujan 2026. ima podatke samo do 10. rujna i izostavljen je iz ovog izvještaja. Vlastiti kanali HNB-a, društvene mreže, tisak, radio i televizija nisu dio ovih brojki.')
    R.note('Aktualni upisnik ne dokazuje da je izvor bio registriran ili praćen u svakom ranijem mjesecu. Mogu nedostajati ugašeni ili preimenovani portali. Razvojna provjera nije neovisna ljudska validacija. Izvor: '+link('downloads/media-methods-hr.html','metode HNB_MEDIA')+'.')

    R.new('Kretanje kroz vrijeme','Vrhovi pripadaju arhivu koji se također mijenja','Mjesečni broj opisuje koliko je objava zabilježeno. Stopa ispod njega uspoređuje taj broj s količinom arhivskog materijala koja prolazi isti filtar izvora, datuma i pronalaženja.')
    R.sub('Mjesečni broj objava s izričitim spominjanjem HNB-a')
    R.figure(timeline(full,height=158),'Plava crta: sve uključene objave. Isprekidana granica: promjena prikupljanja u siječnju 2024.',[[r['period'],number(r['hnb_count'])] for r in full],['Mjesec','Objave'])
    R.sub('Spominjanja na 10.000 prihvatljivih arhivskih objava')
    R.figure(timeline(full,'rate_per_10000',height=158),'Stopa = 10.000 × usklađeni brojnik / usklađeni nazivnik. Izvor: '+src('media-monthly.csv')+'.',[[r['period'],number(r['rate_per_10000'],2)] for r in full],['Mjesec','Na 10.000'])
    R.text('Promjena prikupljanja u siječnju 2024. utječe na usporedivost razina. Podjela na sve prihvatljive objave ublažava neke razlike u opsegu, ali ne uklanja promjene u izboru sadržaja i sastavu izvora. Zbog toga ove krivulje nisu dokaz nacionalnog rasta ili pada zanimanja za HNB.')
    R.note('Najveći zabilježeni mjesečni broj je 1.512 u veljači 2022. Prisutnost podataka na svakom kalendarskom datumu ne jamči potpunost praćenja.')

    R.new('Tri mjesečna portreta','Isti naziv institucije, različiti javni razgovori','Mjeseci su odabrani radi različitih vrsta sadržaja i ilustriraju tri medijska konteksta. Brojevi se odnose na sve HNB objave u mjesecu, a opisani povodi samo su dio tih objava.')
    R.sub('Siječanj 2022. | javna odgovornost i pravila ponašanja','U mjesecu je zabilježena 1.351 objava. U naslovima i izvještajima pojavljuju se trgovanje vrijednosnim papirima, postupanje zaposlenika HNB-a i saborska rasprava. Na sjednici Odbora 27. siječnja otvorena su pitanja nadzora i etičkih očekivanja. Taj primjer pokazuje kako središnja banka postaje predmet javnog propitivanja, uz vlastita očitovanja i stavove drugih institucija. Medijski navod o sporu nije sam po sebi utvrđenje povrede pravila.')
    R.sub('Siječanj 2023. | zamjena valute kao praktično pitanje','U mjesecu je zabilježeno 1.227 objava. Ulazak u europodručje prate informacije o tome gdje se mijenja novac i kada pojedina ustanova pruža uslugu. U Hininom izvještaju od 4. siječnja HNB objašnjava naknade pri zamjeni kunske gotovine u bankama. Institucionalno ime ovdje označuje izvor upute koja građaninu pomaže razumjeti konkretan postupak.')
    R.sub('Veljača 2025. | cijene, potrošači i očekivanja prema HNB-u','U mjesecu je zabilježeno 808 objava. Među sadržajima su potrošački zahtjevi i sastanak predstavnika platforme Halo, inspektore s HNB-om 21. veljače. Izvještaj Hine prenesen u Glasu Istre navodi razgovor o uzrocima inflacije i monetarnoj politici. HNB se tako pojavljuje i kao sugovornik u raspravi o troškovima života, uz druga pitanja u istom mjesečnom korpusu.')
    R.note('Izvori povoda: <a href="https://sabor.hr/hr/press/priopcenja/odbor-za-financije-i-drzavni-proracun-odrzao-tematsku-sjednicu-o-trgovanju">Hrvatski sabor, 27. 1. 2022.</a>; <a href="https://www.hina.hr/OTS/11202381">Hina, 4. 1. 2023.</a>; <a href="https://www.glasistre.hr/gospodarstvo/2025/02/21/sastanak-celnika-platforme-halo-inspektore-i-hnb-a-984828">Glas Istre / Hina, 21. 2. 2025.</a> Mjesečni brojevi: '+src('media-monthly.csv')+'.')

    R.new('Tematska karta','Kreditiranje, valuta i svakodnevno korištenje novca','Osam skupova riječi pokazuje koje sadržaje nalazimo u naslovima i tekstovima koji izričito spominju HNB. Najviše podudaranja ima skup o kreditiranju i potrošačima.')
    items=sorted([(labels[k],v) for k,v in sc.items()],key=lambda r:-r[1])
    R.figure(bars(items,denominator=N,height=282),'Broj objava i udio među 33.235 objava. Skupovi se preklapaju; udjeli se ne zbrajaju do 100%.',[(k,number(v),pct(v,N)) for k,v in items],['Skup','Objave','Udio'])
    R.text(f'Više od jedne oznake ima {number(S["multiple_tags"])} objave ({pct(S["multiple_tags"],N)}). Bez ijedne od osam oznaka ostaje {number(S["untagged"])} objava ({pct(S["untagged"],N)}). To pokazuje i širinu medijskog sadržaja i granice odabranog rječnika.')
    R.sub('Karta otvara pitanja za čitanje','Skup o kreditiranju obuhvaća i opće pojmove poput kredita ili potrošača. Skup o valuti prepoznaje uvođenje eura, tečaj i srodne izraze. Brojevi stoga nisu procjena koliko je članaka posvećeno samo jednoj temi ili koliko puta HNB o njoj govori vlastitim glasom.')
    R.note('Izvor: '+src('media-subjects.csv')+' i '+src('subject-definitions.json')+'. Oznake nisu neovisno potvrđene glavne teme tekstova.')

    R.new('Teme kroz godine','Godišnji raspored otkriva promjene naglasaka','Svaki stupac prikazuje udio HNB objava iz te godine u kojima je pronađen pojedini skup riječi. Tako se godine različite veličine uspoređuju prema sastavu zabilježenog materijala.')
    years=[str(y) for y in range(2021,2027)];annual={y:sum(r['hnb_count'] for r in full if r['period'].startswith(y)) for y in years}
    vals=[[100*sum(r['lexical_count'] for r in D['subjects'] if r['subject_id']==d['id'] and r['period'].startswith(y) and r['period']<='2026-08')/annual[y] for y in years] for d in defs]
    R.figure(heatmap([d['label_hr'] for d in defs],[*years[:-1],'2026*'],vals),'Postoci unutar godine. *2026. obuhvaća siječanj-kolovoz. Tamnija polja imaju veći udio. Skupovi se preklapaju.',[[d['label_hr']]+[number(v,1)+'%' for v in row] for d,row in zip(defs,vals)],['Skup']+years)
    maxes=[]
    for k in ['currency','prices','lending']:
        row=vals[[d['id'] for d in defs].index(k)];j=max(range(6),key=lambda j:row[j]);maxes.append(f'{labels[k]}: najviši godišnji udio u prikazu iznosi {number(row[j],1)}% u {years[j]}.')
    R.text(' '.join(maxes))
    R.text('Godišnji udjeli opisuju strukturu opaženih objava. Na promjenu mogu djelovati javni događaji, urednički izbori, sastav izvora i prikupljanje. Granica u siječnju 2024. ostaje važna i kada se gledaju postoci umjesto ukupnog broja.')
    R.note('Izvor: '+src('media-subjects.csv')+'; godišnji nazivnici iz '+src('media-monthly.csv')+'.')

    R.new('Krediti i kamate','Institucionalna pravila ulaze u kućni proračun','Krediti i kamate približavaju središnju banku pitanjima koja imaju prepoznatljiv osobni sadržaj: mogućnosti zaduživanja, trošku otplate i odnosu dohotka prema dugu.')
    R.table(['Skup riječi','Objave','Udio'],[[labels[k],number(sc[k]),pct(sc[k],N)] for k in ['lending','rates']],[CW-155,75,80])
    R.sub('Od sustava prema pojedinoj odluci','Rječnik kreditiranja može povezati bankovno poslovanje sa stanom, potrošnjom ili postojećim dugom. Kamatna stopa pritom je jedna od poveznica između šire monetarne rasprave i troška koji snosi korisnik kredita. Isti članak može sadržavati sve te razine, pa preklapanje oznaka nosi sadržajnu informaciju.')
    R.sub('Primjer iz 2025.: ograničavanje kriterija kreditiranja','HNB je 19. ožujka 2025. objavio odluku kojom obrazlaže preventivno ograničavanje kreditiranja radi otpornosti kućanstava i financijske stabilnosti, uz početak primjene 1. srpnja. U takvoj poruci javni cilj dobiva operativan oblik: pravilo utječe na kriterije prema kojima se razmatra novi kredit. To je primjer načina obrazlaganja odluke; ovaj izvještaj ne procjenjuje njezin učinak.')
    R.callout('Za razumijevanje medijske poruke treba povezati javni cilj, konkretno pravilo i pitanje koje ono otvara korisniku.')
    R.note('Brojevi: '+src('media-subjects.csv')+'. Primjer: <a href="https://www.hnb.hr/-/priopcenje-o-donosenju-odluke-o-kriterijima-kreditiranja-potrosaca">HNB, Odluka o kriterijima kreditiranja potrošača, 19. 3. 2025.</a> To je institucionalni izvor za objašnjenje povoda, izvan uzorka uredničkih objava.')

    R.new('Euro, plaćanja i gotovina','Valuta je i javni projekt i svakodnevna usluga','Medijska prisutnost HNB-a oko novca nije ograničena na tečaj. U nju ulaze korištenje gotovine, zamjena novčanica i kovanica te pravila platnih usluga.')
    R.table(['Skup riječi','Objave','Udio'],[[labels[k],number(sc[k]),pct(sc[k],N)] for k in ['currency','payments']],[CW-155,75,80])
    R.sub('Dvije razine istog procesa','Uvođenje eura može se opisivati kroz institucionalnu promjenu i kroz pojedini postupak građanina. Prva razina govori o valuti i europskom okviru; druga o tome gdje i kada zamijeniti gotovinu. Medijski tekst često prevodi opći događaj u pitanje koje čitatelj može postaviti u banci ili poslovnici.')
    R.sub('Praktična informacija može biti razlog spominjanja','Izvještaj o zamjeni gotovine ilustrira HNB kao izvor pojašnjenja. U takvom tekstu ime institucije podupire vjerodostojnost upute. Drugi sadržaji mogu je spominjati u raspravi o troškovima i organizaciji procesa. Zbog toga broj spominjanja sam ne razdvaja obavijest, objašnjenje i ocjenu.')
    R.sub('Podudaranje riječi ne određuje povod','Skup euro i valute uključuje i tečaj, a skup plaćanja i gotovina sadrži različite vrste novca i platnog prometa. Objavu o tečaju prije uvođenja eura i objavu o njegovoj zamjeni ne treba smatrati istom pričom. Za takvo razlikovanje potrebno je čitati tekst ili zasebno kodirati povod.')
    R.note('Izvori: '+src('subject-definitions.json')+' i '+src('media-subjects.csv')+'. Primjer zamjene gotovine detaljnije je obrađen u popratnom izvještaju '+link('downloads/hnb-od-rijeci-do-javnih-pitanja.html','HNB: od riječi do javnih pitanja')+'.')

    R.new('Cijene i ekonomsko znanje','Između iskustva poskupljenja i tumačenja podataka','Cijene se u javnosti susreću s prognozama, statistikama i objašnjenjima gospodarskih kretanja. HNB se u takvom sadržaju može pojaviti kao izvor informacije ili kao adresat pitanja.')
    R.table(['Skup riječi','Objave','Udio'],[[labels[k],number(sc[k]),pct(sc[k],N)] for k in ['prices','forecasts']],[CW-155,75,80])
    R.sub('Broj, prognoza i iskustvo čitatelja','Statistički podatak opisuje određeno razdoblje i definiran pokazatelj. Prognoza govori o očekivanom kretanju, dok čitateljevo iskustvo može biti vezano uz konkretnu kupnju. Kada se te razine spoje u vijesti, važno je pratiti na što se pojedina tvrdnja odnosi i kome je pripisana.')
    R.sub('HNB kao sugovornik u raspravi o cijenama','Sastanak s predstavnicima platforme Halo, inspektore u veljači 2025. pokazuje da se rasprava o inflaciji može odvijati i kao razgovor o potrošačkim zahtjevima. To je ilustracija javnog očekivanja prema instituciji. Ne daje mjeru povjerenja svih građana, niti govori koliki je dio uzorka takvu raspravu prenio.')
    R.sub('Veza sa zasebnom inflacijskom studijom','Na hubu postoji specijalistička studija HNB-a u raspravi o inflaciji. Ona ima vlastiti korpus, razdoblje i ponderirane pokazatelje. Broj od 11.142 objave s ovdašnjim skupom riječi o cijenama i inflaciji nije njezin broj opažanja i ne zamjenjuje njezine procjene.')
    R.note('Izvori: '+src('media-subjects.csv')+'; '+link('studies/inflation/hr.html','zasebna inflacijska studija')+'. Opis sastanka: Glas Istre / Hina, 21. 2. 2025., poveznica na str. 5.')

    R.new('Stabilnost i odgovornost','Institucija koja nadzire može postati predmet nadzora','U jeziku bankovne stabilnosti naglasak je na funkcioniranju sustava. U raspravama o upravljanju i odgovornosti otvara se pitanje kako postupa sama institucija i kako se njezino postupanje obrazlaže.')
    R.table(['Skup riječi','Objave','Udio'],[[labels[k],number(sc[k]),pct(sc[k],N)] for k in ['stability','governance']],[CW-155,75,80])
    R.sub('Različita pitanja traže različite odgovore','Pojam nadzora u pojedinom tekstu može upućivati na postupanje HNB-a prema bankama, dok javna rasprava može biti usmjerena na pravila koja vrijede za njegove zaposlenike. Slične riječi zato ne jamče istu institucionalnu ulogu. Za razumijevanje treba pratiti tko postavlja pitanje, o kojem postupku i na temelju kojih ovlasti.')
    R.sub('Siječanj 2022. kao primjer rasprave o odgovornosti','Saborska rasprava o vrijednosnim papirima povezuje medijske navode, institucionalna očitovanja i zahtjeve za provjerom. Ona pokazuje kako HNB ulazi u javni razgovor kao predmet pitanja, a ne samo kao izvor gospodarske informacije. Ovaj opis odnosi se na raspravu u tom trenutku, bez zaključivanja o pravnoj odgovornosti pojedinaca.')
    R.callout('Vidljivost institucije može uključivati njezine poruke, tuđe zahtjeve prema njoj i raspravu o njezinu radu.')
    R.note('Skup upravljanje i odgovornost sadrži i opće izraze poput mandata ili imenovanja. Njegovih 7.308 podudaranja zato nije broj kritika HNB-a. Izvori: '+src('subject-definitions.json')+' i Hrvatski sabor, 27. 1. 2022. (str. 5).')

    R.new('Izvori i raspodjela','Mnogo domena, uz vidljiv skup većih izvora','Poredak se temelji na broju uključenih objava, bez ponderiranja dosega. Veliki portali i specijalizirani gospodarski izvori pojavljuju se uz regionalne i lokalne medije.')
    rows=[(r['source_id'],r['hnb_count']) for r in D['sources'][:10]]
    R.figure(bars(rows,height=308,label_width=146,denominator=N),'Prvih deset domena prema broju objava; udio među 33.235 objava. Izvor: '+src('media-sources.csv')+'.',[(k,number(v),pct(v,N)) for k,v in rows],['Izvor','Objave','Udio'])
    top10=sum(v for _,v in rows)
    R.text(f'Deset prikazanih domena zajedno ima {number(top10)} objava ({pct(top10,N)}). Preostalih {number(S["outlets"]-10)} domena čini {pct(N-top10,N)} uzorka. Širina raspodjele pokazuje da se HNB pojavljuje na brojnim mjestima, iako broj objava po izvoru nije jednak.')
    R.text('Domena nije medijska grupacija. Iz ovog se poretka ne može izvesti vlasnička koncentracija. Jednako tako, objava u portalu s većom publikom i objava u malom lokalnom izvoru ovdje imaju istu težinu: svaka se broji jednom.')

    R.new('Provjere osjetljivosti','Što se mijenja kada sužavamo pogled?','Različite definicije odgovaraju na različita pitanja. Usporedba pokazuje koliko rezultata zadržavamo kada tražimo puni naziv, spominjanje u naslovu ili isti skup opaženih izvora kroz cijelo razdoblje.')
    R.table(['Pogled na korpus','Objave','Udio osnovnog skupa'],[
      ['Izričito spominjanje: kratica ili puni naziv',number(N),'100,0%'],
      ['Samo puni naziv institucije',number(S['formal_mentions']),pct(S['formal_mentions'],N)],
      ['Spominjanje HNB-a u naslovu',number(S['title_mentions']),pct(S['title_mentions'],N)],
      ['128 izvora opaženih u svakom punom mjesecu',number(S['stable_hnb']),pct(S['stable_hnb'],N)],
      ['Bez dvaju izvora s nerazriješenim povezanim sadržajima',number(S['excluding_two_related_content_sources']),pct(S['excluding_two_related_content_sources'],N)]
    ],[CW-190,75,115],size=10.5)
    R.sub('Naslov sužava pitanje na mjesto spominjanja',f'U naslovima je HNB prepoznat u {pct(S["title_mentions"],N)} objava. To je korisna uža mjera, ali i dalje ne dokazuje da je institucija glavni akter, da je citirana ili da je autor prema njoj zauzeo određeni stav.')
    R.sub('Zajednički izvori ne jamče jednako praćenje','Skup od 128 domena ima barem jednu pozadinsku objavu u svakom od 68 mjeseci. Time se provjerava osjetljivost na ulazak i izlazak izvora iz opaženog arhiva. Kontinuitet domene ipak ne znači da je svaka njezina objava dohvaćena ili da se način prikupljanja nije promijenio.')
    R.note('Redci su zasebne provjere, a ne dijelovi koji se zbrajaju. Dva izvora u posljednjem retku su dnevnik.hr i vecernji.hr; provjera obuhvaća nerazriješenu mogućnost povezanih sadržaja. Izvor: '+src('media.json')+' i '+link('downloads/media-methods-hr.html','metodološke napomene')+'.')

    R.new('Završni pogled i izvori','Prisutnost dobiva smisao kada joj se doda sadržaj','HNB se u ovom uzorku pojavljuje na sjecištu novca, institucionalnih odluka i javnih potreba. Krediti, valuta, cijene i plaćanja približavaju je svakodnevici; stabilnost i odgovornost otvaraju pitanje njezine javne uloge.')
    R.sub('Tri pitanja za daljnje čitanje','Kada se HNB spominje, govori li sam ili o njemu govore drugi? Je li razlog spominjanja uputa, tumačenje podataka, odluka ili zahtjev za odgovornošću? Kako se institucionalni pojam povezuje s konkretnim problemom čitatelja? Brojevi u ovom pregledu usmjeravaju takvo čitanje, ali ga ne zamjenjuju.')
    R.sub('Popratni izvještaj o jeziku',link('downloads/hnb-od-rijeci-do-javnih-pitanja.html','HNB: od riječi do javnih pitanja')+' analizira odabrane riječi i izraze u rečenicama s izričitim spominjanjem HNB-a. Jednaki normalizirani tekstovi broje se jednom. Uz tematske rječnike donosi tri pobliže obrađena primjera: zamjenu gotovine, kreditna pravila i raspravu o odgovornosti.')
    R.table(['Izvor / izdanje','Sadržaj'],[
      ['HNB_MEDIA, podaci 2026-09-21.1','Mjesečni agregati, izvori, teme i registar domena. Razdoblje 2021-01/2026-08. Održavani arhiv: presjek 19. 9. 2026.'],
      ['Metoda 1.0','Izričita spominjanja, povezivanje ponovljenih zapisa, provjere teksta i preklapajući skupovi riječi.'],
      ['AEM, upisnik elektroničkih publikacija','Referenca prihvatljivosti domena, provjerena 21. 9. 2026. Aktualni upisnik nije povijesni popis svih medija.'],
      ['Javni hub i objavljeni agregati',link('hr.html','lusiki.github.io/HNB_Media_Attention/media/')+'; poveznice uz grafikone vode na točne podatkovne datoteke.']],[170,CW-170],size=9.7)
    R.note('Predloženo citiranje: HNB u medijskom prostoru: novac, svakodnevne potrebe i javna odgovornost. (2026). HNB_MEDIA, podaci 2026-09-21.1, izvještaj 21. 9. 2026. Javni istraživački nacrt; autorska provjera u tijeku. Bez pripisivanja autorskog odobrenja ili institucionalne potpore.')
    return R.save()
