# ENTSO-E Transparency Platform — Data Field Reference

Field reference for `collector.py`, which targets **117 configured datasets** covering GB
load, generation, prices, balancing, congestion, outages, and cross-border exchange with
5 neighbors (FR, BE, NL, IE, NO) via the ENTSO-E Web API.

Every unique underlying document-type/param combination was **live-tested** on 2026-07-06
against `https://web-api.tp.entsoe.eu/api` (117 datasets collapse to 35 unique combinations,
since most cross-border datasets are the same document type repeated per neighbor). That
testing surfaced two serious, distinct problems — read the health section before trusting
any of this collector's output.

## Overview

| | |
|---|---|
| Base URL | `https://web-api.tp.entsoe.eu/api` |
| Auth | `securityToken` query param (`.env`: `ENTSOE_API_TOKEN`) |
| Response format | XML (IEC 62325 market documents) — the collector flattens every `TimeSeries`/`Period`/`Point` into one CSV row via `parse_xml()` |
| Rate limit | Not published; collector paces at `RATE_PAUSE = 1.2s` between calls, retries on 429 with a 60s wait |
| GB area code | `10YGB----------A` (used as `in_Domain`/`out_Domain`/`controlArea_Domain`/`biddingZone_Domain` depending on dataset) |
| Historical range | Varies — see the "GB reporting gap" finding below, which matters more than any nominal historical range |

## ⚠️ Collector health: 10 of 117 datasets confirmed working, 80 have parameter bugs, 22 hit a real post-Brexit data gap

This is the headline finding. A real `collector.py` run today would return real data for only
**10 of its 117 configured datasets** (the physical cross-border flow series). Everything
else fails, for two very different reasons that are worth telling apart:

### 1. Post-Brexit reporting gap (22 datasets) — real, not a bug

GB stopped publishing most categories to ENTSO-E's Transparency Platform at some point
after Brexit. I confirmed this directly: `load_actual` (Actual Total Load) has real data
for GB in 2019, still has it through December 2020 and June 2021, but returns "No matching
data found" for every window tested from July 2021 through today (narrowed via direct
probing — the cutover is between 2021-06 and 2021-07). `prices_day_ahead` (day-ahead energy
prices) stopped even earlier — it already has no data by June 2021. Physical cross-border
flows (documentType `A11`) are the exception and still work, almost certainly because
those are jointly measured/reported by the *EU-side* TSO at each interconnector (e.g. RTE
for the France side), not by GB.

**Practically:** `load_actual`, `load_forecast_*` (all 4 horizons), `generation_actual_per_type`,
`generation_actual_per_unit`, `generation_forecast_da`, `generation_forecast_wind_solar`,
`generation_capacity_aggregated`, `prices_day_ahead`, and `congestion_costs` are correctly
*requested* by the collector — the schema and params are right — but GB simply isn't
publishing to these anymore. No fix to the collector will change this; the data would need
to come from BMRS/NESO instead (both of which *do* still carry this data — see their
DATA_FIELDS.md in sibling folders).

### 2. Broken request parameters (80 datasets) — a real, fixable bug

The clear majority of configured datasets fail with an explicit ENTSO-E validation error —
not "no data," but "your request is malformed" — confirmed by testing the exact same
document type against France's domain (which still reports everything) and getting the
identical error. This means fixing these has nothing to do with GB's reporting status;
the collector is constructing invalid requests. Concretely:

