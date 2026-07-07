# Testy pluginu dotnet-angular-docs

## Warstwy

| Warstwa | Komenda | Koszt | Kiedy |
|---|---|---|---|
| Statyczna | `python dotnet-angular-docs/scripts/validate.py` | darmowa | każdy commit (CI: `validate.yml`) |
| Oficjalny walidator | `claude plugin validate ./dotnet-angular-docs` | darmowa | każdy commit (CI) |
| Selftest parserów + ekstraktora | `python dotnet-angular-docs/tests/run.py --selftest` | darmowa | każdy commit (CI) |
| Behawioralna | `python dotnet-angular-docs/tests/run.py --target <app>` | tokeny API | on-demand / nightly |

## Testy behawioralne — na Twoich źródłach

Cel podajesz przy uruchomieniu — harness testuje plugin na **prawdziwej
aplikacji**, nie na syntetycznym przykładzie:

```bash
python dotnet-angular-docs/tests/run.py --target C:/Projekty/moja-appka
python dotnet-angular-docs/tests/run.py --target ../appka --only drift
python dotnet-angular-docs/tests/run.py --target ../appka --scope "src/OrdersService"   # duże repo
python dotnet-angular-docs/tests/run.py --target ../appka --timeout 2700                # domyślnie 1800 s
python dotnet-angular-docs/tests/run.py --target ../backend --target ../frontend        # multi-repo
python dotnet-angular-docs/tests/run.py --target ../appka --model sonnet                # inny model
```

Multi-repo: każde `--target` to osobne repo — kopie lądują obok siebie w
jednym workdirze (wzorzec workspace-parent), każda z własną historią git;
ekstraktor liczy ground truth z unii wszystkich drzew, a asercje szukają
`docs/api` zarówno w rootcie, jak i per-repo.

Zasady bezpieczeństwa: źródła są **kopiowane** do `dotnet-angular-docs/tests/.work/` (bez
`node_modules`, `bin`, `obj`, `.git`…) i dostają świeżą historię git —
oryginalne repo nie jest dotykane.

### Skąd ground truth na dowolnej aplikacji

`extract.py` to deterministyczny (regex, bez AI) ekstraktor powierzchni API:
kontrolery atrybutowe (`[Route]` + `[HttpGet]`, token `[controller]`),
minimal API (`app.MapGet`, jeden poziom prefiksów `MapGroup`) oraz
**FastEndpoints** (`Get(...)`/`Post(...)` w `Configure()`, w tym trasa jako
stała w tej samej klasie, np. `Get(Route)`). Wyliczony zestaw to wzorzec dla
asercji.

Ekstraktor jest **best-effort dolnym ograniczeniem** powierzchni API, nie
wyrocznią 1:1. Świadome granice: brak zagnieżdżonych łańcuchów `MapGroup`,
prefiksów `Group<T>` FastEndpoints, `[ApiVersion]`, tras z konkatenacji/
interpolacji. Stąd dwa mechanizmy tolerancji:

- **Grounding (twardy fail)** — endpoint udokumentowany, którego segmentów
  ścieżki **nie ma w źródłach**, to fabrykacja → FAIL. Jeśli segmenty są, ale
  ekstraktor nie rozwiązał trasy dokładnie → `WARN`.
- **Completeness** — w trybie `fixture` (kontrolowany, ekstraktor dokładny)
  brak dokumentacji endpointu = FAIL; w trybie `target` (dowolna aplikacja) =
  `WARN`. Dopasowanie jest tolerancyjne na nierozwiązane prefiksy: trasa
  udokumentowana „pokrywa" oczekiwaną, jeśli jej segmenty kończą się
  segmentami oczekiwanej (`/admin/blog/posts` pokrywa `/blog/posts`).

Przykład realnego biegu (duża aplikacja e-commerce: 76 projektów, FastEndpoints): ekstraktor
znalazł 378 endpointów, skill udokumentował 374 z nich (98%) przy **zero
fabrykacji** — 4 WARN-y completeness to endpointy upload/stats warte ręcznego
sprawdzenia.

Sam ekstraktor jest testowany za darmo: `--selftest` porównuje jego wynik na
`dotnet-angular-docs/tests/fixture/` z ręcznie spisanym `dotnet-angular-docs/tests/expected.json`.

### Testy

| Test | Scenariusz | Asercje |
|---|---|---|
| `api` | `/docs-api` na czystych źródłach | zero wymyślonych endpointów; komplet z ekstraktora udokumentowany (completeness wyłączone przy `--scope`) |
| `idempotency` | generacja → ręczna notatka → regeneracja | sentinel przetrwał; brak zduplikowanych sekcji |
| `drift` | generacja → 3 mutacje **w dokach** → `/docs-drift` | raport wykrywa każdą zasadzoną zmianę (hint-centric) |

