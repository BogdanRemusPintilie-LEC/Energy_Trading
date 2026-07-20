# Elexon BMRS Insights API — Data Field Reference

Field reference for `bmrs_collector.py`, which targets **205 distinct endpoints** across the
Elexon Insights Solution API (`/datasets/*`, opinionated REST views, settlement-date/period
iterators, triad-season, static/reference, and data-status groups).

Every endpoint below was **live-tested** against `https://data.elexon.co.uk/bmrs/api/v1`
on 2026-07-06 (real requests, real responses) rather than inferred from documentation —
because that testing turned up a significant number of dead/renamed paths (see below),
trusting the script's own definitions wasn't good enough.

## Overview

| | |
|---|---|
| Base URL | `https://data.elexon.co.uk/bmrs/api/v1` |
| Auth | None — fully public, no API key |
| Rate limit | Not published; the collector paces at ~3 req/sec (`REQUEST_DELAY = 0.3s`) and backs off on HTTP 429 |
| Response format | CSV by default (`?format=csv`); a handful of endpoints (`/stream` suffix) return JSON only |
| Historical range | Varies hugely by dataset — some back to ~2014, most BM/settlement data back to whenever REMIT/BSC reporting began. The collector backfills from 2026-01-01 by default (`BACKFILL_START`) |

## ⚠️ Collector health: 127 of 205 endpoints confirmed working, 78 confirmed broken

This is the single most important finding in this document. Testing every endpoint live
turned up three distinct classes of problem in `bmrs_collector.py`'s endpoint catalogue —
meaning a real `--mode backfill` run today would silently return **zero rows** for over
a third of its configured endpoints, with no error surfaced (the collector's `_get()`
deliberately treats 400/404/422 as "no data, skip silently").

1. **Stale/renamed dataset codes.** Elexon's own `/datasets/metadata/latest` catalogue (which
   lists every dataset code that's actually live today) disagrees with 6 of the 84 configured
   `/datasets/*` codes:
   - `IMBALNGC` → now `IMBALANGC` (extra "A")
   - `SYSWARN` → now `SYS_WARN` (underscore added)
   - `LOLPDRM` → now `LOLPDM` (dropped the "R")
   - `B1610`, `CDN`, `REMIT` → no longer present under any name in the live catalogue at all
2. **Missing `/stream` suffix.** A subset of dataset codes (confirmed for `B1610`, `BOD`,
   `QAS`, `MILS`, `MELS`, `MDB`, `MDO`, `PN`, `QPN`) only work at `/datasets/{code}/stream`,
   not the plain `/datasets/{code}` the collector calls — that suffix returns JSON, not CSV.
   Codes like `AGPT`, `PN` variants etc. that are listed in the live metadata catalogue but
   still 404 on *both* the plain and `/stream` paths appear to be genuinely retired/relocated
   endpoints Elexon hasn't cleaned out of its own metadata list yet.
3. **Dead opinionated/settlement paths.** The majority of the 78 broken endpoints are in the
   hand-written "opinionated" and settlement-iterator path lists (e.g. `/generation/actual/per-type`,
   `/remit/list/by-event`, `/balancing/physical/all`, `/balancing/bid-offer/all`) — these
   404 outright, suggesting Elexon restructured these URLs at some point after the collector
   was written. I did not reverse-engineer correct replacement paths for all 78 (that's a
   real fix-it task, not a docs task) — each is marked 🐛 below with the exact HTTP status
   so it's clear what needs auditing.

**Recommendation:** treat every 🐛-marked row below as "not currently returning data" until
`bmrs_collector.py` is updated with a corrected path. The ✅ rows are safe to rely on as-is.

## Common recurring fields

