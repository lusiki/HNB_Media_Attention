"""Twelve-page companion on vocabulary and three documented public examples."""
from report_layout import *
from report_extensions import language_pages
from reportlab.graphics.shapes import Group

def language(out,D,L):
    N=L['distinct_normalized_bodies'];T=L['terms'];G=L['groups'];P=L['phrases'];defs=D['subject_definitions'];labels={d['id']:d['label_hr'] for d in defs}
    data_url='https://lusiki.github.io/HNB_Media_Attention/media/data/media/report-language.json'
    provenance='<a href="'+data_url+'">report-language.json</a> · HNB_MEDIA_LEXICAL_1.0'
    R=Report(out/'hnb-od-rijeci-do-javnih-pitanja.pdf','HNB: od riječi do javnih pitanja','Jezik i javna pitanja',14,'jezični dodatak 1.1')
    R.cover(['HNB','Od riječi do javnih pitanja'],'Jezik novca, institucionalne odluke i javni argumenti',[(number(N),'različitih tekstova s dostupnim tijelom'),('8','preklapajućih rječničkih skupova'),('3','javna povoda; jedan čeka provjeru')],'Kako se riječi o novcu i institucijama povezuju s konkretnim postupcima, odlukama i očekivanjima javnosti.')

    R.new('Ključni nalazi','Od naziva institucije prema sadržaju poruke','Ovaj izvještaj analizira rječnik oko izričitih spominjanja HNB-a. Zatim razmatra tri odabrana javna povoda, od kojih primjer zamjene gotovine čeka provjeru izvornika, kako bi pokazao što pojedini institucionalni izraz znači u konkretnom razgovoru.')
    R.sub('Rječnik spaja banke, valutu i institucionalni glas',f'Od odabranih pojmova banka je pronađena u {number(T["banka"])} različitih tekstova, euro u {number(T["euro"])} i guverner u {number(T["guverner"])}. Puni naziv HNB-a uklonjen je prije prebrojavanja, pa banka nije zabilježena samo zato što je dio imena institucije.')
    R.sub('Svakodnevna pitanja imaju prepoznatljive riječi',f'Građanin se pojavljuje u {number(T["građanin"])} tekstova, kredit u {number(T["kredit"])} i cijena u {number(T["cijena"])}. Ti pojmovi približavaju instituciju korisnicima i ekonomskim odlukama. Njihova prisutnost ipak ne govori u čije je ime izjava dana ni slaže li se autor s njom.')
    R.sub('Izrazi su određeniji od pojedinačnih riječi',f'Uvođenje eura pronađeno je u {number(P["uvođenje eura"])} tekstova, a kamatna stopa u {number(P["kamatna stopa"])}. Takvi izrazi preciznije usmjeravaju čitanje od opće riječi euro ili kamata. I dalje mogu biti dio upute, opisa, prijedloga ili kritike.')
    R.callout('Uputa govori kako postupiti. Odluka objašnjava što se mijenja. Rasprava o odgovornosti pita kako institucija postupa.')
    R.note('Brojevi označuju tekstove s barem jednim podudaranjem u izdvojenom kontekstu. Analiza je opisna i istraživačka, bez neovisne ljudske validacije. Metoda i oblak riječi: str. 3; skupovi: str. 4-7; izrazi: str. 8; primjeri: str. 9-11; sinteza i izvori: str. 12; dodatak 1.1: str. 13-14.')

    R.new('Rječnik rasprave','Koje riječi prate HNB?','Polazište su 33.235 objava iz istog razdoblja kao u medijskom pregledu. Njih 99 nema pohranjen tekst. Među preostalih 33.136 objava ima 33.100 različitih normaliziranih tekstova; svaki se u ovom izvještaju broji jednom.')
    R.text('Izdvojeni su naslov, ako izričito spominje HNB, te rečenični odsječci teksta s takvim spominjanjem. Broje se odabrani pojmovi uz obrasce za njihove gramatičke oblike, najviše jednom po tekstu. To je transparentan rječnik od 52 pojma, a ne automatski popis svih riječi ili potpuna lematizacija.',size=11)
    items=list(T.items())[:32]
    R.figure(cloud(items,height=230,max_words=32),'Prikazana su 32 najčešća od 52 odabrana pojma. Veća riječ označuje više tekstova; položaj i boja nemaju dodatno značenje. Naziv HNB-a prethodno je uklonjen.',[(k,number(v),pct(v,N)) for k,v in items],['Pojam','Tekstovi','Udio od 33.100'])
    R.table(['Pojam','Tekstovi','Udio od 33.100'],[[k,number(T[k]),pct(T[k],N)] for k in ['banka','euro','guverner']],[CW-175,85,90])
    R.note('Različitost teksta određena je malim slovima i sažimanjem razmaka, bez prepoznavanja bliskih kopija iste priče. Rečenično razdvajanje može pogriješiti kod kratica ili prijeloma. Preostali navigacijski sadržaj također može utjecati na rezultate. Točni obrasci i agregati: '+provenance+'.')

    R.new('Tematski kontekst','Osam ulaza u isti jezični materijal','Isti skupovi ključnih riječi iz medijskog pregleda ovdje se primjenjuju samo na izdvojeni kontekst HNB-a. Stupci pokazuju u koliko se različitih tekstova takav kontekst podudara s pojedinim skupom.')
    items=sorted([(labels[k],g['n']) for k,g in G.items()],key=lambda r:-r[1])
    R.figure(bars(items,height=280,denominator=N),'Broj različitih tekstova i udio od 33.100. Skupovi se preklapaju; oznaka nije glavna tema cijelog teksta.',[(k,number(v),pct(v,N)) for k,v in items],['Skup','Tekstovi','Udio'])
    R.sub('Zašto se brojke razlikuju od medijskog pregleda','Pregled medijskog prostora broji objave i pregledava cijeli naslov i tekst. Ovdje se jednaki tekstovi povezuju, a riječi traže u užem kontekstu koji izričito imenuje HNB. Razlika između tih dvaju brojeva zato ne mjeri pogrešku jednog od izvještaja, nego promjenu jedinice i područja pretraživanja.')
    R.text('Tematski oblaci na sljedećim stranicama opisuju rječnik unutar ovih skupova. Riječi koje određuju skup očekivano će biti česte i u njegovu oblaku. To nije neovisna potvrda da je računalo otkrilo osam prirodno odvojenih tema.')
    R.note('Izvor: '+provenance+'. Nazivnik je uvijek 33.100 različitih tekstova, a u pojedinačnom tematskom oblaku broj tekstova naveden uz naslov.')

    def four_clouds(keys):
        d=Drawing(CW,430);rows=[]
        for i,k in enumerate(keys):
            x=(i%2)*(CW/2+8);yy=430-(i//2)*215;w=CW/2-12;g=G[k]
            # Use short headings to keep each panel readable at A4 size.
            short={'prices':'Cijene i inflacija','rates':'Monetarna politika i kamate','lending':'Kreditiranje i potrošači','forecasts':'Prognoze i statistika','currency':'Euro i valute','payments':'Plaćanja i gotovina','stability':'Stabilnost i nadzor','governance':'Upravljanje i odgovornost'}[k]
            d.add(String(x,yy-12,short,fontName='Bold',fontSize=11,fillColor=HexColor(INK)))
            d.add(String(x,yy-29,number(g['n'])+' tekstova u skupu',fontName='Sans',fontSize=9,fillColor=HexColor(MUTED)))
            items=list(g['terms'].items())[:15];group=Group();group.add(cloud(items,width=w,height=144,max_words=15));group.translate(x,yy-177);d.add(group)
            top=' · '.join(f'{a} {number(b)}' for a,b in items[:2])
            d.add(String(x,yy-199,top,fontName='Sans',fontSize=8.9,fillColor=HexColor(MUTED)))
            rows.extend([[short,a,number(b)] for a,b in items])
        return d,rows

    R.new('Riječi po skupovima / kućanstva i gospodarstvo','Cijene, kamate, krediti i prognoze','Četiri skupine povezuju iskustvo troška s financijskim odlukama i ekonomskim tumačenjima. Oblaci pokazuju odabrane riječi koje se pojavljuju u istom tekstualnom kontekstu HNB-a.')
    d,rows=four_clouds(['prices','rates','lending','forecasts'])
    R.figure(d,'Po 15 najčešćih odabranih pojmova. Veličine slova uspoređuju se unutar pojedinog oblaka. Ispod su brojevi tekstova za dva vodeća pojma.',rows,['Skup','Pojam','Tekstovi'])
    R.text('U cijenama i inflaciji riječ rast povezuje promjenu s opisom ekonomskog kretanja. U kreditiranju se pojavljuju banka, potrošač i kamata. U prognozama rast dolazi uz inflaciju, projekciju i BDP. Rječnik tako pomaže razlikovati pitanje troška, odluke o zaduživanju i očekivanog gospodarskog razvoja.',size=11)

    R.new('Riječi po skupovima / novac i institucije','Od zamjene gotovine do javne odgovornosti','Druga četiri skupa otvaraju valutu, platne postupke i institucionalni okvir. Zajedničke riječi dobivaju različite naglaske ovisno o okolnom sadržaju.')
    d,rows=four_clouds(['currency','payments','stability','governance'])
    R.figure(d,'Tematski konteksti mogu se preklapati. Broj ispod oblaka označuje tekstove s pojmom u tom skupu, a ne broj svih njegovih pojavljivanja.',rows,['Skup','Pojam','Tekstovi'])
    R.text('Euro, kuna i kovanica približavaju materijalni i operativni dio novca. Stabilnost okuplja i rizik, kapital i kredit. U upravljanju se pojavljuju guverner, savjet i Sabor. Takav rječnik usmjerava pozornost prema institucijama i odgovornosti, ali ne određuje je li pojedini iskaz pohvalan, kritičan ili neutralan.',size=11)

    R.new('Pojmovi kroz različite skupove','Ista riječ ne znači istu ulogu','U tablici su četiri odabrana pojma. Postotak kaže u kojem se dijelu tekstova pojedinog skupa pojam pojavljuje u izdvojenom kontekstu HNB-a.')
    keys=[d['id'] for d in defs];words=['banka','guverner','građanin','euro'];values=[[100*G[k]['terms'].get(w,0)/G[k]['n'] for w in words] for k in keys]
    R.figure(heatmap([labels[k] for k in keys],words,values,height=294),'Udio unutar svakog tematskog skupa; različiti skupovi imaju različite nazivnike. Tamnija boja znači veći udio.',[[labels[k]]+[number(v,1)+'%' for v in row] for k,row in zip(keys,values)],['Skup']+words)
    R.sub('Institucionalni i svakodnevni rječnik mogu stajati zajedno','Guverner imenuje institucionalnu funkciju, a građanin upućuje na ljude na koje se sadržaj može odnositi. Euro može označavati valutu, novčani iznos ili širu raspravu o promjeni sustava. Imenovanje samo po sebi ne govori tko je govornik ili kojem je akteru pripisan zaključak.')
    R.text('Za daljnju analizu potrebno je odvojeno označiti govornika, radnju, predmet izjave i stav. Rječničko podudaranje ne obavlja te korake. Ovaj prikaz zato služi kao karta za čitanje, bez pripisivanja istog značenja svim tekstovima u ćeliji.')
    R.note('Izvor: '+provenance+'. Unutar skupa svi se pojmovi traže u svim izdvojenim HNB odsječcima teksta; tablica ne tvrdi da dvije riječi stoje u istoj rečenici.')

    R.new('Izrazi i javna pitanja','Što se mijenja kada riječi čitamo zajedno?','Susjedne riječi preciznije opisuju predmet razgovora. Uvođenje eura označuje proces, kamatna stopa mjeru troška, a kreditna sposobnost procjenu mogućnosti zaduživanja.')
    items=list(P.items())
    R.figure(bars(items,height=333,denominator=N),'Dvanaest odabranih izraza, uz gramatičke varijante. Svaki se broji najviše jednom po tekstu; udjeli imaju nazivnik 33.100.',[(a,number(b),pct(b,N)) for a,b in items],['Izraz','Tekstovi','Udio'])
    R.text('Izraz financijska stabilnost povezuje cilj s funkcioniranjem sustava. Zaštita potrošača imenuje korisnika i javnu obvezu. Sukob interesa otvara pitanje pravila i odnosa, ali njegovo prepoznavanje u rečenici ne dokazuje da je sukob u pojedinom slučaju utvrđen.')
    R.text('Tri primjera na sljedećim stranicama prate prijelaz od riječi do sadržaja: od informacije o zamjeni gotovine, preko pravila kreditiranja, do pitanja institucionalne odgovornosti. Odabrani su da ilustriraju različite oblike poruke, bez tvrdnje da predstavljaju sve tekstove.')
    R.note('Izvor: '+provenance+'. To su frekvencije unaprijed odabranih izraza, a ne rang svih mogućih izraza u korpusu.')

    R.new('Provjera izvora / valuta','Kandidat za povijesni primjer zamjene gotovine','Zapis od 4. siječnja 2023. u ranijem izdanju korišten je kao primjer praktične upute. Njegovu izvornu objavu i izdavatelja još treba potvrditi.')
    R.text('Poveznica vodi na Hinin OTS kanal. U ovoj provjeri izvorna stranica vraća zabranu pristupa. Zbog toga nije potvrđeno tko je izvorni izdavatelj, točan naslov, vrijeme objave ni povijest izmjena. Taj zapis nije potvrđena neovisna novinarska obrada niti izmjeren prijenos HNB-ove poruke.')
    R.sub('Što treba zabilježiti prije analize','Izvorni izdavatelj, žanr objave, datum i vrijeme te sačuvana verzija prethode provjeri medijskih podudaranja. Razlikuju se datum objave, datum odluke i datum početka primjene. Dok se to ne utvrdi, ovaj slučaj ostaje kandidat.')
    R.table(['Pitanje za provjeru','Status'],[['Izvorni izdavatelj i puni naslov','Nije potvrđeno'],['Datum i verzija izvornika','Datum iz prethodnog zapisa; verzija nepotvrđena'],['Pripadnost medijskom korpusu','Nije provjerena za ovu poveznicu'],['Prijenos pojedinih tvrdnji u medijima','Nije kodirano']],[205,CW-205])
    R.callout('Praktičnu uputu treba vezati uz provjeren izvor, uvjete i vrijeme važenja.')
    R.note('Kandidat: <a href="https://www.hina.hr/OTS/11202381">Hina OTS / 11202381</a>. Status provjeren 22. 9. 2026.: izravni pristup vraća 403. Ova stranica ispravlja ranije pripisivanje izvora; ne daje aktualnu uputu za zamjenu novca.')

    R.new('Primjer / pravilo i javni cilj','Kako stabilnost postaje kriterij za kredit?','OŽUJAK - SRPANJ 2025. · ODLUKA O KRITERIJIMA KREDITIRANJA POTROŠAČA')
    R.text('HNB je u odluci objavljenoj 19. ožujka 2025. ograničenja obrazložio otpornošću kućanstava i financijskog sustava. Početak primjene određen je za 1. srpnja, o čemu izvještava HRT/Hina. Poruka tako povezuje preventivni cilj i trenutak kada se mijenjaju kriteriji odobravanja novih kredita.')
    R.table(['Razina poruke','Što povezuje'],[
      ['Javni cilj','Financijsku otpornost kućanstava i stabilnost sustava.'],
      ['Operativno pravilo','Ukupnu mjesečnu otplatu duga i dohodak; iznos kredita i vrijednost nekretnine.'],
      ['Pitanje korisnika','Kako pravilo utječe na razmatranje novoga zaduženja u konkretnim okolnostima.']],[150,CW-150])
    R.sub('Broj postaje razumljiv uz svoj nazivnik','U odluci su navedeni omjeri otplate i dohotka od 45% za stambene i 40% za nestambene kredite te omjer kredita i vrijednosti zaloga od 90%, uz dopuštene iznimke. Takvi postoci imaju značenje tek kada čitatelj zna što se uspoređuje. U medijskoj poruci važno je povezati broj, kategoriju kredita i ograničenje na koje se broj odnosi.')
    R.sub('Obrazloženje cilja i dokaz učinka različiti su koraci','U ovoj se odluci financijska stabilnost pretvara u kriterij postupanja. Medijski prijenos može približiti taj prijelaz javnosti. Sam tekst odluke i izvještaj o njezinu početku ne pokazuju koliki je naknadni učinak na zaduživanje ili rizike; za to su potrebni podaci i zasebna analiza.')
    R.note('Povijesni primjer formulacije iz 2025., bez savjeta o osobnom kreditu. Izvori: <a href="https://www.hnb.hr/-/priopcenje-o-donosenju-odluke-o-kriterijima-kreditiranja-potrosaca">HNB, 19. 3. 2025.</a>; <a href="https://vijesti.hrt.hr/gospodarstvo/na-snazi-strozi-uvjeti-kreditiranja-cilj-usporiti-zaduzivanje-kucanstava-12227197">HRT / Hina, 1. 7. 2025.</a> HNB-ova objava služi provjeri obrazloženja, izvan uzorka uredničkih objava.')

    R.new('Primjer / javna odgovornost','Što se pita kada je HNB predmet rasprave?','HRVATSKI SABOR · 27. SIJEČNJA 2022. · RASPRAVA O VRIJEDNOSNIM PAPIRIMA')
    R.text('Nakon medijskih navoda o vrijednosnim papirima zaposlenika HNB-a, saborski Odbor održao je tematsku sjednicu. U njegovu izvještaju susreću se zahtjevi za visokim standardima postupanja, očitovanja HNB-a i objašnjenje Hanfine provjere. To je trenutak u kojem institucija postaje predmet pitanja drugih aktera.')
    R.sub('Tri razine koje ne treba spojiti u jednu tvrdnju')
    R.table(['Razina','Što je potrebno razlikovati'],[
      ['Medijski navod','Informaciju ili tvrdnju koja je otvorila javnu raspravu.'],
      ['Institucionalna provjera','Postupak i nadležnost za provjeru konkretnih okolnosti.'],
      ['Etičko očekivanje','Zahtjev da postupanje zadovolji javno očekivani standard.']],[145,CW-145])
    R.text('Vujčić je pozivao da se pričeka završetak nadzora. Hanfin predsjednik Žigman upozorio je da evidentirane preknjižbe ne znače isti broj kupoprodajnih trgovanja. U raspravi su otvorena i etička pitanja. Ovaj prikaz prenosi razlike među iskazima iz toga trenutka; ne donosi zaključak o povredi propisa ili odgovornosti pojedinaca.')
    R.sub('Od riječi nadzor do pitanja tko nadzire koga','Isti pojam može označavati djelovanje središnje banke prema bankama ili provjeru postupanja povezanog s njezinim zaposlenicima. Rječnik bez odnosa među akterima ne može razriješiti tu razliku. Zato za čitanje odgovornosti treba zabilježiti tko iznosi navod, tko odgovara, što se provjerava i je li postupak u tom trenutku dovršen.')
    R.callout('Spominjanje odgovornosti označuje javno pitanje. Odgovor traži provjeru iskaza, postupka i njegova ishoda.')
    R.note('Izvor povijesne rasprave: <a href="https://sabor.hr/hr/press/priopcenja/odbor-za-financije-i-drzavni-proracun-odrzao-tematsku-sjednicu-o-trgovanju">Hrvatski sabor, izvještaj sa sjednice Odbora, 27. 1. 2022.</a> Institucionalni zapis služi provjeri aktera i izjava; nije dio uredničkog uzorka. Ovdje nije provedena zasebna analiza kasnijih pravnih ishoda.')

    R.new('Završni pogled i metoda','Od riječi do pitanja koje javnost može razumjeti','Zajednički rječnik ne znači zajednički tip poruke. Predloženi primjeri razlikuju objašnjenje postupka, obrazloženje odluke i odgovor na pitanja; izvor primjera zamjene gotovine još nije potvrđen. Te uloge postaju vidljive tek kada se pročita odnos između aktera, problema i očekivanog djelovanja.')
    R.table(['Primjer','Pitanje koje daje smisao poruci'],[
      ['Zamjena gotovine','Gdje, kada i pod kojim uvjetima građanin može obaviti postupak?'],
      ['Kreditni kriteriji','Koji se javni cilj prevodi u pravilo i što se njime uspoređuje?'],
      ['Odgovornost','Tko iznosi tvrdnju, tko provjerava i kakav je status zaključka?']],[145,CW-145])
    R.sub('Kako su dobivene frekvencije','Ulaz je korpus HNB_MEDIA iz siječnja 2021. - kolovoza 2026. Tijela tekstova normalizirana su malim slovima i sažimanjem razmaka; ponovljeni tekst broji se jednom, uz naslov najranije objave. Izdvajaju se odsječci s izričitim nazivom ili kraticom HNB-a. Nakon uklanjanja tih naziva broje se 52 odabrana pojma i 12 izraza. Osam skupova primjenjuje se na isti izdvojeni kontekst, uz dopušteno preklapanje.')
    R.sub('Što treba dodatno provjeriti','Razdvajanje rečenica, višeznačni oblici riječi i zaostali dodaci u tekstu mogu utjecati na frekvencije. Jednake tekstove razlikujemo od bliskih prerada, a tematsko podudaranje od glavne teme. Odabrani primjeri nisu reprezentativan uzorak iskaza ni kodiranje sentimenta, citiranosti ili povjerenja.')
    R.note('Podaci i točni izrazi za ponavljanje brojanja: '+provenance+'. Skripta prepare_report_language.py čita prethodno pripremljeni korpus bez izmjene izvornog arhiva; javno se objavljuju samo agregati. Tekstovi i identifikatori članaka nisu uključeni. Izvorni medijski pregled i ovaj jezični dodatak imaju različite jedinice brojanja.')
    R.note('Predloženo citiranje: HNB: od riječi do javnih pitanja. (2026). HNB_MEDIA_LEXICAL_1.0 i dodatak 1.1, podaci HNB_MEDIA 2026-09-21.1, 22. 9. 2026. Javni istraživački nacrt; autorska provjera u tijeku. Izvori triju povoda navedeni su uz svaki primjer.')
    language_pages(R)
    return R.save()
