# HNB_MEDIA: protocol for independent measurement, draft 1.0

Prepared 22 September 2026. Status: ready for Croatian coder calibration, **not a completed validation study**. Population: captured publications in HNB_MEDIA 2026-09-21.1, January 2021–August 2026. No national journalism, readership, trust or causal estimand is implied.

## Sampling and separation

Use three disjoint frames, assigned in order: accepted explicit HNB hits; plausible missed candidates (contextual, then officeholder-only, then generic central-bank route); residual eligible background. Audit the frame counts and intersections before selecting records. The initial evaluation allocation is 280/80/40 (400 total), subject to a separate pilot; record every change before evaluation labels exist. Forty residual observations cannot establish high archive-wide recall.

Prepare a separate 50-record calibration set spanning both collection regimes, retrieval routes, high/low-volume sources and body availability. Use seed 20260922, preserve inclusion probabilities and selection code. Do not show automatic screen/role predictions. Train on calibration cases, amend the codebook, then freeze its hash before evaluation. Calibration records never enter evaluation. Exact and evaluated near-duplicate groups must not cross development/evaluation sets; the grouping must be frozen first. This dependency currently prevents freezing the final evaluation sample.

Within each frame, stratify by regime and retrieval route, then source-volume group when cells are sufficiently populated. Missing bodies remain a recorded stratum/assessment outcome, not replacements selected for convenience. Oversampling must preserve known inclusion probabilities. Draw publications, not one representative per story. Keep selection probabilities, sample IDs, text and coder sheets outside Dropbox; public files contain only codebooks and aggregates.

Two Croatian-speaking people independently code every evaluation record. An adjudicator resolves disagreements only after the unadjudicated agreement file is locked and scored. The implementer/agent is not a substitute for either independent human coder. No invitations or messages have been sent.

## Croatian coding instructions

Za svaku varijablu upišite `1` (prisutno), `0` (odsutno) ili `U` (nije moguće procijeniti). `U` se nikada ne pretvara u `0`. Za primjenu koja ovisi o drugom kodu dopušteno je `NA` (nije primjenjivo). Zabilježite kratko obrazloženje i privatni položaj relevantnog odlomka, bez kopiranja dobavljačeva teksta u javnu datoteku. Naslov može potvrditi prisutnost naziva, ali naslov bez teksta obično ne omogućuje procjenu svih uloga i funkcija.