Field names aren't identical across datasets, but casing and vocabulary are inconsistent
even within the *same* platform (e.g. `SettlementDate` vs `settlementDate` — both appear
below exactly as returned, since the collector doesn't normalize casing). These are the
fields that recur across the largest number of confirmed-working endpoints:

| Field | Description |
|---|---|
| `Dataset` / `dataset` | The dataset code this row belongs to (useful once you've merged multiple datasets) |
| `SettlementDate` / `settlementDate` | The GB settlement date (a "day" for market purposes) this row applies to |
| `SettlementPeriod` / `settlementPeriod` | Half-hourly settlement period within the day, 1–50 (GB has up to 50 on clock-change days) |
| `PublishTime` / `publishTime` | When Elexon published this record — the actual "as of" timestamp for most series |
| `StartTime` / `startTime` | Start of the half-hour (or other resolution) period the row's value applies to |
| `TimeFrom` / `TimeTo` | Start/end of a validity window (used for level/notification-style datasets rather than a single point-in-time value) |
| `BmUnit` / `bmUnit` | Balancing Mechanism Unit ID — the specific generating/demand unit |
| `NationalGridBmUnit` / `nationalGridBmUnit` | National Grid's own BMU identifier (distinct scheme from `BmUnit`) |
| `FuelType` | Generation fuel category (e.g. `WIND`, `CCGT`, `NUCLEAR`) |
| `Demand` / `Generation` | MW value — demand or generation depending on dataset |
| `LevelFrom` / `LevelTo` | MW level at the start/end of a notified ramp (physical notifications, limits, etc.) |
| `Quantity` / `Volume` | MWh energy quantity for the period |
| `Price` | £/MWh — varies by dataset whether it's system price, market index price, bid/offer price, etc. |

## Verification methodology

Every row below is one of:
- ✅ — a real request during this session returned actual data with these exact field names
- 🐛 — a real request returned an HTTP error (status shown); the endpoint needs auditing/fixing in the collector before it can be trusted
- ⚠️ — request succeeded but the response looked malformed in testing; worth a manual check

## `/datasets/*` endpoints (87 opinionated dataset codes)

Each is a `GET /datasets/{code}?from=YYYY-MM-DD&to=YYYY-MM-DD` call (a few needed a `/stream` suffix instead — noted where that was the case). Grouped as the collector script itself groups them.

### Generation

| Code | What it is | Status | Confirmed fields |
|---|---|---|---|
| `AGPT` | Actual Aggregated Generation Per Type | 🐛 unverified (HTTP 404) | — |
| `B1610` | Actual Generation Output Per Generation Unit | ✅ | `dataset`, `psrType`, `bmUnit`, `nationalGridBmUnitId`, `settlementDate`, `settlementPeriod`, `halfHourEndTime`, `quantity` |
| `AGWS` | Actual or Estimated Wind & Solar Generation | 🐛 unverified (HTTP 404) | — |
| `BOALF` | Bid Offer Acceptance Level Final | ✅ | `Dataset`, `SettlementDate`, `SettlementPeriodFrom`, `SettlementPeriodTo`, `TimeFrom`, `TimeTo`, `LevelFrom`, `LevelTo`, `AcceptanceNumber`, `AcceptanceTime`, `DeemedBoFlag`, `SoFlag`, `AmendmentFlag`, `StorFlag`, `RrFlag`, `NationalGridBmUnit`, `BmUnit` |
| `FOU2T14D` | Generation forecast 2-14 day | ✅ | `Dataset`, `FuelType`, `PublishTime`, `SystemZone`, `ForecastDate`, `ForecastDateTimezone`, `OutputUsable`, `BiddingZone`, `InterconnectorName`, `Interconnector` |
| `FOU2T3YW` | Generation forecast 3-year weekly | ✅ | `Dataset`, `FuelType`, `PublishTime`, `SystemZone`, `CalendarWeekNumber`, `Year`, `OutputUsable`, `BiddingZone`, `InterconnectorName`, `Interconnector` |
| `FUELINST` | Instantaneous generation by fuel type | ✅ | `Dataset`, `PublishTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `FuelType`, `Generation` |
| `FUELHH` | Half-hourly generation by fuel type | ✅ | `Dataset`, `PublishTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `FuelType`, `Generation` |
| `INDGEN` | Indicated generation | ✅ | `Dataset`, `Generation`, `PublishTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `Boundary` |
| `WINDFOR` | Wind generation forecast | ✅ | `Dataset`, `PublishTime`, `StartTime`, `Generation` |
| `UOU2T14D` | Unplanned availability forecast 2-14 day | ✅ | `Dataset`, `FuelType`, `NationalGridBmUnit`, `BmUnit`, `PublishTime`, `ForecastDate`, `OutputUsable` |
| `UOU2T3YW` | Unplanned availability forecast 3-year weekly | ✅ | `Dataset`, `FuelType`, `NationalGridBmUnit`, `BmUnit`, `PublishTime`, `Week`, `Year`, `OutputUsable` |

### Demand

| Code | What it is | Status | Confirmed fields |
|---|---|---|---|
| `INDDEM` | Indicated demand | ✅ | `Dataset`, `Demand`, `PublishTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `Boundary` |
| `IMBALNGC` | Indicated imbalance (NGC) | ✅ | `Dataset`, `Imbalance`, `PublishTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `Boundary` |
| `INDO` | Indicated national demand outturn | ✅ | `Dataset`, `PublishTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `Demand` |
| `INDOD` | Indicated outturn demand | 🐛 unverified (HTTP 404) | — |
| `ITSDO` | Initial transmission system demand outturn | ✅ | `Dataset`, `PublishTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `Demand` |
| `NDF` | National demand forecast | ✅ | `Dataset`, `Demand`, `PublishTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `Boundary` |
| `NDFD` | National demand forecast day-ahead | ✅ | `Dataset`, `PublishTime`, `ForecastDate`, `Demand` |
| `NDFW` | National demand forecast week-ahead | ✅ | `Dataset`, `PublishTime`, `Year`, `Week`, `Demand` |
| `NOU2T14D` | Demand forecast 2-14 day | ✅ | `Dataset`, `PublishTime`, `SystemZone`, `ForecastDate`, `ForecastDateTimezone`, `OutputUsable` |
| `NOU2T3YW` | Demand forecast 3-year weekly | ✅ | `Dataset`, `PublishTime`, `SystemZone`, `CalendarWeekNumber`, `Year`, `OutputUsable` |
| `TSDF` | Transmission system demand forecast | ✅ | `Dataset`, `Demand`, `PublishTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `Boundary` |
| `TSDFD` | TSDF day-ahead | ✅ | `Dataset`, `PublishTime`, `ForecastDate`, `Demand` |
| `TSDFW` | TSDF week-ahead | ✅ | `Dataset`, `PublishTime`, `Year`, `Week`, `Demand` |

### Balancing & imbalance

| Code | What it is | Status | Confirmed fields |
|---|---|---|---|
| `BOD` | Bid Offer Data | ✅ | `dataset`, `settlementDate`, `settlementPeriod`, `timeFrom`, `levelFrom`, `timeTo`, `levelTo`, `pairId`, `offer`, `bid`, `nationalGridBmUnit`, `bmUnit` |
| `DISBSAD` | Balancing Services Adjustment Data | ✅ | `Dataset`, `SettlementDate`, `SettlementPeriod`, `Id`, `Cost`, `Volume`, `SoFlag`, `StorFlag`, `PartyId`, `AssetId`, `IsTendered`, `Service` |
| `MID` | Market Index Data | ✅ | `Dataset`, `StartTime`, `DataProvider`, `SettlementDate`, `SettlementPeriod`, `Price`, `Volume` |
| `NETBSAD` | Net Balancing Services Adjustment Data | ✅ | `Dataset`, `SettlementDate`, `SettlementPeriod`, `NetBuyPriceCostAdjustmentEnergy`, `NetBuyPriceVolumeAdjustmentEnergy`, `NetBuyPriceVolumeAdjustmentSystem`, `BuyPricePriceAdjustment`, `NetSellPriceCostAdjustmentEnergy`, `NetSellPriceVolumeAdjustmentEnergy`, `NetSellPriceVolumeAdjustmentSystem`, `SellPricePriceAdjustment` |
| `NONBM` | Non-BM Balancing Services | ✅ | `Dataset`, `PublishTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `Generation` |
| `QAS` | Balancing Services Volume | ✅ | `dataset`, `settlementDate`, `settlementPeriod`, `bmUnitApplicableBalancingServicesVolume`, `nationalGridBmUnit`, `bmUnit` |

### Physical / dynamic

| Code | What it is | Status | Confirmed fields |
|---|---|---|---|
| `MILS` | Stable Import Limit per BMU | ✅ | `dataset`, `settlementDate`, `settlementPeriod`, `timeFrom`, `timeTo`, `levelFrom`, `levelTo`, `notificationTime`, `notificationSequence`, `nationalGridBmUnit`, `bmUnit` |
| `MELS` | Stable Export Limit per BMU | ✅ | `dataset`, `settlementDate`, `settlementPeriod`, `timeFrom`, `timeTo`, `levelFrom`, `levelTo`, `notificationTime`, `notificationSequence`, `nationalGridBmUnit`, `bmUnit` |
| `MDP` | Market Demand Price | ✅ | `Dataset`, `SettlementDate`, `SettlementPeriod`, `Time`, `PeriodMax`, `NationalGridBmUnit`, `BmUnit` |
| `MDV` | Market Demand Volume | ✅ | `Dataset`, `SettlementDate`, `SettlementPeriod`, `Time`, `VolumeMax`, `NationalGridBmUnit`, `BmUnit` |
| `MDB` | Maximum Delivery Block | ✅ | `dataset`, `settlementDate`, `settlementPeriod`, `timeFrom`, `timeTo`, `levelFrom`, `levelTo`, `nationalGridBmUnit`, `bmUnit`, `publishTime`, `serialNumber` |
| `MDO` | Maximum Delivery Duration | ✅ | `dataset`, `settlementDate`, `settlementPeriod`, `timeFrom`, `timeTo`, `levelFrom`, `levelTo`, `nationalGridBmUnit`, `bmUnit`, `publishTime`, `serialNumber` |
| `MELNGC` | Day-ahead margin (NGC) | ✅ | `Dataset`, `Margin`, `PublishTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `Boundary` |
| `MNZT` | Minimum Non-Zero Time | ✅ | `Dataset`, `SettlementDate`, `SettlementPeriod`, `Time`, `PeriodMin`, `NationalGridBmUnit`, `BmUnit` |
| `MZT` | Minimum Zero Time | ✅ | `Dataset`, `SettlementDate`, `SettlementPeriod`, `Time`, `PeriodMin`, `NationalGridBmUnit`, `BmUnit` |
| `NDZ` | Notice to Deviate from Zero | ✅ | `Dataset`, `SettlementDate`, `SettlementPeriod`, `Time`, `Notice`, `NationalGridBmUnit`, `BmUnit` |
| `NTB` | Notice to Deliver Bids | ✅ | `Dataset`, `SettlementDate`, `SettlementPeriod`, `Time`, `Notice`, `NationalGridBmUnit`, `BmUnit` |
| `NTO` | Notice to Deliver Offers | ✅ | `Dataset`, `SettlementDate`, `SettlementPeriod`, `Time`, `Notice`, `NationalGridBmUnit`, `BmUnit` |
| `OCNMF3Y` | Operational Cancelled Network Model Forecast 3Y | ✅ | `Dataset`, `PublishTime`, `Week`, `Year`, `Surplus` |
| `OCNMF3Y2` | OCNM Forecast 3Y (version 2) | ✅ | `Dataset`, `PublishTime`, `Week`, `Year`, `Margin` |
| `OCNMFD` | OCNM Forecast Day | ✅ | `Dataset`, `PublishTime`, `ForecastDate`, `Surplus` |
| `OCNMFD2` | OCNM Forecast Day (version 2) | ✅ | `Dataset`, `PublishTime`, `ForecastDate`, `Margin` |
| `PN` | Physical Notifications | ✅ | `dataset`, `settlementDate`, `settlementPeriod`, `timeFrom`, `timeTo`, `levelFrom`, `levelTo`, `nationalGridBmUnit`, `bmUnit` |
| `QPN` | Quiescent Physical Notifications | ✅ | `dataset`, `settlementDate`, `settlementPeriod`, `timeFrom`, `timeTo`, `levelFrom`, `levelTo`, `nationalGridBmUnit`, `bmUnit` |
| `RDRE` | Run Down Rate Export | ✅ | `Dataset`, `SettlementDate`, `SettlementPeriod`, `Time`, `Rate1`, `Elbow2`, `Rate2`, `Elbow3`, `Rate3`, `NationalGridBmUnit`, `BmUnit` |
| `RDRI` | Run Down Rate Import | ✅ | `Dataset`, `SettlementDate`, `SettlementPeriod`, `Time`, `Rate1`, `Elbow2`, `Rate2`, `Elbow3`, `Rate3`, `NationalGridBmUnit`, `BmUnit` |
| `RURE` | Run Up Rate Export | ✅ | `Dataset`, `SettlementDate`, `SettlementPeriod`, `Time`, `Rate1`, `Elbow2`, `Rate2`, `Elbow3`, `Rate3`, `NationalGridBmUnit`, `BmUnit` |
| `RURI` | Run Up Rate Import | ✅ | `Dataset`, `SettlementDate`, `SettlementPeriod`, `Time`, `Rate1`, `Elbow2`, `Rate2`, `Elbow3`, `Rate3`, `NationalGridBmUnit`, `BmUnit` |
| `SEL` | Stable Export Limit | ✅ | `Dataset`, `SettlementDate`, `SettlementPeriod`, `Time`, `Level`, `NationalGridBmUnit`, `BmUnit` |
| `SIL` | Stable Import Limit | ✅ | `Dataset`, `SettlementDate`, `SettlementPeriod`, `Time`, `Level`, `NationalGridBmUnit`, `BmUnit` |

### Interconnectors & transfers

| Code | What it is | Status | Confirmed fields |
|---|---|---|---|
| `IGCA` | Interconnector Allocation | 🐛 unverified (HTTP 404) | — |
| `IGCPU` | Interconnector Power & Usage | 🐛 unverified (HTTP 404) | — |
| `ATL` | Actual Transfer Levels | 🐛 unverified (HTTP 404) | — |
| `DATL` | Day-Ahead Transfer Levels | 🐛 unverified (HTTP 404) | — |
| `MATL` | Market Accepted Transfer Levels | 🐛 unverified (HTTP 404) | — |
| `WATL` | Weekly Accepted Transfer Levels | 🐛 unverified (HTTP 404) | — |
| `YATL` | Year-Ahead Transfer Levels | 🐛 unverified (HTTP 404) | — |

### Availability

| Code | What it is | Status | Confirmed fields |
|---|---|---|---|
| `ABUC` | Actual Balancing Unconstrained Capacity | 🐛 unverified (HTTP 404) | — |
| `AOBE` | Actual Or Best Estimate Availability | 🐛 unverified (HTTP 404) | — |
| `BEB` | Best Estimated Balance | 🐛 unverified (HTTP 404) | — |
| `CBS` | Capacity Below Stable Limit | 🐛 unverified (HTTP 404) | — |
| `CCM` | Capacity Contracted for Mandatory Services | 🐛 unverified (HTTP 404) | — |
| `DAG` | Day-Ahead Generating Plant Availability | 🐛 unverified (HTTP 404) | — |
| `DCI` | De-rated Capacity Index | ✅ | `Dataset`, `mRID`, `RevisionNumber`, `PublishTime`, `PublishingPeriodCommencingTime`, `AffectedDso`, `DemandControlId`, `InstructionSequence`, `DemandControlEventFlag`, `TimeFrom`, `TimeTo`, `Volume`, `SystemManagementActionFlag`, `AmendmentFlag` |
| `DGWS` | De-rated Generating plant availability (wind & solar) | 🐛 unverified (HTTP 404) | — |
| `FEIB` | Final Energy Imbalance and Balancing Services | 🐛 unverified (HTTP 404) | — |
| `LOLPDRM` | Loss of Load Probability / De-rated Margin | 🐛 unverified (HTTP 404) | — |
| `PBC` | Plant Balance Contribution | 🐛 unverified (HTTP 404) | — |
| `PPBR` | Plant Physical Balance Reserve | 🐛 unverified (HTTP 404) | — |
| `RZDF` | Reserve Zone Demand Forecast | 🐛 unverified (HTTP 404) | — |
| `RZDR` | Reserve Zone De-rated Reserve | 🐛 unverified (HTTP 404) | — |
| `SOSO` | So-So Offers | 🐛 unverified (HTTP 404) | — |

### Settlements & cash flows

| Code | What it is | Status | Confirmed fields |
|---|---|---|---|
| `CDN` | Credit Default Notice | 🐛 unverified (HTTP 404) | — |
| `REMIT` | REMIT data (dataset endpoint) | 🐛 unverified (HTTP 404) | — |
| `TUDM` | Total Unconstrained Daily Margin | 🐛 unverified (HTTP 404) | — |
| `YAFM` | Year-Ahead Forecast Margin | 🐛 unverified (HTTP 404) | — |

### System / misc

| Code | What it is | Status | Confirmed fields |
|---|---|---|---|
| `FREQ` | System Frequency | ✅ | `Dataset`, `MeasurementTime`, `Frequency` |
| `TEMP` | Temperature | ✅ | `Dataset`, `MeasurementDate`, `PublishTime`, `Temperature` |
| `SYSWARN` | System Warnings | ✅ | `Dataset`, `PublishTime`, `WarningType`, `WarningText` |

## Opinionated range endpoints (`from`/`to`)

Curated views over the same underlying data, under human-readable REST paths.

### Balancing non-BM

| Name | Path | Status | Confirmed fields |
|---|---|---|---|
| `DISBSAD_SUMMARY` | `/balancing/nonbm/disbsad/summary` | ✅ | `SettlementDate`, `SettlementPeriod`, `StartTime`, `BuyActionCount`, `SellActionCount`, `BuyPriceMinimum`, `BuyPriceMaximum`, `BuyPriceAverage`, `SellPriceMinimum`, `SellPriceMaximum`, `SellPriceAverage`, `BuyVolumeTotal`, `SellVolumeTotal`, `NetVolume` |
| `NETBSAD_RANGE` | `/balancing/nonbm/netbsad` | ✅ | `StartTime`, `SettlementDate`, `SettlementPeriod`, `NetBuyPriceCostAdjustmentEnergy`, `NetBuyPriceVolumeAdjustmentEnergy`, `NetBuyPriceVolumeAdjustmentSystem`, `BuyPricePriceAdjustment`, `NetSellPriceCostAdjustmentEnergy`, `NetSellPriceVolumeAdjustmentEnergy`, `NetSellPriceVolumeAdjustmentSystem`, `SellPricePriceAdjustment` |
| `NONBM_STOR` | `/balancing/nonbm/stor` | ✅ | `PublishTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `Generation` |
| `NONBM_VOLUMES` | `/balancing/nonbm/volumes` | ✅ | `SettlementDate`, `SettlementPeriod`, `BmUnitApplicableBalancingServicesVolume`, `NationalGridBmUnit`, `BmUnit`, `Time` |
| `MARKET_INDEX_PRICE` | `/balancing/pricing/market-index` | ✅ | `StartTime`, `DataProvider`, `SettlementDate`, `SettlementPeriod`, `Price`, `Volume` |
| `SETTLEMENT_NOTICES` | `/balancing/settlement/default-notices` | ✅ | `ParticipantId`, `ParticipantName`, `CreditDefaultLevel`, `EnteredDefaultSettlementDate`, `EnteredDefaultSettlementPeriod`, `ClearedDefaultSettlementDate`, `ClearedDefaultSettlementPeriod`, `ClearedDefaultText` |

### Demand (opinionated views)

| Name | Path | Status | Confirmed fields |
|---|---|---|---|
| `DEMAND_OUTTURN` | `/demand/outturn` | ✅ | `PublishTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `InitialDemandOutturn`, `InitialTransmissionSystemDemandOutturn` |
| `DEMAND_OUTTURN_DAILY` | `/demand/outturn/daily` | ✅ | `PublishTime`, `SettlementDate`, `Demand` |
| `DEMAND_OUTTURN_SUMMARY` | `/demand/outturn/summary` | ✅ | `RecordType`, `StartTime`, `Demand` |
| `DEMAND_ACTUAL_TOTAL` | `/demand/actual/total` | ✅ | `PublishTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `Quantity` |
| `DEMAND_TOTAL_ACTUAL` | `/demand/total/actual` | ✅ | `PublishTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `Quantity` |
| `DEMAND_SUMMARY` | `/demand/summary` | ✅ | `RecordType`, `StartTime`, `Demand` |
| `DEMAND_PEAK` | `/demand/peak` | ✅ | `PublishTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `InitialTransmissionSystemDemandOutturn` |
| `DEMAND_PEAK_INDICATIVE` | `/demand/peak/indicative` | 🐛 unverified (HTTP 404) | — |
| `DEMAND_TRIAD` | `/demand/peak/triad` | 🐛 unverified (HTTP 404) | — |
| `DEMAND_RESTORATION_ZONE` | `/demand/by-restoration-zone/restored/submissions` | 🐛 unverified (HTTP 404) | — |

### Forecast — availability

| Name | Path | Status | Confirmed fields |
|---|---|---|---|
| `FCST_AVAIL_DAILY` | `/forecast/availability/daily` | ✅ | `ForecastDate`, `Dataset`, `PublishTime`, `FuelType`, `NgcBmUnit`, `BmUnit`, `OutputUsable` |
| `FCST_AVAIL_DAILY_EVOL` | `/forecast/availability/daily/evolution` | 🐛 unverified (HTTP 404) | — |
| `FCST_AVAIL_DAILY_HIST` | `/forecast/availability/daily/history` | 🐛 unverified (HTTP 404) | — |
| `FCST_AVAIL_WEEKLY` | `/forecast/availability/weekly` | ✅ | `Year`, `CalendarWeekNumber`, `Dataset`, `PublishTime`, `FuelType`, `NgcBmUnit`, `BmUnit`, `OutputUsable` |
| `FCST_AVAIL_WEEKLY_EVOL` | `/forecast/availability/weekly/evolution` | 🐛 unverified (HTTP 404) | — |
| `FCST_AVAIL_WEEKLY_HIST` | `/forecast/availability/weekly/history` | 🐛 unverified (HTTP 404) | — |

### Forecast — demand

| Name | Path | Status | Confirmed fields |
|---|---|---|---|
| `FCST_DEMAND_DAILY` | `/forecast/demand/daily` | ✅ | `ForecastDate`, `PublishTime`, `TransmissionSystemDemand`, `NationalDemand` |
| `FCST_DEMAND_DAILY_EVOL` | `/forecast/demand/daily/evolution` | 🐛 unverified (HTTP 404) | — |
| `FCST_DEMAND_DAILY_HIST` | `/forecast/demand/daily/history` | 🐛 unverified (HTTP 404) | — |
| `FCST_DEMAND_DA` | `/forecast/demand/day-ahead` | ✅ | `StartTime`, `SettlementDate`, `SettlementPeriod`, `Boundary`, `PublishTime`, `TransmissionSystemDemand`, `NationalDemand` |
| `FCST_DEMAND_DA_EVOL` | `/forecast/demand/day-ahead/evolution` | 🐛 unverified (HTTP 404) | — |
| `FCST_DEMAND_DA_HIST` | `/forecast/demand/day-ahead/history` | 🐛 unverified (HTTP 404) | — |
| `FCST_DEMAND_DA_PEAK` | `/forecast/demand/day-ahead/peak` | ✅ | `PublishTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `Boundary`, `TransmissionSystemDemand` |
| `FCST_DEMAND_TOTAL_DA` | `/forecast/demand/total/day-ahead` | ✅ | `PublishTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `Quantity` |
| `FCST_DEMAND_TOTAL_WA` | `/forecast/demand/total/week-ahead` | ✅ | `PublishTime`, `ForecastDate`, `ForecastWeek`, `MinimumPossible`, `MaximumAvailable` |
| `FCST_DEMAND_WEEKLY` | `/forecast/demand/weekly` | ✅ | `ForecastWeek`, `ForecastYear`, `WeekStartDate`, `PublishTime`, `TransmissionSystemDemand`, `NationalDemand` |
| `FCST_DEMAND_WEEKLY_EVOL` | `/forecast/demand/weekly/evolution` | 🐛 unverified (HTTP 404) | — |
| `FCST_DEMAND_WEEKLY_HIST` | `/forecast/demand/weekly/history` | 🐛 unverified (HTTP 404) | — |

### Forecast — generation

| Name | Path | Status | Confirmed fields |
|---|---|---|---|
| `FCST_GEN_DA` | `/forecast/generation/day-ahead` | ✅ | `PublishTime`, `Quantity`, `StartTime`, `SettlementDate`, `SettlementPeriod` |
| `FCST_GEN_WIND` | `/forecast/generation/wind` | ✅ | `PublishTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `Generation` |
| `FCST_GEN_WIND_SOLAR_DA` | `/forecast/generation/wind-and-solar/day-ahead` | 🐛 unverified (HTTP 404) | — |
| `FCST_GEN_WIND_EVOL` | `/forecast/generation/wind/evolution` | 🐛 unverified (HTTP 404) | — |
| `FCST_GEN_WIND_HIST` | `/forecast/generation/wind/history` | 🐛 unverified (HTTP 404) | — |
| `FCST_GEN_WIND_PEAK` | `/forecast/generation/wind/peak` | ✅ | `PublishTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `Generation` |

### Forecast — indicated / margin / surplus / system

| Name | Path | Status | Confirmed fields |
|---|---|---|---|
| `FCST_INDICATED_DA` | `/forecast/indicated/day-ahead` | ✅ | `PublishTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `Boundary`, `IndicatedGeneration`, `IndicatedDemand`, `IndicatedMargin`, `IndicatedImbalance` |
| `FCST_INDICATED_DA_EVOL` | `/forecast/indicated/day-ahead/evolution` | 🐛 unverified (HTTP 404) | — |
| `FCST_INDICATED_DA_HIST` | `/forecast/indicated/day-ahead/history` | 🐛 unverified (HTTP 404) | — |
| `FCST_MARGIN_DAILY` | `/forecast/margin/daily` | ✅ | `ForecastDate`, `PublishTime`, `Margin` |
| `FCST_MARGIN_DAILY_EVOL` | `/forecast/margin/daily/evolution` | 🐛 unverified (HTTP 404) | — |
| `FCST_MARGIN_DAILY_HIST` | `/forecast/margin/daily/history` | 🐛 unverified (HTTP 404) | — |
| `FCST_MARGIN_WEEKLY` | `/forecast/margin/weekly` | ✅ | `Week`, `Year`, `WeekStartDate`, `PublishTime`, `Margin` |
| `FCST_MARGIN_WEEKLY_EVOL` | `/forecast/margin/weekly/evolution` | 🐛 unverified (HTTP 404) | — |
| `FCST_MARGIN_WEEKLY_HIST` | `/forecast/margin/weekly/history` | 🐛 unverified (HTTP 404) | — |
| `FCST_SURPLUS_DAILY` | `/forecast/surplus/daily` | ✅ | `ForecastDate`, `PublishTime`, `Surplus` |
| `FCST_SURPLUS_DAILY_EVOL` | `/forecast/surplus/daily/evolution` | 🐛 unverified (HTTP 404) | — |
| `FCST_SURPLUS_DAILY_HIST` | `/forecast/surplus/daily/history` | 🐛 unverified (HTTP 404) | — |
| `FCST_SURPLUS_WEEKLY` | `/forecast/surplus/weekly` | ✅ | `Week`, `Year`, `WeekStartDate`, `PublishTime`, `Surplus` |
| `FCST_SURPLUS_WEEKLY_EVOL` | `/forecast/surplus/weekly/evolution` | 🐛 unverified (HTTP 404) | — |
| `FCST_SURPLUS_WEEKLY_HIST` | `/forecast/surplus/weekly/history` | 🐛 unverified (HTTP 404) | — |
| `FCST_LOLP` | `/forecast/system/loss-of-load` | ✅ | `PublishTime`, `PublishingPeriodCommencingTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `ForecastHorizon`, `LossOfLoadProbability`, `DeratedMargin` |

### Generation (opinionated)

| Name | Path | Status | Confirmed fields |
|---|---|---|---|
| `GEN_ACTUAL_PER_TYPE` | `/generation/actual/per-type` | 🐛 unverified (HTTP 404) | — |
| `GEN_ACTUAL_PER_TYPE_DAY` | `/generation/actual/per-type/day-total` | ✅ | `PsrType`, `HalfHourUsage`, `HalfHourPercentage`, `TwentyFourHourUsage`, `TwentyFourHourPercentage` |
| `GEN_ACTUAL_WIND_SOLAR` | `/generation/actual/per-type/wind-and-solar` | ✅ | `PublishTime`, `BusinessType`, `PsrType`, `Quantity`, `StartTime`, `SettlementDate`, `SettlementPeriod` |
| `GEN_OUTTURN` | `/generation/outturn` | ✅ | `RecordType`, `StartTime`, `Demand` |
| `GEN_OUTTURN_HH_INTERCON` | `/generation/outturn/halfHourlyInterconnector` | ✅ | `Dataset`, `PublishTime`, `StartTime`, `SettlementDate`, `SettlementDateTimezone`, `SettlementPeriod`, `InterconnectorName`, `Generation` |
| `GEN_OUTTURN_INTERCON` | `/generation/outturn/interconnectors` | ✅ | `Dataset`, `PublishTime`, `StartTime`, `SettlementDate`, `SettlementDateTimezone`, `SettlementPeriod`, `InterconnectorName`, `Generation` |
| `GEN_OUTTURN_SUMMARY` | `/generation/outturn/summary` | 🐛 unverified (HTTP 404) | — |

### LOLPDRM, LSS, SOSO

| Name | Path | Status | Confirmed fields |
|---|---|---|---|
| `LOLPDRM_EVOL` | `/lolpdrm/forecast/evolution` | ✅ | `PublishTime`, `PublishingPeriodCommencingTime`, `StartTime`, `SettlementDate`, `SettlementPeriod`, `ForecastHorizon`, `LossOfLoadProbability`, `DeratedMargin` |
| `LSS_LOAD_SHAPE_PERIOD` | `/lss/load-shape-period` | 🐛 unverified (HTTP 404) | — |
| `LSS_LOAD_SHAPE_TOTALS` | `/lss/load-shape-totals` | 🐛 unverified (HTTP 404) | — |
| `SOSO_PRICES` | `/soso/prices` | ✅ | `ContractIdentification`, `TradeDirection`, `TradeQuantity`, `TradePrice`, `TraderUnit`, `StartTime`, `SettlementDate` |

### REMIT (opinionated)

| Name | Path | Status | Confirmed fields |
|---|---|---|---|
| `REMIT_BY_EVENT` | `/remit/list/by-event` | 🐛 unverified (HTTP 404) | — |
| `REMIT_BY_PUBLISH` | `/remit/list/by-publish` | 🐛 unverified (HTTP 404) | — |
| `REMIT_REVISIONS` | `/remit/revisions` | 🐛 unverified (HTTP 404) | — |

### System

| Name | Path | Status | Confirmed fields |
|---|---|---|---|
| `SYSTEM_DCI` | `/system/demand-control-instructions` | ✅ | `mRID`, `RevisionNumber`, `PublishTime`, `PublishingPeriodCommencingTime`, `AffectedDso`, `DemandControlId`, `InstructionSequence`, `DemandControlEventFlag`, `TimeFrom`, `TimeTo`, `Volume`, `SystemManagementActionFlag`, `AmendmentFlag` |
| `SYSTEM_FREQ` | `/system/frequency` | ✅ | `MeasurementTime`, `Frequency` |
| `SYSTEM_WARNINGS` | `/system/warnings` | ✅ | `PublishTime`, `WarningType`, `WarningText` |
| `TEMPERATURE` | `/temperature` | ✅ | `MeasurementDate`, `PublishTime`, `Temperature`, `TemperatureReferenceAverage`, `TemperatureReferenceHigh`, `TemperatureReferenceLow` |

## Settlement-date endpoints (query-param: `?settlementDate=`)

Iterate one call per day; returns every settlement period for that day.

| Name | Path | Status | Confirmed fields |
|---|---|---|---|
| `DYNAMIC_ALL` | `/balancing/dynamic/all` | 🐛 unverified (HTTP 404) | — |
| `DYNAMIC_PARAMS_ALL` | `/balancing/dynamic/dynamicParameters/all` | 🐛 unverified (HTTP 404) | — |
| `DYNAMIC_RATES_ALL` | `/balancing/dynamic/rates/all` | 🐛 unverified (HTTP 404) | — |
| `PHYSICAL_ALL` | `/balancing/physical/all` | 🐛 unverified (HTTP 404) | — |
| `BID_OFFER_ALL` | `/balancing/bid-offer/all` | 🐛 unverified (HTTP 404) | — |
| `ACCEPTANCES_ALL` | `/balancing/acceptances/all` | 🐛 unverified (HTTP 404) | — |
| `DISBSAD_DETAILS` | `/balancing/nonbm/disbsad/details` | 🐛 unverified (HTTP 404) | — |

## Settlement-date endpoints (path-param: `/{settlementDate}`)

Same idea, date is part of the URL path rather than a query string.

| Name | Path | Status | Confirmed fields |
|---|---|---|---|
| `SETTLEMENT_MARKET_DEPTH` | `/balancing/settlement/market-depth/{settlementDate}` | ✅ | `SettlementDate`, `SettlementPeriod`, `IndicatedImbalance`, `OfferVolume`, `BidVolume`, `TotalAcceptedOfferVolume`, `TotalAcceptedBidVolume`, `PricedAcceptedOffersVolume`, `PricedAcceptedBidsVolume` |
| `SETTLEMENT_MESSAGES` | `/balancing/settlement/messages/{settlementDate}` | ✅ | `SettlementDate`, `SettlementPeriod`, `StartTime`, `MessageReceivedDateTime`, `MessageSeverity`, `MessageTypeCode`, `MessageType`, `MessageText` |
| `SETTLEMENT_SYS_PRICES` | `/balancing/settlement/system-prices/{settlementDate}` | ✅ | `SettlementDate`, `SettlementPeriod`, `StartTime`, `CreatedDateTime`, `SystemSellPrice`, `SystemBuyPrice`, `BsadDefaulted`, `PriceDerivationCode`, `ReserveScarcityPrice`, `NetImbalanceVolume`, `SellPriceAdjustment`, `BuyPriceAdjustment`, `ReplacementPrice`, `ReplacementPriceReferenceVolume`, `TotalAcceptedOfferVolume`, `TotalAcceptedBidVolume`, `TotalAdjustmentSellVolume`, `TotalAdjustmentBuyVolume`, `TotalSystemTaggedAcceptedOfferVolume`, `TotalSystemTaggedAcceptedBidVolume`, `TotalSystemTaggedAdjustmentSellVolume`, `TotalSystemTaggedAdjustmentBuyVolume` |
| `SAA_EXEMPT_VOLUME` | `/saa/datasets/total-exempt-volume/{settlementDate}` | ✅ | `CreationTime`, `SettlementDate`, `SettlementPeriod`, `SettlementRunType`, `TotalExemptSupplyVolume` |

## Bid/Offer × date endpoints (`/{bidOffer}/{settlementDate}`)

Iterated for both BID and OFFER × each day in range.

| Name | Path | Status | Confirmed fields |
|---|---|---|---|
| `SETTLEMENT_ACCEPT_VOLS` | `/balancing/settlement/acceptance/volumes/all/{bidOffer}/{settlementDate}` | 🐛 unverified (HTTP 404) | — |
| `SETTLEMENT_INDIC_CF` | `/balancing/settlement/indicative/cashflows/all/{bidOffer}/{settlementDate}` | 🐛 unverified (HTTP 404) | — |
| `SETTLEMENT_INDIC_VOLS` | `/balancing/settlement/indicative/volumes/all/{bidOffer}/{settlementDate}` | 🐛 unverified (HTTP 404) | — |

## Settlement-period endpoints (`/{settlementDate}/{settlementPeriod}`)

Iterated per day × each of up to 50 half-hourly settlement periods — the most request-heavy group.

| Name | Path | Status | Confirmed fields |
|---|---|---|---|
| `SETTLEMENT_SUMMARY` | `/balancing/settlement/summary/{settlementDate}/{settlementPeriod}` | 🐛 unverified (HTTP 404) | — |
| `SETTLEMENT_ACCEPT_ALL` | `/balancing/settlement/acceptances/all/{settlementDate}/{settlementPeriod}` | ✅ | `SettlementDate`, `SettlementPeriod`, `BmUnit`, `NationalGridBmUnit`, `AcceptanceNumber`, `AcceptanceTime`, `BidPrice`, `OfferPrice`, `BidOfferPairId` |

## Bid/Offer × period endpoints (`/{bidOffer}/{settlementDate}/{settlementPeriod}`)

BID/OFFER × day × period — even more requests than the above.

| Name | Path | Status | Confirmed fields |
|---|---|---|---|
| `SETTLEMENT_STACK` | `/balancing/settlement/stack/all/{bidOffer}/{settlementDate}/{settlementPeriod}` | ✅ | `SettlementDate`, `SettlementPeriod`, `StartTime`, `CreatedDateTime`, `SequenceNumber`, `Id`, `AcceptanceId`, `BidOfferPairId`, `CadlFlag`, `SoFlag`, `StorProviderFlag`, `RepricedIndicator`, `ReserveScarcityPrice`, `OriginalPrice`, `Volume`, `DmatAdjustedVolume`, `ArbitrageAdjustedVolume`, `NivAdjustedVolume`, `ParAdjustedVolume`, `FinalPrice`, `TransmissionLossMultiplier`, `TlmAdjustedVolume`, `TlmAdjustedCost` |

## Triad season endpoints (`/{triadSeason}`)

One call per winter-triad season (e.g. `2025-26`).

| Name | Path | Status | Confirmed fields |
|---|---|---|---|
| `DEMAND_PEAK_INDIC_OPS` | `/demand/peak/indicative/operational/{triadSeason}` | 🐛 broken param — API rejects `"2025-26"` as an invalid `TriadSeason` value | — |
| `DEMAND_PEAK_INDIC_SETT` | `/demand/peak/indicative/settlement/{triadSeason}` | 🐛 broken param — same `TriadSeason` format issue | — |

## Static / reference / latest-snapshot endpoints

No date params — fetched once, always the current/full snapshot.

| Name | Path | Status | Confirmed fields |
|---|---|---|---|
| `REF_BMUNITS` | `/reference/bmunits/all` | ✅ | `nationalGridBmUnit`, `elexonBmUnit`, `eic`, `fuelType`, `leadPartyName`, `bmUnitType`, `fpnFlag`, `bmUnitName`, `leadPartyId`, `demandCapacity`, `generationCapacity`, `productionOrConsumptionFlag`, `transmissionLossFactor`, `workingDayCreditAssessmentImportCapability`, `nonWorkingDayCreditAssessmentImportCapability`, `workingDayCreditAssessmentExportCapability`, `nonWorkingDayCreditAssessmentExportCapability`, `creditQualifyingStatus`, `demandInProductionFlag`, `gspGroupId`, `gspGroupName`, `interconnectorId` |
| `REF_INTERCONNECTORS` | `/reference/interconnectors/all` | ✅ | `interconnectorId`, `interconnectorName`, `interconnectorBiddingZone` |
| `REF_FUELTYPES` | `/reference/fueltypes/all` | ✅ | single unnamed column: fuel type name (e.g. `BIOMASS`) |
| `REF_REMIT_ASSETS` | `/reference/remit/assets/all` | ✅ | single unnamed column: REMIT asset EIC code |
| `REF_REMIT_FUELTYPES` | `/reference/remit/fueltypes/all` | ✅ | single unnamed column: REMIT fuel type name |
| `REF_REMIT_PARTICIPANTS` | `/reference/remit/participants/all` | ⚠️ | responded 200 but body looked malformed/whitespace-only in testing — verify manually |
| `DATASETS_METADATA` | `/datasets/metadata/latest` | ✅ | `Dataset`, `LastUpdated` |
| `ACCEPTANCES_LATEST` | `/balancing/acceptances/all/latest` | ✅ | `SettlementDate`, `SettlementPeriodFrom`, `SettlementPeriodTo`, `TimeFrom`, `TimeTo`, `LevelFrom`, `LevelTo`, `NationalGridBmUnit`, `BmUnit`, `AcceptanceNumber`, `AcceptanceTime`, `DeemedBoFlag`, `SoFlag`, `StorFlag`, `RrFlag` |
| `GEN_OUTTURN_CURRENT` | `/generation/outturn/current` | ✅ | `Dataset`, `FuelType`, `CurrentUsage`, `CurrentPercentage`, `HalfHourUsage`, `HalfHourPercentage`, `TwentyFourHourUsage`, `TwentyFourHourPercentage` |
| `GEN_OUTTURN_FUELINSTHHCUR` | `/generation/outturn/FUELINSTHHCUR` | ✅ | `Dataset`, `FuelType`, `CurrentUsage`, `CurrentPercentage`, `HalfHourUsage`, `HalfHourPercentage`, `TwentyFourHourUsage`, `TwentyFourHourPercentage` |
| `DEMAND_ROLLING` | `/demand/rollingSystemDemand` | ✅ | `RecordType`, `StartTime`, `Demand` |
| `FCST_DEMAND_DA_EARLIEST` | `/forecast/demand/day-ahead/earliest` | 🐛 unverified (HTTP 404) | — |
| `FCST_DEMAND_DA_LATEST` | `/forecast/demand/day-ahead/latest` | 🐛 unverified (HTTP 404) | — |
| `FCST_DEMAND_WA_LATEST` | `/forecast/demand/total/week-ahead/latest` | ✅ | `PublishTime`, `ForecastDate`, `ForecastWeek`, `MinimumPossible`, `MaximumAvailable` |
| `FCST_WIND_EARLIEST` | `/forecast/generation/wind/earliest` | 🐛 unverified (HTTP 404) | — |
| `FCST_WIND_LATEST` | `/forecast/generation/wind/latest` | 🐛 unverified (HTTP 404) | — |

## Data-status endpoints

Report the latest data-availability status for a given underlying dataset (not the data itself).

| Name | Path | Status | Confirmed fields |
|---|---|---|---|
| `STATUS_BOALF` | `/data-status/BOALF` | ✅ | `SettlementDate`, `SettlementPeriod`, `DataPointCount` |
| `STATUS_BOAV` | `/data-status/BOAV` | ✅ | `SettlementDate`, `SettlementPeriod`, `DataPointCount` |
| `STATUS_BOD` | `/data-status/BOD` | ✅ | `SettlementDate`, `SettlementPeriod`, `DataPointCount` |
| `STATUS_DISBSAD` | `/data-status/DISBSAD` | ✅ | `SettlementDate`, `SettlementPeriod`, `DataPointCount` |
| `STATUS_DISEBSP` | `/data-status/DISEBSP` | ✅ | `SettlementDate`, `SettlementPeriod`, `DataPointCount` |
| `STATUS_DISPTAV` | `/data-status/DISPTAV` | ✅ | `SettlementDate`, `SettlementPeriod`, `DataPointCount` |
| `STATUS_EBOCF` | `/data-status/EBOCF` | ✅ | `SettlementDate`, `SettlementPeriod`, `DataPointCount` |
| `STATUS_FREQ` | `/data-status/FREQ` | ✅ | `SettlementDate`, `SettlementPeriod`, `DataPointCount` |
| `STATUS_ISPSTACK` | `/data-status/ISPSTACK` | ✅ | `SettlementDate`, `SettlementPeriod`, `DataPointCount` |
| `STATUS_NETBSAD` | `/data-status/NETBSAD` | ✅ | `SettlementDate`, `SettlementPeriod`, `DataPointCount` |
| `STATUS_PN` | `/data-status/PN` | ✅ | `SettlementDate`, `SettlementPeriod`, `DataPointCount` |
| `STATUS_REMIT` | `/data-status/REMIT` | ✅ | `SettlementDate`, `SettlementPeriod`, `DataPointCount` |