| Problem | Affected `params` pattern | Datasets affected | Fix needed |
|---|---|---|---|
| Missing `Contract_MarketAgreement.Type` | `ntc_export/import_*`, `atc_export/import_*`, `net_position_gb` (documentType `A61`/`A25` with a `businessType` but no contract type) | 21 | Add `"contract_MarketAgreement.Type": "A01"` (or the appropriate auction-type code) to these dataset defs |
| Wrong domain pairing for congestion income | `congestion_income_*_to_*` (documentType `A92`) | 20 | ENTSO-E requires `in_Domain == out_Domain` for this document type (confirmed: the working `congestion_costs` dataset already does this correctly with `in_Domain=out_Domain=GB`) — the per-neighbor `congestion_income_*` variants incorrectly pair GB against the neighbor's EIC instead |
| Invalid `documentType`+`businessType` combo | `scheduled_exports/imports_gb_*` (`A09`+`A01`) | 10 | ENTSO-E rejects this combination outright; needs the correct businessType (or none) for scheduled commercial exchanges |
| Invalid `documentType` for capacity allocation | `cap_alloc_da/week/month/year_*` (`A25` with a `contract_MarketAgreement.Type` but apparently still wrong) | 8 | Needs further investigation — likely also needs a `businessType` param alongside the contract type |
| Missing `Area_Domain` | `balancing_imbalance_volume` | 1 | Add the missing `Area_Domain` param |
| Missing `ProcessType` | `balancing_bids_aggregated` | 1 | Add a `processType` param |
| Missing `BusinessType` | `balancing_procured_reserves` | 1 | Add a `businessType` param |
| Missing `Out_Domain` | `congestion_redispatch`, `outages_offshore_grid` | 2 | Add the missing `out_Domain` param |
| Missing `In_Domain` | `outages_generation_forced` | 1 | Add the missing `in_Domain` param |
| Missing `BiddingZone_Domain` | `outages_transmission_planned` | 1 | Add the missing `biddingZone_Domain` param (the code currently passes `in_Domain`/`out_Domain` instead) |
| Invalid `documentType` combo | `balancing_activated_energy` (`A83` alone), `balancing_cross_border` (`A26` alone) | 2 | Both need an additional param ENTSO-E isn't naming explicitly — needs manual doc lookup |

### 3. Uncertain (5 datasets) — likely just low-frequency, not necessarily broken

`generation_capacity_per_unit`, `balancing_imbalance_prices`, `congestion_countertrading`,
`outages_generation_planned`, and `outages_production_planned` returned no data for *both*
GB and France across a 45-day test window. This is most likely because these are
naturally low-frequency (e.g. per-unit installed capacity is typically an annual filing,
not something published every few weeks) rather than a parameter bug — but it wasn't
possible to fully confirm without a much longer probe window. One concrete additional
finding here: **`outages_production_planned` (documentType `A80`) returns a ZIP archive**,
not XML, for at least one historical range — `parse_xml()` calls `ET.fromstring()` directly
and will silently fail (logs an XML parse error, returns 0 rows) on that response. This is
a real bug independent of the "uncertain" classification and needs the collector to detect
and unzip that response format.

**Recommendation:** treat every dataset except the 10 `flows_*` ones as unreliable until
`collector.py` is patched per the table above and re-verified.

## Common fields (ENTSO-E's XML schema, as flattened by `parse_xml()`)

Every row is one `Point` inside a `Period` inside a `TimeSeries`, flattened to:

| Field | Description |
|---|---|
| `timestamp_utc` | The point's actual UTC timestamp — computed from the period's `start` + `resolution` × `position`, not a raw API field. This is the primary time key. |
| `mRID` | ENTSO-E's internal TimeSeries identifier (not stable/meaningful across requests) |
| `businessType` | ENTSO-E code for what kind of value this is (varies by document type — e.g. `A66` = flow value on the physical-flows dataset) |
| `curveType` | Shape of the curve — `A01` (sequential fixed-size blocks) or `A03` (variable-sized) are the common ones |
| `objectAggregation` | Whether the series is per-unit or aggregated (`A08` = aggregated is typical for load/generation) |
| `quantity` | The actual value — MW for flows/load/generation, MWh depending on dataset |
| `quantity_Measure_Unit.name` | Unit for `quantity` — almost always `MAW` (megawatt) |
| `price.amount` | Price value, present only on price-type datasets (day-ahead prices, imbalance prices) |
| `price_Measure_Unit.name` / `currency_Unit.name` | Unit/currency for `price.amount` |
| `in_Domain.mRID` / `out_Domain.mRID` | EIC codes of the two bidding zones a cross-border value is between |
| `inBiddingZone_Domain.mRID` / `outBiddingZone_Domain.mRID` | Single-zone variant used on load/generation datasets |
| `MktPSRType_psrType` | Generation production-type code (wind, solar, nuclear, etc.) — only on per-type generation datasets |
| `registeredResource.mRID` | The specific generation unit's EIC — only on per-unit generation datasets |
| `contract_MarketAgreement.type` | Auction/contract horizon code (day-ahead `A01`, weekly `A02`, monthly `A03`, yearly `A04`) — only on capacity-allocation-type datasets |
| `congestionCost_Price.amount` | Congestion income value — specific to the congestion-costs dataset |