| Skup | Oznaka | Pravilo i granica |
|---|---|---|
| Institucija | `entity_hnb`, `entity_ecb_eurosystem`, `entity_other_cb` | Kodirati prisutnost svake institucije zasebno. Spominjanje HNB-a i ESB-a u istoj objavi nije pogreška pripisivanja samo po sebi. Neodređena „središnja banka” ostaje nerazjašnjena bez dovoljnog konteksta. |
| Odgovornost za tvrdnju | `action_attribution` | Za svaku važnu tvrdnju/radnju označiti HNB / ESB-Eurosustav / druga institucija / neodređeno / U. Razlikovati prisutnost naziva od stvarnog aktera. Kodirati ono što tekst pripisuje; zasebno zabilježiti pogrešku ako je provjerena. |
| Izravno citiranje | `role_quote` | Tekst izričito pripisuje citirane riječi HNB-u ili imenovanom dužnosniku u tadašnjoj ulozi. Navodnici oko tuđeg komentara o HNB-u ne zadovoljavaju pravilo. |
| Parafraza | `role_paraphrase` | Necitirana izjava, objašnjenje ili stajalište izričito je pripisano HNB-u. Sam naziv izvora statistike kodira se u sljedećoj varijabli. |
| Mjera/radnja | `role_policy_action` | HNB je označen kao donositelj/provoditelj opisane mjere; odvojiti ESB-ovu odluku od domaće provedbe. Općenito spominjanje kamatnih stopa nije dovoljno. |
| Statistički izvor | `role_statistics` | Podaci, broj ili projekcija izričito su pripisani HNB-u. Dužnosnik koji o njima govori može istodobno imati kod citiranja/parafraze. |
| Predmet kritike | `role_criticism` | Kritička tvrdnja usmjerena je na HNB ili njegovo postupanje; ne na banke općenito. Prisutnost kritike ne znači da ju je autor članka usvojio. |
| Usputna prisutnost | `role_incidental` | HNB je prepoznat, ali nijedna od prethodnih pet uloga nije prisutna. Isključivo u odnosu na njih: ako je neka `1`, incidental je `0`; ako se druge ne mogu procijeniti, incidental je `U`. |
| Uputa | `function_instruction` | Navodi što određena osoba/skupina treba ili može učiniti u vezi s opisanim pravilom, uslugom ili postupkom. Samo navođenje da mjera postoji nije uputa. |
| Objašnjenje | `function_explanation` | Objašnjava razlog, mehanizam ili posljedicu mjere/događaja; samo broj ili datum nije dovoljno. |
| Odgovornost | `function_accountability` | Raspravlja o odgovornosti, obrazloženju odluke, nadzoru ili mogućnosti preispitivanja. Ne zahtijeva negativan ton. |
| Ostalo | `function_other` | Dovoljno teksta za procjenu, ali nema nijedne od tri funkcije; isključivo s njima. Nema oznake „glavna funkcija” u ovoj inačici. |
| Javna usluga | `service_affected_group`, `service_change`, `service_when`, `service_how_to_act` | Kodirati svaki element zasebno samo za slučajeve s uputom ili objašnjenjem. Vrijednosti: prisutan / odsutan / NA / U. „Odsutan” nije „netočan”. Ne stvarati zajednički rezultat učinkovitosti. |
| Neobavezne teme | osam oznaka iz javnog rječnika | Ako se uključe, kodirati ih neovisno od automatskih rezultata i odvojiti glavnu od usputne teme. Bez ove komponente osam leksičkih skupova ostaje istraživačko, čak i ako su uloge pouzdane. |

Uloge i funkcije mogu se preklapati osim navedenih isključivih oznaka. Izostanak povjerenja, tona, odnosa moći ili utjecaja iz ovog kodiranja znači da ti konstrukti nisu izmjereni, a ne da ih nema.

## Agreement, estimation and publication gates

Before adjudication, report confusion counts, raw agreement, positive/negative agreement and nominal Krippendorff alpha separately for each categorical/binary construct. Bootstrap entire story groups within sampling strata (2,000 replicates, seed 20260922); report the number of usable replicates. A no-variation category has undefined alpha and cannot pass. Primary reference: [Krippendorff reliability resources](https://www.asc.upenn.edu/krippendorffs-alpha-reliability), located by the execution plan; methods still need reviewer confirmation before the freeze.

Freeze project gates before evaluation: alpha ≥0.80 for headline claims; 0.67–0.79 tentative/exploratory only; below 0.67 revise or withhold. Low positive counts or wide intervals can still require withholding. These are project release rules, not proof of validity. Any automated classifier used over the corpus also needs its own held-out precision/recall analysis.

Estimate prevalence as a design-weighted ratio in the relevant frame and assessable population, with weight `1 / inclusion_probability`. Report unweighted n, sum of weights, effective sample size `(sum w)^2 / sum(w^2)`, missingness, overlap and 95% intervals from the stratified story-group resampling. Publish assessable-case estimates and worst-case bounds assigning all unassessable cases first negative then positive. No subgroup display if effective n <30 or interval half-width >0.10. If a stratum has too few independent groups to support resampling, combine only a predeclared compatible stratum or withhold its interval; do not silently drop it.

Overall recall needs estimated relevant totals from all three frames and their uncertainty. The accepted-hit weights cannot stand in for the combined population. Publish narrower accepted-hit role/function results if misses remain weakly identified. Preserve `independent_validation=false`; add construct-specific records only after the relevant gates actually pass.

## Reviewable handoff

Needed next: two named Croatian-speaking coders, an adjudicator, frozen grouping, calibration timing, and approval of the final frame allocation after its sizes are known. The first deliverable is 50 independent pilot label pairs and elapsed coding times, not a claim about 400 completed evaluations. No article-level evaluation sample or fabricated labels accompany this draft.
