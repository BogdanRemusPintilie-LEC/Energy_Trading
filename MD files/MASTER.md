# Master Data Inventory — What's Actually Been Collected

A consolidated view across all 5 collectors' `DATA_FIELDS_*.md` references in this folder,
cross-checked against what's actually sitting on disk right now (not just what each API
*could* provide). If you just want "what data do I have," read sections 1 and 2. Section 3
is the thematic cross-reference across sources. Section 4 rolls up every reliability caveat
in one place, since three of the five collectors have real, confirmed gaps.

## 1. At a glance

| Source | Scope | Files on disk | Rows on disk | Size | Date coverage (real data) | Health |
|---|---|---|---|---|---|---|
| **National Grid ESO** (NESO) | GB system operator — 129 datasets, 16 categories | 38 CSVs | ~1.04M rows | 61.5 MB | Scattered (only the first ~3% of the catalog was ever actually pulled — see §2) | Catalog fully mapped; **actual collection ~3% complete** |
| **GIE AGSI+/ALSI/IIP** | GB\* (post-Brexit UK) gas storage + LNG + REMIT messages | 20 CSVs | ~76,500 rows | 12.3 MB | Real (non-placeholder) data from 2020-12-31 to 2026-07-04 | ✅ Healthy, fully verified |
| **Elexon BMRS** | GB balancing mechanism, settlement, generation, demand | 69 CSVs | ~3.98M rows (**inflated — see §4**) | 240.9 MB | Mostly 2026 (varies by dataset) | ⚠️ 127/205 endpoints work; **rolling-mode files have heavy duplicate rows** |
| **ENTSO-E Transparency Platform** | GB + 5 interconnected neighbors (FR/BE/NL/IE/NO) | 10 CSVs | ~45,900 rows | 3.7 MB | 2026-01-01 to 2026-06-25 | 🔴 Only 10/117 datasets work at all |
| **OpenWeather** | GB (+ Cyprus Sovereign Base Areas) current weather | 1 CSV | 4,882 rows | 1.0 MB | Single snapshot round, not a time series | ✅ Healthy, but snapshot-only |

**Total: ~5.16M rows, ~319 MB, across 138 files.** BMRS dominates the row count, but a large
share of that is duplicated (see §4) — NESO and BMRS both have real caveats that make the
raw row/file counts overstate what's actually usable.

## 2. What's actually been collected, per source

### National Grid ESO — the big gap
The collector's endpoint catalogue is fully mapped (129 datasets, 1,323 resources, ~577M
rows *available*), but the actual backfill that's been run only got through **42 of 1,323
resources (~3%)** before being interrupted — and it stopped alphabetically early, so what's
on disk is a somewhat arbitrary slice: demand forecasts (1/2/7/2-14-day-ahead), some
constraint-management, generation wind forecasts, one network-charges tariff table, and the
`ancillary-services/aggregated-bsad` + notification datasets. **Nothing from balancing,
carbon-intensity, FES, interconnectors, system, or trade-data categories has actually been
pulled yet**, despite the schema for all of it being documented in
`DATA_FIELDS_National Grid ESO.md`. Resuming `neso_collector.py --mode backfill` would pick
up exactly where it left off (state is tracked per-resource) rather than starting over.

### GIE AGSI+/ALSI/IIP — complete for its intended scope
Fully backfilled for the GB\* scope you asked for: gas storage (AGSI) and LNG (ALSI) daily
reports for all 4 UK storage operators + 2 LNG terminals, plus unavailability reports and
news. IIP (Urgent Market Messages) is confirmed genuinely empty for GB\* — not a bug. One
nuance: the date range technically runs back to 2011-01-01 in the files, but everything
before 2020-12-31 is a GIE-generated placeholder row (`status: N`, all values `-`) — real
readings only exist from the Brexit re-coding date onward, exactly as documented.

### Elexon BMRS — partial, and the collected rows need deduplication
69 of the 205 configured endpoints have ever produced a file (consistent with only 127
being confirmed reachable at all — the other ~58 confirmed-working ones just haven't been
backfilled yet, and the 78 broken ones never will produce a file no matter how often it's
run). **New finding this pass:** checking actual row content, several files — confirmed on
`FUELINST.csv` (187,520 rows, all one single settlement date) and `FUELHH.csv` (30,800 rows,
also one date) — show heavy duplication. The collector's `_append_csv()` has no dedup logic,
unlike GIE's `_key`-based upsert or the Transparency Platform's explicit
`drop_duplicates()`. If this collector has been run in `--mode rolling` repeatedly (e.g. on
a schedule) without a corresponding dedup pass, every run re-appends that day's data again.
**Practical implication: don't trust BMRS row counts as row-equivalent-to-unique-readings
until this is fixed or the files are de-duplicated.**

### ENTSO-E Transparency Platform — only the cross-border flows are real
The 10 files on disk are exactly the 10 physical cross-border flow datasets (GB↔FR/BE/NL/IE/NO)
— the only group confirmed working. Every other configured dataset (load, generation, prices,
balancing, most of the interconnector-capacity/auction data) either hits a genuine
post-Brexit GB reporting gap or a parameter bug in the collector, so no file exists for them
and none will appear until `collector.py` is patched per `DATA_FIELDS_Transparency Platform.md`.

### OpenWeather — one full snapshot round
4,882 of 4,883 UK-tagged cities (per OpenWeatherMap's city list, which includes the Cyprus
Sovereign Base Areas under the `GB` code) have a current-weather snapshot. This is **not a
time series** — rerunning the script adds another round of snapshots rather than filling in
history, since the free tier has no historical/forecast endpoint.