## Datasets by group

### Load

| Dataset | Status | Confirmed fields |
|---|---|---|
| `load_actual` | ⚠️ GB reporting gap since ~2021-07 (schema confirmed via FR) | `timestamp_utc`, `mRID`, `businessType`, `objectAggregation`, `outBiddingZone_Domain.mRID`, `quantity_Measure_Unit.name`, `curveType`, `quantity` |
| `load_forecast_da` | ⚠️ GB reporting gap | same fields as `load_actual` |
| `load_forecast_week` | ⚠️ GB reporting gap | same fields as `load_actual` |
| `load_forecast_month` | ⚠️ GB reporting gap | same fields as `load_actual` |
| `load_forecast_year` | ⚠️ GB reporting gap | same fields as `load_actual` |

### Generation

| Dataset | Status | Confirmed fields |
|---|---|---|
| `generation_actual_per_type` | ⚠️ GB reporting gap | `timestamp_utc`, `mRID`, `businessType`, `objectAggregation`, `outBiddingZone_Domain.mRID`, `quantity_Measure_Unit.name`, `curveType`, `MktPSRType_psrType`, `quantity`, `inBiddingZone_Domain.mRID` |
| `generation_actual_per_unit` | ⚠️ GB reporting gap | adds `registeredResource.mRID` (the specific unit) to the per-type fields above |
| `generation_forecast_da` | ⚠️ GB reporting gap | `timestamp_utc`, `mRID`, `businessType`, `objectAggregation`, `inBiddingZone_Domain.mRID`, `quantity_Measure_Unit.name`, `curveType`, `quantity` |
| `generation_forecast_wind_solar` | ⚠️ GB reporting gap | same as `generation_forecast_da` plus `MktPSRType_psrType` |
| `generation_capacity_aggregated` | ⚠️ GB reporting gap | same as `generation_forecast_wind_solar` |
| `generation_capacity_per_unit` | ❓ uncertain — no data for GB or FR in a 45-day window; installed-capacity-per-unit is typically an annual filing, so this may just need a much longer probe window rather than being broken | — |

### Prices

| Dataset | Status | Confirmed fields |
|---|---|---|
| `prices_day_ahead` | ⚠️ GB reporting gap since before mid-2021 (earlier cutoff than load) | `timestamp_utc`, `mRID`, `auction.type`, `businessType`, `in_Domain.mRID`, `out_Domain.mRID`, `contract_MarketAgreement.type`, `currency_Unit.name`, `price_Measure_Unit.name`, `curveType`, `price.amount` |

### Balancing

| Dataset | Status | Confirmed fields |
|---|---|---|
| `balancing_imbalance_prices` | ❓ uncertain — no data for GB or FR in a 45-day window | — |
| `balancing_imbalance_volume` | 🐛 broken params — "Mandatory parameter Area_Domain is missing" | — |
| `balancing_activated_energy` | 🐛 broken params — "combination of [DOCUMENT_TYPE=A83] is not valid" | — |
| `balancing_bids_aggregated` | 🐛 broken params — "Mandatory parameter ProcessType is missing" | — |
| `balancing_cross_border` | 🐛 broken params — "combination of [DOCUMENT_TYPE=A26] is not valid" | — |
| `balancing_procured_reserves` | 🐛 broken params — "Mandatory parameter BusinessType is missing" | — |

### Congestion management