Mutacje driftowe działają na wygenerowanym markdownie (nie na C#), więc są
niezależne od aplikacji: STALE = podmiana auth na fikcyjną policy `PhantomAdmin`
(fallback: status → 418), ORPHANED = dopisany fikcyjny `GET /api/phantom-widgets`,
MISSING = usunięcie wszystkich linii z trasą realnego endpointu. Każda mutacja
niesie **distinctive hint** (`phantomadmin`, `phantom-widgets`, segment trasy),
którego poprawny raport musi użyć — to jest twardy gate detekcji, odporny na
format raportu.

**Odporność na format.** Skill generuje niedeterministyczny układ — raz
`### GET /route` (metoda w nagłówku), raz `#### Tytuł` + osobna linia
`POST /route`, czasem `**POST** \`/route\``. Parser (`ENDPOINT_RE`) dopasowuje
parę metoda+trasa gdziekolwiek, tolerując markdown między nimi.

**Capture.** Harness używa `--output-format stream-json` i zbiera **całą**
transkrypcję (wszystkie tury asystenta), nie tylko finalną wiadomość — inaczej
raport zapisany w turach pośrednich, zakończony zwięzłym podsumowaniem, byłby
utracony.

Artefakty każdego biegu (doki, logi `claude`) zostają w `dotnet-angular-docs/tests/.work/` —
przy failu zacznij od `*.log`.

## Interpretacja wyników

- `PASS … (N warning(s))` — warningi (`~`) to informacja o granicach
  ekstraktora, nie regresja.
- Pojedynczy `FAIL` — obejrzyj artefakty; output LLM jest niedeterministyczny.
  Powtarzalny fail tej samej asercji po zmianie w `skills/` = realna regresja.
- Znany słaby punkt: `idempotency` może wykazać lukę — szablon `api-docs`
  nie wymusza markerów `docgen:begin/end`. Jeśli failuje właśnie tak,
  poprawką jest dodanie markerów do szablonu skilla, nie zmiana testu.

## Ustalenia z biegów na realnej aplikacji (mikroserwisowy e-commerce, 76 projektów)

- **`docs-api` — mocny.** 76 projektów, FastEndpoints: **0 fabrykacji**,
  374/378 endpointów (98%) udokumentowanych; wykrył nawet realny bug prefiksów
  (docs prefiksują trasy `/api/`, kod rejestruje bez prefiksu).
- **`idempotency` — PASS** na serwisie Payments: ręczna notatka przetrwała
  regenerację.
- **`drift` — PASS.** Audytor wykrył wszystkie zasadzone zmiany
  (STALE/ORPHANED/MISSING) **oraz** realny bug prefiksów.
- **Zagadka „raport nie trafia do pliku" — ROZWIĄZANA.** Przyczyną nie był
  tryb headless, lecz **kolizja nazw**: skill `docs-drift` i komenda
  `docs-drift` rejestrowały się pod tym samym `/plugin:docs-drift`, komenda
  przesłaniała skill i SKILL.md nigdy nie trafiał do kontekstu — model
  improwizował z tekstu wrappera („Report only…"). Po usunięciu wrappera
  Sonnet zapisuje `docs/drift-report.md` idealnie wg szablonu.
  **Reguła:** nazwa komendy nigdy nie może równać się nazwie skilla.
  **Diagnostyka:** grep transkrypcji stream-json po unikalnych frazach ze
  SKILL.md — zero trafień = skill się nie załadował.

## Optymalizacja pod prostsze modele (Sonnet) — zweryfikowana

Bieg `drift` pod `--model sonnet` na tej samej aplikacji: PASS **bez warningów** —
plik raportu zapisany, szablon (Summary/werdykt/dowody file:line) odtworzony
1:1, wszystkie planty wykryte + dodatkowy realny drift. Baseline `api-docs`
pod Sonnetem: 100% nagłówków w ścisłym formacie `### METHOD /route`,
markery `docgen` zbalansowane w każdym pliku, podział per-feature zgodny z
kontraktem. Kluczowe zmiany, które to dały:

1. **Kontrakty wyjścia w skillach** — jawne ścieżki plików, przypięty format
   nagłówka, markery, limit długości odpowiedzi w czacie, checklisty
   "before finishing".
2. **„Plik najpierw"** w `docs-drift` — deliverable powstaje przed audytem.
3. **Komendy-wrappery wymuszają załadowanie skilla** ("REQUIRED FIRST STEP:
   invoke the Skill tool…") i niosą krytyczny kontrakt inline (defense in
   depth, gdy słabszy model pominie indirection).
4. **Harness wywołuje skille bezpośrednio** (`/plugin:api-docs`), nie przez
   wrappery — testuje treść skilla, a `--model sonnet|haiku` pozwala mierzyć
   plugin pod dowolnym modelem.

## Fixture

`dotnet-angular-docs/tests/fixture/` (mini .NET 8 + Angular 17 + EF Core) służy do darmowej
cross-walidacji ekstraktora i jako smoke bez `--target`; do oceny jakości
skilli używaj prawdziwych aplikacji przez `--target`.

## CI

- `.github/workflows/validate.yml` — warstwy darmowe, każdy push/PR.
- `.github/workflows/behavioral.yml` — nightly + `workflow_dispatch`
  (input `only`), na fixture (CI nie ma dostępu do prywatnych aplikacji).
  Wymaga sekretu `ANTHROPIC_API_KEY`.