## 3. Data available by theme (cross-reference across all sources)

| Theme | Sources that cover it | Notes |
|---|---|---|
| **Electricity demand** | BMRS (`INDDEM`, `NDF*`, `TSDF*`, `DEMAND_*` — mostly ✅), NESO (day-ahead/2-14-day/7-day/historic demand forecasts — schema documented, mostly not yet pulled), ENTSO-E (`load_*` — ⚠️ GB gap since 2021) | BMRS is the only source with confirmed *and collected* GB demand data right now |
| **Generation / fuel mix** | BMRS (`FUELINST`/`FUELHH` ✅ collected but duplicated, `B1610` per-unit ✅), NESO (wind forecasts, OPMR, embedded wind/solar — documented, not yet collected), ENTSO-E (⚠️ GB gap) | |
| **Wholesale / balancing prices** | BMRS (`MID` market index ✅, `MDP`/`MDV` ✅), ENTSO-E `prices_day_ahead` (⚠️ GB gap since before mid-2021) | BMRS is the only live source for GB prices |
| **Balancing mechanism / imbalance** | BMRS (`BOD`, `DISBSAD`, `NETBSAD`, `QAS` — all ✅ and collected), ENTSO-E balancing group (mostly 🐛 broken params) | |
| **Ancillary services (reserve, response, DFS)** | NESO (31 datasets — FFR, STOR, EAC auctions, DFS, ODFM — documented, mostly not yet collected) | NESO is the only source for this theme; nothing pulled yet |
| **System frequency / inertia / stability** | BMRS (`FREQ`/`SYSTEM_FREQ` ✅), NESO (`system-frequency-data`, `system-inertia*` — documented, not yet collected) | |
| **Interconnectors / cross-border flows** | ENTSO-E (10 flow datasets — ✅ fully collected), NESO (per-interconnector datasets: BritNed, ElecLink, IFA/IFA2, NSL, Viking — documented, not yet collected), BMRS (`IGCA`/`IGCPU`/`*ATL` — 🐛 all broken) | ENTSO-E flows are the one clean win here |
| **Outages / unavailability (REMIT)** | GIE (AGSI/ALSI unavailability ✅ collected), ENTSO-E outages group (mostly 🐛/⚠️), BMRS REMIT endpoints (🐛 all broken) | GIE is the only fully working REMIT-outage source |
| **Gas storage** | GIE AGSI (✅ fully collected for GB\*) | Sole source |
| **LNG** | GIE ALSI (✅ fully collected for GB\*) | Sole source |
| **Network charges / constraint costs** | NESO (TNUoS, AAHEDC, constraint-management category — partially collected: AAHEDC tariffs + one constraint forecast) | |
| **Long-range planning (FES, capacity market)** | NESO (15 FES datasets + capacity market register — documented, not yet collected) | Sole source |
| **Weather** | OpenWeather (✅ one snapshot round) | Sole source; not historical |
| **Reference / static data** (BMU registers, EIC mappings, fuel types) | BMRS (`REF_*` ✅), GIE (EIC listing, embedded in collector's own catalog file) | |

## 4. Known issues, all in one place

| Issue | Affects | Severity |
|---|---|---|
| Only ~3% of the catalog ever collected | NESO | High — most of NESO's documented data doesn't exist on disk yet |
| 78/205 endpoints dead (stale codes, missing `/stream` suffix, restructured paths) | BMRS | High — silently returns 0 rows, no error |
| Rolling-mode files likely contain heavy duplicate rows (`_append_csv` has no dedup) | BMRS | **New finding** — inflates row counts, needs a dedup pass or a fix mirroring GIE's `_key` upsert |
| 80/117 datasets have genuine parameter bugs (missing/invalid params, confirmed via France) | ENTSO-E | High — most of the collector doesn't work at all |
| 22/117 datasets hit a real post-Brexit GB reporting gap (not fixable in the collector) | ENTSO-E | Structural — GB stopped publishing these to ENTSO-E; use BMRS/NESO instead |
| API key hardcoded in source rather than `.env` | OpenWeather | Low — cosmetic/security hygiene, not a data issue |
| `country: GB` includes Cyprus Sovereign Base Areas, not just mainland UK | OpenWeather | Low — filter by city name/coords if you need UK-only |
| GIE date range includes pre-2020-12-31 placeholder rows (`status: N`) that look like real history but aren't | GIE | Low — documented, just don't mistake `N`-status rows for real readings |

## 5. Geographic scope

Everything here is GB-centric by design: BMRS and NESO are GB-only by nature; GIE is scoped
to `GB*` (post-Brexit UK) specifically; ENTSO-E covers GB plus its 5 physical interconnector
neighbors (France, Belgium, Netherlands, Ireland, Norway); OpenWeather is nominally GB but
also sweeps in the Cyprus Sovereign Base Areas as a side effect of how OpenWeatherMap tags
country codes.

## 6. Full reference docs

- `DATA_FIELDS_National Grid ESO.md` — full 129-dataset field catalog
- `DATA_FIELDS_GIE AGSI+.md` — AGSI/ALSI/IIP field reference
- `DATA_FIELDS_Elexon BMRS API.md` — all 205 endpoints, health-tested
- `DATA_FIELDS_Transparency Platform.md` — all 117 datasets, health-tested with root causes
- `DATA_FIELDS_OpenWeather API.md` — current-weather field reference