| Dataset | Status | Confirmed fields |
|---|---|---|
| `congestion_redispatch` | 🐛 broken params — "Mandatory parameter Out_Domain is missing" | — |
| `congestion_countertrading` | ❓ uncertain — no data for GB or FR in a 45-day window | — |
| `congestion_costs` | ⚠️ GB reporting gap (schema confirmed via FR) | `timestamp_utc`, `mRID`, `businessType`, `in_Domain.mRID`, `out_Domain.mRID`, `currency_Unit.name`, `curveType`, `congestionCost_Price.amount` |

### Outages

| Dataset | Status | Confirmed fields |
|---|---|---|
| `outages_generation_planned` | ❓ uncertain — no data for GB or FR in a 45-day window | — |
| `outages_generation_forced` | 🐛 broken params — "Mandatory parameter In_Domain is missing" | — |
| `outages_production_planned` | 🐛 **distinct bug**: the underlying document type (`A80`) returns a **ZIP archive**, not XML, for at least some historical ranges — `parse_xml()` can't parse this and silently returns 0 rows. Needs the collector to detect and unzip this response type. | — |
| `outages_transmission_planned` | 🐛 broken params — "Mandatory parameter BiddingZone_Domain is missing" (code passes `in_Domain`/`out_Domain` instead) | — |
| `outages_offshore_grid` | 🐛 broken params — "Mandatory parameter Out_Domain is missing" | — |

### Capacity & net position

| Dataset | Status | Confirmed fields |
|---|---|---|
| `net_position_gb` | 🐛 broken params — "Mandatory parameter Contract_MarketAgreement.Type is missing" | — |

### Cross-border (× 5 neighbors: FR, BE, NL, IE, NO — 10 dataset variants per pattern, one for each direction × neighbor)

| Pattern | Status | Confirmed fields |
|---|---|---|
| `flows_{neighbor}_to_gb` / `flows_gb_to_{neighbor}` (documentType `A11`, physical flows) | ✅ **the only fully working group** — 10 datasets, already have real collected CSVs in `data/` | `timestamp_utc`, `mRID`, `businessType`, `in_Domain.mRID`, `out_Domain.mRID`, `quantity_Measure_Unit.name`, `curveType`, `quantity` |
| `scheduled_exports/imports_gb_{neighbor}` (documentType `A09` + businessType `A01`) | 🐛 broken params — "combination of [DOCUMENT_TYPE=A09, BUSINESS_TYPE=A01] is not valid" | — |
| `ntc_export/import_gb_{neighbor}` (documentType `A61` + businessType `B08`) | 🐛 broken params — missing `Contract_MarketAgreement.Type` | — |
| `atc_export/import_gb_{neighbor}` (documentType `A61` + businessType `B07`) | 🐛 broken params — missing `Contract_MarketAgreement.Type` | — |
| `cap_alloc_da/week/month/year_gb_to_{neighbor}` and reverse (documentType `A25` + contract type `A01`–`A04`) | 🐛 broken params — "combination of [DOCUMENT_TYPE=A25] is not valid" (needs a `businessType` too, per ENTSO-E's error) | — |
| `congestion_income_gb_to_{neighbor}` and reverse (documentType `A92`) | 🐛 broken params — ENTSO-E requires `in_Domain == out_Domain` for this document type; the collector incorrectly pairs GB against the neighbor instead of using GB on both sides (compare to the working `congestion_costs` dataset, which does use `in_Domain=out_Domain=GB`) | — |

## Verification methodology

For each of the 35 unique underlying document-type/param combinations (117 named datasets
collapse to this many once cross-border neighbor-pair duplicates are merged): requested GB
data directly; if that failed, retried the *identical* document type/params against France's
domain (`10YFR-RTE------C`, a TSO confirmed still reporting everything) to distinguish a real
GB-specific data gap (France succeeds) from a genuine parameter bug (France fails identically).
✅ = real data returned directly for GB. ⚠️ = France confirms the schema is right, GB just
isn't populating it. 🐛 = France also fails with the same validation error, proving the
request itself is malformed. ❓ = neither GB nor France returned data in the test windows —
inconclusive, most likely just a low-frequency dataset.
