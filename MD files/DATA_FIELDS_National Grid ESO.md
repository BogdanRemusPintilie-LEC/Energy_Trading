# National Grid ESO (NESO) Data Portal — Data Field Reference

Field reference for `neso_collector.py`, which harvests the entire NESO Data Portal
(a CKAN instance at `api.neso.energy`) — **129 datasets, 1,323 resources, 16 categories,
~577 million rows** across datastore (queryable CSV) resources, plus 140 raw file
downloads (PDF/XLSX/PNG/etc.).

## How this API is different from GIE/BMRS/ENTSO-E

The other three collectors in this folder each hit ONE api with a consistent field
dictionary — every dataset shares roughly the same shape. NESO is structurally different:
it's a **meta-catalog** — 129 independently-published tables, each defined by whichever
NESO team owns that dataset, with no shared schema across them (or even always across
years within the same dataset — see e.g. Aggregated BSAD below, whose columns and types
literally changed between 2020-21 and 2021-22). So there's no single field glossary to
write; instead, every dataset's resources are listed with their real field names and
types below, generated directly from a live discovery run of the whole catalog.

## Overview

| | |
|---|---|
| Base URL | `https://api.neso.energy/api/3/action/` (standard CKAN API) |
| Auth | None — fully public, no API key |
| Rate limits (per NESO) | CKAN metadata: 1 request/sec. Datastore queries: 2/min. The collector throttles globally to stay under both. |
| Datastore (queryable) resources | 1,183 — fetched via `datastore_search`, paginated 10,000 rows/page |
| File resources | 140 — raw downloads (PDF/XLSX/PNG/DOCX/ZIP/GeoJSON/etc.), fetched as-is, not queryable |
| Total rows (datastore, per catalog metadata) | ~576.6 million |
| Publication frequency | No single rule — varies per dataset. Many dataset names self-describe their cadence (`1-day-ahead-*`, `7-day-ahead-*`, `weekly-*`, `monthly-*`, `half-hourly` fields) — noted per dataset below where the name makes it obvious. Others (registers, GIS boundaries, FES tables) are static/occasional-update reference data, not time series. |
| Lag | Follows from the above — day-ahead forecast datasets update daily; long-range forecasts (year-ahead, FES) update on whatever cycle NESO republishes them; historical/register data updates only when NESO issues a correction |

## How this was generated

Every field list below comes from `neso_data/_structure_report.json`, produced by
`python neso_collector.py --mode discover` — a fast, low-footprint pass that samples
5 rows + the field schema from every datastore resource (via `datastore_search`) and a
HEAD request for every file resource, without downloading full data. This is real,
live-confirmed schema information, not inferred from names.

Where a dataset has multiple resources with byte-identical field signatures (e.g. 13
years of "Aggregated BSAD 20xx-yy" files), they're grouped under one schema listing
rather than repeated — but every distinct schema variant is still shown, including
year-to-year drift in column names/types within what is nominally "the same" dataset.

## Datasets by category

129 datasets across 16 categories, 1,323 resources total. Each dataset is its own independently-published table (or set of file downloads) — there is no shared schema across datasets the way there is for GIE/BMRS/ENTSO-E, so fields are listed per-resource below rather than in one glossary.

### Categories

- [Ancillary Services](#ancillary-services) — 31 datasets
- [Balancing](#balancing) — 9 datasets
- [Carbon Intensity](#carbon-intensity) — 5 datasets
- [Connection Registers](#connection-registers) — 3 datasets
- [Constraint Management](#constraint-management) — 9 datasets
- [Demand](#demand) — 13 datasets
- [Demand Flexibility Service (DFS)](#demand-flexibility-service-dfs) — 4 datasets
- [Electricity Market Reform](#electricity-market-reform) — 1 datasets
- [Future Energy Scenarios (FES)](#future-energy-scenarios-fes) — 15 datasets
- [Generation](#generation) — 12 datasets
- [Interconnectors](#interconnectors) — 7 datasets
- [Network Charges](#network-charges) — 3 datasets
- [Plans, Reports & Analysis](#plans-reports--analysis) — 1 datasets
- [Strategic Energy Planning](#strategic-energy-planning) — 1 datasets
- [System](#system) — 9 datasets
- [Trade Data](#trade-data) — 6 datasets

## Ancillary Services

### Aggregated BSAD (Balancing Services Adjustment Data)

`neso_data/ancillary-services/aggregated-bsad/` — 13 resource(s)

- **2 resources sharing this schema:** Aggregated BSAD 2013-14, Aggregated BSAD 2014-15 (CSV via API, ~20,562 rows combined)
  Fields: `Date` (timestamp), `Settlement Period` (numeric), `EBCA (£)` (numeric), `EBVA (MWh)` (numeric), `ESCA (£)` (numeric), `ESVA (MWh)` (numeric), `SBVA (MWh)` (numeric), `SSVA (MWh)` (numeric), `BPA (£/MWh)` (numeric), `SPA (£/MWh)` (numeric)

- **4 resources sharing this schema:** Aggregated BSAD 2016-17, Aggregated BSAD 2017-18, Aggregated BSAD 2018-19, Aggregated BSAD 2019-20 (CSV via API, ~70,148 rows combined)
  Fields: `Date` (timestamp), `Settlement Period` (numeric), `EBCA (£)` (numeric), `EBVA (MWh)` (numeric), `SBVA (MWh)` (numeric), `BPA (£/MWh)` (numeric), `ESCA (£)` (numeric), `ESVA (MWh)` (numeric), `SSVA (MWh)` (numeric), `SPA (£/MWh)` (numeric)

- **Aggregated BSAD 2020-21** (CSV via API, ~17,531 rows)
  Fields: `Date` (date), `Settlement Period` (numeric), `EBCA (£)` (numeric), `EBVA (MWh)` (numeric), `SBVA (MWh)` (numeric), `BPA (£/MWh)` (numeric), `ESCA (£)` (numeric), `ESVA (MWh)` (numeric), `SSVA (MWh)` (numeric), `SPA (£/MWh)` (numeric)

- **6 resources sharing this schema:** Aggregated BSAD 2021-22, Aggregated BSAD 2022-23, Aggregated BSAD 2023-24, Aggregated BSAD 2024-25, Aggregated BSAD 2025-26, Aggregated BSAD 2026-27 (CSV via API, ~92,208 rows combined)
  Fields: `Date` (text), `SettlementPeriod` (int4), `EBCA` (float8), `EBVA` (float8), `SBVA` (float8), `BPA` (float8), `ESCA` (float8), `ESVA` (float8), `SSVA` (float8), `SPA` (float8)

### Ancillary Services Important Industry Notifications

`neso_data/ancillary-services/ancillary-services-important-industry-notifications/` — 6 resource(s)

- **4 resources sharing this schema:** Balancing Reserve Important Industry Notifications, DC, DM, DR Important Industry Notifications, SFFR Important Industry Notifications, STOR Important Industry Notifications (CSV via API, ~45 rows combined)
  Fields: `Notification Issued Date Time` (timestamp), `Service` (text), `Description` (text), `Effective From Date Time` (timestamp), `Effective To Date Time` (timestamp), `Notes` (text)

- **2 resources sharing this schema:** Quick Reserve Important Industry Notifications, Slow Reserve Important Industry Notification (CSV via API, ~14 rows combined)
  Fields: `Notification Issued Date Time` (timestamp), `Description` (text), `Effective From Date Time` (timestamp), `Effective To Date Time` (timestamp), `Notes` (text)

### Balancing Reserve Auction Requirement Forecast _(cadence hint from name: forecast series)_

`neso_data/ancillary-services/balancing-reserve-auction-requirement-forecast/` — 4 resource(s)

- **Balancing Reserve Requirements Medium term forecast (Archive)** (CSV via API, ~41,806 rows)
  Fields: `Auction Date` (text), `Service Delivery Date` (text), `Service Window` (text), `Service window start time` (text), `Service Window End Time` (text), `Positive Balancing Reserve Requirement MW` (text), `Negative Balancing Reserve Requirement MW` (text), `Forecast produced on` (text), `Forecast type` (text)

- **3 resources sharing this schema:** Balancing Reserve Day ahead auction requirement forecast (Archive), Balancing Reserve Day ahead auction requirements forecast, Balancing Reserve Requirements Medium term forecast (CSV via API, ~42,526 rows combined)
  Fields: `Auction Date` (date), `Service Delivery Date` (date), `Service Window` (text), `Service window start time` (timestamp), `Service Window End Time` (timestamp), `Positive Balancing Reserve Requirement MW` (int4), `Negative Balancing Reserve Requirement MW` (int4), `Forecast produced on` (date), `Forecast type` (text)

### Balancing Services Adjustment Data Forward Contracts

`neso_data/ancillary-services/balancing-services-adjustment-data-forward-contracts/` — 11 resource(s)

- **4 resources sharing this schema:** BSAD Forward Contracts 2016-17, BSAD Forward Contracts 2017-18, BSAD Forward Contracts 2018-19, BSAD Forward Contracts 2019-20 (CSV via API, ~70,150 rows combined)
  Fields: `Date` (timestamp), `Settlement Period` (numeric), `BCA (£)` (numeric), `BSA (MWh)` (numeric), `BVA (MWh)` (numeric), `SCA (£)` (numeric), `SSA (MWh)` (numeric), `SVA (MWh)` (numeric)

- **BSAD Forward Contracts 2020-21** (CSV via API, ~17,536 rows)
  Fields: `Date` (date), `Settlement Period` (numeric), `BCA (£)` (numeric), `BSA (MWh)` (numeric), `BVA (MWh)` (numeric), `SCA (£)` (numeric), `SSA (MWh)` (numeric), `SVA (MWh)` (numeric)

- **6 resources sharing this schema:** BSAD Forward Contracts 2021-22, BSAD Forward Contracts 2022-23, BSAD Forward Contracts 2023-24, BSAD Forward Contracts 2024-25, BSAD Forward Contracts 2025-26, BSAD Forward Contracts 2026-27 (CSV via API, ~92,208 rows combined)
  Fields: `Date` (text), `SettlementPeriod` (int4), `BCA` (float8), `BSA` (float8), `BVA` (float8), `SCA` (float8), `SSA` (float8), `SVA` (float8)

### Contract Transfer Of Obligation

`neso_data/ancillary-services/contract-transfer-of-obligation/` — 1 resource(s)

- **Contract Transfer of Obligation 2025-2026** (CSV via API, ~62 rows)
  Fields: `registeredAuctionParticipant` (text), `auctionUnit` (text), `serviceType` (text), `auctionProduct` (text), `executedQuantity` (numeric), `clearingPrice` (numeric), `deliveryStart` (timestamp), `deliveryEnd` (timestamp), `Transfer To Unit` (text), `Transfer Status` (text)

### Disaggregated BSAD (Balancing Services Adjustment Data)

`neso_data/ancillary-services/disaggregated-bsad/` — 14 resource(s)

- **4 resources sharing this schema:** Disaggregated BSAD 2013-14, Disaggregated BSAD 2014-15, Disaggregated BSAD 2015-16, Disaggregated BSAD 2017-18 (CSV via API, ~260,574 rows combined)
  Fields: `Date` (timestamp), `Settlement Period` (numeric), `Disaggregated BSAD Volume (MWh)` (numeric), `Disaggregated BSAD Cost (£)` (numeric), `Trade Flag System (T) / Energy (F)` (text)

- **3 resources sharing this schema:** Disaggregated BSAD 2016-17, Disaggregated BSAD 2018-19, Disaggregated BSAD 2019-20 (CSV via API, ~431,375 rows combined)
  Fields: `Date` (date), `Settlement Period` (numeric), `Disaggregated BSAD Volume (MWh)` (numeric), `Disaggregated BSAD Cost (£)` (numeric), `Trade Flag System (T) / Energy (F)` (text)

- **Disaggregated BSAD 2020-21** (CSV via API, ~167,785 rows)
  Fields: `Date` (date), `Settlement Period` (numeric), `Disaggregated BSAD Volume (MWh)` (numeric), `Disaggregated BSAD Cost (£)` (numeric), `Trade Flag` (text)

- **5 resources sharing this schema:** Disaggregated BSAD 2021-22, Disaggregated BSAD 2023-24, Disaggregated BSAD 2024-25, Disaggregated BSAD 2025-26, Disaggregated BSAD 2026-27 (CSV via API, ~605,376 rows combined)
  Fields: `Date` (text), `SettlementPeriod` (int4), `DisaggregatedBSADCost` (float8), `DisaggregatedBSADVolume` (float8), `TradeFlag` (text)

- **Disaggregated BSAD 2022-23** (CSV via API, ~175,863 rows)
  Fields: `Date` (timestamp), `SettlementPeriod` (numeric), `DisaggregatedBSADCost` (numeric), `DisaggregatedBSADVolume` (numeric), `TradeFlag` (text)

### Dynamic Containment 4 Day Forecast _(cadence hint from name: forecast series)_

`neso_data/ancillary-services/dynamic-containment-4-day-forecast/` — 2 resource(s)

- **Dynamic Containment - 4 Day forecast** (CSV via API, ~8 rows)
  Fields: `Date` (date), `Service_Type` (text), `EFA_1` (int4), `EFA_2` (int4), `EFA_3` (int4), `EFA_4` (int4), `EFA_5` (int4), `EFA_6` (int4)

- **Dynamic Containment 4 Day Forecast - History** (CSV via API, ~12,244 rows)
  Fields: `Forecast_Created` (date), `Forecast_Target_Date` (date), `Service_Type` (text), `EFA_1` (int4), `EFA_2` (int4), `EFA_3` (int4), `EFA_4` (int4), `EFA_5` (int4), `EFA_6` (int4)

### Dynamic Containment Data

`neso_data/ancillary-services/dynamic-containment-data/` — 5 resource(s)

- **Dynamic Containment Masterdata** (CSV via API, ~10,388 rows)
  Fields: `Market Name` (text), `Delivery Date` (date), `Unique bid number` (text), `Response Unit` (text), `Unit type` (text), `Agent/Applicant` (text), `Related Entity` (text), `Volume offered` (numeric), `Volume Accepted` (numeric), `Delivery Start UTC` (timestamp), `Delivery End UTC` (timestamp), `Service Duration` (numeric), `Availability Fee` (numeric), `Total Cost` (numeric), `RTM/no RTM` (text), `Accepted/Rejected` (text), `Rejection code` (numeric), `Technology Type` (text)

- **DC, DR & DM Results Summary Master Data 2021-2023** (CSV via API, ~23,424 rows)
  Fields: `Service` (text), `EFA Date` (date), `Delivery Start` (timestamp), `Delivery End` (timestamp), `EFA` (numeric), `Cleared Volume` (numeric), `Clearing Price` (numeric)

- **DC, DR & DM Results By Unit Master Data 2021-2023** (CSV via API, ~397,662 rows)
  Fields: `Company` (text), `Unit Name` (text), `EFA Date` (date), `Delivery Start` (timestamp), `Delivery End` (timestamp), `EFA` (numeric), `Service` (text), `Cleared Volume` (numeric), `Clearing Price` (numeric), `Technology Type` (text), `Location` (text), `Cancelled` (text)

- **DC, DR & DM Linear Orders Master Data 2021-2023** (CSV via API, ~23,154 rows)
  Fields: `MarketName` (text), `BiddingLevelName` (text), `MemberName` (text), `OrderID` (numeric), `Portfolio` (text), `OrderEntryTime` (timestamp), `OrderEntryUser` (text), `SettlementCurrency` (text), `OrderPeriodID` (numeric), `TradeID` (numeric), `EFA` (numeric), `DeliveryStart` (timestamp), `DeliveryEnd` (timestamp), `ExecutedVolume` (numeric), `1P` (numeric), `1V` (numeric), `2P` (numeric), `2V` (numeric), `3P` (numeric), `3V` (numeric), `4P` (numeric), `4V` (numeric), `5P` (numeric), `5V` (numeric), `6P` (numeric), `6V` (numeric), `7P` (numeric), `7V` (numeric), `8P` (numeric), `8V` (numeric), `9P` (numeric), `9V` (numeric), `10P` (numeric), `10V` (numeric), `11P` (numeric), `11V` (numeric), `12P` (numeric), `12V` (numeric), `13P` (numeric), `13V` (numeric), `14P` (numeric), `14V` (numeric), `15P` (numeric), `15V` (numeric), `16P` (numeric), `16V` (numeric), `17P` (numeric), `17V` (numeric), `18P` (numeric), `18V` (numeric), `19P` (numeric), `19V` (numeric), `20P` (numeric), `20V` (numeric), `21P` (numeric), `21V` (numeric), `22P` (numeric), `22V` (numeric), `23P` (numeric), `23V` (numeric), `24P` (numeric), `24V` (numeric), `25P` (numeric), `25V` (numeric), `26P` (numeric), `26V` (numeric), `27P` (numeric), `27V` (numeric), `28P` (numeric), `28V` (numeric), `29P` (numeric), `29V` (numeric), `30P` (numeric), `30V` (numeric), `31P` (numeric), `31V` (numeric), `32P` (numeric), `32V` (numeric)

- **DC, DR & DM Block Orders Master Data 2021-2023** (CSV via API, ~728,794 rows)
  Fields: `MarketName` (text), `BiddingLevelName` (text), `MemberName` (text), `OrderID` (numeric), `Portfolio` (text), `OrderEntryTime` (timestamp), `OrderEntryUser` (text), `SettlementCurrency` (text), `ClearingPrice` (numeric), `Price` (numeric), `MAR` (numeric), `Status` (text), `BlockCode` (text), `BlockCodePRM` (text), `Paradoxically` (text), `OrderPeriodID` (numeric), `TradeID` (numeric), `EFA` (numeric), `DeliveryStart` (timestamp), `DeliveryEnd` (timestamp), `ExecutedVolume` (numeric), `Volume` (numeric), `Invalid` (text), `Bid Validity` (text)

### Dynamic Moderation Requirements

`neso_data/ancillary-services/dynamic-moderation-requirements/` — 1 resource(s)

- **Indicative DM Requirements** (CSV via API, ~78 rows)
  Fields: `EFA_DATE` (date), `Service` (text), `EFA1` (numeric), `EFA2` (numeric), `EFA3` (numeric), `EFA4` (numeric), `EFA5` (numeric), `EFA6` (numeric)

### Dynamic Regulation Requirements

`neso_data/ancillary-services/dynamic-regulation-requirements/` — 1 resource(s)

- **Indicative DR Requirements** (CSV via API, ~78 rows)
  Fields: `EFA_DATE` (date), `Service` (text), `EFA1` (numeric), `EFA2` (numeric), `EFA3` (numeric), `EFA4` (numeric), `EFA5` (numeric), `EFA6` (numeric)

### EAC (Enduring Auction Capability) Auction Results

`neso_data/ancillary-services/eac-auction-results/` — 48 resource(s)

- **5 resources sharing this schema:** NESO Response-Reserve Daily Results By Unit, NESO Response-Reserve Results By Unit, NESO Response-Reserve Results By Unit FY2023 (Archive), NESO Response-Reserve Results By Unit FY2024 (Archive), NESO Response-Reserve Results By Unit FY2025 (Archive) (CSV via API, ~2,594,614 rows combined)
  Fields: `registeredAuctionParticipant` (text), `auctionUnit` (text), `serviceType` (text), `auctionProduct` (text), `executedQuantity` (numeric), `clearingPrice` (numeric), `deliveryStart` (timestamp), `deliveryEnd` (timestamp), `technologyType` (text), `postCode` (text), `unitResultID` (text)

- **5 resources sharing this schema:** NESO Response-Reserve Buy Orders, NESO Response-Reserve Buy Orders FY2023 (Archive), NESO Response-Reserve Buy Orders FY2024 (Archive), NESO Response-Reserve Buy Orders FY2025 (Archive), NESO Response-Reserve Daily Buy Orders (CSV via API, ~394,543 rows combined)
  Fields: `auctionID` (int4), `orderID` (int4), `serviceType` (text), `auctionProduct` (text), `deliveryStart` (timestamp), `deliveryEnd` (timestamp), `quantity` (numeric), `price` (numeric), `substitutabilityFamily` (int4), `paradoxicallyAcceptanceAllowed` (text), `orderEntryTime` (timestamp), `acceptanceRatio` (numeric), `status` (text), `executedQuantity` (numeric), `clearingPrice` (numeric), `reasonRejected` (text), `joinedFamily` (numeric)

- **16 resources sharing this schema** (e.g. NESO Response-Reserve Daily Sell Orders, NESO Response-Reserve Sell Orders, NESO Response-Reserve Sell Orders 202504 (Archive), …) (CSV via API, ~18,511,004 rows combined)
  Fields: `auctionID` (int4), `registeredAuctionParticipant` (text), `auctionUnit` (text), `basketID` (int4), `serviceType` (text), `deliveryStart` (timestamp), `deliveryEnd` (timestamp), `orderID` (int4), `orderType` (text), `auctionProduct` (text), `productID` (int4), `quantity` (numeric), `priceLimit` (numeric), `loopedBasketID` (int4), `orderEntryTime` (timestamp), `acceptanceRatio` (numeric), `status` (text), `executedQuantity` (numeric), `clearingPrice` (numeric), `reasonRejected` (text), `flexibleGroupID` (int4), `minimumConsecutiveWindows` (int4)

- **5 resources sharing this schema:** NESO Response-Reserve Daily Results Summary, NESO Response-Reserve Results Summary, NESO Response-Reserve Results Summary FY2023 (Archive), NESO Response-Reserve Results Summary FY2024 (Archive), NESO Response-Reserve Results Summary FY2025 (Archive) (CSV via API, ~123,832 rows combined)
  Fields: `auctionID` (int4), `auctionProduct` (text), `serviceType` (text), `deliveryStart` (timestamp), `deliveryEnd` (timestamp), `clearedVolume` (numeric), `clearingPrice` (numeric), `linkedServiceWindowID` (int4)

- **7 resources sharing this schema:** NESO Response-Reserve Sell Orders 202311 (Archive), NESO Response-Reserve Sell Orders 202401 (Archive), NESO Response-Reserve Sell Orders 202404 (Archive), NESO Response-Reserve Sell Orders 202406 (Archive), NESO Response-Reserve Sell Orders 202407 (Archive), NESO Response-Reserve Sell Orders 202408 (Archive), NESO Response-Reserve Sell Orders 202410 (Archive) (CSV via API, ~2,010,303 rows combined)
  Fields: `auctionID` (int4), `registeredAuctionParticipant` (text), `auctionUnit` (text), `basketID` (int4), `serviceType` (text), `deliveryStart` (timestamp), `deliveryEnd` (timestamp), `orderID` (int4), `orderType` (text), `auctionProduct` (text), `productID` (int4), `quantity` (numeric), `priceLimit` (numeric), `loopedBasketID` (int4), `orderEntryTime` (timestamp), `acceptanceRatio` (numeric), `status` (text), `executedQuantity` (numeric), `clearingPrice` (numeric), `reasonRejected` (int4), `flexibleGroupID` (text), `minimumConsecutiveWindows` (text)

- **5 resources sharing this schema:** NESO Response-Reserve Sell Orders 202312 (Archive), NESO Response-Reserve Sell Orders 202402 (Archive), NESO Response-Reserve Sell Orders 202403 (Archive), NESO Response-Reserve Sell Orders 202405 (Archive), NESO Response-Reserve Sell Orders 202409 (Archive) (CSV via API, ~1,362,361 rows combined)
  Fields: `auctionID` (int4), `registeredAuctionParticipant` (text), `auctionUnit` (text), `basketID` (int4), `serviceType` (text), `deliveryStart` (timestamp), `deliveryEnd` (timestamp), `orderID` (int4), `orderType` (text), `auctionProduct` (text), `productID` (int4), `quantity` (numeric), `priceLimit` (numeric), `loopedBasketID` (text), `orderEntryTime` (timestamp), `acceptanceRatio` (numeric), `status` (text), `executedQuantity` (numeric), `clearingPrice` (numeric), `reasonRejected` (int4), `flexibleGroupID` (text), `minimumConsecutiveWindows` (text)

- **4 resources sharing this schema:** NESO Response-Reserve Sell Orders 202411 (Archive), NESO Response-Reserve Sell Orders 202412 (Archive), NESO Response-Reserve Sell Orders 202501 (Archive), NESO Response-Reserve Sell Orders 202502 (Archive) (CSV via API, ~2,622,547 rows combined)
  Fields: `auctionID` (int4), `registeredAuctionParticipant` (text), `auctionUnit` (text), `basketID` (int4), `serviceType` (text), `deliveryStart` (timestamp), `deliveryEnd` (timestamp), `orderID` (int4), `orderType` (text), `auctionProduct` (text), `productID` (int4), `quantity` (numeric), `priceLimit` (numeric), `loopedBasketID` (int4), `orderEntryTime` (timestamp), `acceptanceRatio` (numeric), `status` (text), `executedQuantity` (numeric), `clearingPrice` (numeric), `reasonRejected` (int4)

- **NESO Response-Reserve Sell Orders 202503 (Archive)** (CSV via API, ~781,966 rows)
  Fields: `auctionID` (int4), `registeredAuctionParticipant` (text), `auctionUnit` (text), `basketID` (int4), `serviceType` (text), `deliveryStart` (timestamp), `deliveryEnd` (timestamp), `orderID` (int4), `orderType` (text), `auctionProduct` (text), `productID` (int4), `quantity` (numeric), `priceLimit` (numeric), `loopedBasketID` (text), `orderEntryTime` (timestamp), `acceptanceRatio` (numeric), `status` (text), `executedQuantity` (numeric), `clearingPrice` (numeric), `reasonRejected` (int4)

### EAC (Enduring Auction Capability) Br Auction Results

`neso_data/ancillary-services/eac-br-auction-results/` — 4 resource(s)

- **NESO Balancing-Reserve Results By Unit 2023-2024** (CSV via API, ~621,111 rows)
  Fields: `registeredAuctionParticipant` (text), `auctionUnit` (text), `serviceType` (text), `auctionProduct` (text), `executedQuantity` (numeric), `clearingPrice` (numeric), `deliveryStart` (timestamp), `deliveryEnd` (timestamp), `technologyType` (text), `postCode` (text), `unitResultID` (text)

- **NESO Balancing-Reserve Buy Orders 2023-2024** (CSV via API, ~98,592 rows)
  Fields: `auctionID` (int4), `orderID` (int4), `serviceType` (text), `auctionProduct` (text), `deliveryStart` (timestamp), `deliveryEnd` (timestamp), `quantity` (numeric), `price` (numeric), `joinedFamily` (numeric), `substitutabilityFamily` (int4), `paradoxicallyAcceptanceAllowed` (text), `orderEntryTime` (timestamp), `acceptanceRatio` (numeric), `status` (text), `executedQuantity` (numeric), `clearingPrice` (numeric), `reasonRejected` (text)

- **NESO Balancing-Reserve Sell Orders 2023-2024** (CSV via API, ~3,124,058 rows)
  Fields: `auctionID` (int4), `registeredAuctionParticipant` (text), `auctionUnit` (text), `basketID` (int4), `serviceType` (text), `deliveryStart` (timestamp), `deliveryEnd` (timestamp), `orderID` (int4), `orderType` (text), `auctionProduct` (text), `productID` (int4), `quantity` (numeric), `priceLimit` (numeric), `loopedBasketID` (int4), `orderEntryTime` (timestamp), `acceptanceRatio` (numeric), `status` (text), `executedQuantity` (numeric), `clearingPrice` (numeric), `reasonRejected` (text)

- **NESO Balancing-Reserve Results Summary 2023-2024** (CSV via API, ~57,216 rows)
  Fields: `auctionID` (int4), `auctionProduct` (text), `serviceType` (text), `deliveryStart` (timestamp), `deliveryEnd` (timestamp), `clearedVolume` (numeric), `clearingPrice` (numeric)

### EAC (Enduring Auction Capability) Br Mock Auction Results

`neso_data/ancillary-services/eac-br-mock-auction-results/` — 4 resource(s)

- **NESO Mock Balancing-Reserve Results By Unit 2023-2024** (CSV via API, ~7,074 rows)
  Fields: `registeredAuctionParticipant` (text), `auctionUnit` (text), `serviceType` (text), `auctionProduct` (text), `executedQuantity` (numeric), `clearingPrice` (numeric), `deliveryStart` (timestamp), `deliveryEnd` (timestamp), `technologyType` (text), `postCode` (text), `unitResultID` (text)

- **NESO Mock Balancing-Reserve Buy Orders 2023-2024** (CSV via API, ~3,696 rows)
  Fields: `auctionID` (int4), `orderID` (int4), `serviceType` (text), `auctionProduct` (text), `deliveryStart` (timestamp), `deliveryEnd` (timestamp), `quantity` (numeric), `price` (numeric), `joinedFamily` (numeric), `substitutabilityFamily` (int4), `paradoxicallyAcceptanceAllowed` (text), `orderEntryTime` (timestamp), `acceptanceRatio` (numeric), `status` (text), `executedQuantity` (numeric), `clearingPrice` (numeric), `reasonRejected` (text)

- **NESO Mock Balancing-Reserve Sell Orders 2023-2024** (CSV via API, ~23,263 rows)
  Fields: `auctionID` (int4), `registeredAuctionParticipant` (text), `auctionUnit` (text), `basketID` (int4), `serviceType` (text), `deliveryStart` (timestamp), `deliveryEnd` (timestamp), `orderID` (int4), `orderType` (text), `auctionProduct` (text), `productID` (int4), `quantity` (numeric), `priceLimit` (numeric), `loopedBasketID` (int4), `orderEntryTime` (timestamp), `acceptanceRatio` (numeric), `status` (text), `executedQuantity` (numeric), `clearingPrice` (numeric), `reasonRejected` (text)

- **NESO Mock Balancing-Reserve Results Summary 2023-2024** (CSV via API, ~1,632 rows)
  Fields: `auctionID` (int4), `auctionProduct` (text), `serviceType` (text), `deliveryStart` (timestamp), `deliveryEnd` (timestamp), `clearedVolume` (numeric), `clearingPrice` (numeric)

### EAC (Enduring Auction Capability) Mock Auction Results

`neso_data/ancillary-services/eac-mock-auction-results/` — 8 resource(s)

- **2 resources sharing this schema:** NESO Mock Response-Reserve Daily Results By Unit, NESO Mock Response-Reserve Results By Unit 2025-2026 (CSV via API, ~13,073 rows combined)
  Fields: `registeredAuctionParticipant` (text), `auctionUnit` (text), `serviceType` (text), `auctionProduct` (text), `executedQuantity` (numeric), `clearingPrice` (numeric), `deliveryStart` (timestamp), `deliveryEnd` (timestamp), `technologyType` (text), `postCode` (text), `unitResultID` (text)

- **2 resources sharing this schema:** NESO Mock Response-Reserve Buy Orders 2025-2026, NESO Mock Response-Reserve Daily Buy Orders (CSV via API, ~16,938 rows combined)
  Fields: `auctionID` (int4), `orderID` (int4), `serviceType` (text), `auctionProduct` (text), `deliveryStart` (timestamp), `deliveryEnd` (timestamp), `quantity` (numeric), `price` (numeric), `substitutabilityFamily` (int4), `paradoxicallyAcceptanceAllowed` (text), `orderEntryTime` (timestamp), `acceptanceRatio` (numeric), `status` (text), `executedQuantity` (numeric), `clearingPrice` (numeric), `reasonRejected` (text), `joinedFamily` (numeric)

- **2 resources sharing this schema:** NESO Mock Response-Reserve Daily Sell Orders, NESO Mock Response-Reserve Sell Orders 2025-2026 (CSV via API, ~30,869 rows combined)
  Fields: `auctionID` (int4), `registeredAuctionParticipant` (text), `auctionUnit` (text), `basketID` (int4), `serviceType` (text), `deliveryStart` (timestamp), `deliveryEnd` (timestamp), `orderID` (int4), `orderType` (text), `auctionProduct` (text), `productID` (int4), `quantity` (numeric), `priceLimit` (numeric), `loopedBasketID` (int4), `orderEntryTime` (timestamp), `acceptanceRatio` (numeric), `status` (text), `executedQuantity` (numeric), `clearingPrice` (numeric), `reasonRejected` (text), `flexibleGroupID` (int4), `minimumConsecutiveWindows` (int4)

- **2 resources sharing this schema:** NESO Mock Response-Reserve Daily Results Summary, NESO Mock Response-Reserve Results Summary 2025-2026 (CSV via API, ~7,128 rows combined)
  Fields: `auctionID` (int4), `auctionProduct` (text), `serviceType` (text), `deliveryStart` (timestamp), `deliveryEnd` (timestamp), `clearedVolume` (numeric), `clearingPrice` (numeric), `linkedServiceWindowID` (int4)

### Firm Frequency Response Post Tender Reports

`neso_data/ancillary-services/firm-frequency-response-post-tender-reports/` — 89 resource(s)

- **Post Tender Report TR139 July 2021 CSV- EXT ** (CSV via API, ~97 rows)
  Fields: `Tender Ref` (numeric), `Status` (text), `Rejection Codes` (text), `Company Name` (text), `Tendered Unit 
(BMU/Unit ID)` (text), `TO connection  /  DNO connection` (text), `Generation Type` (text), `Start Date` (timestamp), `End Date` (timestamp), `Tendered Period 
(dd.mm.yy - dd.mm.yy)` (text), `Applicable FFR Capability Data Table` (text), `Tendered Frames per Service Day - From (Mon-Fri)` (numeric), `Tendered Frames per Service Day - To (Mon- Fri)` (numeric), `Tendered Frames per Service Day - Duration (Mon-Fri)` (numeric), `Tendered Frames per Service Day - From (Saturday)` (numeric), `Tendered Frames per Service Day - To (Saturday)` (numeric), `Tendered Frames per Service Day - Duration (Saturday)` (numeric), `Tendered Frames per Service Day - From (Sunday/Bank Holidays)` (numeric), `Tendered Frames per Service Day - To (Sunday/Bank Holidays)` (numeric), `Tendered Frames per Service Day - Duration (Sunday/Bank Hol)` (numeric), `Tendered Prices - Availability Fee (£/h)` (numeric), `Tendered Prices - Nomination Fee (£/h)` (numeric), `Tendered Prices -  Window Initiation Fee (£/window)` (text), `BMUs  Only` (text), `Maximum Part Load Point (MW)` (text), `Minimum Part Load Point (MW)` (text), `Minimum MEL (MW)` (text), `Maximum SEL (MW)` (text), `Primary Response (max.) @ 0.2Hz (MW)` (numeric), `Primary Response (max.) @ 0.5Hz (MW)` (numeric), `Primary Response (max.) @ 0.8Hz (MW)` (numeric), `Secondary Response (max.) @ 0.2/0.2Hz (MW)` (numeric), `Secondary Response (max.) @ 0.5/0.5Hz (MW)` (numeric), `High Frequency Response (max.) @ 0.2Hz (MW)` (numeric), `High Frequency Response (max.) @ 0.5Hz (MW)` (numeric), `Are you adding volume as per detail change provision` (text), `Please state the accepted tender that you are stacking onto` (text), `Please state if this is an all or nothing bid.` (text), `Please indicate if this is a mutually exclusive tender` (text), `Automatic Response Energy Deliverable by 10s (MW)` (text), `Automatic Response Energy Deliverable by 30s (MW)` (text), `Comments` (text)

- **8 resources sharing this schema:** Post Tender Report TR140 August 2021 CSV- EXT , Post Tender Report TR142 October 2021 EXT , Post Tender Report TR143 November 2021 EXT , Post Tender Report TR148 April 2022 CSV EXT , Post Tender Report TR149 May 2022 CSV EXT , Post Tender Report TR149 May 2022 EXT , Post Tender Report TR150  June 2022CSV  EXT , Post Tender Report TR151 July 2022 CSV EXT  (CSV via API, ~1,412 rows combined)
  Fields: `Tender Ref` (numeric), `Status` (text), `Rejection Codes` (text), `Company Name` (text), `Tendered Unit 
(BMU/Unit ID)` (text), `TO connection  /  DNO connection` (text), `Generation Type` (text), `Start Date` (timestamp), `End Date` (timestamp), `Tendered Period 
(dd.mm.yy - dd.mm.yy)` (text), `Applicable FFR Capability Data Table` (text), `Tendered Frames per Service Day - From (Mon-Fri)` (numeric), `Tendered Frames per Service Day - To (Mon- Fri)` (numeric), `Tendered Frames per Service Day - Duration (Mon-Fri)` (numeric), `Tendered Frames per Service Day - From (Saturday)` (numeric), `Tendered Frames per Service Day - To (Saturday)` (numeric), `Tendered Frames per Service Day - Duration (Saturday)` (numeric), `Tendered Frames per Service Day - From (Sunday/Bank Holidays)` (numeric), `Tendered Frames per Service Day - To (Sunday/Bank Holidays)` (numeric), `Tendered Frames per Service Day - Duration (Sunday/Bank Hol)` (numeric), `Tendered Prices - Availability Fee (£/h)` (numeric), `Tendered Prices - Nomination Fee (£/h)` (text), `Tendered Prices -  Window Initiation Fee (£/window)` (text), `BMUs  Only` (text), `Maximum Part Load Point (MW)` (text), `Minimum Part Load Point (MW)` (text), `Minimum MEL (MW)` (text), `Maximum SEL (MW)` (text), `Primary Response (max.) @ 0.2Hz (MW)` (numeric), `Primary Response (max.) @ 0.5Hz (MW)` (numeric), `Primary Response (max.) @ 0.8Hz (MW)` (numeric), `Secondary Response (max.) @ 0.2/0.2Hz (MW)` (numeric), `Secondary Response (max.) @ 0.5/0.5Hz (MW)` (numeric), `High Frequency Response (max.) @ 0.2Hz (MW)` (numeric), `High Frequency Response (max.) @ 0.5Hz (MW)` (numeric), `Are you adding volume as per detail change provision` (text), `Please state the accepted tender that you are stacking onto` (text), `Please state if this is an all or nothing bid.` (text), `Please indicate if this is a mutually exclusive tender` (text), `Automatic Response Energy Deliverable by 10s (MW)` (text), `Automatic Response Energy Deliverable by 30s (MW)` (numeric), `Post code` (text), `Comments` (text)

- **4 resources sharing this schema:** Post Tender Report TR141 September 2021 CSV-  EXT , Post Tender Report TR155 November 2022 CSV-  EXT , Post Tender Report TR158 February 2023 CSV EXT , Post Tender Report TR159 March 2023 CSV EXT  (CSV via API, ~954 rows combined)
  Fields: `Tender Ref` (numeric), `Status` (text), `Rejection Codes` (text), `Company Name` (text), `Tendered Unit  (BMU/Unit ID)` (text), `TO connection  /  DNO connection` (text), `Generation Type` (text), `Start Date` (text), `End Date` (text), `Tendered Period  (dd.mm.yy - dd.mm.yy)` (text), `Applicable FFR Capability Data Table` (text), `Tendered Frames per Service Day - From (Mon-Fri)` (int4), `Tendered Frames per Service Day - To (Mon- Fri)` (int4), `Tendered Frames per Service Day - Duration (Mon-Fri)` (int4), `Tendered Frames per Service Day - From (Saturday)` (int4), `Tendered Frames per Service Day - To (Saturday)` (int4), `Tendered Frames per Service Day - Duration (Saturday)` (int4), `Tendered Frames per Service Day - From (Sunday/Bank Holidays)` (int4), `Tendered Frames per Service Day - To (Sunday/Bank Holidays)` (int4), `Tendered Frames per Service Day - Duration (Sunday/Bank Hol)` (int4), `Tendered Prices - Availability Fee (£/h)` (numeric), `Tendered Prices - Nomination Fee (£/h)` (text), `Tendered Prices -  Window Initiation Fee (£/window)` (text), `BMUs  Only` (text), `Maximum Part Load Point (MW)` (text), `Minimum Part Load Point (MW)` (text), `Minimum MEL (MW)` (text), `Maximum SEL (MW)` (text), `Primary Response (max.) @ 0.2Hz (MW)` (numeric), `Primary Response (max.) @ 0.5Hz (MW)` (int4), `Primary Response (max.) @ 0.8Hz (MW)` (int4), `Secondary Response (max.) @ 0.2/0.2Hz (MW)` (numeric), `Secondary Response (max.) @ 0.5/0.5Hz (MW)` (int4), `High Frequency Response (max.) @ 0.2Hz (MW)` (numeric), `High Frequency Response (max.) @ 0.5Hz (MW)` (int4), `Are you adding volume as per detail change provision` (text), `Please state the accepted tender that you are stacking onto` (text), `Please state if this is an all or nothing bid.` (text), `Please indicate if this is a mutually exclusive tender` (text), `Automatic Response Energy Deliverable by 10s (MW)` (text), `Automatic Response Energy Deliverable by 30s (MW)` (int4), `Post code` (text), `Comments` (text)

- **3 resources sharing this schema:** Post Tender Report TR144 December 2021 CSV, Post Tender Report TR152 August 2022 CSV EXT , Post Tender Report TR153 September 2022 CSV- EXT  (CSV via API, ~778 rows combined)
  Fields: `Tender Ref` (numeric), `Status` (text), `Rejection Codes` (text), `Company Name` (text), `Tendered Unit 
(BMU/Unit ID)` (text), `TO connection  /  DNO connection` (text), `Generation Type` (text), `Start Date` (text), `End Date` (text), `Tendered Period 
(dd.mm.yy - dd.mm.yy)` (text), `Applicable FFR Capability Data Table` (text), `Tendered Frames per Service Day - From (Mon-Fri)` (numeric), `Tendered Frames per Service Day - To (Mon- Fri)` (numeric), `Tendered Frames per Service Day - Duration (Mon-Fri)` (numeric), `Tendered Frames per Service Day - From (Saturday)` (numeric), `Tendered Frames per Service Day - To (Saturday)` (numeric), `Tendered Frames per Service Day - Duration (Saturday)` (numeric), `Tendered Frames per Service Day - From (Sunday/Bank Holidays)` (numeric), `Tendered Frames per Service Day - To (Sunday/Bank Holidays)` (numeric), `Tendered Frames per Service Day - Duration (Sunday/Bank Hol)` (numeric), `Tendered Prices - Availability Fee (£/h)` (numeric), `Tendered Prices - Nomination Fee (£/h)` (text), `Tendered Prices -  Window Initiation Fee (£/window)` (text), `BMUs  Only` (text), `Maximum Part Load Point (MW)` (text), `Minimum Part Load Point (MW)` (text), `Minimum MEL (MW)` (text), `Maximum SEL (MW)` (text), `Primary Response (max.) @ 0.2Hz (MW)` (numeric), `Primary Response (max.) @ 0.5Hz (MW)` (numeric), `Primary Response (max.) @ 0.8Hz (MW)` (numeric), `Secondary Response (max.) @ 0.2/0.2Hz (MW)` (numeric), `Secondary Response (max.) @ 0.5/0.5Hz (MW)` (numeric), `High Frequency Response (max.) @ 0.2Hz (MW)` (numeric), `High Frequency Response (max.) @ 0.5Hz (MW)` (numeric), `Are you adding volume as per detail change provision` (text), `Please state the accepted tender that you are stacking onto` (text), `Please state if this is an all or nothing bid.` (text), `Please indicate if this is a mutually exclusive tender` (text), `Automatic Response Energy Deliverable by 10s (MW)` (text), `Automatic Response Energy Deliverable by 30s (MW)` (numeric), `Post code` (text), `Comments` (text)

- **Post Tender Report TR145 January 2022 CSV EXT ** (CSV via API, ~229 rows)
  Fields: `Tender Ref` (numeric), `Status` (text), `Rejection Codes` (text), `Company Name` (text), `Tendered Unit 
(BMU/Unit ID)` (text), `TO connection  /  DNO connection` (text), `Generation Type` (text), `Start Date` (numeric), `End Date` (numeric), `Tendered Period 
(dd.mm.yy - dd.mm.yy)` (text), `Applicable FFR Capability Data Table` (text), `Tendered Frames per Service Day - From (Mon-Fri)` (numeric), `Tendered Frames per Service Day - To (Mon- Fri)` (numeric), `Tendered Frames per Service Day - Duration (Mon-Fri)` (numeric), `Tendered Frames per Service Day - From (Saturday)` (numeric), `Tendered Frames per Service Day - To (Saturday)` (numeric), `Tendered Frames per Service Day - Duration (Saturday)` (numeric), `Tendered Frames per Service Day - From (Sunday/Bank Holidays)` (numeric), `Tendered Frames per Service Day - To (Sunday/Bank Holidays)` (numeric), `Tendered Frames per Service Day - Duration (Sunday/Bank Hol)` (numeric), `Tendered Prices - Availability Fee (£/h)` (numeric), `Tendered Prices - Nomination Fee (£/h)` (text), `Tendered Prices -  Window Initiation Fee (£/window)` (text), `BMUs  Only` (text), `Maximum Part Load Point (MW)` (text), `Minimum Part Load Point (MW)` (text), `Minimum MEL (MW)` (text), `Maximum SEL (MW)` (text), `Primary Response (max.) @ 0.2Hz (MW)` (numeric), `Primary Response (max.) @ 0.5Hz (MW)` (numeric), `Primary Response (max.) @ 0.8Hz (MW)` (numeric), `Secondary Response (max.) @ 0.2/0.2Hz (MW)` (numeric), `Secondary Response (max.) @ 0.5/0.5Hz (MW)` (numeric), `High Frequency Response (max.) @ 0.2Hz (MW)` (numeric), `High Frequency Response (max.) @ 0.5Hz (MW)` (numeric), `Are you adding volume as per detail change provision` (text), `Please state the accepted tender that you are stacking onto` (text), `Please state if this is an all or nothing bid.` (text), `Please indicate if this is a mutually exclusive tender` (text), `Automatic Response Energy Deliverable by 10s (MW)` (text), `Automatic Response Energy Deliverable by 30s (MW)` (numeric), `Post code` (text), `Comments` (text)

- **Post Tender Report TR146 February 2022 CSV- EXT ** (CSV via API, ~196 rows)
  Fields: `Tender Ref` (numeric), `Status` (text), `Rejection Codes` (text), `Company Name` (text), `Tendered Unit  (BMU/Unit ID)` (text), `TO connection  /  DNO connection` (text), `Generation Type` (text), `Start Date` (text), `End Date` (text), `Tendered Period  (dd.mm.yy - dd.mm.yy)` (text), `Applicable FFR Capability Data Table` (text), `Tendered Frames per Service Day - From (Mon-Fri)` (int4), `Tendered Frames per Service Day - To (Mon- Fri)` (int4), `Tendered Frames per Service Day - Duration (Mon-Fri)` (int4), `Tendered Frames per Service Day - From (Saturday)` (int4), `Tendered Frames per Service Day - To (Saturday)` (int4), `Tendered Frames per Service Day - Duration (Saturday)` (int4), `Tendered Frames per Service Day - From (Sunday/Bank Holidays)` (int4), `Tendered Frames per Service Day - To (Sunday/Bank Holidays)` (int4), `Tendered Frames per Service Day - Duration (Sunday/Bank Hol)` (int4), `Tendered Prices - Availability Fee (£/h)` (numeric), `Tendered Prices - Nomination Fee (£/h)` (text), `Tendered Prices -  Window Initiation Fee (£/window)` (text), `BMUs  Only` (text), `Maximum Part Load Point (MW)` (text), `Minimum Part Load Point (MW)` (text), `Minimum MEL (MW)` (text), `Maximum SEL (MW)` (text), `Primary Response (max.) @ 0.2Hz (MW)` (numeric), `Primary Response (max.) @ 0.5Hz (MW)` (int4), `Primary Response (max.) @ 0.8Hz (MW)` (int4), `Secondary Response (max.) @ 0.2/0.2Hz (MW)` (numeric), `Secondary Response (max.) @ 0.5/0.5Hz (MW)` (int4), `High Frequency Response (max.) @ 0.2Hz (MW)` (numeric), `High Frequency Response (max.) @ 0.5Hz (MW)` (int4), `Are you adding volume as per detail change provision` (text), `Please state the accepted tender that you are stacking onto` (text), `Please state if this is an all or nothing bid.` (text), `Please indicate if this is a mutually exclusive tender` (text), `Automatic Response Energy Deliverable by 10s (MW)` (int4), `Automatic Response Energy Deliverable by 30s (MW)` (int4), `Post code` (text), `Comments` (text)

- **Post Tender Report TR147 March 2022 CSV EXT ** (CSV via API, ~212 rows)
  Fields: `Tender Ref` (numeric), `Status` (text), `Rejection Codes` (text), `Company Name` (text), `Tendered Unit 
(BMU/Unit ID)` (text), `TO connection  /  DNO connection` (text), `Generation Type` (text), `Start Date` (timestamp), `End Date` (timestamp), `Tendered Period 
(dd.mm.yy - dd.mm.yy)` (text), `Applicable FFR Capability Data Table` (text), `Tendered Frames per Service Day - From (Mon-Fri)` (numeric), `Tendered Frames per Service Day - To (Mon- Fri)` (numeric), `Tendered Frames per Service Day - Duration (Mon-Fri)` (numeric), `Tendered Frames per Service Day - From (Saturday)` (numeric), `Tendered Frames per Service Day - To (Saturday)` (numeric), `Tendered Frames per Service Day - Duration (Saturday)` (numeric), `Tendered Frames per Service Day - From (Sunday/Bank Holidays)` (numeric), `Tendered Frames per Service Day - To (Sunday/Bank Holidays)` (numeric), `Tendered Frames per Service Day - Duration (Sunday/Bank Hol)` (numeric), `Tendered Prices - Availability Fee (£/h)` (text), `Tendered Prices - Nomination Fee (£/h)` (text), `Tendered Prices -  Window Initiation Fee (£/window)` (text), `BMUs  Only` (text), `Maximum Part Load Point (MW)` (text), `Minimum Part Load Point (MW)` (text), `Minimum MEL (MW)` (text), `Maximum SEL (MW)` (text), `Primary Response (max.) @ 0.2Hz (MW)` (numeric), `Primary Response (max.) @ 0.5Hz (MW)` (numeric), `Primary Response (max.) @ 0.8Hz (MW)` (numeric), `Secondary Response (max.) @ 0.2/0.2Hz (MW)` (numeric), `Secondary Response (max.) @ 0.5/0.5Hz (MW)` (numeric), `High Frequency Response (max.) @ 0.2Hz (MW)` (numeric), `High Frequency Response (max.) @ 0.5Hz (MW)` (numeric), `Are you adding volume as per detail change provision` (text), `Please state the accepted tender that you are stacking onto` (text), `Please state if this is an all or nothing bid.` (text), `Please indicate if this is a mutually exclusive tender` (text), `Automatic Response Energy Deliverable by 10s (MW)` (text), `Automatic Response Energy Deliverable by 30s (MW)` (numeric), `Post code` (text), `Comments` (text)

- **Post Tender Report TR154 October 2022 CSV- EXT ** (CSV via API, ~272 rows)
  Fields: `Tender Ref` (numeric), `Status` (text), `Rejection Codes` (text), `Company Name` (text), `Tendered Unit  (BMU/Unit ID)` (text), `TO connection  /  DNO connection` (text), `Generation Type` (text), `Start Date` (text), `End Date` (text), `Tendered Period  (dd.mm.yy - dd.mm.yy)` (text), `Applicable FFR Capability Data Table` (text), `Tendered Frames per Service Day - From (Mon-Fri)` (int4), `Tendered Frames per Service Day - To (Mon- Fri)` (int4), `Tendered Frames per Service Day - Duration (Mon-Fri)` (int4), `Tendered Frames per Service Day - From (Saturday)` (int4), `Tendered Frames per Service Day - To (Saturday)` (int4), `Tendered Frames per Service Day - Duration (Saturday)` (int4), `Tendered Frames per Service Day - From (Sunday/Bank Holidays)` (int4), `Tendered Frames per Service Day - To (Sunday/Bank Holidays)` (int4), `Tendered Frames per Service Day - Duration (Sunday/Bank Hol)` (int4), `Tendered Prices - Availability Fee (£/h)` (numeric), `Tendered Prices - Nomination Fee (£/h)` (int4), `Tendered Prices -  Window Initiation Fee (£/window)` (text), `BMUs  Only` (text), `Maximum Part Load Point (MW)` (text), `Minimum Part Load Point (MW)` (text), `Minimum MEL (MW)` (text), `Maximum SEL (MW)` (text), `Primary Response (max.) @ 0.2Hz (MW)` (numeric), `Primary Response (max.) @ 0.5Hz (MW)` (int4), `Primary Response (max.) @ 0.8Hz (MW)` (int4), `Secondary Response (max.) @ 0.2/0.2Hz (MW)` (numeric), `Secondary Response (max.) @ 0.5/0.5Hz (MW)` (int4), `High Frequency Response (max.) @ 0.2Hz (MW)` (numeric), `High Frequency Response (max.) @ 0.5Hz (MW)` (int4), `Are you adding volume as per detail change provision` (text), `Please state the accepted tender that you are stacking onto` (text), `Please state if this is an all or nothing bid.` (text), `Please indicate if this is a mutually exclusive tender` (text), `Automatic Response Energy Deliverable by 10s (MW)` (text), `Automatic Response Energy Deliverable by 30s (MW)` (int4), `Post code` (text), `Comments` (text)

- **Post Tender Report TR156 December 2022 CSV - EXT ** (CSV via API, ~281 rows)
  Fields: `Tender Ref` (numeric), `Status` (text), `Rejection Codes` (text), `Company Name` (text), `Tendered Unit  (BMU/Unit ID)` (text), `TO connection  /  DNO connection` (text), `Generation Type` (text), `Start Date` (text), `End Date` (text), `Tendered Period  (dd.mm.yy - dd.mm.yy)` (text), `Applicable FFR Capability Data Table` (text), `Tendered Frames per Service Day - From (Mon-Fri)` (int4), `Tendered Frames per Service Day - To (Mon- Fri)` (int4), `Tendered Frames per Service Day - Duration (Mon-Fri)` (int4), `Tendered Frames per Service Day - From (Saturday)` (int4), `Tendered Frames per Service Day - To (Saturday)` (int4), `Tendered Frames per Service Day - Duration (Saturday)` (int4), `Tendered Frames per Service Day - From (Sunday/Bank Holidays)` (int4), `Tendered Frames per Service Day - To (Sunday/Bank Holidays)` (int4), `Tendered Frames per Service Day - Duration (Sunday/Bank Hol)` (int4), `Tendered Prices - Availability Fee (£/h)` (numeric), `Tendered Prices - Nomination Fee (£/h)` (int4), `Tendered Prices -  Window Initiation Fee (£/window)` (int4), `BMUs  Only` (text), `Maximum Part Load Point (MW)` (text), `Minimum Part Load Point (MW)` (text), `Minimum MEL (MW)` (text), `Maximum SEL (MW)` (text), `Primary Response (max.) @ 0.2Hz (MW)` (numeric), `Primary Response (max.) @ 0.5Hz (MW)` (int4), `Primary Response (max.) @ 0.8Hz (MW)` (int4), `Secondary Response (max.) @ 0.2/0.2Hz (MW)` (numeric), `Secondary Response (max.) @ 0.5/0.5Hz (MW)` (int4), `High Frequency Response (max.) @ 0.2Hz (MW)` (numeric), `High Frequency Response (max.) @ 0.5Hz (MW)` (int4), `Are you adding volume as per detail change provision` (text), `Please state the accepted tender that you are stacking onto` (text), `Please state if this is an all or nothing bid.` (text), `Please indicate if this is a mutually exclusive tender` (text), `Automatic Response Energy Deliverable by 10s (MW)` (text), `Automatic Response Energy Deliverable by 30s (MW)` (int4), `Post code` (text), `Comments` (text)

- **Post Tender Report TR157 January 2023 CSV EXT ** (CSV via API, ~291 rows)
  Fields: `Tender Ref` (numeric), `Status` (text), `Rejection Codes` (text), `Company Name` (text), `Tendered Unit  (BMU/Unit ID)` (text), `TO connection  /  DNO connection` (text), `Generation Type` (text), `Start Date` (text), `End Date` (text), `Tendered Period  (dd.mm.yy - dd.mm.yy)` (text), `Applicable FFR Capability Data Table` (text), `Tendered Frames per Service Day - From (Mon-Fri)` (int4), `Tendered Frames per Service Day - To (Mon- Fri)` (int4), `Tendered Frames per Service Day - Duration (Mon-Fri)` (int4), `Tendered Frames per Service Day - From (Saturday)` (int4), `Tendered Frames per Service Day - To (Saturday)` (int4), `Tendered Frames per Service Day - Duration (Saturday)` (int4), `Tendered Frames per Service Day - From (Sunday/Bank Holidays)` (int4), `Tendered Frames per Service Day - To (Sunday/Bank Holidays)` (int4), `Tendered Frames per Service Day - Duration (Sunday/Bank Hol)` (int4), `Tendered Prices - Availability Fee (£/h)` (numeric), `Tendered Prices - Nomination Fee (£/h)` (text), `Tendered Prices -  Window Initiation Fee (£/window)` (text), `BMUs  Only` (text), `Maximum Part Load Point (MW)` (text), `Minimum Part Load Point (MW)` (text), `Minimum MEL (MW)` (text), `Maximum SEL (MW)` (text), `Primary Response (max.) @ 0.2Hz (MW)` (numeric), `Primary Response (max.) @ 0.5Hz (MW)` (int4), `Primary Response (max.) @ 0.8Hz (MW)` (numeric), `Secondary Response (max.) @ 0.2/0.2Hz (MW)` (numeric), `Secondary Response (max.) @ 0.5/0.5Hz (MW)` (int4), `High Frequency Response (max.) @ 0.2Hz (MW)` (numeric), `High Frequency Response (max.) @ 0.5Hz (MW)` (int4), `Are you adding volume as per detail change provision` (text), `Please state the accepted tender that you are stacking onto` (text), `Please state if this is an all or nothing bid.` (text), `Please indicate if this is a mutually exclusive tender` (text), `Automatic Response Energy Deliverable by 10s (MW)` (text), `Automatic Response Energy Deliverable by 30s (MW)` (int4), `Post code` (text), `Comments` (text)

- **Post Tender Report TR160 April 2023 CSV EXT ** (CSV via API, ~206 rows)
  Fields: `Tender Ref` (numeric), `Status` (text), `Rejection Codes` (text), `Company Name` (text), `Tendered Unit  (BMU/Unit ID)` (text), `TO connection  /  DNO connection` (text), `Generation Type` (text), `Start Date` (date), `End Date` (date), `Tendered Period  (dd.mm.yy - dd.mm.yy)` (text), `Applicable FFR Capability Data Table` (text), `Tendered Frames per Service Day - From (Mon-Fri)` (int4), `Tendered Frames per Service Day - To (Mon- Fri)` (int4), `Tendered Frames per Service Day - Duration (Mon-Fri)` (int4), `Tendered Frames per Service Day - From (Saturday)` (int4), `Tendered Frames per Service Day - To (Saturday)` (int4), `Tendered Frames per Service Day - Duration (Saturday)` (int4), `Tendered Frames per Service Day - From (Sunday/Bank Holidays)` (int4), `Tendered Frames per Service Day - To (Sunday/Bank Holidays)` (int4), `Tendered Frames per Service Day - Duration (Sunday/Bank Hol)` (int4), `Tendered Prices - Availability Fee (£/h)` (numeric), `Tendered Prices - Nomination Fee (£/h)` (numeric), `Tendered Prices -  Window Initiation Fee (£/window)` (numeric), `BMUs  Only` (text), `Maximum Part Load Point (MW)` (numeric), `Minimum Part Load Point (MW)` (numeric), `Minimum MEL (MW)` (numeric), `Maximum SEL (MW)` (numeric), `Primary Response (max.) @ 0.2Hz (MW)` (numeric), `Primary Response (max.) @ 0.5Hz (MW)` (numeric), `Primary Response (max.) @ 0.8Hz (MW)` (numeric), `Secondary Response (max.) @ 0.2/0.2Hz (MW)` (numeric), `Secondary Response (max.) @ 0.5/0.5Hz (MW)` (numeric), `High Frequency Response (max.) @ 0.2Hz (MW)` (numeric), `High Frequency Response (max.) @ 0.5Hz (MW)` (numeric), `Are you adding volume as per detail change provision` (text), `Please state the accepted tender that you are stacking onto` (numeric), `Please state if this is an all or nothing bid.` (text), `Please indicate if this is a mutually exclusive tender` (text), `Automatic Response Energy Deliverable by 10s (MW)` (numeric), `Automatic Response Energy Deliverable by 30s (MW)` (numeric), `Post code` (text), `Comments` (text)

- **6 resources sharing this schema:** Post Tender Report TR161 May 2023 CSV EXT , Post Tender Report TR162 JUNE 2023 CSV EXT , Post Tender Report TR163 July 2023 CSV EXT , Post Tender Report TR164 August 2023 CSV EXT , Post Tender Report TR165 September 2023 CSV EXT , Post Tender Report TR166 October 2023 CSV EXT  (CSV via API, ~1,158 rows combined)
  Fields: `Tender Ref` (numeric), `Status` (text), `Rejection Codes` (text), `Company Name` (text), `Tendered Unit  (BMU/Unit ID)` (text), `TO connection  /  DNO connection` (text), `Generation Type` (text), `Start Date` (text), `End Date` (text), `Tendered Period  (dd.mm.yy - dd.mm.yy)` (text), `Applicable FFR Capability Data Table` (text), `Tendered Frames per Service Day - From (Mon-Fri)` (int4), `Tendered Frames per Service Day - To (Mon- Fri)` (int4), `Tendered Frames per Service Day - Duration (Mon-Fri)` (int4), `Tendered Frames per Service Day - From (Saturday)` (int4), `Tendered Frames per Service Day - To (Saturday)` (int4), `Tendered Frames per Service Day - Duration (Saturday)` (int4), `Tendered Frames per Service Day - From (Sunday/Bank Holidays)` (int4), `Tendered Frames per Service Day - To (Sunday/Bank Holidays)` (int4), `Tendered Frames per Service Day - Duration (Sunday/Bank Hol)` (int4), `Tendered Prices - Availability Fee (£/h)` (numeric), `Tendered Prices - Nomination Fee (£/h)` (text), `Tendered Prices -  Window Initiation Fee (£/window)` (text), `BMUs  Only` (text), `Maximum Part Load Point (MW)` (text), `Minimum Part Load Point (MW)` (text), `Minimum MEL (MW)` (text), `Maximum SEL (MW)` (text), `Primary Response (max.) @ 0.2Hz (MW)` (numeric), `Primary Response (max.) @ 0.5Hz (MW)` (int4), `Primary Response (max.) @ 0.8Hz (MW)` (int4), `Secondary Response (max.) @ 0.2/0.2Hz (MW)` (numeric), `Secondary Response (max.) @ 0.5/0.5Hz (MW)` (int4), `High Frequency Response (max.) @ 0.2Hz (MW)` (numeric), `High Frequency Response (max.) @ 0.5Hz (MW)` (int4), `Are you adding volume as per detail change provision` (text), `Please state the accepted tender that you are stacking onto` (text), `Please state if this is an all or nothing bid.` (text), `Please indicate if this is a mutually exclusive tender` (text), `Automatic Response Energy Deliverable by 10s (MW)` (text), `Automatic Response Energy Deliverable by 30s (MW)` (text), `Post code` (text), `Comments` (text)

- **Post Tender Report - TR122 Feb-20** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report - TR121 Jan-20** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report - TR120 Dec-19** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report - TR119 Nov-19** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report - TR118 Oct-19** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report - TR117 Sep-19** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report - TR116 Aug-19** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report - TR115 Jul-19** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report - TR114 Jun-19** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report - TR113 May-19** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report - TR112 Apr-19** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report - TR111 Mar-19** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report - TR110 Feb-19** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report - TR109 Jan-19** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report - TR108 Dec-18** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report - TR123 Mar-20** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report- TR124 Apr- 20** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report- TR125 May 2020- EXT** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report - TR126 June 2020** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report - TR127 July 2020** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report - TR127 July 2020 - Amended** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR128 August 2020** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR129 September 2020** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR130 October 2020** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR131 November 2020 - EXT** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR132 December 2020 EXT** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR133 January 2021 - EXT** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR134 February 2021- EXT** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR136 April 2021- EXT** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR135 March 2021- EXT** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR136 April 2021 EXT- Amended ** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR137 May 2021 EXT ** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR138 June 2021 EXT ** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR139 July 2021 EXT ** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR140 August 2021 EXT ** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR141 September 2021 EXT ** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR142 October 2021 EXT xlms** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR143 November 2021.xlms. EXT ** (XLSM file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR144 December 2021 EXT ** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR145 January 2022 EXT ** (XLSM file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR146 February 2022 EXT ** (XLSM file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR147 March 2022 EXT ** (XLSM file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR148 April 2022 EXT ** (XLSM file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR150 June 2022 EXT ** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR151 July 2022 EXT ** (XLSM file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR152 August 2022 EXT ** (XLSM file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR153 September 2022 EXT ** (XLSM file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR154 October 2022 EXT ** (XLSM file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR155 November 2022-  EXT ** (XLSM file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR156 December 2022- EXT ** (XLSM file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR157 January 2023 EXT ** (XLSM file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR158 February 2023 EXT ** (XLSM file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR159 March 2023 EXT ** (XLSM file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR160 April 2023 EXT ** (XLSM file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR161 May 2023 EXT ** (XLSM file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR162 June 2023  EXT ** (XLSM file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR163 July 2023 EXT ** (XLSM file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR164 August 2023 EXT ** (XLSM file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR165 September 2023 EXT ** (XLSM file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Post Tender Report TR166 October 2023 EXT ** (XLSM file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Long Term Forecasts For Dc Dm Dynamic Regulation Requirements _(cadence hint from name: forecast series)_

`neso_data/ancillary-services/long-term-forecasts-for-dc-dm-dr-requirements/` — 1 resource(s)

- **DX Future Requirement** (CSV via API, ~4,212 rows)
  Fields: `Forecast Created` (date), `Forecast Target Month` (date), `Service Type` (text), `EFA` (int4), `Interval` (text), `Possibilities` (numeric)

### Non Bm Ancillary Service Dispatch Platform ASDP (Ancillary Service Dispatch Platform) Instructions

`neso_data/ancillary-services/non-bm-ancillary-service-dispatch-platform-asdp-instructions/` — 70 resource(s)

- **2 resources sharing this schema:** Non BM Dispatch Cease Instructions_Jul_2020, Non BM Dispatch Cease Instructions_Jun_2020 (CSV via API, ~13 rows combined)
  Fields: `EntryID` (int4), `ServiceType` (text), `InstructionStartDateTime` (text), `MW` (int4), `IndicativePrice` (numeric), `InstructionCeaseDateTime` (text), `DispatchDateTimeStamp` (text), `CeaseDateTimeStamp` (text)

- **Non BM Dispatch Cease Instructions_Aug_2020** (CSV via API, ~5 rows)
  Fields: `EntryID` (int4), `ServiceType` (text), `InstructionStartDateTime` (text), `MW` (int4), `IndicativePrice` (int4), `InstructionCeaseDateTime` (text), `DispatchDateTimeStamp` (text), `CeaseDateTimeStamp` (text)

- **3 resources sharing this schema:** Non BM Dispatch Cease Instructions_Dec_2020, Non BM Dispatch Cease Instructions_Nov_2020, Non BM Dispatch Cease Instructions_Oct_2020 (CSV via API, ~2,731 rows combined)
  Fields: `EntryID` (int4), `ServiceType` (text), `InstructionStartDateTime` (text), `MW` (int4), `IndicativePrice` (float8), `InstructionCeaseDateTime` (text), `DispatchDateTimeStamp` (text), `CeaseDateTimeStamp` (text)

- **10 resources sharing this schema** (e.g. Non BM Dispatch Cease Instructions_Apr_2021, Non BM Dispatch Cease Instructions_Aug_2021, Non BM Dispatch Cease Instructions_Feb_2021, …) (CSV via API, ~9,692 rows combined)
  Fields: `EntryID` (int4), `ServiceType` (text), `InstructionStartDateTime` (timestamp), `MW` (int4), `IndicativePrice` (float8), `InstructionCeaseDateTime` (timestamp), `DispatchDateTimeStamp` (timestamp), `CeaseDateTimeStamp` (timestamp)

- **53 resources sharing this schema** (e.g. Non BM Dispatch Cease Instructions_Apr_2022, Non BM Dispatch Cease Instructions_Apr_2023, Non BM Dispatch Cease Instructions_Apr_2024, …) (CSV via API, ~60,929 rows combined)
  Fields: `EntryID` (int4), `ServiceType` (text), `InstructionStartDateTime` (timestamp), `MW` (int4), `IndicativePrice` (float8), `InstructionCeaseDateTime` (timestamp), `DispatchDateTimeStamp` (timestamp), `CeaseDateTimeStamp` (timestamp), `PartyID` (text), `AssetID` (text), `Tendered` (text)

- **Non BM Dispatch Cease Instructions_Jan_2023** (CSV via API, ~767 rows)
  Fields: `EntryID` (numeric), `ServiceType` (text), `InstructionStartDateTime` (timestamp), `MW` (numeric), `IndicativePrice` (numeric), `InstructionCeaseDateTime` (timestamp), `DispatchDateTimeStamp` (timestamp), `CeaseDateTimeStamp` (timestamp), `PartyID` (text), `AssetID` (text), `Tendered` (text)

### Non Bm Ancillary Service Dispatch Platform ASDP (Ancillary Service Dispatch Platform) Window Prices

`neso_data/ancillary-services/non-bm-ancillary-service-dispatch-platform-asdp-window-prices/` — 2 resource(s)

- **Non BM Window Price Change_2025** (CSV via API, ~25,933 rows)
  Fields: `EntryID` (int4), `ServiceType` (text), `SPStartDateTime` (timestamp), `SPEndDateTime` (timestamp), `WindowPrice` (numeric), `CreatedTime` (timestamp), `PartyID` (text), `AssetID` (text)

- **Non BM Window Price Change_2026** (CSV via API, ~13,309 rows)
  Fields: `EntryID` (int4), `ServiceType` (text), `SPStartDateTime` (timestamp), `SPEndDateTime` (timestamp), `WindowPrice` (float8), `CreatedTime` (timestamp), `PartyID` (text), `AssetID` (text)

### Obligatory Reactive Power Service ORPS (Obligatory Reactive Power Service) Utilisation

`neso_data/ancillary-services/obligatory-reactive-power-service-orps-utilisation/` — 7 resource(s)

- **Historic Reactive Utilisation Data - Apr-2013 - March 2020** (CSV via API, ~295 rows)
  Fields: `Company` (text), `Unit` (text), `Default/Market` (text), `Location` (text), `Oct 13 - LEAD` (numeric), `Oct 13  - LAG` (numeric), `Oct 13  - TOTAL` (numeric), `Nov 13 - LEAD` (numeric), `Nov 13 - LAG` (numeric), `Nov 13 - TOTAL` (numeric), `Dec 13 - LEAD` (numeric), `Dec 13 -LAG` (numeric), `Dec 13 - TOTAL` (numeric), `Jan 14 - LEAD` (numeric), `Jan 14 - LAG` (numeric), `Jan 14 - TOTAL` (numeric), `Feb 14 - LEAD` (numeric), `Feb 14- LAG` (numeric), `Feb 14 - TOTAL` (numeric), `Mar 14 - LEAD` (numeric), `Mar 14  - LAG` (numeric), `Mar 14 - TOTAL` (numeric), `Apr 14 - LEAD` (numeric), `Apr 14  - LAG` (numeric), `Apr 14   - TOTAL` (numeric), `May 14 - LEAD` (numeric), `May 14 - LAG` (numeric), `May 14 - TOTAL` (numeric), `Jun 14 - LEAD` (numeric), `Jun 14 -LAG` (numeric), `Jun 14 - TOTAL` (numeric), `Jul 14 - LEAD` (numeric), `Jul 14  - LAG` (numeric), `Jul 14  - TOTAL` (numeric), `Aug 14 - LEAD` (numeric), `Aug 14 - LAG` (numeric), `Aug 14  - TOTAL` (numeric), `Sep 14- LEAD` (numeric), `Sep 14  - LAG` (numeric), `Sep 14- TOTAL` (numeric), `Oct 14- LEAD` (numeric), `Oct 14- LAG` (numeric), `Oct 14   - TOTAL` (numeric), `Nov 14 - LEAD` (numeric), `Nov 14- LAG` (numeric), `Nov 14- TOTAL` (numeric), `Dec 14 - LEAD` (numeric), `Dec 14  -LAG` (numeric), `Dec 14  - TOTAL` (numeric), `Jan 15 - LEAD` (numeric), `Jan 15  - LAG` (numeric), `Jan 15 - TOTAL` (numeric), `Feb 15 - LEAD` (numeric), `Feb 15  - LAG` (numeric), `Feb 15 - TOTAL` (numeric), `Mar 15- LEAD` (numeric), `Mar 15  - LAG` (numeric), `Mar 15- TOTAL` (numeric), `Apr 15- LEAD` (numeric), `Apr 15- LAG` (numeric), `Apr 15  - TOTAL` (numeric), `May 15 - LEAD` (numeric), `May 15- LAG` (numeric), `May 15- TOTAL` (numeric), `Jun 15 - LEAD` (numeric), `Jun 15  -LAG` (numeric), `Jun 15  - TOTAL` (numeric), `Jul 15 - LEAD` (numeric), `Jul 15  - LAG` (numeric), `Jul 15  - TOTAL` (numeric), `Aug 15 - LEAD` (numeric), `Aug 15  - LAG` (numeric), `Aug 15  - TOTAL` (numeric), `Sep 15- LEAD` (numeric), `Sep 15 - LAG` (numeric), `Sep 15- TOTAL` (numeric), `Oct 15- LEAD` (numeric), `Oct 15- LAG` (numeric), `Oct 15  - TOTAL` (numeric), `Nov 15 - LEAD` (numeric), `Nov 15- LAG` (numeric), `Nov 15- TOTAL` (numeric), `Dec 15 - LEAD` (numeric), `Dec 15  -LAG` (numeric), `Dec 15  - TOTAL` (numeric), `Jan 16 - LEAD` (numeric), `Jan 16  - LAG` (numeric), `Jan 16   - TOTAL` (numeric), `Feb 16 - LEAD` (numeric), `Feb 16- LAG` (numeric), `Feb 16 - TOTAL` (numeric), `Mar 16 - LEAD` (numeric), `Mar 16  - LAG` (numeric), `Mar 16 - TOTAL` (numeric), `Apr 16 - LEAD` (numeric), `Apr 16  - LAG` (numeric), `Apr 16- TOTAL` (numeric), `May 16 - LEAD` (numeric), `May 16 - LAG` (numeric), `May 16 - TOTAL` (numeric), `Jun 16 - LEAD` (numeric), `Jun 16 -LAG` (numeric), `Jun 16- TOTAL` (numeric), `Jul 16 - LEAD` (numeric), `Jul 16 - LAG` (numeric), `Jul 16 - TOTAL` (numeric), `Aug 16 - LEAD` (numeric), `Aug 16- LAG` (numeric), `Aug 16 - TOTAL` (numeric), `Sep 16 - LEAD` (numeric), `Sep 16  - LAG` (numeric), `Sep 16  - TOTAL` (numeric), `Oct 16 - LEAD` (numeric), `Oct 16  - LAG` (numeric), `Oct 16 - TOTAL` (numeric), `Nov 16 - LEAD` (numeric), `Nov 16 - LAG` (numeric), `Nov 16 - TOTAL` (numeric), `Dec 16 - LEAD` (numeric), `Dec 16 -LAG` (numeric), `Dec 16 - TOTAL` (numeric), `Jan 17 - LEAD` (numeric), `Jan 17 - LAG` (numeric), `Jan 17 - TOTAL` (numeric), `Feb 17 - LEAD` (numeric), `Feb 17 - LAG` (numeric), `Feb 17 - TOTAL` (numeric), `Mar 17- LEAD` (numeric), `Mar 17  - LAG` (numeric), `Mar 17 - TOTAL` (numeric), `Apr 17 - LEAD` (numeric), `Apr 17  - LAG` (numeric), `Apr 17 - TOTAL` (numeric), `May 17 - LEAD` (numeric), `May 17 - LAG` (numeric), `May 17 - TOTAL` (numeric), `Jun 17 - LEAD` (numeric), `Jun 17  -LAG` (numeric), `Jun 17  - TOTAL` (numeric), `Jul 17 - LEAD` (numeric), `Jul 17 - LAG` (numeric), `Jul 17- TOTAL` (numeric), `Aug 17 - LEAD` (numeric), `Aug 17 - LAG` (numeric), `Aug 17 - TOTAL` (numeric), `Sep 17- LEAD` (numeric), `Sep 17  - LAG` (numeric), `Sep 17 - TOTAL` (numeric), `Oct 17 - LEAD` (numeric), `Oct 17  - LAG` (numeric), `Oct 17 - TOTAL` (numeric), `Nov 17 - LEAD` (numeric), `Nov 17 - LAG` (numeric), `Nov 17 - TOTAL` (numeric), `Dec 17 - LEAD` (numeric), `Dec 17  -LAG` (numeric), `Dec 17  - TOTAL` (numeric), `Jan 18 - LEAD` (numeric), `Jan 18  - LAG` (numeric), `Jan 18 - TOTAL` (numeric), `Feb 18 - LEAD` (numeric), `Feb 18 - LAG` (numeric), `Feb 18 - TOTAL` (numeric), `Mar 18 - LEAD` (numeric), `Mar 18  - LAG` (numeric), `Mar 18 - TOTAL` (numeric), `Apr 18 - LEAD` (numeric), `Apr 18  - LAG` (numeric), `Apr 18 - TOTAL` (numeric), `May 18 - LEAD` (numeric), `May 18 - LAG` (numeric), `May 18 - TOTAL` (numeric), `Jun 18 - LEAD` (numeric), `Jun 18 -LAG` (numeric), `Jun 18  - TOTAL` (numeric), `Jul 18 - LEAD` (numeric), `Jul 18  - LAG` (numeric), `Jul 18 - TOTAL` (numeric), `Aug 18 - LEAD` (numeric), `Aug 18 - LAG` (numeric), `Aug 18 - TOTAL` (numeric), `Sep 18 - LEAD` (numeric), `Sep 18  - LAG` (numeric), `Sep 18 - TOTAL` (numeric), `Oct 18 - LEAD` (numeric), `Oct 18  - LAG` (numeric), `Oct 18 - TOTAL` (numeric), `Nov 18 - LEAD` (numeric), `Nov 18 - LAG` (numeric), `Nov 18 - TOTAL` (numeric), `Dec 18 - LEAD` (numeric), `Dec 18 -LAG` (numeric), `Dec 18  - TOTAL` (numeric), `Jan 19 - LEAD` (numeric), `Jan 19  - LAG` (numeric), `Jan 19 - TOTAL` (numeric), `Feb 19 - LEAD` (numeric), `Feb 19 - LAG` (numeric), `Feb 19- TOTAL` (numeric), `Mar 19 - LEAD` (numeric), `Mar 19  - LAG` (numeric), `Mar 19 - TOTAL` (numeric), `Apr 19 - LEAD` (numeric), `Apr 19 -LAG` (numeric), `Apr 19- TOTAL` (numeric), `May 19 - LEAD` (text), `May 19 -LAG` (text), `May 19- TOTAL` (text), `Jun 19 - LEAD` (numeric), `Jun 19 -LAG` (numeric), `Jun 19- TOTAL` (numeric), `Jul 19 - LEAD` (numeric), `Jul 19 -LAG` (numeric), `Jul 19- TOTAL` (numeric), `Aug 19 - LEAD` (text), `Aug 19 -LAG` (text), `Aug 19- TOTAL` (text), `Sep 19 - LEAD` (text), `Sep 19 -LAG` (text), `Sep 19- TOTAL` (text), `Oct 19 -LEAD` (text), `Oct 19 - LAG` (text), `Oct -19 TOTAL` (text), `Nov 19 -LEAD` (text), `Nov 19 - LAG` (text), `Nov -19 TOTAL` (text), `Dec 19 -LEAD` (numeric), `Dec 19 - LAG` (numeric), `Dec 19 - TOTAL` (text), `Jan 20 -LEAD` (text), `Jan 20 - LAG` (text), `Jan 20 - TOTAL` (text), `Feb 20 -LEAD` (numeric), `Feb 20 - LAG` (numeric), `Feb 20 - TOTAL` (numeric), `Mar 20 -LEAD` (text), `Mar 20 - LAG` (text), `Mar 20 - TOTAL` (text)

- **Reactive Utilisation Data - Apr-2020 - Dec-2024** (CSV via API, ~243 rows)
  Fields: `id` (numeric), `Company` (text), `Unit` (text), `Default/Market` (text), `Location` (text), `Apr 20 -LEAD` (numeric), `Apr 20 - LAG` (numeric), `Apr 20 - TOTAL` (numeric), `May 20 -LEAD` (numeric), `May 20 - LAG` (numeric), `May 20 - TOTAL` (numeric), `Jun 20 -LEAD` (numeric), `Jun 20 - LAG` (numeric), `Jun 20 - TOTAL` (numeric), `Jul 20 -LEAD` (numeric), `Jul 20 - LAG` (numeric), `Jul 20 - TOTAL` (numeric), `Aug 20 -LEAD` (numeric), `Aug 20 - LAG` (numeric), `Aug 20 - TOTAL` (numeric), `Sep 20 -LEAD` (numeric), `Sep 20 - LAG` (numeric), `Sep 20 - TOTAL` (numeric), `Oct 20 -LEAD` (numeric), `Oct 20 - LAG` (numeric), `Oct 20 - TOTAL` (numeric), `Nov 20 -LEAD` (numeric), `Nov 20 - LAG` (numeric), `Nov 20 - TOTAL` (numeric), `Dec 20 -LEAD` (numeric), `Dec 20 - LAG` (numeric), `Dec 20 - TOTAL` (numeric), `Jan 21 -LEAD` (numeric), `Jan 21 - LAG` (numeric), `Jan 21 - TOTAL` (numeric), `Feb 21 -LEAD` (numeric), `Feb 21 - LAG` (numeric), `Feb 21 - TOTAL` (numeric), `Mar 21 -LEAD` (numeric), `Mar 21 - LAG` (numeric), `Mar 21 - TOTAL` (numeric), `Apr 21 -LEAD` (numeric), `Apr 21 - LAG` (numeric), `Apr 21 - TOTAL` (numeric), `May 21 -LEAD` (numeric), `May 21 - LAG` (numeric), `May 21 - TOTAL` (numeric), `Jun 21 -LEAD` (numeric), `Jun 21 - LAG` (numeric), `Jun 21 - TOTAL` (numeric), `Jul 21 -LEAD` (numeric), `Jul 21 - LAG` (numeric), `Jul 21 - TOTAL` (numeric), `Aug 21 -LEAD` (numeric), `Aug 21 - LAG` (numeric), `Aug 21 - TOTAL` (numeric), `Sep 21 -LEAD` (numeric), `Sep 21 - LAG` (numeric), `Sep 21 - TOTAL` (numeric), `Oct 21 -LEAD` (numeric), `Oct 21 - LAG` (numeric), `Oct 21 - TOTAL` (numeric), `Nov 21 -LEAD` (numeric), `Nov  21 - LAG` (numeric), `Nov  21 - TOTAL` (numeric), `Dec 21 - LEAD` (numeric), `Dec 21 - LAG` (numeric), `Dec 21 - Total` (numeric), `Jan 22 - LEAD` (numeric), `Jan 22 - LAG` (numeric), `Jan 22 - Total` (numeric), `Feb 22 - LEAD` (numeric), `Feb 22 - LAG` (numeric), `Feb 22 - Total` (numeric), `Mar 22 - LEAD` (numeric), `Mar 22 - LAG` (numeric), `Mar 22 - Total` (numeric), `Apr 22 - LEAD` (numeric), `Apr 22 - LAG` (numeric), `Apr 22 - Total` (numeric), `May 22 - LEAD` (numeric), `May 22 - LAG` (numeric), `May 22 - Total` (numeric), `Jun 22 - LEAD` (numeric), `Jun 22 - LAG` (numeric), `Jun 22 - Total` (numeric), `Jul 22 - LEAD` (numeric), `Jul 22 - LAG` (numeric), `Jul 22 - Total` (numeric), `Aug 22 - LEAD` (numeric), `Aug 22 - LAG` (numeric), `Aug 22 - Total` (numeric), `Sep 22 - LEAD` (numeric), `Sep 22 - LAG` (numeric), `Sep 22 - Total` (numeric), `Oct 22 - LEAD` (numeric), `Oct 22 - LAG` (numeric), `Oct 22 - Total` (numeric), `Nov 22 - LEAD` (numeric), `Nov 22 - LAG` (numeric), `Nov 22 - Total` (numeric), `Dec 22 - LEAD` (numeric), `Dec 22 - LAG` (numeric), `Dec 22 - Total` (numeric), `Jan 23 - LEAD` (numeric), `Jan 23 - LAG` (numeric), `Jan 23 - Total` (numeric), `Feb 23 - LEAD` (numeric), `Feb 23 - LAG` (numeric), `Feb 23 - Total` (numeric), `Mar 23 - LEAD` (numeric), `Mar 23 - LAG` (numeric), `Mar 23 - Total` (numeric), `Apr 23 - LEAD` (numeric), `Apr 23 - LAG` (numeric), `Apr 23 - Total` (numeric), `May 23 - LEAD` (numeric), `May 23 - LAG` (numeric), `May 23 - Total` (numeric), `June 23 - LEAD` (numeric), `June 23 - LAG` (numeric), `June 23 - Total` (numeric), `July 23 - LEAD` (numeric), `July 23 - LAG` (numeric), `July 23 - Total` (numeric), `Aug 23 - LEAD` (numeric), `Aug 23 - LAG` (numeric), `Aug 23 - Total` (numeric), `Sep 23 - LEAD` (numeric), `Sep 23 - LAG` (numeric), `Sep 23 - Total` (numeric), `Oct 23 - LEAD` (numeric), `Oct 23 - LAG` (numeric), `Oct 23 - Total` (numeric), `Nov 23 - LEAD` (numeric), `Nov 23 - LAG` (numeric), `Nov 23 - Total` (numeric), `Dec 23 - LEAD` (numeric), `Dec 23 - LAG` (numeric), `Dec 23 - Total` (numeric), `Jan 24 - LEAD` (numeric), `Jan 24 - LAG` (numeric), `Jan 24 - Total` (numeric), `Feb 24 - LEAD` (numeric), `Feb 24 - LAG` (numeric), `Feb 24 - Total` (numeric), `Mar 24 - LEAD` (numeric), `Mar 24 - LAG` (numeric), `Mar 24 - Total` (numeric), `Apr 24 - LEAD` (numeric), `Apr 24 - LAG` (numeric), `Apr 24 - Total` (numeric), `May 24 - LEAD` (numeric), `May 24 - LAG` (numeric), `May 24 - Total` (numeric), `June 24 - LEAD` (numeric), `June 24 - LAG` (numeric), `June 24 - Total` (numeric), `July 24 - LEAD` (numeric), `July 24 - LAG` (numeric), `July 24 - Total` (numeric), `Aug 24 - LEAD` (numeric), `Aug 24 - LAG` (numeric), `Aug 24 - Total` (numeric), `Sep 24 - LEAD` (numeric), `Sep 24 - LAG` (numeric), `Sep 24 - Total` (numeric), `Oct 24 - LEAD` (numeric), `Oct 24 - LAG` (numeric), `Oct 24 - Total` (numeric), `Nov 24 - LEAD` (numeric), `Nov 24 - LAG` (numeric), `Nov 24 - Total` (numeric), `Dec 24 - LEAD` (numeric), `Dec 24 - LAG` (numeric), `Dec 24 - Total` (numeric)

- **Reactive Default Payment Rate - July - 2026** (CSV via API, ~225 rows)
  Fields: `Year` (text), `Month` (int4), `HPIm` (numeric), `PAPIm` (numeric), `PPIm` (numeric), `FRPIm` (numeric), `Im` (numeric), `X = 1` (numeric), `X = 0.2` (numeric)

- **Reactive Utilisation Data** (CSV via API, ~18,006 rows)
  Fields: `Company` (text), `Unit` (text), `Default/Market` (text), `Location` (text), `Month-Year` (text), `LEAD` (numeric), `LAG` (numeric), `TOTAL` (numeric)

- **Reactive Utilisation-Nov-2021** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Reactive Default Payment Rate - July - 2026** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Obligatory Reactive Power Guide** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Obp Non Bm Physical Notifications

`neso_data/ancillary-services/obp-non-bm-physical-notifications/` — 1 resource(s)

- **Non-BM Physical Notifications** (CSV via API, ~251,184 rows)
  Fields: `Data` (text), `Unit ID` (text), `Time From` (timestamp), `Level From` (numeric), `Time To` (timestamp), `Level To` (numeric)

### Obp Non Bm Reserve Instructions

`neso_data/ancillary-services/obp-non-bm-reserve-instructions/` — 1 resource(s)

- **Non-BM Instructions from OBP** (CSV via API, ~293 rows)
  Fields: `Instruction ID` (int4), `Sequence` (int4), `Unit ID` (text), `Service ID` (text), `Instruction Point Type` (text), `Issue Datetime` (timestamp), `Point Datetime` (timestamp), `Target MW` (numeric), `Target Price` (numeric), `Instruction Point ID` (int4), `Instruction Status` (text)

### Obp Reserve Availability Utilisation Price

`neso_data/ancillary-services/obp-reserve-availability-utilisation-price/` — 1 resource(s)

- ** Non-BM Reserve Availability MW and Utilisation Price** (CSV via API, ~56,102 rows)
  Fields: `Data` (text), `Unit ID` (text), `Time From` (timestamp), `Time To` (timestamp), `Pair ID` (numeric), `Availability Power` (numeric), `Utilisation Price` (numeric), `Service ID` (text)

### Optional Downward Flexibility Management ODFM (Optional Downward Flexibility Management) Market Information

`neso_data/ancillary-services/optional-downward-flexibility-management-odfm-market-information/` — 13 resource(s)

- **Market Information Results 2020** (CSV via API, ~7,321 rows)
  Fields: `Unique ID` (text), `Contracted Unit ID` (text), `Applicant/Agent` (text), `Price (£/MW/hr)` (numeric), `Allocated Registered Service Volume (MW)` (numeric), `Technology type` (text), `Start time (BST)` (text), `Start date` (timestamp), `Cease time (BST)` (text), `Cease Date` (timestamp), `GSP` (text), `DNO` (text), `Accept/Reject` (text), `Reasons` (text), `Date` (text)

- **2 resources sharing this schema:** ODFM Instructed Volume for 05-07-2020, ODFM Instructed Volume for 05-07-2020 V2 (CSV via API, ~98 rows combined)
  Fields: `Settlement Period` (numeric), `ODFM Instructed MW` (numeric), `Time` (text), `Date` (timestamp)

- **ODFM Load Factors** (CSV via API, ~240 rows)
  Fields: `Datetime` (timestamp), `Scottish Hydro Wind` (numeric), `Scottish Power Wind` (numeric), `Electricity North West Wind` (numeric), `NPG North East Wind` (numeric), `NPG Yorkshire Wind` (numeric), `SP Manweb Wind` (numeric), `WPD West Midlands Wind` (numeric), `WPD East Midlands Wind` (numeric), `UKPN East Anglia Wind` (numeric), `UKPN London Wind` (numeric), `WPD South Wales Wind` (numeric), `WPD South West Wind` (numeric), `SSE South Wind` (numeric), `UKPN South East Wind` (numeric), `Scottish Hydro Solar` (numeric), `Scottish Power Solar` (numeric), `Electricity North West Solar` (numeric), `NPG North East Solar` (numeric), `NPG Yorkshire Solar` (numeric), `SP Manweb Solar` (numeric), `WPD West Midlands Solar` (numeric), `WPD East Midlands Solar` (numeric), `UKPN East Anglia Solar` (numeric), `UKPN London Solar` (numeric), `WPD South Wales Solar` (numeric), `WPD South West Solar` (numeric), `SSE South Solar` (numeric), `UKPN South East Solar` (numeric), `Scottish Hydro Other` (numeric), `Scottish Power Other` (numeric), `Electricity North West Other` (numeric), `NPG North East Other` (numeric), `NPG Yorkshire Other` (numeric), `SP Manweb Other` (numeric), `WPD West Midlands Other` (numeric), `WPD East Midlands Other` (numeric), `UKPN East Anglia Other` (numeric), `UKPN London Other` (numeric), `WPD South Wales Other` (numeric), `WPD South West Other` (numeric), `SSE South Other` (numeric), `UKPN South East Other` (numeric)

- **Market Information Results 2021** (CSV via API, ~35,574 rows)
  Fields: `Unique ID` (text), `Contracted Unit ID` (text), `Applicant/Agent` (text), `Price (£/MW/hr)` (numeric), `Allocated Registered Service Volume (MW)` (numeric), `Technology type` (text), `Start time (BST)` (text), `Start date` (text), `Cease time (BST)` (text), `Cease Date` (text), `GSP` (text), `DNO` (text), `Accept/Reject` (text), `Reasons` (numeric), `Date` (timestamp)

- **Market Information Report for 10.05.20** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Requirements paper** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Market Information Report for 22.05.20** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Market Information Report for 23.05.20** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Market Information Report for 24.05.20** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Market Information Report - General Information** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Market Information Report for 05.07.20** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **ODFM Requirement - Summer 2021** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Phase 2 FFR (Firm Frequency Response) Auction Results Summary

`neso_data/ancillary-services/phase-2-ffr-auction-results-summary/` — 20 resource(s)

- **4 resources sharing this schema:** Phase 2 FFR Auction BlockOrders Masterdata 2019-2020, Phase 2 FFR Auction BlockOrders Masterdata 2020-2021, Phase 2 FFR Auction BlockOrders Masterdata 2021-2022, Phase 2: FFR Auction Block Order 26.11.2021 (CSV via API, ~86,041 rows combined)
  Fields: `MarketName` (text), `BiddingLevelName` (text), `MemberName` (text), `OrderID` (numeric), `Portfolio` (text), `OrderEntryTime` (timestamp), `OrderEntryUser` (text), `SettlementCurrency` (text), `ClearingPrice` (numeric), `Price` (numeric), `MAR` (numeric), `Status` (text), `BlockCode` (text), `BlockCodePRM` (text), `Paradoxically` (text), `OrderPeriodID` (numeric), `TradeID` (numeric), `EFA` (numeric), `DeliveryStart` (timestamp), `DeliveryEnd` (timestamp), `ExecutedVolume` (numeric), `Volume` (numeric), `Invalid` (text), `Bid Validity` (text)

- **4 resources sharing this schema:** Phase 2 FFR Auction LinearOrders Masterdata 2020-2021, Phase 2 FFR Auction LinearOrders Masterdata 2021-2022, Phase 2 FFR Auction LinearOrders Masterdata-2019-2020, Phase 2: FFR Auction Linear Orders 26.11.2021 (CSV via API, ~8,042 rows combined)
  Fields: `MarketName` (text), `BiddingLevelName` (text), `MemberName` (text), `OrderID` (numeric), `Portfolio` (text), `OrderEntryTime` (timestamp), `OrderEntryUser` (text), `SettlementCurrency` (text), `OrderPeriodID` (numeric), `TradeID` (numeric), `EFA` (numeric), `DeliveryStart` (timestamp), `DeliveryEnd` (timestamp), `ExecutedVolume` (numeric), `1P` (numeric), `1V` (numeric), `2P` (numeric), `2V` (numeric), `3P` (numeric), `3V` (numeric), `4P` (numeric), `4V` (numeric)

- **Phase 2 FFR Auction ResultsByUnit Masterdata-2019-2020** (CSV via API, ~9,985 rows)
  Fields: `Company` (text), `Unit Name` (text), `EFA Date` (timestamp), `Delivery Start` (timestamp), `Delivery End` (timestamp), `EFA` (numeric), `Service` (text), `Cleared Volume` (numeric), `Clearing Price` (numeric), `Cancelled` (text)

- **2 resources sharing this schema:** Phase 2 FFR Auction ResultSummary Masterdata 2021-2022, Phase 2 FFR Auction ResultSummary Masterdata-2019-2020 (CSV via API, ~4,368 rows combined)
  Fields: `Service` (text), `EFA Date` (timestamp), `Delivery Start` (timestamp), `Delivery End` (timestamp), `EFA` (numeric), `Cleared Volume` (numeric), `Clearing Price` (numeric)

- **Phase 2 FFR Auction ResultsByUnit Masterdata 2020-2021** (CSV via API, ~39,765 rows)
  Fields: `Company` (text), `Unit Name` (text), `EFA Date` (text), `Delivery Start` (timestamp), `Delivery End` (timestamp), `EFA` (text), `Service` (text), `Cleared Volume` (numeric), `Clearing Price` (numeric), `Cancelled` (text)

- **2 resources sharing this schema:** Phase 2 FFR Auction ResultSummary Masterdata 2020-2021, Phase 2: FFR Auction Results Summary 26.11.2021 (CSV via API, ~4,368 rows combined)
  Fields: `Service` (text), `EFA Date` (date), `Delivery Start` (timestamp), `Delivery End` (timestamp), `EFA` (numeric), `Cleared Volume` (numeric), `Clearing Price` (numeric)

- **2 resources sharing this schema:** Phase 2 FFR Auction ResultsByUnit Masterdata 2021-2022, Phase 2: FFR Auction Results by Unit 26.11.2021 (CSV via API, ~19,457 rows combined)
  Fields: `Company` (text), `Unit Name` (text), `EFA Date` (date), `Delivery Start` (timestamp), `Delivery End` (timestamp), `EFA` (numeric), `Service` (text), `Cleared Volume` (numeric), `Clearing Price` (numeric), `Cancelled` (text)

- **BlockOrders 2019-11-22 to 2019-11-29** (ZIP file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **LinearOrders 2019-11-22 to 2020-01-03** (ZIP file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **ResultByUnit 2019-11-22 to 2019-11-29** (ZIP file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **ResultSummary 2019-11-22 to 2019-11-29** (ZIP file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Quick Reserve Auction Requirement Forecast _(cadence hint from name: forecast series)_

`neso_data/ancillary-services/quick-reserve-auction-requirement-forecast/` — 1 resource(s)

- **Quick Reserve Auction Requirement Forecast** (CSV via API, ~1,872 rows)
  Fields: `Auction Date` (date), `Service Delivery Date` (date), `Service Window` (text), `Service window Start Time` (timestamp), `Service Window End Time` (timestamp), `Positive Quick Reserve Requirement MW` (int4), `Negative Quick Reserve Requirement MW` (int4), `Forecast produced on` (date)

### Short Term Operating Reserve STOR (Short Term Operating Reserve) Day Ahead Auction Results _(cadence hint from name: daily / day-ahead)_

`neso_data/ancillary-services/short-term-operating-reserve-stor-day-ahead-auction-results/` — 1 resource(s)

- **STOR DA Auction Results ** (CSV via API, ~121,480 rows)
  Fields: `Service Name` (text), `Tender Round ID` (text), `Buy Curve ID` (text), `Tender Submission ID` (text), `Service Delivery From` (timestamp), `Service Delivery To` (timestamp), `Unit ID` (text), `Company Name` (text), `BM/NBM` (text), `Fuel Type` (text), `Tendered MW` (numeric), `Minimum Acceptable MW` (numeric), `Contracted MW` (numeric), `Tendered Availability Price` (numeric), `Market Clearing Price` (numeric), `Status` (text)

### Short Term Operating Reserve STOR (Short Term Operating Reserve) Day Ahead Buy Curve _(cadence hint from name: daily / day-ahead)_

`neso_data/ancillary-services/short-term-operating-reserve-stor-day-ahead-buy-curve/` — 2 resource(s)

- **STOR DA Auction Buy Curve Report** (CSV via API, ~5,475 rows)
  Fields: `Buy Curve Name` (text), `Service Catalog` (text), `Curve to be applied to` (text), `Effective From Date` (timestamp), `Effective To Date` (timestamp), `Buy Curve Step: Buy Curve Step Id` (text), `MW` (int4), `Availability Price (£/MWh)` (numeric), `Buy Curve: Buy Curve ID` (text)

- **STOR Day Ahead Buy Curve Hash** (TXT file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Slow Reserve Requirement Forecast _(cadence hint from name: forecast series)_

`neso_data/ancillary-services/slow-reserve-requirement-forecast/` — 1 resource(s)

- **Slow Reserve Requirement Forecast** (CSV via API, ~1,872 rows)
  Fields: `Auction Date` (date), `Service Delivery Date` (date), `Service Window` (text), `Service Window Start Time` (timestamp), `Service Window End Time` (timestamp), `Positive Slow Reserve Requirement MW` (int4), `Negative Slow Reserve Requirement MW` (int4), `Forecast produced on` (date)

### Static Firm Frequency Response Auction Results

`neso_data/ancillary-services/static-firm-frequency-response-auction-results/` — 2 resource(s)

- **Static Firm Frequency Response Auction Buy Orders** (CSV via API, ~7,140 rows)
  Fields: `EFA Date` (date), `EFA` (int4), `25` (numeric), `50` (numeric), `75` (numeric), `100` (numeric), `125` (numeric), `150` (numeric), `175` (numeric), `200` (numeric), `225` (numeric), `250` (numeric)

- **Static Firm Frequency Response Auction Results** (CSV via API, ~209,613 rows)
  Fields: `Date` (date), `Provider` (text), `Unit` (text), `Delivery Start` (timestamp), `Delivery End` (timestamp), `EFA` (int4), `Service` (text), `Status` (text), `Volume` (numeric), `Accepted Volume` (numeric), `Price` (numeric), `Clearing Price` (numeric), `Technology Type` (text), `Location` (text), `Rank` (int4)

### Static Firm Frequency Response Requirement

`neso_data/ancillary-services/static-firm-frequency-response-requirement/` — 1 resource(s)

- **Static Firm Frequency Response Requirement** (CSV via API, ~39 rows)
  Fields: `EFA_DATE` (date), `Service` (text), `EFA1` (numeric), `EFA2` (numeric), `EFA3` (numeric), `EFA4` (numeric), `EFA5` (numeric), `EFA6` (numeric)

### STOR (Short Term Operating Reserve) Windows

`neso_data/ancillary-services/stor-windows/` — 1 resource(s)

- **STOR Windows** (CSV via API, ~1,826 rows)
  Fields: `Date` (date), `Season` (numeric), `WD/NWD` (text), `Window 1 Start Time` (text), `Window 1 End Time` (text), `Window 2 Start Time` (text), `Window 2 End Time` (text)


## Balancing

### Balancing Services Use Of System Bsuos Daily Forecast _(cadence hint from name: daily / day-ahead)_

`neso_data/balancing/balancing-services-use-of-system-bsuos-daily-forecast/` — 5 resource(s)

- **2 resources sharing this schema:** Daily BSUoS Forecast 2018-19, Daily BSUoS Forecast 2019-20 (CSV via API, ~24,374 rows combined)
  Fields: `Date` (text), `SP` (numeric), `BSUoS £/MWh` (numeric), `Half hourly cost £` (numeric), `Half hourly volume MWh` (numeric)

- **Daily BSUoS Forecast 2020-21** (CSV via API, ~30,622 rows)
  Fields: `Date` (timestamp), `SP` (numeric), `BSUoS £/MWh` (numeric), `Half hourly cost £` (numeric), `Half hourly volume MWh` (numeric)

- **2 resources sharing this schema:** Daily BSUoS Forecast 2021-22, Daily BSUoS Forecast 2022-23 (CSV via API, ~34,890 rows combined)
  Fields: `Date` (date), `SP` (numeric), `BSUoS £/MWh` (numeric), `Half hourly cost £` (numeric), `Half hourly volume MWh` (numeric)

### Bsuos Fixed Tariffs

`neso_data/balancing/bsuos-fixed-tariffs/` — 1 resource(s)

- ** Balancing Services Use of System Charges (BSUoS) Tariffs** (CSV via API, ~15 rows)
  Fields: `Publication` (text), `Fixed Tariff Title` (text), `Published Date` (date), `Fixed Tariff Start Date` (date), `Fixed Tariff End Date` (date), `Fixed Tariff £/MWh` (numeric)

### Bsuos Monthly Forecast _(cadence hint from name: monthly)_

`neso_data/balancing/bsuos-monthly-forecast/` — 141 resource(s)

- **38 resources sharing this schema** (e.g. BSUoS Forecast for May 2020 – Including new services, Impact on BSUoS due to COVID-19 low demands – Excluding new services, Monthly BSUOS Actual Summary February 2021, …) (CSV via API, ~1,008 rows combined)
  Fields: `Month` (text), `Energy Imbalance` (numeric), `Operating Reserve` (numeric), `STOR` (numeric), `Constraints - E&W` (numeric), `Constraints - Cheviot` (numeric), `Constraints - Scotland` (numeric), `Constraints - AS` (numeric), `Negative Reserve` (numeric), `Fast Reserve` (numeric), `Response` (numeric), `Other Reserve` (numeric), `Reactive` (numeric), `Minor Components` (numeric), `Black Start` (numeric), `Total` (numeric), `Demand` (numeric), `Estimated Internal BSUos(£m)` (numeric), `Esitmated NGET Profit/(Loss)` (numeric), `ALoMCP` (numeric)

- **22 resources sharing this schema** (e.g. Monthly BSUOS Forecast Summary August 10 Percent, Monthly BSUOS Forecast Summary August 15 Percent, Monthly BSUOS Forecast Summary August 5 Percent, …) (CSV via API, ~542 rows combined)
  Fields: `Month` (text), `Energy Imbalance (£m)` (numeric), `Operating Reserve (£m)` (numeric), `STOR (£m)` (numeric), `Constraints - E&W (£m)` (numeric), `Constraints - Cheviot (£m)` (numeric), `Constraints - Scotland (£m)` (numeric), `Constraints - AS (£m)` (numeric), `Negative Reserve (£m)` (numeric), `Fast Reserve (£m)` (numeric), `Response (£m)` (numeric), `Other Reserve (£m)` (numeric), `Reactive (£m)` (numeric), `Minor Components (£m)` (numeric), `Black Start (£m)` (numeric), `Total (£m)` (numeric), `Demand` (numeric), `Estimated Internal BSUos(£m)` (numeric), `Esitmated NGET Profit/(Loss)` (numeric), `Esitimated BSUoS Charge (£/MWh)` (numeric), `Constraints` (numeric), `ALoMCP` (numeric)

- **16 resources sharing this schema** (e.g. Monthly BSUoS Actual Summary August 2021, Monthly BSUoS Actual Summary December 2021, Monthly BSUoS Actual Summary July 2021, …) (CSV via API, ~384 rows combined)
  Fields: `Month` (text), `Energy Imbalance` (numeric), `Operating Reserve` (numeric), `STOR` (numeric), `Constraints - E&W` (numeric), `Constraints - Cheviot` (numeric), `Constraints - Scotland` (numeric), `Constraints - AS` (numeric), `Negative Reserve` (numeric), `Fast Reserve` (numeric), `Response` (numeric), `Other Reserve` (numeric), `Reactive` (numeric), `Minor Components` (numeric), `Black Start` (numeric), `Total` (numeric), `Demand` (numeric), `Estimated Internal BSUos(£m)` (numeric), `Esitmated NGET Profit/(Loss)` (numeric), `ALoMCP` (numeric), `CMP345/350 Deferred Costs` (numeric)

- **8 resources sharing this schema:** Monthly BSUoS Forecast Summary August 2021, Monthly BSUoS Forecast Summary December 2021, Monthly BSUoS Forecast Summary July 2021, Monthly BSUoS Forecast Summary June 2021, Monthly BSUoS Forecast Summary May 2021, Monthly BSUoS Forecast Summary November 2021, Monthly BSUoS Forecast Summary October 2021, Monthly BSUoS Forecast Summary September 2021 (CSV via API, ~194 rows combined)
  Fields: `Month` (text), `Energy Imbalance (£m)` (numeric), `Operating Reserve (£m)` (numeric), `STOR (£m)` (numeric), `Constraints - E&W (£m)` (numeric), `Constraints - Cheviot (£m)` (numeric), `Constraints - Scotland (£m)` (numeric), `Constraints - AS (£m)` (numeric), `Negative Reserve (£m)` (numeric), `Fast Reserve (£m)` (numeric), `Response (£m)` (numeric), `Other Reserve (£m)` (numeric), `Reactive (£m)` (numeric), `Minor Components (£m)` (numeric), `Black Start (£m)` (numeric), `Total (£m)` (numeric), `Demand` (numeric), `Estimated Internal BSUos(£m)` (numeric), `Esitmated NGET Profit/(Loss)` (numeric), `Esitimated BSUoS Charge (£/MWh)` (numeric), `Constraints` (numeric), `ALoMCP` (numeric), `CMP345/350 Deferred Costs` (numeric)

- **2 resources sharing this schema:** Monthly BSUoS Forecast Summary April 2022, Monthly BSUoS Forecast Summary February 2022 (CSV via API, ~50 rows combined)
  Fields: `Month` (text), `Energy_Imbalance_£m` (numeric), `Positive_Reserve_£m` (numeric), `Negative_Reserve_£m` (numeric), `Frequency_Control_£m` (numeric), `Other_£m` (numeric), `Constraints_£m` (numeric), `Restoration_£m` (numeric), `Balancing Costs (Central) £m` (numeric), `Estimated Internal BSUoS & ESO Incentive £m` (numeric), `BSUoS Cost Recovery £m` (numeric), `ALoMCP £m` (numeric), `CMP345/350 Deferred Costs £m` (numeric), `CMP381 Deferred Costs £m` (numeric), `Estimated BSUoS Volume (TWh)` (numeric)

- **Monthly BSUoS Forecast Summary March 2022** (CSV via API, ~25 rows)
  Fields: `Month` (text), `Energy_Imbalance_£m` (numeric), `Positive_Reserve_£m` (numeric), `Negative_Reserve_£m` (numeric), `Frequency_Control_£m` (numeric), `Other_£m` (numeric), `Constraints_£m` (numeric), `Balancing Costs (Central) £m` (numeric), `Estimated Internal BSUoS & ESO Incentive £m` (numeric), `BSUoS Cost Recovery £m` (numeric), `ALoMCP £m` (numeric), `CMP345/350 Deferred Costs £m` (numeric), `CMP381 Deferred Costs £m` (numeric), `Estimated BSUoS Volume (TWh)` (numeric)

- **5 resources sharing this schema:** Monthly BSUoS Forecast Summary August 2022, Monthly BSUoS Forecast Summary July 2022, Monthly BSUoS Forecast Summary June 2022, Monthly BSUoS Forecast Summary May 2022, Monthly BSUoS Forecast Summary September 2022 (CSV via API, ~121 rows combined)
  Fields: `Month` (text), `Energy_Imbalance_£m` (numeric), `Positive_Reserve_£m` (numeric), `Negative_Reserve_£m` (numeric), `Frequency_Control_£m` (numeric), `Other_£m` (numeric), `Constraints_£m` (numeric), `Restoration_£m` (numeric), `Balancing Costs (Central) £m` (numeric), `Estimated Internal BSUoS & ESO Incentive £m` (numeric), `ALoMCP £m` (numeric), `CMP381 Deferred Costs £m` (numeric), `Estimated BSUoS Volume (TWh)` (numeric)

- **Monthly BSUoS Forecast Summary September 2022 with Winter Contingency Cost** (CSV via API, ~24 rows)
  Fields: `Month` (text), `Energy_Imbalance_Â£m` (numeric), `Positive_Reserve_Â£m` (numeric), `Negative_Reserve_Â£m` (numeric), `Frequency_Control_Â£m` (numeric), `Other_Â£m` (numeric), `Constraints_Â£m` (numeric), `Restoration_Â£m` (numeric), `Balancing Costs (Central) Â£m` (numeric), `Estimated Internal BSUoS & ESO Incentive Â£m` (numeric), `ALoMCP Â£m` (numeric), `CMP381 Deferred Costs Â£m` (numeric), `Winter Contingency Cost (Central) £m` (numeric), `Estimated BSUoS Volume (TWh)` (numeric)

- **6 resources sharing this schema:** Monthly BSUoS Forecast Summary December 2022, Monthly BSUoS Forecast Summary February 2023, Monthly BSUoS Forecast Summary January 2023, Monthly BSUoS Forecast Summary March 2023, Monthly BSUoS Forecast Summary November 2022, Monthly BSUoS Forecast Summary October 2022 (CSV via API, ~144 rows combined)
  Fields: `Month` (text), `Energy_Imbalance_£m` (numeric), `Positive_Reserve_£m` (numeric), `Negative_Reserve_£m` (numeric), `Frequency_Control_£m` (numeric), `Other_£m` (numeric), `Constraints_£m` (numeric), `Restoration_£m` (numeric), `Balancing Costs (Central) £m` (numeric), `Estimated Internal BSUoS & ESO Incentive £m` (numeric), `ALoMCP £m` (numeric), `CMP381 Deferred Costs £m` (numeric), `Winter Contingency Cost (Central) £m` (numeric), `Estimated BSUoS Volume (TWh)` (numeric)

- **2 resources sharing this schema:** Monthly BSUoS Forecast Summary April 2023, Monthly BSUoS Forecast Summary May 2023 (CSV via API, ~48 rows combined)
  Fields: `Month` (text), `Energy_Imbalance_£m` (numeric), `Positive_Reserve_£m` (numeric), `Negative_Reserve_£m` (numeric), `Frequency_Control_£m` (numeric), `Other_£m` (numeric), `Constraints_£m` (numeric), `Restoration_£m` (numeric), `Balancing Costs (Central) £m` (numeric), `Estimated Internal BSUoS & ESO Incentive £m` (numeric), `ALoMCP £m` (numeric), `CMP381 Deferred Costs £m` (numeric), `Winter Contingency Cost (Central) £m` (numeric), `Winter Security of Supply Cost (£m)` (numeric), `Estimated BSUoS Volume (TWh)` (numeric)

- **Monthly BSUoS Forecast Summary June 2023** (CSV via API, ~24 rows)
  Fields: `Month` (text), `Energy_Imbalance_£m` (numeric), `Positive_Reserve_£m` (numeric), `Negative_Reserve_£m` (numeric), `Frequency_Control_£m` (numeric), `Other_£m` (numeric), `Constraints_£m` (numeric), `Restoration_£m` (numeric), `Balancing Costs (Central) £m` (numeric), `Estimated Internal BSUoS & ESO Incentive £m` (numeric), `ALoMCP £m` (int4), `CMP381 Deferred Costs £m` (int4), `Winter Contingency Cost (Central) £m` (int4), `Winter Security of Supply Cost (£m)` (numeric), `Estimated BSUoS Volume (TWh)` (numeric)

- **Monthly BSUoS Forecast Summary July 2023** (CSV via API, ~24 rows)
  Fields: `Month` (text), `Energy_Imbalance_£m` (numeric), `Positive_Reserve_£m` (numeric), `Negative_Reserve_£m` (numeric), `Frequency_Control_£m` (numeric), `Constraints_£m` (numeric), `Other_£m` (numeric), `Restoration_£m` (numeric), `Balancing Costs (Central) £m` (numeric), `Estimated Internal BSUoS & ESO Incentive £m` (numeric), `ALoMCP £m` (int4), `CMP381 Deferred Costs £m` (int4), `Winter Contingency Cost (Central) £m` (int4), `Winter Security of Supply Cost (£m)` (numeric), `Volume` (numeric)

- **6 resources sharing this schema:** Monthly BSUoS Forecast Summary August 2023, Monthly BSUoS Forecast Summary December 2023, Monthly BSUoS Forecast Summary January 2024, Monthly BSUoS Forecast Summary November 2023, Monthly BSUoS Forecast Summary October 2023, Monthly BSUoS Forecast Summary September 2023 (CSV via API, ~144 rows combined)
  Fields: `Month` (text), `Energy_Imbalance_£m` (numeric), `Positive_Reserve_£m` (numeric), `Negative_Reserve_£m` (numeric), `Frequency_Control_£m` (numeric), `Constraints_£m` (numeric), `Other_£m` (numeric), `Restoration_£m` (numeric), `Balancing Costs (Central) £m` (numeric), `Estimated Internal BSUoS & ESO Incentive £m` (numeric), `Winter Security of Supply Cost (£m)` (numeric), `Estimated BSUoS Volume (TWh)` (numeric)

- **3 resources sharing this schema:** Monthly BSUoS Forecast Summary February 2024, Monthly BSUoS Forecast Summary July 2024, Monthly BSUoS Forecast Summary June 2024 (CSV via API, ~72 rows combined)
  Fields: `Month` (text), `Energy_Imbalance_£m` (numeric), `Positive_Reserve_£m` (numeric), `Negative_Reserve_£m` (numeric), `Frequency_Control_£m` (numeric), `Constraints_£m` (numeric), `Other_£m` (numeric), `Restoration_£m` (numeric), `Balancing Costs (Central) £m` (numeric), `Estimated Internal BSUoS & ESO Incentive £m` (numeric), `Winter Security of Supply Cost (£m)` (numeric), `21/22 Under-Recovered Costs (£m)` (numeric), `Estimated BSUoS Volume (TWh)` (numeric)

- **3 resources sharing this schema:** Monthly BSUoS Forecast Summary April 2024, Monthly BSUoS Forecast Summary March 2024, Monthly BSUoS Forecast Summary May 2024 (CSV via API, ~73 rows combined)
  Fields: `Month` (text), `Energy_Imbalance_£m` (numeric), `Positive_Reserve_£m` (numeric), `Negative_Reserve_£m` (numeric), `Frequency_Control_£m` (numeric), `Constraints_£m` (numeric), `Other_£m` (numeric), `Restoration_£m` (numeric), `Balancing Costs (Central) £m` (numeric), `Estimated Internal BSUoS & ESO Incentive £m` (numeric), `Winter Security of Supply Cost (£m)` (text), `21/22 Under-Recovered Costs (£m)` (text), `Estimated BSUoS Volume (TWh)` (numeric)

- **5 resources sharing this schema:** Monthly BSUoS Forecast Summary - March 2026, Monthly BSUoS Forecast Summary August 2024, Monthly BSUoS Forecast Summary December 2024, Monthly BSUoS Forecast Summary March 2025, Monthly BSUoS Forecast Summary October 2024 (CSV via API, ~121 rows combined)
  Fields: `Month` (text), `Energy_Imbalance_£m` (numeric), `Positive_Reserve_£m` (numeric), `Negative_Reserve_£m` (numeric), `Frequency_Control_£m` (numeric), `Constraints_£m` (numeric), `Other_£m` (numeric), `Restoration_£m` (numeric), `Balancing Costs (Central) £m` (numeric), `Estimated Internal BSUoS & ESO Incentive £m` (numeric), `Winter Security of Supply Cost (£m)` (numeric), `21/22 Under-Recovered Costs (£m)` (numeric), `CMP398/412 Claim Costs (£m)` (numeric), `Interest Repayment (£m)` (numeric), `Additional NESO Framework Costs (£m)` (numeric), `Estimated BSUoS Volume (TWh)` (numeric)

- **2 resources sharing this schema:** Monthly BSUoS Forecast Summary November 2024, Monthly BSUoS Forecast Summary September 2024 (CSV via API, ~48 rows combined)
  Fields: `Month` (text), `Energy_Imbalance_£m` (numeric), `Positive_Reserve_£m` (numeric), `Negative_Reserve_£m` (numeric), `Frequency_Control_£m` (numeric), `Constraints_£m` (numeric), `Other_£m` (numeric), `Restoration_£m` (int4), `Balancing Costs (Central) £m` (numeric), `Estimated Internal BSUoS & ESO Incentive £m` (numeric), `Winter Security of Supply Cost (£m)` (numeric), `21/22 Under-Recovered Costs (£m)` (numeric), `CMP398/412 Claim Costs (£m)` (numeric), `Interest Repayment (£m)` (numeric), `Additional NESO Framework Costs (£m)` (numeric), `Estimated BSUoS Volume (TWh)` (numeric)

- **3 resources sharing this schema:** Monthly BSUoS Forecast Summary April 2025, Monthly BSUoS Forecast Summary February 2025, Monthly BSUoS Forecast Summary January 2025 (CSV via API, ~72 rows combined)
  Fields: `Month` (text), `Energy_Imbalance_£m` (numeric), `Positive_Reserve_£m` (numeric), `Negative_Reserve_£m` (numeric), `Frequency_Control_£m` (numeric), `Constraints_£m` (numeric), `Other_£m` (numeric), `Restoration_£m` (numeric), `Balancing Costs (Central) £m` (numeric), `Estimated Internal BSUoS & ESO Incentive £m` (numeric), `Winter Security of Supply Cost (£m)` (numeric), `21/22 Under-Recovered Costs (£m)` (numeric), `CMP398/412 Claim Costs (£m)` (numeric), `Interest Repayment (£m)` (int4), `Additional NESO Framework Costs (£m)` (int4), `Estimated BSUoS Volume (TWh)` (numeric)

- **8 resources sharing this schema:** Monthly BSUoS Forecast Summary August 2025, Monthly BSUoS Forecast Summary January 2026, Monthly BSUoS Forecast Summary July 2025, Monthly BSUoS Forecast Summary June 2025, Monthly BSUoS Forecast Summary May 2025, Monthly BSUoS Forecast Summary November 2025, Monthly BSUoS Forecast Summary October 2025, Monthly BSUoS Forecast Summary September 2025 (CSV via API, ~192 rows combined)
  Fields: `Month` (text), `Energy_Imbalance_£m` (numeric), `Positive_Reserve_£m` (numeric), `Negative_Reserve_£m` (numeric), `Frequency_Control_£m` (numeric), `Constraints_£m` (numeric), `Other_£m` (numeric), `Restoration_£m` (numeric), `Balancing Costs (Central) £m` (numeric), `Estimated Internal BSUoS & ESO Incentive £m` (numeric), `Winter Security of Supply Cost (£m)` (int4), `21/22 Under-Recovered Costs (£m)` (int4), `CMP398/412 Claim Costs (£m)` (numeric), `Interest Repayment (£m)` (int4), `Additional NESO Framework Costs (£m)` (int4), `Estimated BSUoS Volume (TWh)` (numeric)

- **Monthly BSUoS Forecast Summary December 2025** (CSV via API, ~24 rows)
  Fields: `Month` (text), `Energy_Imbalance_£m` (numeric), `Positive_Reserve_£m` (numeric), `Negative_Reserve_£m` (numeric), `Frequency_Control_£m` (numeric), `Constraints_£m` (numeric), `Other_£m` (numeric), `Restoration_£m` (int4), `Balancing Costs (Central) £m` (numeric), `Estimated Internal BSUoS & ESO Incentive £m` (numeric), `Winter Security of Supply Cost (£m)` (int4), `21/22 Under-Recovered Costs (£m)` (int4), `CMP398/412 Claim Costs (£m)` (numeric), `Interest Repayment (£m)` (int4), `Additional NESO Framework Costs (£m)` (int4), `Estimated BSUoS Volume (TWh)` (numeric)

- **5 resources sharing this schema:** Monthly BSUoS Forecast Summary - April 2026, Monthly BSUoS Forecast Summary - July 2026, Monthly BSUoS Forecast Summary - June 2026, Monthly BSUoS Forecast Summary - May 2026, Monthly BSUoS Forecast Summary February 2026 (CSV via API, ~120 rows combined)
  Fields: `Month` (text), `Energy_Imbalance_£m` (numeric), `Positive_Reserve_£m` (numeric), `Negative_Reserve_£m` (numeric), `Frequency_Control_£m` (numeric), `Constraints_£m` (numeric), `Other_£m` (numeric), `Restoration_£m` (numeric), `Balancing Costs (Central) £m` (numeric), `Estimated Internal BSUoS & ESO Incentive £m` (numeric), `Winter Security of Supply Cost (£m)` (int4), `21/22 Under-Recovered Costs (£m)` (int4), `CMP398/412 Claim Costs (£m)` (int4), `Interest Repayment (£m)` (int4), `Additional NESO Framework Costs (£m)` (int4), `Estimated BSUoS Volume (TWh)` (numeric)

- **BSUoS_Report_Jan 19 - Mar 20** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **BSUoS Forecasting Update Jan 2022 - Communications Pack** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Constraint Breakdown

`neso_data/balancing/constraint-breakdown/` — 10 resource(s)

- **3 resources sharing this schema:** Constraint Breakdown 2017-2018, Constraint Breakdown 2018-2019, Constraint Breakdown 2020-2021 (CSV via API, ~1,095 rows combined)
  Fields: `Date` (timestamp), `Reducing largest loss cost` (numeric), `Increasing system inertia cost` (numeric), `Voltage constraints cost` (numeric), `Thermal constraints cost` (numeric), `Reducing largest loss volume` (numeric), `Increasing system inertia volume` (numeric), `Voltage constraints volume` (numeric), `Thermal constraints volume` (numeric)

- **6 resources sharing this schema:** Constraint Breakdown 2019-2020, Constraint Breakdown 2021-2022, Constraint Breakdown 2022-2023, Constraint Breakdown 2023-2024, Constraint Breakdown 2024-2025, Constraint Breakdown 2026-2027 (CSV via API, ~1,912 rows combined)
  Fields: `Date` (date), `Reducing largest loss cost` (numeric), `Increasing system inertia cost` (numeric), `Voltage constraints cost` (numeric), `Thermal constraints cost` (numeric), `Reducing largest loss volume` (numeric), `Increasing system inertia volume` (numeric), `Voltage constraints volume` (numeric), `Thermal constraints volume` (numeric)

- **Constraint Breakdown 2025-2026** (CSV via API, ~364 rows)
  Fields: `Date` (date), `Reducing largest loss cost` (numeric), `Increasing system inertia cost` (numeric), `Voltage constraints cost` (numeric), `Thermal constraints cost` (text), `Reducing largest loss volume` (numeric), `Increasing system inertia volume` (numeric), `Voltage constraints volume` (numeric), `Thermal constraints volume` (numeric)

### Current Balancing Services Use Of System Bsuos Data

`neso_data/balancing/current-balancing-services-use-of-system-bsuos-data/` — 17 resource(s)

- **3 resources sharing this schema:** Historic II BSUoS Data, Historic RF BSUoS Data, Historic SF BSUoS Data (CSV via API, ~333,025 rows combined)
  Fields: `Settlement Day` (timestamp), `Settlement Period` (int4), `BSUoS Price (£/MWh Hour)` (numeric), `Half-hourly Charge` (numeric), `Total Daily BSUoS Charge` (numeric), `Run Type` (text)

- **Historic II BSUoS Data 2023-2024** (CSV via API, ~18,384 rows)
  Fields: `Settlement Day` (timestamp), `Settlement Period` (int4), `BSUoS Tariff (£/MWh)` (numeric), `BSUoS Fund Tariff (£/MWh)` (text), `Volume (MWh)` (numeric), `BSUoS Recovery (£)` (numeric), `BSUoS Fund Recovery (£)` (int4), `BSUoS Total Recovery (£)` (numeric), `Run Type` (text), `Actual BSUoS Cost(£)` (numeric)

- **2 resources sharing this schema:** Historic SF BSUoS Data 2023-2024, Historic SF BSUoS Data 2024-2025 (CSV via API, ~35,088 rows combined)
  Fields: `Settlement Day` (timestamp), `Settlement Period` (int4), `BSUoS Tariff (£/MWh)` (numeric), `BSUoS Fund Tariff (£/MWh)` (text), `Volume (MWh)` (numeric), `BSUoS Recovery (£)` (numeric), `BSUoS Fund Recovery (£)` (int4), `BSUoS Total Recovery ()` (numeric), `Run Type` (text), `Actual BSUoS Cost (£)` (numeric)

- **Current II BSUoS Data** (CSV via API, ~4,080 rows)
  Fields: `Settlement Day` (date), `Settlement Period` (int4), `BSUoS Tariff (£/MWh)` (numeric), `Volume (MWh)` (numeric), `BSUoS Recovery (£)` (numeric), `Run Type` (text), `Actual BSUoS Cost (£)` (numeric)

- **2 resources sharing this schema:** Current RF BSUoS Data, Current SF BSUoS Data (CSV via API, ~5,472 rows combined)
  Fields: `Settlement Date` (date), `Settlement Period` (int4), `BSUoS Tariff (£/MWh)` (numeric), `Volume (MWh)` (numeric), `BSUoS Total Recovery (£)` (numeric), `Run Type` (text), `Actual BSUoS Cost (£)` (numeric)

- **Historic II BSUoS Data 2024-2025** (CSV via API, ~624 rows)
  Fields: `Settlement Day` (timestamp), `Settlement Period` (int4), `BSUoS Tariff (£/MWh)` (numeric), `BSUoS Fund Tariff (£/MWh)` (text), `Volume (MWh)` (numeric), `BSUoS Recovery (£)` (numeric), `BSUoS Fund Recovery (£)` (int4), `BSUoS Total Recovery (£)` (numeric), `Run Type` (text), `Actual BSUoS Cost (£)` (numeric)

- **Historic RF BSUoS Data 2023-2024** (CSV via API, ~17,568 rows)
  Fields: `Settlement Day` (date), `Settlement Period` (int4), `BSUoS Tariff (£/MWh)` (numeric), `BSUoS Fund Tariff (£/MWh)` (numeric), `Volume (MWh)` (numeric), `BSUoS Recovery (£)` (numeric), `BSUoS Fund Recovery (£)` (numeric), `BSUoS Total Recovery ()` (numeric), `Run Type` (text), `Actual BSUoS Cost (£)` (numeric)

- **Historic II BSUoS Data 2025-2026** (CSV via API, ~17,520 rows)
  Fields: `Settlement Day` (date), `Settlement Period` (int4), `BSUoS Tariff (£/MWh)` (numeric), `BSUoS Fund Tariff (£/MWh)` (numeric), `Volume (MWh)` (numeric), `BSUoS Recovery (£)` (numeric), `BSUoS Fund Recovery (£)` (numeric), `BSUoS Total Recovery (£)` (numeric), `Run Type` (text), `Actual BSUoS Cost (£)` (numeric)

- **Historic SF BSUoS Data 2025-2026** (CSV via API, ~17,520 rows)
  Fields: `Settlement Day` (date), `Settlement Period` (numeric), `BSUoS Tariff (£/MWh)` (numeric), `BSUoS Fund Tariff (£/MWh)` (numeric), `Volume (MWh)` (numeric), `BSUoS Recovery (£)` (numeric), `BSUoS Fund Recovery (£)` (numeric), `BSUoS Total Recovery ()` (numeric), `Run Type` (text), `Actual BSUoS Cost (£)` (numeric)

- **CMP381 II BSUoS Data** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **CMP381 SF BSUoS Data** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **CMP395 II BSUoS Data** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **CMP395 SF BSUoS Data** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Daily Balancing Costs Balancing Services Use Of System _(cadence hint from name: daily / day-ahead)_

`neso_data/balancing/daily-balancing-costs-balancing-services-use-of-system/` — 11 resource(s)

- **3 resources sharing this schema:** Daily Balancing Costs 2017-2018, Daily Balancing Costs 2019-2020, Daily Balancing Costs 2020-2021 (CSV via API, ~52,588 rows combined)
  Fields: `SETT_DATE` (date), `SETT_PERIOD` (numeric), `Energy Imbalance` (numeric), `Frequency Control` (numeric), `Positive Reserve` (numeric), `Negative Reserve` (numeric), `Constraints` (numeric), `Other` (numeric)

- **7 resources sharing this schema:** Daily Balancing Costs 2018-2019, Daily Balancing Costs 2021-2022, Daily Balancing Costs 2022-2023, Daily Balancing Costs 2023-2024, Daily Balancing Costs 2024-2025, Daily Balancing Costs 2025-2026, Daily Balancing Costs 2026-2027 (CSV via API, ~109,247 rows combined)
  Fields: `SETT_DATE` (date), `SETT_PERIOD` (int4), `Energy Imbalance` (numeric), `Frequency Control` (numeric), `Positive Reserve` (numeric), `Constraints` (numeric), `Negative Reserve` (numeric), `Other` (numeric)

- **Missing Settlement Periods since January 2017** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Daily Balancing Volume Balancing Services Use Of System _(cadence hint from name: daily / day-ahead)_

`neso_data/balancing/daily-balancing-volume-balancing-services-use-of-system/` — 11 resource(s)

- **4 resources sharing this schema:** Daily Balancing Volume 2017-2018, Daily Balancing Volume 2019-2020, Daily Balancing Volume 2020-2021, Daily Balancing Volume 2022-2023 (CSV via API, ~70,107 rows combined)
  Fields: `SETT_DATE` (date), `SETT_PERIOD` (numeric), `Energy Imbalance (MWh)` (numeric), `Frequency Control Offers (MWh)` (numeric), `Frequency Control Bids (MWh)` (numeric), `Positive Reserve (MWh)` (numeric), `Constraint Offers (MWh)` (numeric), `Constraint Bids (MWh)` (numeric), `Negative Reserve (MWh)` (numeric), `Other (MWh)` (numeric)

- **6 resources sharing this schema:** Daily Balancing Volume 2018-2019, Daily Balancing Volume 2021-2022, Daily Balancing Volume 2023-2024, Daily Balancing Volume 2024-2025, Daily Balancing Volume 2025-2026, Daily Balancing Volume 2026-2027 (CSV via API, ~91,728 rows combined)
  Fields: `SETT_DATE` (date), `SETT_PERIOD` (int4), `Energy Imbalance (MWh)` (numeric), `Frequency Control Offers (MWh)` (numeric), `Frequency Control Bids (MWh)` (numeric), `Positive Reserve (MWh)` (numeric), `Constraint Offers (MWh)` (numeric), `Constraint Bids (MWh)` (numeric), `Negative Reserve (MWh)` (numeric), `Other (MWh)` (numeric)

- **Missing Settlement Periods since January 2017** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### GB System Inertia Bid And Offer Costs

`neso_data/balancing/gb-system-inertia-bid-and-offer-costs/` — 1 resource(s)

- **GB System Inertia Costs – combined bids and offers** (CSV via API, ~1,096 rows)
  Fields: `Date` (date), `Method A: Average bid price` (int4), `Method B: Average wind price` (int4), `Method C: Highest bid price` (int4)

### Skip Rates

`neso_data/balancing/skip-rates/` — 63 resource(s)

- **15 resources sharing this schema** (e.g. Skip Rate - In Merit All Balancing Mechanism - April 2025, Skip Rate - In Merit All Balancing Mechanism - December 2024, Skip Rate - In Merit All Balancing Mechanism - February 2025, …) (CSV via API, ~38,918,238 rows combined)
  Fields: `date` (timestamp), `bm_unit` (text), `fuel` (text), `bid_offer` (text), `stage` (int4), `available_volume_MWh` (numeric), `average_price_per_MWh` (numeric), `pair_id` (text), `accepted_volume_MWh` (numeric), `in_merit_volume_MWh` (numeric), `skipped_volume_MWh` (numeric)

- **25 resources sharing this schema** (e.g. In Merit PSA for Demand Side Flexibility Unit, Skip Rate - In Merit All Balancing Mechanism - April 2026, Skip Rate - In Merit All Balancing Mechanism - August 2025, …) (CSV via API, ~93,720,332 rows combined)
  Fields: `date` (timestamp), `bm_unit` (text), `fuel` (text), `bid_offer` (text), `stage` (int4), `available_volume_MWh` (numeric), `average_price_per_MWh` (numeric), `pair_id` (int4), `accepted_volume_MWh` (numeric), `in_merit_volume_MWh` (numeric), `skipped_volume_MWh` (numeric)

- **9 resources sharing this schema** (e.g. Skip Rate - Exclusion Reasons - April 2025, Skip Rate - Exclusion Reasons - August 2025, Skip Rate - Exclusion Reasons - December 2024, …) (CSV via API, ~4,901,503 rows combined)
  Fields: `date` (timestamp), `bm_unit` (text), `fuel` (text), `bid_offer` (text), `excluded_from_accepted_or_feasible_merit_stack` (text), `exclusion_stage` (int4), `pair_id` (text), `average_price_per_MWh` (numeric), `excluded_volume_MWh` (numeric), `exclusion_reason` (text)

- **Stage 5 PSA Skip Rate by Technology** (CSV via API, ~112,921 rows)
  Fields: `settlement_period_start` (timestamp), `bid_offer` (text), `fuel` (text), `relative_technology_skip_rate` (numeric), `technology_specific_skip_rate` (numeric), `fuel_in_merit_volume_MWh` (numeric), `fuel_skipped_volume_MWh` (numeric)

- **10 resources sharing this schema** (e.g. Skip Rate - Exclusion Reasons - April 2026, Skip Rate - Exclusion Reasons - December 2025, Skip Rate - Exclusion Reasons - February 2026, …) (CSV via API, ~7,580,237 rows combined)
  Fields: `date` (timestamp), `bm_unit` (text), `fuel` (text), `bid_offer` (text), `excluded_from_accepted_or_feasible_merit_stack` (text), `exclusion_stage` (int4), `pair_id` (int4), `average_price_per_MWh` (numeric), `excluded_volume_MWh` (numeric), `exclusion_reason` (text)

- **Skip Rate - Stage 6 Acceptance** (CSV via API, ~2,909,408 rows)
  Fields: `date` (timestamp), `stage` (int4), `bm_unit` (text), `fuel` (text), `bid_offer` (text), `pair_id` (int4), `average_price_per_MWh` (numeric), `accepted_volume_MWh` (numeric)

- **Skip Rate - Summary** (CSV via API, ~162,720 rows)
  Fields: `settlement_period_start` (timestamp), `stage` (int4), `bm_skip_rate_offers_percent` (numeric), `bm_total_volume_skipped_offers_MWh` (numeric), `post_system_action_skip_rate_offers_percent` (numeric), `post_system_action_total_volume_skipped_offers_MWh` (numeric), `bm_skip_rate_bids_percent` (numeric), `bm_total_volume_skipped_bids_MWh` (numeric), `post_system_action_skip_rate_bids_percent` (numeric), `post_system_action_total_volume_skipped_bids_MWh` (numeric)

- **Stage 5 DSF Technology-Specific Skip Rate** (CSV via API, ~5,483 rows)
  Fields: `settlement_period_start` (timestamp), `bm_unit` (text), `bid_offer` (text), `fuel` (text), `in_merit_volume_MWh` (numeric), `skipped_volume_MWh` (numeric), `technology_specific_skip_rate` (numeric)


## Carbon Intensity

### Carbon Intensity Of Balancing Actions

`neso_data/carbon-intensity1/carbon-intensity-of-balancing-actions/` — 2 resource(s)

- **Carbon Intensity of Balancing Actions** (CSV via API, ~91,555 rows)
  Fields: `DATETIME` (timestamp), `FPN` (numeric), `BOA` (numeric), `Difference` (numeric)

- **Carbon Intensity Balancing Actions Methodology** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Country Carbon Intensity Forecast _(cadence hint from name: forecast series)_

`neso_data/carbon-intensity1/country-carbon-intensity-forecast/` — 1 resource(s)

- **Country Carbon Intensity Forecast** (CSV via API, ~136,367 rows)
  Fields: `datetime` (timestamp), `Scotland` (numeric), `England` (numeric), `Wales` (numeric)

### Historic Generation Mix _(cadence hint from name: static/historical reference)_

`neso_data/carbon-intensity1/historic-generation-mix/` — 1 resource(s)

- **Historic GB Generation Mix** (CSV via API, ~306,847 rows)
  Fields: `DATETIME` (timestamp), `GAS` (numeric), `COAL` (numeric), `NUCLEAR` (numeric), `WIND` (numeric), `WIND_EMB` (numeric), `HYDRO` (numeric), `IMPORTS` (numeric), `BIOMASS` (numeric), `OTHER` (numeric), `SOLAR` (numeric), `STORAGE` (numeric), `GENERATION` (numeric), `CARBON_INTENSITY` (numeric), `LOW_CARBON` (numeric), `ZERO_CARBON` (numeric), `RENEWABLE` (numeric), `FOSSIL` (numeric), `GAS_perc` (numeric), `COAL_perc` (numeric), `NUCLEAR_perc` (numeric), `WIND_perc` (numeric), `WIND_EMB_perc` (numeric), `HYDRO_perc` (numeric), `IMPORTS_perc` (numeric), `BIOMASS_perc` (numeric), `OTHER_perc` (numeric), `SOLAR_perc` (numeric), `STORAGE_perc` (numeric), `GENERATION_perc` (numeric), `LOW_CARBON_perc` (numeric), `ZERO_CARBON_perc` (numeric), `RENEWABLE_perc` (numeric), `FOSSIL_perc` (numeric)

### National Carbon Intensity Forecast _(cadence hint from name: forecast series)_

`neso_data/carbon-intensity1/national-carbon-intensity-forecast/` — 2 resource(s)

- **National Carbon Intensity Forecast** (CSV via API, ~150,513 rows)
  Fields: `datetime` (timestamp), `forecast` (numeric), `actual` (numeric), `index` (text)

- **National Carbon Intensity Forecast Methodology** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Regional Carbon Intensity Forecast _(cadence hint from name: forecast series)_

`neso_data/carbon-intensity1/regional-carbon-intensity-forecast/` — 2 resource(s)

- **Regional Carbon Intensity Forecast** (CSV via API, ~135,291 rows)
  Fields: `datetime` (timestamp), `North Scotland` (numeric), `South Scotland` (numeric), `North West England` (numeric), `North East England` (numeric), `Yorkshire` (numeric), `North Wales and Merseyside` (numeric), `South Wales` (numeric), `West Midlands` (numeric), `East Midlands` (numeric), `East England` (numeric), `South West England` (numeric), `South England` (numeric), `London` (numeric), `South East England` (numeric)

- **Regional Carbon Intensity Forecast Methodology** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)


## Connection Registers

### Embedded Register _(cadence hint from name: static/historical reference)_

`neso_data/connection-registers/embedded-register/` — 1 resource(s)

- **Embedded Register** (CSV via API, ~561 rows)
  Fields: `Project Name` (text), `Customer Name` (text), `Connection Site` (text), `Stage` (int4), `MW Connected` (numeric), `MW Increase / Decrease` (numeric), `Cumulative Total Capacity (MW)` (numeric), `MW Effective From` (date), `Project Status` (text), `HOST TO` (text), `Plant Type` (text), `Project ID` (text), `Project Number` (text), `Gate` (numeric)

### Interconnector Register _(cadence hint from name: static/historical reference)_

`neso_data/connection-registers/interconnector-register/` — 1 resource(s)

- **Interconnector Register** (CSV via API, ~33 rows)
  Fields: `Project Name` (text), `Customer Name` (text), `Connection Site` (text), `Stage` (numeric), `MW Import - Current` (numeric), `MW Export - Current` (numeric), `MW Import - Increase / Decrease` (numeric), `MW Export - Increase / Decrease` (numeric), `MW Import - Total` (numeric), `MW Export - Total` (numeric), `MW Effective From` (date), `Project Status` (text), `HOST TO` (text), `Project Number` (text), `Gate` (numeric)

### Transmission Entry Capacity TEC (Transmission Entry Capacity) Register _(cadence hint from name: static/historical reference)_

`neso_data/connection-registers/transmission-entry-capacity-tec-register/` — 1 resource(s)

- **TEC Register** (CSV via API, ~2,215 rows)
  Fields: `Project Name` (text), `Customer Name` (text), `Connection Site` (text), `Stage` (numeric), `MW Connected` (numeric), `MW Increase / Decrease` (numeric), `Cumulative Total Capacity (MW)` (numeric), `MW Effective From` (date), `Project Status` (text), `Agreement Type` (text), `HOST TO` (text), `Plant Type` (text), `Project ID` (text), `Project Number` (text), `Gate` (numeric)


## Constraint Management

### 24 Months Ahead Constraint Cost Forecast _(cadence hint from name: long-range (year+ ahead))_

`neso_data/constraint-management/24-months-ahead-constraint-cost-forecast/` — 1 resource(s)

- **24 Months Ahead Constraint Cost Forecast** (CSV via API, ~24 rows)
  Fields: `Month` (text), `Constraint Cost (£m)` (numeric)

### 24 Months Ahead Constraint Limits _(cadence hint from name: long-range (year+ ahead))_

`neso_data/constraint-management/24-months-ahead-constraint-limits/` — 3 resource(s)

- **24 Months ahead constraint limits ** (CSV via API, ~108 rows)
  Fields: `YEAR` (int4), `Week No` (numeric), `DRESHEX1` (int4), `ESTEX` (int4), `FLOWSTH` (int4), `GM+ SNOW5A` (int4), `HARSPNBLY` (int4), `NKILGRMO` (int4), `SCOTEX` (int4), `SEIMPPR2` (int4), `SSE+GRM` (int4), `SSEN-S` (int4), `SSE-SP2` (int4), `SSHARN3` (int4)

- **Scotland network constraint diagram** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **E&W network constraint diagram** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Constraint Management Intertrip Service Information CMIS (Constraint Management Intertrip Service)

`neso_data/constraint-management/constraint-management-intertrip-service-information-cmis/` — 5 resource(s)

- **2 resources sharing this schema:** Constraint Management Intertrip Arming 2022-2023, Constraint Management Intertrip Arming 2023-2024 (CSV via API, ~551 rows combined)
  Fields: `BMU ID` (text), `Arming Date Time` (timestamp), `Disarming Date Time` (timestamp), `Current Arming Fee (£ / SP)` (numeric), `Cost for this utilisation (£)` (numeric)

- **3 resources sharing this schema:** Constraint Management Intertrip Arming 2024-2025, Constraint Management Intertrip Arming 2025-2026, Constraint Management Intertrip Arming 2026-2027 (CSV via API, ~425 rows combined)
  Fields: `BMU ID` (text), `Arming Date Time` (timestamp), `Disarming Date Time` (timestamp), `Current Arming Fee (£ / MWH)` (numeric), `Cost for this utilisation (£)` (numeric), `B6/EC5` (text)

### Day Ahead Constraint Flows And Limits _(cadence hint from name: daily / day-ahead)_

`neso_data/constraint-management/day-ahead-constraint-flows-and-limits/` — 3 resource(s)

- **Day Ahead Constraint Flows and Limits** (CSV via API, ~648,906 rows)
  Fields: `Constraint Group` (text), `Date (GMT/BST)` (timestamp), `Limit (MW)` (int4), `Flow (MW)` (numeric)

- **Network Diagram England & Wales** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Network Diagram Scotland** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Operational Transparency Forum Network Congestion Data

`neso_data/constraint-management/operational-transparency-forum-network-congestion-data/` — 1 resource(s)

- **Network congestion Forecast and Actual data** (CSV via API, ~53 rows)
  Fields: `DATE` (date), `Min of B4 B5 - Actual` (numeric), `B6- Actual` (numeric), `B6a - Actual` (numeric), `B7 - Actual` (numeric), `GMSNOW - Actual` (numeric), `LE1 - Actual` (numeric), `B9 - Actual` (numeric), `DRESHEX - Actual` (numeric), `EC5 - Actual` (numeric), `B15 -Actual` (numeric), `SC -Actual` (numeric), `Min of B4 B5 - Forecast` (numeric), `B6- Forecast` (numeric), `B6a - Forecast` (numeric), `B7 - Forecast` (numeric), `GMSNOW - Forecast` (numeric), `LE1 - Forecast` (numeric), `B9 - Forecast` (numeric), `DRESHEX - Forecast` (numeric), `EC5 - Forecast` (numeric), `B15 -Forecast` (numeric), `SC -Forecast` (numeric)

### Outturn Voltage Costs

`neso_data/constraint-management/outturn-voltage-costs/` — 13 resource(s)

- **10 resources sharing this schema** (e.g. Historical Outturn Voltage Costs 2014-2015, Historical Outturn Voltage Costs 2015-2016, Historical Outturn Voltage Costs 2016-2017, …) (CSV via API, ~2,090 rows combined)
  Fields: `Settlement Month` (text), `Voltage Constraint Group` (text), `Sync Costs (£m)` (numeric), `Utilisation Costs (£m)` (numeric), `Coordinates` (text)

- **2 resources sharing this schema:** Historical Outturn Voltage Costs 2019-2020, Historical Outturn Voltage Costs 2020-2021 (CSV via API, ~456 rows combined)
  Fields: `Settlement Month` (date), `Voltage Constraint Group` (text), `Sync Costs (£m)` (numeric), `Utilisation Costs (£m)` (numeric), `Coordinates` (text)

- **Network Diagram** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Thermal Constraint Costs

`neso_data/constraint-management/thermal-constraint-costs/` — 11 resource(s)

- **Thermal Constraint Costs Data 21-22** (CSV via API, ~2,190 rows)
  Fields: `Settlement Date` (date), `Constraint Group` (text), `Daily Cost (GBP)` (text)

- **5 resources sharing this schema:** Thermal Constraint Costs Data 22-23, Thermal Constraint Costs Data 23-24, Thermal Constraint Costs Data 24-25, Thermal Constraint Costs Data 25-26, Thermal Constraint Costs Data 26-27 (CSV via API, ~9,270 rows combined)
  Fields: `Settlement Date` (date), `Constraint Group` (text), `Daily Cost (GBP)` (int4)

- **Thermal Constraint Costs 19-20** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Thermal Constraint Costs 20-21** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Network Diagram England & Wales** (PNG file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Network Diagram Scotland** (PNG file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Constraint Map** (PNG file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Voltage Requirement

`neso_data/constraint-management/voltage-requirement/` — 4 resource(s)

- **Week Ahead Overnight Voltage Requirement 20-26** (CSV via API, ~4,987 rows)
  Fields: `Start Date` (date), `End Date` (date), `Group` (text), `Units` (int4), `Notes` (text), `Last Updated` (timestamp)

- **Voltage Deep Dive** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Introduction to voltage management** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Week ahead overnight voltage requirement group map** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Year Ahead Constraint Limits _(cadence hint from name: long-range (year+ ahead))_

`neso_data/constraint-management/year-ahead-constraint-limits/` — 1 resource(s)

- **Year Ahead Constraint Limits** (CSV via API, ~53 rows)
  Fields: `Week` (timestamp), `B6 - SCOTEX` (numeric), `B6 import - HARETORIM` (numeric), `B5 - SSE+GRM` (numeric), `B2 - SSEN-S` (numeric), `B4 - SSE-SP2` (numeric), `B5 - NKILGRMO` (numeric), `SW1 - SWALEX` (numeric), `LE1 - SEIMPPR2` (numeric), `no equivalent - HUMBEREX` (numeric), `B15 - ESTEX` (numeric), `B7 - SSHARN3` (numeric)


## Demand

### 1 Day Ahead Demand Forecast _(cadence hint from name: daily / day-ahead)_

`neso_data/demand/1-day-ahead-demand-forecast/` — 3 resource(s)

- **Day Ahead National Demand Forecast** (CSV via API, ~11 rows)
  Fields: `DAYSAHEAD` (int4), `TARGETDATE` (int4), `FORECASTDEMAND` (int4), `CARDINALPOINT` (text), `CP_TYPE` (text), `CP_ST_TIME` (numeric), `CP_END_TIME` (int4), `F_Point` (text)

- **Historic Day Ahead Demand Forecasts** (CSV via API, ~57,456 rows)
  Fields: `DAYSAHEAD` (int4), `TARGETDATE` (date), `FORECASTDEMAND` (int4), `CARDINALPOINT` (text), `CP_TYPE` (text), `CP_ST_TIME` (numeric), `CP_END_TIME` (numeric), `F_Point` (text), `FORECAST_TIMESTAMP` (timestamp)

- **Demand Curve - Sample** (PNG file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### 2 14 Days Ahead National Demand Forecast _(cadence hint from name: every 2–14 days ahead)_

`neso_data/demand/2-14-days-ahead-national-demand-forecast/` — 3 resource(s)

- **Historic 2-14 Day Ahead Demand Forecasts** (CSV via API, ~358,782 rows)
  Fields: `DAYSAHEAD` (int4), `TARGETDATE` (date), `FORECASTDEMAND` (int4), `CARDINALPOINT` (text), `CP_TYPE` (text), `CP_ST_TIME` (int4), `CP_END_TIME` (int4), `F_Point` (text), `FORECAST_TIMESTAMP` (text)

- **2-14 Days Ahead Cardinal Point Forecast** (CSV via API, ~121 rows)
  Fields: `DAYSAHEAD` (int4), `TARGETDATE` (date), `FORECASTDEMAND` (int4), `CARDINALPOINT` (text), `CP_TYPE` (text), `CP_ST_TIME` (int4), `CP_END_TIME` (int4), `F_Point` (text)

- **2-14 Days Ahead Half Hourly Forecast** (CSV via API, ~624 rows)
  Fields: `DATE` (date), `CTIME` (int4), `GDATETIME` (timestamp), `NATIONALDEMAND` (int4)

### 2 Day Ahead Demand Forecast _(cadence hint from name: daily / day-ahead)_

`neso_data/demand/2-day-ahead-demand-forecast/` — 3 resource(s)

- **2 Day Ahead Demand Forecast** (CSV via API, ~11 rows)
  Fields: `DAYSAHEAD` (int4), `TARGETDATE` (date), `FORECASTDEMAND` (int4), `CARDINALPOINT` (text), `CP_TYPE` (text), `CP_ST_TIME` (int4), `CP_END_TIME` (int4), `F_Point` (text)

- **Historic 2 Day Ahead Demand Forecasts** (CSV via API, ~0 rows)
  Fields: `DAYSAHEAD` (int4), `TARGETDATE` (date), `FORECASTDEMAND` (int4), `CARDINALPOINT` (text), `CP_TYPE` (text), `CP_ST_TIME` (text), `CP_END_TIME` (text), `F_Point` (text), `FORECAST_TIMESTAMP` (timestamp)

- **Demand Curve - Sample** (PNG file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### 7 Day Ahead National Forecast _(cadence hint from name: daily / day-ahead)_

`neso_data/demand/7-day-ahead-national-forecast/` — 3 resource(s)

- **7 Day Ahead Demand Forecast** (CSV via API, ~11 rows)
  Fields: `DAYSAHEAD` (numeric), `TARGETDATE` (int4), `FORECASTDEMAND` (int4), `CARDINALPOINT` (text), `CP_TYPE` (text), `CP_ST_TIME` (int4), `CP_END_TIME` (text), `F_Point` (text)

- **Historic 7 Day Ahead Demand Forecasts** (CSV via API, ~807 rows)
  Fields: `DAYSAHEAD` (int4), `TARGETDATE` (date), `FORECASTDEMAND` (int4), `CARDINALPOINT` (text), `CP_TYPE` (text), `CP_ST_TIME` (int4), `CP_END_TIME` (int4), `F_Point` (text), `FORECAST_TIMESTAMP` (timestamp)

- **Demand Curve - Sample** (PNG file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Daily Demand Update _(cadence hint from name: daily / day-ahead)_

`neso_data/demand/daily-demand-update/` — 2 resource(s)

- **Demand Data Update** (CSV via API, ~1,920 rows)
  Fields: `SETTLEMENT_DATE` (date), `SETTLEMENT_PERIOD` (int4), `ND` (int4), `FORECAST_ACTUAL_INDICATOR` (text), `TSD` (int4), `ENGLAND_WALES_DEMAND` (int4), `EMBEDDED_WIND_GENERATION` (int4), `EMBEDDED_WIND_CAPACITY` (int4), `EMBEDDED_SOLAR_GENERATION` (int4), `EMBEDDED_SOLAR_CAPACITY` (int4), `NON_BM_STOR` (int4), `PUMP_STORAGE_PUMPING` (int4), `SCOTTISH_TRANSFER` (int4), `IFA_FLOW` (int4), `IFA2_FLOW` (int4), `BRITNED_FLOW` (int4), `MOYLE_FLOW` (int4), `EAST_WEST_FLOW` (int4), `NEMO_FLOW` (int4), `NSL_FLOW` (int4), `ELECLINK_FLOW` (int4), `VIKING_FLOW` (int4), `GREENLINK_FLOW` (int4)

- **Frequently Asked Questions (FAQ)** (DOC file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Day Ahead Half Hourly Demand Forecast Performance _(cadence hint from name: half-hourly)_

`neso_data/demand/day-ahead-half-hourly-demand-forecast-performance/` — 1 resource(s)

- **Day Ahead Half Hourly Demand Forecast Performance** (CSV via API, ~92,130 rows)
  Fields: `Month` (text), `Date` (date), `Datetime` (timestamp), `Settlement_Period` (int4), `Demand_Forecast` (int4), `Demand_Outturn` (int4), `TRIAD_Avoidance_Estimate` (int4), `TRIAD_Avoidance_Corrected_Demand_Outturn` (int4), `APE` (numeric), `Absolute_Error` (int4), `Publish_Datetime` (timestamp)

### Demand Profile Dates

`neso_data/demand/demand-profile-dates/` — 1 resource(s)

- **Demand Profile Dates** (CSV via API, ~3,125 rows)
  Fields: `FORECAST_DATE` (date), `PROFILE_DATE` (date)

### Historic Demand Data _(cadence hint from name: static/historical reference)_

`neso_data/demand/historic-demand-data/` — 27 resource(s)

- **9 resources sharing this schema** (e.g. Historic Demand Data 2009, Historic Demand Data 2010, Historic Demand Data 2011, …) (CSV via API, ~157,728 rows combined)
  Fields: `SETTLEMENT_DATE` (date), `SETTLEMENT_PERIOD` (int4), `ND` (int4), `TSD` (int4), `ENGLAND_WALES_DEMAND` (int4), `EMBEDDED_WIND_GENERATION` (int4), `EMBEDDED_WIND_CAPACITY` (int4), `EMBEDDED_SOLAR_GENERATION` (int4), `EMBEDDED_SOLAR_CAPACITY` (int4), `NON_BM_STOR` (int4), `PUMP_STORAGE_PUMPING` (int4), `IFA_FLOW` (int4), `IFA2_FLOW` (int4), `BRITNED_FLOW` (int4), `MOYLE_FLOW` (int4), `EAST_WEST_FLOW` (int4), `NEMO_FLOW` (int4)

- **Historic Demand Data 2016** (CSV via API, ~17,568 rows)
  Fields: `SETTLEMENT_DATE` (date), `SETTLEMENT_PERIOD` (int4), `ND` (int4), `TSD` (int4), `ENGLAND_WALES_DEMAND` (int4), `EMBEDDED_WIND_GENERATION` (int4), `EMBEDDED_WIND_CAPACITY` (int4), `EMBEDDED_SOLAR_GENERATION` (int4), `EMBEDDED_SOLAR_CAPACITY` (text), `NON_BM_STOR` (int4), `PUMP_STORAGE_PUMPING` (int4), `IFA_FLOW` (int4), `IFA2_FLOW` (int4), `BRITNED_FLOW` (int4), `MOYLE_FLOW` (int4), `EAST_WEST_FLOW` (int4), `NEMO_FLOW` (int4)

- **4 resources sharing this schema:** Historic Demand Data 2019, Historic Demand Data 2020, Historic Demand Data 2021, Historic Demand Data 2022 (CSV via API, ~70,128 rows combined)
  Fields: `SETTLEMENT_DATE` (text), `SETTLEMENT_PERIOD` (int4), `ND` (int4), `TSD` (int4), `ENGLAND_WALES_DEMAND` (int4), `EMBEDDED_WIND_GENERATION` (int4), `EMBEDDED_WIND_CAPACITY` (int4), `EMBEDDED_SOLAR_GENERATION` (int4), `EMBEDDED_SOLAR_CAPACITY` (int4), `NON_BM_STOR` (int4), `PUMP_STORAGE_PUMPING` (int4), `IFA_FLOW` (int4), `IFA2_FLOW` (int4), `BRITNED_FLOW` (int4), `MOYLE_FLOW` (int4), `EAST_WEST_FLOW` (int4), `NEMO_FLOW` (int4), `NSL_FLOW` (int4), `ELECLINK_FLOW` (int4), `VIKING_FLOW` (int4), `GREENLINK_FLOW` (int4)

- **Historic Demand Data 2023** (CSV via API, ~17,520 rows)
  Fields: `SETTLEMENT_DATE` (text), `SETTLEMENT_PERIOD` (int4), `ND` (int4), `TSD` (int4), `ENGLAND_WALES_DEMAND` (int4), `EMBEDDED_WIND_GENERATION` (int4), `EMBEDDED_WIND_CAPACITY` (int4), `EMBEDDED_SOLAR_GENERATION` (int4), `EMBEDDED_SOLAR_CAPACITY` (int4), `NON_BM_STOR` (int4), `PUMP_STORAGE_PUMPING` (int4), `SCOTTISH_TRANSFER` (int4), `IFA_FLOW` (int4), `IFA2_FLOW` (int4), `BRITNED_FLOW` (int4), `MOYLE_FLOW` (int4), `EAST_WEST_FLOW` (int4), `NEMO_FLOW` (int4), `NSL_FLOW` (int4), `ELECLINK_FLOW` (int4), `VIKING_FLOW` (int4), `GREENLINK_FLOW` (int4)

- **2 resources sharing this schema:** Historic Demand Data 2024, Historic Demand Data 2025 (CSV via API, ~35,088 rows combined)
  Fields: `SETTLEMENT_DATE` (date), `SETTLEMENT_PERIOD` (int4), `ND` (int4), `TSD` (int4), `ENGLAND_WALES_DEMAND` (int4), `EMBEDDED_WIND_GENERATION` (int4), `EMBEDDED_WIND_CAPACITY` (int4), `EMBEDDED_SOLAR_GENERATION` (int4), `EMBEDDED_SOLAR_CAPACITY` (int4), `NON_BM_STOR` (int4), `PUMP_STORAGE_PUMPING` (int4), `SCOTTISH_TRANSFER` (int4), `IFA_FLOW` (int4), `IFA2_FLOW` (int4), `BRITNED_FLOW` (int4), `MOYLE_FLOW` (int4), `EAST_WEST_FLOW` (int4), `NEMO_FLOW` (int4), `NSL_FLOW` (int4), `ELECLINK_FLOW` (int4), `VIKING_FLOW` (int4), `GREENLINK_FLOW` (int4)

- **4 resources sharing this schema:** Historic Demand Data 2001, Historic Demand Data 2002, Historic Demand Data 2003, Historic Demand Data 2004 (CSV via API, ~70,128 rows combined)
  Fields: `SETTLEMENT_DATE` (date), `SETTLEMENT_PERIOD` (int4), `ND` (int4), `TSD` (text), `ENGLAND_WALES_DEMAND` (int4), `EMBEDDED_WIND_GENERATION` (text), `EMBEDDED_WIND_CAPACITY` (text), `EMBEDDED_SOLAR_GENERATION` (text), `EMBEDDED_SOLAR_CAPACITY` (text), `NON_BM_STOR` (int4), `PUMP_STORAGE_PUMPING` (int4), `SCOTTISH_TRANSFER` (text), `IFA_FLOW` (int4), `IFA2_FLOW` (text), `BRITNED_FLOW` (text), `MOYLE_FLOW` (text), `EAST_WEST_FLOW` (text), `NEMO_FLOW` (text), `NSL_FLOW` (text), `ELECLINK_FLOW` (text), `VIKING_FLOW` (text), `GREENLINK_FLOW` (text)

- **2 resources sharing this schema:** Historic Demand Data 2005, Historic Demand Data 2006 (CSV via API, ~35,040 rows combined)
  Fields: `SETTLEMENT_DATE` (date), `SETTLEMENT_PERIOD` (int4), `ND` (int4), `TSD` (int4), `ENGLAND_WALES_DEMAND` (int4), `EMBEDDED_WIND_GENERATION` (text), `EMBEDDED_WIND_CAPACITY` (text), `EMBEDDED_SOLAR_GENERATION` (text), `EMBEDDED_SOLAR_CAPACITY` (text), `NON_BM_STOR` (int4), `PUMP_STORAGE_PUMPING` (int4), `SCOTTISH_TRANSFER` (text), `IFA_FLOW` (int4), `IFA2_FLOW` (text), `BRITNED_FLOW` (text), `MOYLE_FLOW` (int4), `EAST_WEST_FLOW` (text), `NEMO_FLOW` (text), `NSL_FLOW` (text), `ELECLINK_FLOW` (text), `VIKING_FLOW` (text), `GREENLINK_FLOW` (text)

- **2 resources sharing this schema:** Historic Demand Data 2007, Historic Demand Data 2008 (CSV via API, ~35,088 rows combined)
  Fields: `SETTLEMENT_DATE` (date), `SETTLEMENT_PERIOD` (int4), `ND` (int4), `TSD` (int4), `ENGLAND_WALES_DEMAND` (int4), `EMBEDDED_WIND_GENERATION` (int4), `EMBEDDED_WIND_CAPACITY` (int4), `EMBEDDED_SOLAR_GENERATION` (text), `EMBEDDED_SOLAR_CAPACITY` (text), `NON_BM_STOR` (int4), `PUMP_STORAGE_PUMPING` (int4), `SCOTTISH_TRANSFER` (text), `IFA_FLOW` (int4), `IFA2_FLOW` (text), `BRITNED_FLOW` (text), `MOYLE_FLOW` (int4), `EAST_WEST_FLOW` (text), `NEMO_FLOW` (text), `NSL_FLOW` (text), `ELECLINK_FLOW` (text), `VIKING_FLOW` (text), `GREENLINK_FLOW` (text)

- **Historic Demand Data 2026** (CSV via API, ~7,796 rows)
  Fields: `SETTLEMENT_DATE` (date), `SETTLEMENT_PERIOD` (int4), `ND` (int4), `FORECAST_ACTUAL_INDICATOR` (text), `TSD` (int4), `ENGLAND_WALES_DEMAND` (int4), `EMBEDDED_WIND_GENERATION` (int4), `EMBEDDED_WIND_CAPACITY` (int4), `EMBEDDED_SOLAR_GENERATION` (int4), `EMBEDDED_SOLAR_CAPACITY` (int4), `NON_BM_STOR` (int4), `PUMP_STORAGE_PUMPING` (int4), `SCOTTISH_TRANSFER` (int4), `IFA_FLOW` (int4), `IFA2_FLOW` (int4), `BRITNED_FLOW` (int4), `MOYLE_FLOW` (int4), `EAST_WEST_FLOW` (int4), `NEMO_FLOW` (int4), `NSL_FLOW` (int4), `ELECLINK_FLOW` (int4), `VIKING_FLOW` (int4), `GREENLINK_FLOW` (int4)

- **Frequently Asked Questions (FAQ)** (DOC file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Long Term 2 52 Weeks Ahead National Demand Forecast _(cadence hint from name: forecast series)_

`neso_data/demand/long-term-2-52-weeks-ahead-national-demand-forecast/` — 1 resource(s)

- **Long term demand forecast** (CSV via API, ~67 rows)
  Fields: `calendar_year` (int4), `financial_year` (int4), `ESIWK` (int4), `CDATE_peak` (date), `tsd_peak` (int4), `tsd_min` (int4), `day_min` (int4), `night_min` (int4)

### National Demand Balancing Mechanism Units

`neso_data/demand/national-demand-balancing-mechanism-units/` — 1 resource(s)

- **National Demand Balancing Mechanism Units** (CSV via API, ~894 rows)
  Fields: `BM_Name` (text)

### School Holiday Percentages

`neso_data/demand/school-holiday-percentages/` — 6 resource(s)

- **School Holiday Percentages 2024/25** (CSV via API, ~71,829 rows)
  Fields: `Local_Authority` (text), `Multiplier` (text), `Date` (date), `School_Holiday` (numeric)

- **5 resources sharing this schema:** School Holiday Percentages 2021/22, School Holiday Percentages 2022/23, School Holiday Percentages 2023/24, School Holiday Percentages 2025/26, School Holiday Percentages 2026/27 (CSV via API, ~363,104 rows combined)
  Fields: `Local_Authority` (text), `Multiplier` (numeric), `Date` (date), `School_Holiday` (numeric)

### Transmission Losses

`neso_data/demand/transmission-losses/` — 2 resource(s)

- **Transmission Losses** (CSV via API, ~158 rows)
  Fields: `Financial Year` (text), `Month` (text), `NGET` (numeric), `SPT` (numeric), `SHETL` (numeric), `GB totals` (numeric)

- **Financial Year Losses** (CSV via API, ~13 rows)
  Fields: `Financial Year` (text), `Sum of NGET` (numeric), `Sum of SPT` (numeric), `Sum of SHETL` (numeric), `Sum of GB totals` (numeric)

### Tresp Demand Pathways

`neso_data/demand/tresp-demand-pathways/` — 8 resource(s)

- **tRESP Demand Pathways per Grid Supply Point Area** (CSV via API, ~160,776 rows)
  Fields: `Building_block_id` (text), `tRESP_GSP_area` (text), `Pathway` (text), `Year` (int4), `Value` (numeric), `Unit` (text), `DNO_licence_area` (text)

- **tRESP Demand Pathways per RESP Nation and Region** (CSV via API, ~7,656 rows)
  Fields: `Building_block_id` (text), `RESP_region` (text), `Pathway` (text), `Year` (int4), `Value` (numeric), `Unit` (text)

- **3 resources sharing this schema:** tRESP Indicative Demand Pathways per Local Authority for England, tRESP Indicative Demand Pathways per Local Authority for Scotland, tRESP Indicative Demand Pathways per Local Authority for Wales (CSV via API, ~243,600 rows combined)
  Fields: `Building_block_id` (text), `LAD24CD` (text), `LAD24NM` (text), `Pathway` (text), `Year` (int4), `Unit` (text), `Value` (numeric)

- **tRESP Grid Supply Point (GSP) Areas** (GPKG file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **RESP Nations and Regions Areas** (GPKG file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Lists of tRESP Pathways Building Blocks and of tRESP GSP areas with names** (XLSX file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)


## Demand Flexibility Service (DFS)

### Demand Flexibility

`neso_data/dfs/demand-flexibility/` — 7 resource(s)

- **DFS Service Requirement (Archive 2025/2026)** (CSV via API, ~1,132 rows)
  Fields: `Delivery Date` (date), `From` (text), `To` (text), `Service Requirement MW` (int4), `Service Requirement Type` (text), `Guaranteed Acceptance Price GBP per MWh` (numeric), `Dispatch Type` (text), `Participant Bids Eligible` (text)

- **DFS Industry Notification (Archive 2025/2026)** (CSV via API, ~191 rows)
  Fields: `Notification Issued Date` (date), `Notification Issued Time` (text), `Requirement For` (date), `Requirement Type` (text), `Status` (text), `Notification Type` (text)

- **DFS Utilisation Report (Archive 2025/2026)** (CSV via API, ~9,950 rows)
  Fields: `Delivery Date` (date), `Registered DFS Participant` (text), `DFS Unit ID` (text), `DFS Volume MW` (numeric), `From` (text), `To` (text), `Service Requirement Type` (text), `Utilisation Price GBP per MWh` (numeric), `Status` (text), `North Scotland` (numeric), `South and Central Scotland` (numeric), `North East England` (numeric), `North West England` (numeric), `Yorkshire` (numeric), `East Midlands` (numeric), `West Midlands` (numeric), `London` (numeric), `East England` (numeric), `South East England` (numeric), `South West England` (numeric), `Southern England` (numeric), `North Wales Merseyside and Cheshire` (numeric), `South Wales` (numeric), `Other` (numeric), `Total` (numeric)

- **DFS Utilisation Report Summary (Archive 2025/2026)** (CSV via API, ~1,130 rows)
  Fields: `Delivery Date` (date), `From` (text), `To` (text), `Service Requirement Type` (text), `Service Requirement MW` (numeric), `DFS Procured MW` (numeric), `DFS Provider Bids Accepted Total Cost GBP` (numeric), `Settled Volume MW` (numeric), `Settled Cost GBP` (numeric)

- **DFS Service Requirement** (CSV via API, ~548 rows)
  Fields: `Event ID` (numeric), `DFS Submission Time (Local)` (text), `Event Type` (text), `Event Tag` (text), `Delivery Date` (date), `From_Local` (text), `To_Local` (text), `From_UTC` (text), `To_UTC` (text), `Service Requirement MW` (int4), `Service Requirement Type` (text), `Guaranteed Acceptance Price GBP per MWh` (numeric), `Dispatch Type` (text), `Participant Bids Eligible` (text), `Zonal Cap` (text)

- **DFS Utilisation Report Summary** (CSV via API, ~548 rows)
  Fields: `Event ID` (numeric), `Event Type` (text), `Event Tag` (text), `Delivery Date` (date), `From_Local` (text), `To_Local` (text), `From_UTC` (text), `To_UTC` (text), `Service Requirement Type` (text), `Service Requirement MW` (numeric), `DFS Procured MW` (numeric), `DFS Provider Bids Accepted Total Cost GBP` (numeric), `Settled Volume MW` (numeric), `Settled Cost GBP` (numeric)

- **DFS Utilisation Report** (CSV via API, ~3,236 rows)
  Fields: `Event ID` (numeric), `Event Type` (text), `Event Tag` (text), `Delivery Date` (date), `From_Local` (text), `To_Local` (text), `From_UTC` (text), `To_UTC` (text), `Registered DFS Participant` (text), `DFS Unit ID` (text), `Zone` (numeric), `DFS Procured MW` (numeric), `Service Requirement Type` (text), `Utilisation Price GBP per MWh` (numeric), `Status` (text)

### Demand Flexibility Service

`neso_data/dfs/demand-flexibility-service/` — 4 resource(s)

- **DFS Industry Notification** (CSV via API, ~30 rows)
  Fields: `Notification Issued Date` (date), `Notification Issued Time` (time), `Requirement For` (date), `Requirement Type` (text), `Status` (text), `Notification Type` (text)

- **DFS Service Requirements** (CSV via API, ~32 rows)
  Fields: `Delivery Date` (date), `From` (time), `To` (time), `DFS Required MW` (int4), `Service Requirement Type` (text), `Guaranteed Acceptance Price GBP per MWh` (numeric), `Despatch Type` (text), `Participant Bids Eligible` (text)

- **DFS Utilisation Report** (CSV via API, ~1,220 rows)
  Fields: `Delivery Date` (date), `Registered DFS Participant` (text), `DFS Unit ID` (text), `DFS Volume MW` (numeric), `From` (text), `To` (text), `Service Requirement Type` (text), `Despatch Time` (text), `Utilisation Price GBP per MWh` (int4), `Status` (text), `North Scotland` (numeric), `South and Central Scotland` (numeric), `North East England` (numeric), `North West England` (numeric), `Yorkshire` (numeric), `East Midlands` (numeric), `West Midlands` (numeric), `London` (numeric), `East England` (numeric), `South East England` (numeric), `South West England` (numeric), `Southern England` (numeric), `North Wales, Merseyside and Cheshire` (numeric), `South Wales` (numeric), `Other` (numeric), `Total` (numeric)

- **DFS Utilisation Report Summary** (CSV via API, ~32 rows)
  Fields: `Delivery Date` (date), `From` (time), `To` (time), `Service Requirement Type` (text), `DFS Required MW` (numeric), `DFS Procured MW` (numeric), `DFS Provider Bids Accepted Total Cost GBP` (numeric), `Settled Volume MW` (numeric), `Settled Cost GBP` (numeric)

### Demand Flexibility Service Live Events

`neso_data/dfs/demand-flexibility-service-live-events/` — 4 resource(s)

- **DFS Service Requirement - LIVE** (CSV via API, ~5 rows)
  Fields: `Delivery Date` (date), `From GMT` (text), `To GMT` (text), `DFS Required MW` (int4)

- **Service Update Industry Notifications - LIVE** (CSV via API, ~7 rows)
  Fields: `Date` (date), `Status` (text), `Type` (text), `Time` (text)

- **DFS Utilisation Report - LIVE** (CSV via API, ~170 rows)
  Fields: `Date` (date), `DFS Provider` (text), `Unit` (text), `DFS Volume (MW)` (numeric), `From (GMT)` (text), `To (GMT)` (text), `Price (£/MWh)` (int4), `Status` (text), `North Scotland` (numeric), `South and Central Scotland` (numeric), `North East England` (numeric), `North West England` (numeric), `Yorkshire` (numeric), `East Midlands` (numeric), `West Midlands` (numeric), `London` (numeric), `East England` (numeric), `South East England` (numeric), `South West England` (numeric), `Southern England` (numeric), `North Wales, Merseyside and Cheshire` (numeric), `South Wales` (numeric), `Other` (numeric), `Total` (numeric), `D0 North Scotland` (numeric), `D0 South and Central Scotland` (numeric), `D0 North East England` (numeric), `D0 North West England` (numeric), `D0 Yorkshire` (numeric), `D0 East Midlands` (numeric), `D0 West Midlands` (numeric), `D0 London` (numeric), `D0 East England` (numeric), `D0 South East England` (numeric), `D0 South West England` (numeric), `D0 Southern England` (numeric), `D0 North Wales Merseyside and Cheshire` (numeric), `D0 South Wales` (numeric), `D0 Other` (numeric), `D0 Total` (numeric)

- **Utilisation Report Summary - LIVE** (CSV via API, ~5 rows)
  Fields: `Date` (date), `From (GMT)` (time), `To (GMT)` (time), `DFS Required (MW)` (numeric), `DFS Procured (MW)` (numeric), `DFS Provider Bids Accepted Total Cost (£)` (numeric), `D0 DFS Procured (MW)` (numeric), `D0 DFS Provider Bids Accepted Total Cost (£)` (numeric), `Settled Volume` (numeric), `Settled Cost` (numeric)

### Demand Flexibility Service Test Events

`neso_data/dfs/demand-flexibility-service-test-events/` — 4 resource(s)

- **DFS Service Requirement - TEST** (CSV via API, ~40 rows)
  Fields: `Delivery Date` (date), `From GMT` (text), `To GMT` (text), `DFS Required MW` (numeric)

- **Service Update Industry Notifications - TEST** (CSV via API, ~40 rows)
  Fields: `Date` (date), `Status` (text), `Type` (text), `Time` (time)

- **DFS Utilisation Report - TEST** (CSV via API, ~739 rows)
  Fields: `Date` (date), `DFS Provider` (text), `Unit` (text), `DFS Volume (MW)` (numeric), `From (GMT)` (text), `To (GMT)` (text), `Price (£/MWh)` (numeric), `Status` (text), `North Scotland` (numeric), `South and Central Scotland` (numeric), `North East England` (numeric), `North West England` (numeric), `Yorkshire` (numeric), `East Midlands` (numeric), `West Midlands` (numeric), `London` (numeric), `East England` (numeric), `South East England` (numeric), `South West England` (numeric), `Southern England` (numeric), `North Wales, Merseyside and Cheshire` (numeric), `South Wales` (numeric), `Other` (numeric), `Total` (numeric), `D0 North Scotland` (numeric), `D0 South and Central Scotland` (numeric), `D0 North East England` (numeric), `D0 North West England` (numeric), `D0 Yorkshire` (numeric), `D0 East Midlands` (numeric), `D0 West Midlands` (numeric), `D0 London` (numeric), `D0 East England` (numeric), `D0 South East England` (numeric), `D0 South West England` (numeric), `D0 Southern England` (numeric), `D0 North Wales Merseyside and Cheshire` (numeric), `D0 South Wales` (numeric), `D0 Other` (numeric), `D0 Total` (numeric)

- **Utilisation Report Summary - TEST** (CSV via API, ~40 rows)
  Fields: `Date` (date), `From (GMT)` (time), `To (GMT)` (time), `DFS Required (MW)` (numeric), `DFS Procured (MW)` (numeric), `DFS Provider Bids Accepted Total Cost (£)` (numeric), `D0 DFS Procured (MW)` (numeric), `D0 DFS Provider Bids Accepted Total Cost (£)` (numeric), `Settled Volume` (numeric), `Settled Cost` (numeric)


## Electricity Market Reform

### Capacity Market Register _(cadence hint from name: static/historical reference)_

`neso_data/electricity-market-reform/capacity-market-register/` — 7 resource(s)

- **Components** (CSV via API, ~1,833,096 rows)
  Fields: `Auction Name` (text), `Application ID` (text), `CMU ID` (text), `Delivery Year` (int4), `Component ID` (text), `Type` (text), `Generating Technology Class` (text), `Permitted on-Site Generating Unit` (text), `Primary Fuel of Component` (text), `Connection / DSR Capacity` (numeric), `De-Rated Capacity` (numeric), `Pre-Refurbishing De-Rated Capacity` (numeric), `Post-Refurbishing De-Rated Capacity` (numeric), `Generating Capacity of on-site Generating Unit` (numeric), `Description of CMU Components` (text), `Location and Post Code` (text), `OS Grid Reference` (text)

- **Capacity Market Unit (CMU)** (CSV via API, ~18,034 rows)
  Fields: `Auction Name` (text), `Application ID` (text), `CMU ID` (text), `Type` (text), `Auction` (text), `Delivery Year` (int4), `Name of Applicant` (text), `Agent Name` (text), `CM Unit Name` (text), `Parent Company` (text), `Secondary Trading Contact - Telephone` (text), `Secondary Trading Contact - Email` (text), `Transmission / Distribution` (text), `CM Unit Type` (text), `CM Unit Category` (text), `Primary Fuel Type` (text), `CMU Technology` (text), `Storage Facility` (text), `Pre-Qualification Decision` (text), `Opt Out Status` (text), `Opt-Out Reason` (text), `Maximum Obligation Period` (int4), `Unproven DSR` (text), `New Build Yet to Satisfy FCM` (text), `Connection Agreement Deferral Declaration` (text), `TEC Deferral` (text), `Amount of Credit Cover` (numeric), `Planning Consents Conditions` (text), `Connection / DSR Capacity` (numeric), `Proven DSR Capacity` (numeric), `DSR Bidding Capacity` (numeric), `De-Rated Capacity` (numeric), `Pre-Refurbishing De-Rated Capacity` (numeric), `Post-Refurbishing De-Rated Capacity` (numeric), `Pre-Refurbishing CMU Status` (text), `Anticipated De-Rated Capacity` (numeric), `Anticipated Pre-Refurbishing De-Rated Capacity` (numeric), `Anticipated Post-Refurbishing De-Rated Capacity` (numeric), `Date of Issue of DSR Test Certificate` (date), `DSR Test Method` (text), `CMU confirmed entry into Auction` (text), `Duration of Capacity Agreement in First Bidding Round` (int4), `Pre-Refurbishment Bidding Status` (text), `Capacity Agreement Awarded` (text), `Duration of Capacity Agreement Awarded` (int4), `Unique Agreement Identifier` (text), `Registered Holder` (text), `Date of Issue of Capacity Agreement` (date), `Term of the Capacity Agreement` (int4), `Delivery Years for which Agreement Valid` (text), `Auction Acquired Capacity Obligation` (numeric), `Is FCM required` (text), `Date for Financial Commitment Milestone` (date), `Is Connection Agreement required` (text), `Date for provision of deferred Connection Agreement` (date), `Subject to a Minimum Completion Requirement` (text), `Subject to Substantial Completion Milestone` (text), `Long-Stop Date for the Minimum Completion Requirement` (date), `Earliest Date SCM is expected to be achieved` (date), `Latest Date SCM is expected to be achieved` (date), `Is copy of Grid Connection Agreement required` (text), `Date for provision of deferred TEC` (date), `Termination Fee 1 Rate` (text), `Termination Fee 2 Rate` (text), `Termination Fee 3 Rate` (text), `Termination Fee 4 Rate` (text), `Termination Fee 5 Rate` (text), `Annual Penalty Cap` (text), `Monthly Penalty Cap` (text), `Legal Name of any Person with a Security Interest` (text), `Nature of the Security Interest` (text), `Capacity Agreement has been Terminated` (text), `Date of Termination of Capacity Agreement` (date), `List of Traded Capacity Obligations` (text), `Period for which the transfer applies` (text), `Capacity obligation Summary` (text), `Beta Value` (text), `Has Capacity Agreement been Suspended` (text)

- **Component History** (CSV via API, ~1,863,356 rows)
  Fields: `Auction Name` (text), `Application ID` (text), `CMU ID` (text), `Component ID` (text), `Type` (text), `Delivery Year` (int4), `Attribute` (text), `Previous` (text), `Latest` (text), `Change Type` (text), `Change Date` (date)

- **Capacity Market Unit (CMU) History** (CSV via API, ~57,178 rows)
  Fields: `Auction Name` (text), `Application ID` (text), `CMU ID` (text), `Type` (text), `Delivery Year` (int4), `Attribute` (text), `Previous` (text), `Latest` (text), `Change Type` (text), `Change Date` (date)

- **Capacity Market Auction Capacity and Cost** (CSV via API, ~192 rows)
  Fields: `Auction Name` (text), `Delivery Year` (text), `Capacity Awarded` (numeric), `Forecast Cost (£)` (numeric)

- **Capacity Market De-Rating Factors** (CSV via API, ~801 rows)
  Fields: `Auction Name` (text), `Primary Fuel Type` (text), `Generating Technology Class` (text), `De-Rating Factor` (numeric)

- **Capacity Market Auction Static Data** (CSV via API, ~25 rows)
  Fields: `Auction Name` (text), `Clearing Price (£kW/year)` (numeric), `Base Period for the Agreement` (text), `Total Volume of Agreements Awarded` (numeric), `Termination Fee 1 Rate` (text), `Termination Fee 2 Rate` (text), `Termination Fee 3 Rate` (text), `Termination Fee 4 Rate` (text), `Termination Fee 5 Rate` (text), `Annual Penalty Cap` (text), `Monthly Penalty Cap` (text)


## Future Energy Scenarios (FES)

### FES (Future Energy Scenarios) Electricity Demand Summary Data Table Ed1

`neso_data/future-energy-scenarios/fes-electricity-demand-summary-data-table-ed1/` — 6 resource(s)

- **Electricity Demand Summary (ED1) 2023** (CSV via API, ~530 rows)
  Fields: `Aggregation Level` (numeric), `Data item` (text), `Unit` (text), `Scenario` (text), `Fuel` (text), `Peak/ Annual/ Minimum` (text), `2010` (numeric), `2011` (numeric), `2012` (numeric), `2013` (numeric), `2014` (numeric), `2015` (numeric), `2016` (numeric), `2017` (numeric), `2018` (numeric), `2019` (numeric), `2020` (numeric), `2021` (numeric), `2022` (numeric), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

- **Electricity Demand Summary (ED1) 2024** (CSV via API, ~525 rows)
  Fields: `Aggregation Level` (numeric), `Data item` (text), `Unit` (text), `Pathway` (text), `Fuel` (text), `Peak/ Annual/ Minimum` (text), `2020` (text), `2021` (numeric), `2022` (numeric), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

- **Electricity Demand Summary (ED1) 2025** (CSV via API, ~250 rows)
  Fields: `Aggregation Level` (numeric), `Data item` (text), `Unit` (text), `Pathway` (text), `Fuel` (text), `Peak/ Annual/ Minimum` (text), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

- **Electricity Demand Definitions Data table (ED2) 2023 - Version 2** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Electricity Demand Definitions Data table (ED2) 2024** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- ** Electricity Demand Definitions Data table (ED2) 2025** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### FES (Future Energy Scenarios) European Electricity Supply Data Table Es2

`neso_data/future-energy-scenarios/fes-european-electricity-supply-data-table-es2/` — 3 resource(s)

- **European Electricity Supply Data Table (ES2) 2023** (CSV via API, ~793 rows)
  Fields: `Country` (text), `EU Scenario` (text), `FES Scenario Alignment` (text), `Variable` (text), `Category` (text), `Type` (text), `SubType` (text), `SubSubType` (text), `2022` (numeric), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

- **European Electricity Supply Data Table (ES2) 2024** (CSV via API, ~880 rows)
  Fields: `Country` (text), `EU Scenario` (text), `FES Pathway Alignment` (text), `Variable` (text), `Category` (text), `Type` (text), `SubType` (text), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

- ** European Electricity Supply Data Table (ES2) 2025** (CSV via API, ~753 rows)
  Fields: `Country` (text), `EU Scenario` (text), `FES Pathway Alignment` (text), `Variable` (text), `Category` (text), `Type` (text), `SubType` (text), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

### FES (Future Energy Scenarios) Flexibility Data Table Data Table Flx1

`neso_data/future-energy-scenarios/fes-flexibility-data-table-data-table-flx1/` — 3 resource(s)

- **Flexibility data table (FLX1) 2023** (CSV via API, ~185 rows)
  Fields: `Flexibility type` (text), `Flexibility sub-type` (text), `Data item` (text), `Unit` (text), `Scenario` (text), `Fuel` (text), `Detail` (text), `2021` (numeric), `2022` (numeric), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

- **Flexibility data table (FLX1) 2024** (CSV via API, ~185 rows)
  Fields: `Flexibility type` (text), `Flexibility sub-type` (text), `Data item` (text), `Unit` (text), `Pathway` (text), `Fuel` (text), `Detail` (text), `2021` (numeric), `2022` (numeric), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

- **Flexibility data table (FLX1) 2025** (CSV via API, ~180 rows)
  Fields: `Flexibility type` (text), `Flexibility sub-type` (text), `Data item` (text), `Unit` (text), `Pathway` (text), `Fuel` (text), `Detail` (text), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

### FES (Future Energy Scenarios) Natural Gas Demand Definitions Ed4

`neso_data/future-energy-scenarios/fes-natural-gas-demand-definitions-ed4/` — 3 resource(s)

- **Natural Gas demand definitions (ED4) 2023** (CSV via API, ~10 rows)
  Fields: `Item no.` (numeric), `Description` (text), `Definition` (text)

- **2 resources sharing this schema:** Natural Gas demand definitions (ED4) 2024, Natural Gas demand definitions (ED4) 2025 (CSV via API, ~21 rows combined)
  Fields: `Item no.` (int4), `Description` (text), `Definition` (text)

### FES (Future Energy Scenarios) Natural Gas Residential And Non Domestic I C Heat Demand Summary Data Table Ed3

`neso_data/future-energy-scenarios/fes-natural-gas-residential-and-non-domestic-i-c-heat-demand-summary-data-table-ed3/` — 4 resource(s)

- **Natural Gas and Residential Heat Demand Summary (ED3) 2023** (CSV via API, ~960 rows)
  Fields: `Scenario` (text), `Sector` (text), `Fuel` (text), `Technology` (text), `Time` (text), `Units` (text), `2020` (numeric), `2021` (numeric), `2022` (numeric), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

- **Natural Gas and Residential Heat Demand Summary (ED3) 2024** (CSV via API, ~1,223 rows)
  Fields: `Pathway` (text), `Sector/Aggregation Level` (text), `Fuel` (text), `Technology` (text), `Data Type` (text), `Units` (text), `2020` (numeric), `2021` (numeric), `2022` (numeric), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

- **Heat Demand Summary (ED7) 2025** (CSV via API, ~1,297 rows)
  Fields: `Pathway` (text), `Sector/Aggregation Level` (text), `Fuel` (text), `Technology` (text), `Data Type` (text), `Units` (text), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

- ** Natural Gas Demand Summary (ED3) 2025** (CSV via API, ~55 rows)
  Fields: `Pathway` (text), `Description` (text), `Fuel` (text), `Component` (text), `Data Type` (text), `Units` (text), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

### FES (Future Energy Scenarios) Road Transport Notes Data Table Ed6

`neso_data/future-energy-scenarios/fes-road-transport-notes-data-table-ed6/` — 3 resource(s)

- **3 resources sharing this schema:** Road Transport Notes (ED6) 2023, Road Transport Notes (ED6) 2024, Road Transport Notes (ED6) 2025 (CSV via API, ~89 rows combined)
  Fields: `Column` (text), `Category` (text), `Description` (text)

### FES (Future Energy Scenarios) Road Transport Summary Data Table Ed5

`neso_data/future-energy-scenarios/fes-road-transport-summary-data-table-ed5/` — 3 resource(s)

- **Road Transport Summary (ED5) 2023** (CSV via API, ~315 rows)
  Fields: `Data item` (text), `Unit` (text), `Scenario` (text), `Fuel` (text), `Peak/Annual/Minimum` (text), `2017` (numeric), `2018` (numeric), `2019` (numeric), `2020` (numeric), `2021` (numeric), `2022` (numeric), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

- **Road Transport Summary (ED5) 2024** (CSV via API, ~315 rows)
  Fields: `Data item` (text), `Unit` (text), `Pathway` (text), `Fuel` (text), `Peak/Annual/Minimum` (text), `2020` (numeric), `2021` (numeric), `2022` (numeric), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

- **Road Transport Summary (ED5) 2025** (CSV via API, ~315 rows)
  Fields: `Data item` (text), `Unit` (text), `Pathway` (text), `Fuel` (text), `Peak/Annual/Minimum` (text), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

### FES (Future Energy Scenarios) Whole System Gas Supply Data Table Ws1

`neso_data/future-energy-scenarios/fes-whole-system-gas-supply-data-table-ws1/` — 3 resource(s)

- **Whole System & Gas Supply (WS1) 2023** (CSV via API, ~547 rows)
  Fields: `Fuel Type` (text), `Scenario` (text), `Units` (text), `Category` (text), `Sector` (text), `Fuel` (text), `Feedstock` (text), `Category Lookup` (text), `2020` (numeric), `2021` (numeric), `2022` (numeric), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

- **Whole System & Gas Supply (WS1) 2024** (CSV via API, ~0 rows)
  Fields: `Fuel Type` (text), `Pathway` (text), `Units` (text), `Category` (text), `Sector` (text), `Fuel` (text), `Feedstock` (text), `Category Lookup` (text), `2020` (numeric), `2021` (numeric), `2022` (numeric), `2023` (text), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

- **Whole System & Gas Supply (WS1) 2025** (CSV via API, ~657 rows)
  Fields: `Fuel Type` (text), `Pathway` (text), `Units` (text), `Category` (text), `Sector` (text), `Fuel` (text), `Feedstock` (text), `Category Lookup` (text), `2020` (numeric), `2021` (numeric), `2022` (numeric), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

### FES (Future Energy Scenarios) Whole System Gas Supply Emissions Data Table Ws2

`neso_data/future-energy-scenarios/fes-whole-system-gas-supply-emissions-data-table-ws2/` — 3 resource(s)

- **Whole System & Gas Supply - Emissions (WS2) 2023** (CSV via API, ~91 rows)
  Fields: `Scenario` (text), `Sector` (text), `2021` (numeric), `2022` (numeric), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

- **2 resources sharing this schema:** Whole System & Gas Supply - Emissions (WS2) 2024, Whole System & Gas Supply - Emissions (WS2) 2025 (CSV via API, ~197 rows combined)
  Fields: `Pathway` (text), `Sector` (text), `2021` (numeric), `2022` (numeric), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

### Future Energy Scenario Electricity Supply Data Table Es1

`neso_data/future-energy-scenarios/future-energy-scenario-electricity-supply-data-table-es1/` — 6 resource(s)

- **Electricity Supply Data table (ES1) 2020** (CSV via API, ~581 rows)
  Fields: `Connection` (text), `Scenario` (text), `Variable` (text), `Category` (text), `Type` (text), `SubType` (text), `2019` (text), `2020` (text), `2021` (text), `2022` (text), `2023` (text), `2024` (text), `2025` (text), `2026` (text), `2027` (text), `2028` (text), `2029` (text), `2030` (text), `2031` (text), `2032` (text), `2033` (text), `2034` (text), `2035` (text), `2036` (text), `2037` (text), `2038` (text), `2039` (text), `2040` (text), `2041` (text), `2042` (text), `2043` (text), `2044` (text), `2045` (text), `2046` (text), `2047` (text), `2048` (text), `2049` (text), `2050` (text)

- **Electricity Supply Data table (ES1) 2021** (CSV via API, ~581 rows)
  Fields: `Connection` (text), `Scenario` (text), `Variable` (text), `Category` (text), `Type` (text), `SubType` (text), `2020` (numeric), `2021` (numeric), `2022` (numeric), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

- **Electricity Supply Data table (ES1) 2022** (CSV via API, ~678 rows)
  Fields: `Connection` (text), `Scenario` (text), `Variable` (text), `Category` (text), `Type` (text), `SubType` (text), `2021` (text), `2022` (text), `2023` (text), `2024` (text), `2025` (text), `2026` (text), `2027` (text), `2028` (text), `2029` (text), `2030` (text), `2031` (text), `2032` (text), `2033` (text), `2034` (text), `2035` (text), `2036` (text), `2037` (text), `2038` (text), `2039` (text), `2040` (text), `2041` (text), `2042` (text), `2043` (text), `2044` (text), `2045` (text), `2046` (text), `2047` (text), `2048` (text), `2049` (text), `2050` (text)

- **Electricity Supply Data table (ES1) 2023** (CSV via API, ~588 rows)
  Fields: `Connection` (text), `Scenario` (text), `Variable` (text), `Category` (text), `Type` (text), `SubType` (text), `2022` (numeric), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

- **Electricity Supply Data table (ES1) 2024** (CSV via API, ~614 rows)
  Fields: `Connection` (text), `Pathway` (text), `Variable` (text), `Category` (text), `Type` (text), `SubType` (text), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

- **Electricity Supply Data table (ES1) 2025** (CSV via API, ~620 rows)
  Fields: `Connection` (text), `Pathway` (text), `Variable` (text), `Category` (text), `Type` (text), `SubType` (text), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric)

### Future Energy Scenario FES (Future Energy Scenarios) Building Block Data

`neso_data/future-energy-scenarios/future-energy-scenario-fes-building-block-data/` — 13 resource(s)

- **FES 2020 Building Blocks - Version 1.3** (CSV via API, ~25,500 rows)
  Fields: `Building Block ID Number` (text), `Unit` (text), `DNO License Area` (text), `FES Scenario` (text), `GSP` (text), `Baseline (2019)` (numeric), `2020` (numeric), `2021` (numeric), `2022` (numeric), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric), `Comment` (text)

- **Building Block Definitions 2020** (CSV via API, ~53 rows)
  Fields: `Template` (text), `Technology` (text), `Building Block ID Number` (text), `Technology Detail` (text), `Units` (text), `Detail` (text), `Comments` (text), `ESO Additional Notes` (text)

- **FES 2021 Building Blocks - Version 8.0** (CSV via API, ~44,336 rows)
  Fields: `FES Scenario` (text), `Building Block ID Number` (text), `Unit` (text), `DNO License Area` (text), `GSP` (text), `Share of GSP` (text), `Baseline (2020)` (numeric), `2021` (numeric), `2022` (numeric), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric), `Comment` (text)

- **Building Block Definitions 2021** (CSV via API, ~64 rows)
  Fields: `Template` (text), `Technology` (text), `Building Block ID Number` (text), `Technology Detail` (text), `Units` (text), `Detail` (text), `Comments` (text), `Alignment with Ofgem Core Scenario Key Drivers` (text), `ESO Comments` (text)

- **2 resources sharing this schema:** Building Block Definitions 2022, Building Block Definitions 2023 (CSV via API, ~132 rows combined)
  Fields: `Template` (text), `Technology` (text), `Building Block ID Number` (text), `Technology Detail` (text), `Units` (text), `Detail` (text), `Comments` (text), `Alignment with Ofgem Core Scenario Key Drivers` (text), `Included in ESO Data` (text), `ESO Comments` (text)

- **FES 2022 Building Blocks - Version 4.0** (CSV via API, ~50,812 rows)
  Fields: `FES Scenario` (text), `Building Block ID Number` (text), `Unit` (text), `DNO License Area` (text), `GSP` (text), `Share of GSP` (text), `2021` (numeric), `2022` (numeric), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric), `Comment` (text)

- **FES 2023 Building Blocks - Version 1.1** (CSV via API, ~50,809 rows)
  Fields: `FES Scenario` (text), `Building Block ID Number` (text), `Unit` (text), `DNO License Area` (text), `GSP` (text), `Share of GSP` (text), `2022` (numeric), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric), `Comment` (text)

- **FES 2024 Building Blocks - Version 1.1** (CSV via API, ~56,527 rows)
  Fields: `FES Pathway` (text), `Building Block ID Number` (text), `Unit` (text), `DNO License Area` (text), `GSP` (text), `Share of GSP` (text), `2023` (numeric), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric), `Comment` (text)

- **Building Block Licence Area Name Mapping 2024** (CSV via API, ~19 rows)
  Fields: `Area Type` (text), `FES23 BB Area Name` (text), `Full Licence Name` (text), `Elexon GSP Group` (text), `Elexon GSP Group Name` (text), `FES2024 Area Name` (text), `Comments` (text)

- **2 resources sharing this schema:** Building Block Definitions 2024, Building Block Definitions 2025 (CSV via API, ~132 rows combined)
  Fields: `Template` (text), `Technology` (text), `Building Block ID Number` (text), `Technology Detail` (text), `Units` (text), `Detail` (text), `Comments` (text), `Alignment with Ofgem Core Scenario Key Drivers` (text)

- **FES 2025 Building Blocks** (CSV via API, ~48,019 rows)
  Fields: `FES Pathway` (text), `Building Block ID Number` (text), `Unit` (text), `DNO License Area` (text), `GSP` (text), `Share of GSP` (text), `2024` (numeric), `2025` (numeric), `2026` (numeric), `2027` (numeric), `2028` (numeric), `2029` (numeric), `2030` (numeric), `2031` (numeric), `2032` (numeric), `2033` (numeric), `2034` (numeric), `2035` (numeric), `2036` (numeric), `2037` (numeric), `2038` (numeric), `2039` (numeric), `2040` (numeric), `2041` (numeric), `2042` (numeric), `2043` (numeric), `2044` (numeric), `2045` (numeric), `2046` (numeric), `2047` (numeric), `2048` (numeric), `2049` (numeric), `2050` (numeric), `Comment` (text)

### Levelised Cost Of Green Hydrogen

`neso_data/future-energy-scenarios/levelised-cost-of-green-hydrogen/` — 3 resource(s)

- **Levelised cost of blue hydrogen modelling, 2025 to 2050** (CSV via API, ~120 rows)
  Fields: `Tech` (text), `Build Year` (int4), `Discount Factor` (numeric), `Units` (text), `LCOH` (numeric), `LCOH Capex` (numeric), `LCOH Fixed Opex` (numeric), `LCOH Variable Opex` (numeric), `LCOH Electricity Cost` (numeric), `LCOH Fuel Cost` (numeric), `LCOH CO2 T&S Cost` (numeric), `LCOH Emissions Cost` (numeric)

- **Levelised cost of green hydrogen modelling, 2025 to 2050** (CSV via API, ~424,080 rows)
  Fields: `Tech` (text), `Scenario` (text), `Build Year` (text), `Capacity Factor` (numeric), `Electricity Price` (numeric), `Discount Factor` (numeric), `Units` (text), `LCOH` (numeric), `LCOH Capex` (numeric), `LCOH Electricity Cost` (numeric), `LCOH Fixed Opex` (numeric), `LCOH Variable Opex` (numeric)

- **Capex and opex input assumptions for PEM and Alkaline electrolyser systems** (CSV via API, ~36 rows)
  Fields: `Tech` (text), `Scenario` (text), `Build Year` (int4), `Capex (£/kWe)` (numeric), `Efficiency` (numeric), `Capex (£/kW H2 HHV)` (numeric), `Fixed Opex % of capex` (numeric), `Fixed Opex` (numeric), `Variable Opex` (numeric), `Plant Lifetime` (numeric)

### Local Authority Level Spatial Heat Model Outputs FES (Future Energy Scenarios)

`neso_data/future-energy-scenarios/local-authority-level-spatial-heat-model-outputs-fes/` — 20 resource(s)

- **FES 22 local authority outputs 2020 domestic all scenarios** (CSV via API, ~1,480 rows)
  Fields: `CODE_x` (text), `Local_Authority` (text), `Year` (numeric), `Scenario` (text), `Sector` (text), `stock ASHP` (numeric), `stock Community` (numeric), `stock DH` (numeric), `stock Electric resistive` (numeric), `stock Electric storage` (numeric), `stock GSHP` (numeric), `stock Gas boiler` (numeric), `stock Oil boiler` (numeric), `stock Total` (numeric), `stock TotalHPs` (numeric), `stock_proportion ASHP` (numeric), `stock_proportion Community` (numeric), `stock_proportion DH` (numeric), `stock_proportion Electric resistive` (numeric), `stock_proportion Electric storage` (numeric), `stock_proportion GSHP` (numeric), `stock_proportion Gas boiler` (numeric), `stock_proportion Oil boiler` (numeric), `stock_proportion TotalHPs` (numeric)

- **FES 22 local authority outputs 2025 domestic all scenarios** (CSV via API, ~1,482 rows)
  Fields: `CODE_x` (text), `Local_Authority` (text), `Year` (numeric), `Scenario` (text), `Sector` (text), `stock ASHP` (numeric), `stock BioLPG boiler` (numeric), `stock Biomass boiler` (numeric), `stock Community` (numeric), `stock DH` (numeric), `stock Electric resistive` (numeric), `stock Electric storage` (numeric), `stock GSHP` (numeric), `stock Gas boiler` (numeric), `stock Hybrid (ASHP + BioLPG boiler)` (numeric), `stock Hybrid (ASHP + Electric resistive)` (numeric), `stock Oil boiler` (numeric), `stock Total` (numeric), `stock TotalHPs` (numeric), `stock_proportion ASHP` (numeric), `stock_proportion BioLPG boiler` (numeric), `stock_proportion Biomass boiler` (numeric), `stock_proportion Community` (numeric), `stock_proportion DH` (numeric), `stock_proportion Electric resistive` (numeric), `stock_proportion Electric storage` (numeric), `stock_proportion GSHP` (numeric), `stock_proportion Gas boiler` (numeric), `stock_proportion Hybrid (ASHP + BioLPG boiler)` (numeric), `stock_proportion Hybrid (ASHP + Electric resistive)` (numeric), `stock_proportion Oil boiler` (numeric), `stock_proportion TotalHPs` (numeric)

- **5 resources sharing this schema:** FES 22 local authority outputs 2030 domestic all scenarios, FES 22 local authority outputs 2035 domestic all scenarios, FES 22 local authority outputs 2040 domestic all scenarios, FES 22 local authority outputs 2045 domestic all scenarios, FES 22 local authority outputs 2050 domestic all scenarios (CSV via API, ~7,410 rows combined)
  Fields: `CODE_x` (text), `Local_Authority` (text), `Year` (numeric), `Scenario` (text), `Sector` (text), `stock ASHP` (numeric), `stock BioLPG boiler` (numeric), `stock Biomass boiler` (numeric), `stock Community` (numeric), `stock DH` (numeric), `stock Electric resistive` (numeric), `stock Electric storage` (numeric), `stock GSHP` (numeric), `stock Gas boiler` (numeric), `stock Hybrid (ASHP + BioLPG boiler)` (numeric), `stock Hybrid (ASHP + Electric resistive)` (numeric), `stock Hybrid (ASHP + Hydrogen boiler)` (numeric), `stock Hydrogen boiler` (numeric), `stock Oil boiler` (numeric), `stock Total` (numeric), `stock TotalHPs` (numeric), `stock_proportion ASHP` (numeric), `stock_proportion BioLPG boiler` (numeric), `stock_proportion Biomass boiler` (numeric), `stock_proportion Community` (numeric), `stock_proportion DH` (numeric), `stock_proportion Electric resistive` (numeric), `stock_proportion Electric storage` (numeric), `stock_proportion GSHP` (numeric), `stock_proportion Gas boiler` (numeric), `stock_proportion Hybrid (ASHP + BioLPG boiler)` (numeric), `stock_proportion Hybrid (ASHP + Electric resistive)` (numeric), `stock_proportion Hybrid (ASHP + Hydrogen boiler)` (numeric), `stock_proportion Hydrogen boiler` (numeric), `stock_proportion Oil boiler` (numeric), `stock_proportion TotalHPs` (numeric)

- **7 resources sharing this schema:** FES 2024 local authority outputs 2020 residential all scenarios, FES 2024 local authority outputs 2025 residential all scenarios, FES 2024 local authority outputs 2030 residential all scenarios, FES 2024 local authority outputs 2035 residential all scenarios, FES 2024 local authority outputs 2040 residential all scenarios, FES 2024 local authority outputs 2045 residential all scenarios, FES 2024 local authority outputs 2050 residential all scenarios (CSV via API, ~10,388 rows combined)
  Fields: `la_code` (text), `Local_Authority` (text), `Year` (int4), `Pathway` (text), `Sector` (text), `stock ASHP` (numeric), `stock Biofuel boiler` (numeric), `stock Biomass boiler` (numeric), `stock Community` (numeric), `stock DH` (numeric), `stock Electric resistive` (numeric), `stock Electric storage` (numeric), `stock GSHP` (numeric), `stock Gas boiler` (numeric), `stock Hybrid (ASHP + Biofuel boiler)` (numeric), `stock Hybrid (ASHP + Electric resistive)` (numeric), `stock Hybrid (ASHP + Hydrogen boiler)` (numeric), `stock Hydrogen boiler` (numeric), `stock Oil boiler` (numeric)

- **6 resources sharing this schema:** FES 2025 local authority outputs 2025 residential all scenarios, FES 2025 local authority outputs 2030 residential all scenarios, FES 2025 local authority outputs 2035 residential all scenarios, FES 2025 local authority outputs 2040 residential all scenarios, FES 2025 local authority outputs 2045 residential all scenarios, FES 2025 local authority outputs 2050 residential all scenarios (CSV via API, ~8,904 rows combined)
  Fields: `la_code` (text), `Local_Authority` (text), `Year` (int4), `Pathway` (text), `Sector` (text), `stock ASHP` (numeric), `stock BioLPG boiler` (numeric), `stock Biomass boiler` (numeric), `stock Electric resistive` (numeric), `stock Electric storage` (numeric), `stock Fossil fuel communal heating` (numeric), `stock GSHP` (numeric), `stock Gas boiler` (numeric), `stock Hybrid (ASHP + BioLPG boiler)` (numeric), `stock Hybrid (ASHP + Electric resistive)` (numeric), `stock Hybrid (ASHP + Hydrogen boiler)` (numeric), `stock Hydrogen boiler` (numeric), `stock Low carbon district heating` (numeric), `stock Oil boiler` (numeric)

### Regional Breakdown Of FES (Future Energy Scenarios) Data Electricity

`neso_data/future-energy-scenarios/regional-breakdown-of-fes-data-electricity/` — 27 resource(s)

- **3 resources sharing this schema:** FES 2021 Grid Supply Point Info, FES 2023 Grid Supply Point Info, FES 2024 Grid Supply Point Info (CSV via API, ~993 rows combined)
  Fields: `GSP ID` (text), `GSP Group` (text), `Minor FLOP` (text), `Name` (text), `Latitude` (numeric), `Longitude` (numeric), `Comments` (text)

- **2 resources sharing this schema:** Regional Breakdown of 2021 FES: Demands from distributed storage sites greater than 1 MW, Regional Breakdown of 2022 FES: Demands from distributed storage sites greater than 1 MW (CSV via API, ~26,023 rows combined)
  Fields: `scenario` (text), `tech` (text), `year` (numeric), `location` (text), `Capacity` (numeric), `wintpk` (numeric), `summam` (numeric), `summpm` (numeric)

- **2 resources sharing this schema:** Regional Breakdown of 2021 FES: Demands from distributed storage sites less than 1 MW, Regional Breakdown of 2022 FES: Demands from distributed storage sites less than 1 MW (CSV via API, ~86,945 rows combined)
  Fields: `scenario` (text), `year` (numeric), `etys_location` (text), `capacity` (numeric), `wintpk` (numeric), `summam` (numeric), `summpm` (numeric)

- **4 resources sharing this schema:** Regional Breakdown of 2021 FES: Distributed generation greater than 1 MW, Regional Breakdown of 2021 FES: Distributed generation less than 1 MW, Regional Breakdown of 2022 FES: Distributed generation greater than 1 MW, Regional Breakdown of 2022 FES: Distributed generation less than 1 MW (CSV via API, ~621,737 rows combined)
  Fields: `scenario` (text), `tech` (text), `year` (numeric), `etys_location` (text), `capacity` (numeric), `wintpk` (numeric), `summam` (numeric), `summpm` (numeric)

- **2 resources sharing this schema:** Regional Breakdown of 2021 FES: Demand Side Response (DSR), Regional Breakdown of 2022 FES: Demand Side Response (DSR) (CSV via API, ~89,304 rows combined)
  Fields: `scenario` (text), `GSP` (text), `DSR` (numeric), `year` (numeric)

- **2 resources sharing this schema:** Regional Breakdown of 2021 FES: Demand (Active Power), Regional Breakdown of 2022 FES: Demand (Active Power) (CSV via API, ~693,204 rows combined)
  Fields: `scenario` (text), `GSP` (text), `DemandPk` (numeric), `DemandAM` (numeric), `DemandPM` (numeric), `type` (text), `year` (numeric)

- **FES 2022 Grid Supply Point Info** (CSV via API, ~370 rows)
  Fields: `GSP ID` (text), `GSP Group` (text), `Minor FLOP` (text), `Name` (text), `Latitude` (text), `Longitude` (text), `Comments` (text)

- **Regional Breakdown of 2023 FES: Demand Side Response (DSR)** (CSV via API, ~42,456 rows)
  Fields: `scenario` (text), `GSP` (text), `DSR` (numeric), `year` (int4)

- **2 resources sharing this schema:** Regional Breakdown of 2023 FES: Demand (Active Power), Regional Breakdown of 2024 FES: Demand (Active Power) (CSV via API, ~587,520 rows combined)
  Fields: `scenario` (text), `GSP` (text), `DemandPk` (numeric), `DemandAM` (numeric), `DemandPM` (numeric), `type` (text), `year` (int4)

- **Regional Breakdown of 2023 FES: Demand from distributed storage sites greater than 1 MW** (CSV via API, ~14,042 rows)
  Fields: `scenario` (text), `tech` (text), `year` (int4), `location` (text), `Capacity` (numeric), `wintpk` (int4), `summam` (int4), `summpm` (numeric)

- **Regional Breakdown of 2023 FES: Demand from distributed storage sites less than 1 MW** (CSV via API, ~45,510 rows)
  Fields: `scenario` (text), `year` (int4), `etys_location` (text), `capacity` (numeric), `wintpk` (int4), `summam` (int4), `summpm` (numeric)

- **Regional Breakdown of 2023 FES: Distributed generation less than 1 MW** (CSV via API, ~227,671 rows)
  Fields: `scenario` (text), `tech` (text), `year` (text), `etys_location` (text), `capacity` (text), `wintpk` (text), `summam` (numeric), `summpm` (text)

- **3 resources sharing this schema:** Regional Breakdown of 2023 FES: Distributed generation greater than 1 MW, Regional Breakdown of 2024 FES: Demand from distributed storage sites less than 1 MW, Regional Breakdown of 2024 FES: Distributed generation greater than 1 MW (CSV via API, ~213,588 rows combined)
  Fields: `scenario` (text), `tech` (text), `year` (int4), `etys_location` (text), `capacity` (numeric), `wintpk` (numeric), `summam` (numeric), `summpm` (numeric)

- **Regional Breakdown of 2024 FES: Demand from distributed storage sites greater than 1 MW** (CSV via API, ~10,627 rows)
  Fields: `scenario` (text), `tech` (text), `year` (int4), `location` (text), `Capacity` (numeric), `wintpk` (numeric), `summam` (numeric), `summpm` (numeric)

- **Regional Breakdown of 2024 FES: Distributed generation less than 1 MW** (CSV via API, ~156,324 rows)
  Fields: `scenario` (text), `tech` (text), `year` (text), `etys_location` (text), `capacity` (text), `wintpk` (text), `summam` (numeric), `summpm` (numeric)

### Resource Adequacy In 2030s

`neso_data/future-energy-scenarios/resource-adequacy-in-2030s/` — 3 resource(s)

- **Portfolio Capacities** (CSV via API, ~315 rows)
  Fields: `Name` (text), `Category` (text), `Technology` (text), `Future Year` (text), `Installed Capacity (MW)` (int4), `Stored energy (MWh)` (int4)

- **Peak Demand** (CSV via API, ~102 rows)
  Fields: `Spotlight year` (text), `Historical weather year` (text), `Peak Demand (MW)` (numeric)

- **Resource Adequacy Results** (CSV via API, ~1,462 rows)
  Fields: `Simulation Name` (text), `Spotlight year` (text), `Historical weather year` (text), `Weather-conditional LOLE (h/year)` (numeric), `Weather-conditional EEU (MWh/year)` (numeric)


## Generation

### 14 Days Ahead Operational Metered Wind Forecasts _(cadence hint from name: 14-day-ahead)_

`neso_data/generation/14-days-ahead-operational-metered-wind-forecasts/` — 2 resource(s)

- **14 Day Ahead Operational Metered Windfarm-Level Wind Forecast** (CSV via API, ~167,418 rows)
  Fields: `Datetime` (timestamp), `Date` (date), `Settlement_Period` (int4), `Generator_Name` (text), `Generator_Full_Name` (text), `Region` (text), `Capacity` (numeric), `Wind_Forecast` (numeric)

- **14 Day Ahead Operational Metered Wind Forecast** (CSV file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### 14 Days Ahead Wind Forecasts _(cadence hint from name: 14-day-ahead)_

`neso_data/generation/14-days-ahead-wind-forecasts/` — 2 resource(s)

- **14 Days Ahead Wind Forecast** (CSV via API, ~672 rows)
  Fields: `Datetime` (timestamp), `Date` (date), `Settlement_Period` (int4), `Capacity` (int4), `Wind_Forecast` (int4), `ForecastDateTime` (timestamp)

- **14 Day Ahead Wind BMU Forecast** (CSV via API, ~143,808 rows)
  Fields: `Datetime` (timestamp), `Date` (date), `Settlement_Period` (int4), `Generator_Name` (text), `Generator_Full_Name` (text), `Region` (text), `Capacity` (int4), `Wind_Forecast` (int4)

### Daily OPMR (Operational Planning and Metered Restoration / Operational Metered) _(cadence hint from name: daily / day-ahead)_

`neso_data/generation/daily-opmr/` — 1 resource(s)

- **Daily Operational Planning Margin Requirement** (CSV via API, ~25,485 rows)
  Fields: `Publish Date` (date), `Date` (date), `Peak Demand Forecast` (int4), `Generator Availability` (int4), `Maximum I/C Import` (int4), `Maximum I/C Export` (int4), `Generation Availability Margin` (int4), `Operating Reserve provided by I/Cs` (int4), `OPMR total` (int4), `Constrained Plant` (int4), `National Surplus` (int4), `Minimum Demand Forecast` (int4), `High Freq Response Requirement` (int4), `Negative Reserve` (int4)

### Daily Wind Availability _(cadence hint from name: daily / day-ahead)_

`neso_data/generation/daily-wind-availability/` — 1 resource(s)

- **Daily Wind Availability** (CSV via API, ~3,588 rows)
  Fields: `BMU_ID` (text), `Date` (date), `MW` (int4)

### Day Ahead Wind Forecast _(cadence hint from name: daily / day-ahead)_

`neso_data/generation/day-ahead-wind-forecast/` — 3 resource(s)

- **Day Ahead Wind Forecast** (CSV via API, ~48 rows)
  Fields: `Datetime_GMT` (timestamp), `Date` (date), `Settlement_period` (int4), `Capacity` (numeric), `Incentive_forecast` (numeric)

- **Historic Day Ahead Wind Forecasts** (CSV via API, ~143,977 rows)
  Fields: `Datetime_GMT` (timestamp), `Date` (date), `Settlement_period` (int4), `Capacity` (numeric), `Incentive_forecast` (numeric), `Forecast_Timestamp` (timestamp)

- **Day Ahead Wind BMU Forecast** (CSV via API, ~10,800 rows)
  Fields: `Datetime` (timestamp), `Date` (date), `Settlement_Period` (int4), `Generator_Name` (text), `Generator_Full_Name` (text), `Region` (text), `Capacity` (numeric), `Wind_Forecast` (numeric)

### Embedded Wind And Solar Forecasts _(cadence hint from name: forecast series)_

`neso_data/generation/embedded-wind-and-solar-forecasts/` — 11 resource(s)

- **Embedded Solar and Wind Forecast** (CSV via API, ~638 rows)
  Fields: `DATE_GMT` (timestamp), `TIME_GMT` (text), `SETTLEMENT_DATE` (timestamp), `SETTLEMENT_PERIOD` (int4), `EMBEDDED_WIND_FORECAST` (numeric), `EMBEDDED_WIND_CAPACITY` (int4), `EMBEDDED_SOLAR_FORECAST` (int4), `EMBEDDED_SOLAR_CAPACITY` (int4)

- **6 resources sharing this schema:** Embedded Solar and Wind Forecast Archive 2019, Embedded Solar and Wind Forecast Archive 2020, Embedded Solar and Wind Forecast Archive 2022, Embedded Solar and Wind Forecast Archive 2023, Embedded Solar and Wind Forecast Archive 2024, Embedded Solar and Wind Forecast Archive 2026 (Jan- Jun) (CSV via API, ~26,783,470 rows combined)
  Fields: `DATE_GMT` (timestamp), `TIME_GMT` (time), `SETTLEMENT_DATE` (timestamp), `SETTLEMENT_PERIOD` (int4), `EMBEDDED_WIND_FORECAST` (int4), `EMBEDDED_WIND_CAPACITY` (int4), `EMBEDDED_SOLAR_FORECAST` (int4), `EMBEDDED_SOLAR_CAPACITY` (int4), `Forecast_Datetime` (timestamp)

- **Embedded Solar and Wind Forecast Archive 2021** (CSV via API, ~5,465,982 rows)
  Fields: `DATE_GMT` (timestamp), `TIME_GMT` (time), `SETTLEMENT_DATE` (timestamp), `SETTLEMENT_PERIOD` (int4), `EMBEDDED_WIND_FORECAST` (int4), `EMBEDDED_WIND_CAPACITY` (text), `EMBEDDED_SOLAR_FORECAST` (int4), `EMBEDDED_SOLAR_CAPACITY` (int4), `Forecast_Datetime` (timestamp)

- **Embedded Solar and Wind Forecast Archive 2025** (CSV via API, ~5,369,698 rows)
  Fields: `DATE_GMT` (timestamp), `TIME_GMT` (time), `SETTLEMENT_DATE` (timestamp), `SETTLEMENT_PERIOD` (int4), `EMBEDDED_WIND_FORECAST` (int4), `EMBEDDED_WIND_CAPACITY` (int4), `EMBEDDED_SOLAR_FORECAST` (int4), `EMBEDDED_SOLAR_CAPACITY` (int4), `Forecast_Datetime` (timestamp), `source_file` (text)

- **Embedded Solar and Wind Forecast Archive 2026 (Jun - Dec)** (CSV via API, ~315,086 rows)
  Fields: `DATE_GMT` (timestamp), `TIME_GMT` (text), `SETTLEMENT_DATE` (timestamp), `SETTLEMENT_PERIOD` (int4), `EMBEDDED_WIND_FORECAST` (int4), `EMBEDDED_WIND_CAPACITY` (int4), `EMBEDDED_SOLAR_FORECAST` (int4), `EMBEDDED_SOLAR_CAPACITY` (int4), `Forecast_Datetime` (timestamp)

- **Embedded Definition** (DOC file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Monthly Operational Metered Wind Output _(cadence hint from name: monthly)_

`neso_data/generation/monthly-operational-metered-wind-output/` — 9 resource(s)

- **3 resources sharing this schema:** Monthly Operational Metered Wind Output 2018-2019, Monthly Operational Metered Wind Output 2019-2020, Monthly Operational Metered Wind Output 2020-2021 (CSV via API, ~52,608 rows combined)
  Fields: `Sett_Date` (timestamp), `Sett_Period` (numeric), `Scottish Wind Output` (numeric), `England/Wales Wind Output` (numeric), `Total` (numeric)

- **Monthly Operational Metered Wind Output 2021-2022** (CSV via API, ~17,520 rows)
  Fields: `Sett_Date` (date), `Sett_Period` (numeric), `Scottish Wind Output` (numeric), `England/Wales Wind Output` (numeric), `Total` (numeric)

- **5 resources sharing this schema:** Monthly Operational Metered Wind Output 2022-2023, Monthly Operational Metered Wind Output 2023-2024, Monthly Operational Metered Wind Output 2024-2025, Monthly Operational Metered Wind Output 2025-2026, Monthly Operational Metered Wind Output 2026-2027 (CSV via API, ~74,354 rows combined)
  Fields: `Sett_Date` (date), `Sett_Period` (int4), `Scottish Wind Output` (numeric), `England/Wales Wind Output` (numeric), `Total` (numeric)

### Negative Reserve Active Power Margin NRAPM (Negative Reserve Active Power Margin) Forecast _(cadence hint from name: forecast series)_

`neso_data/generation/negative-reserve-active-power-margin-nrapm-forecast/` — 4 resource(s)

- **National Daily 2-14 days NRAPM Forecast** (CSV via API, ~26 rows)
  Fields: `Date` (date), `CP` (text), `MW away from risk of System Level NRAPM (Forecast Conditions)` (numeric)

- **Scotland Daily 2-14 days NRAPM Forecast** (CSV via API, ~26 rows)
  Fields: `Date` (date), `CP` (text), `MW away from risk of Scotland Level NRAPM (Forecast Conditions)` (numeric)

- **Weekly 2-52 week National NRAPM Forecast** (CSV via API, ~55 rows)
  Fields: `Week number` (text), `Date` (date), `Wind Load Factor required to cause a System Level NRAPM` (numeric), `Probability of seeing Wind load factor above` (numeric)

- **Weekly 2-52 week Scotland NRAPM forecast** (CSV via API, ~55 rows)
  Fields: `Week number` (text), `Date` (date), `Wind Load Factor required to cause a Scotland Level NRAPM` (numeric), `Probability of seeing Wind load factor above` (numeric)

### Tresp Generation Pathways

`neso_data/generation/tresp-generation-pathways/` — 5 resource(s)

- **3 resources sharing this schema:** tRESP Indicative Generation Pathways per Local Authority for England, tRESP Indicative Generation Pathways per Local Authority for Scotland, tRESP Indicative Generation Pathways per Local Authority for Wales (CSV via API, ~466,900 rows combined)
  Fields: `Building_block_id` (text), `LAD24CD` (text), `LAD24NM` (text), `Pathway` (text), `Year` (int4), `Unit` (text), `Value` (numeric)

- **tRESP Generation Pathways per RESP Nation and Region** (CSV via API, ~14,674 rows)
  Fields: `Building_block_id` (text), `RESP_region` (text), `Pathway` (text), `Year` (int4), `Value` (numeric), `Unit` (text)

- **tRESP Generation Pathways per Grid Supply Point Area** (CSV via API, ~308,154 rows)
  Fields: `Building_block_id` (text), `tRESP_GSP_area` (text), `Pathway` (text), `Year` (int4), `Value` (numeric), `Unit` (text), `DNO_licence_area` (text)

### Weekly OPMR (Operational Planning and Metered Restoration / Operational Metered) _(cadence hint from name: weekly)_

`neso_data/generation/weekly-opmr/` — 1 resource(s)

- **Weekly Operational Planning Margin Requirement (OPMR)** (CSV via API, ~299,818 rows)
  Fields: `ENG.Week` (int4), `ENG.Year` (int4), `Publish Date` (date), `Peak Demand Forecast` (int4), `Generator Availability` (int4), `Maximum I/C Import` (int4), `Maximum I/C Export` (int4), `Generation Availability Margin` (int4), `Operating Reserve provided by I/Cs` (int4), `OPMR total` (int4), `Constrained Plant` (int4), `National Surplus` (int4), `Minimum Demand Forecast` (int4), `High Freq Response Requirement` (int4), `Negative Reserve` (int4)

### Weekly Wind Availability _(cadence hint from name: weekly)_

`neso_data/generation/weekly-wind-availability/` — 1 resource(s)

- **Weekly Wind Availability** (CSV via API, ~42,780 rows)
  Fields: `BMU_ID` (text), `Week Number` (text), `MW` (int4)

### Wind Bmu Boa Volumes

`neso_data/generation/wind-bmu-boa-volumes/` — 10 resource(s)

- **10 resources sharing this schema** (e.g. Wind BOA Volumes 2018/19, Wind BOA Volumes 2019/20, Wind BOA Volumes 2020/21, …) (CSV via API, ~1,524,752 rows combined)
  Fields: `Date` (date), `Settlement_Period` (int4), `Generator_Name` (text), `Generator_Full_Name` (text), `BOA_Volume` (numeric)


## Interconnectors

### Brit Ned

`neso_data/interconnectors/brit-ned/` — 174 resource(s)

- **BritNed DA & ID Weekly ITLs 20221012** (CSV via API, ~168 rows)
  Fields: `Operational Date (YYYY-MM-DD) & Time GMT/BST (HH:MM - HH:MM)` (text), `Flow (MW) From GB` (text), `Flow (MW) To GB` (int4), `Reason For Restiction` (text)

- **3 resources sharing this schema:** BritNed DA & ID Weekly ITLs 20221019, BritNed DA & ID Weekly ITLs 20221102, BritNed DA & ID Weekly ITLs 20221109 (CSV via API, ~457 rows combined)
  Fields: `Operational Date (YYYY-MM-DD) & Time GMT/BST (HH:MM - HH:MM)` (text), `Flow (MW) to GB` (int4), `Flow (MW) from GB` (int4), `Reason For Restriction` (text)

- **BritNed DA & ID Weekly ITLs 20221026** (CSV via API, ~144 rows)
  Fields: `Operational Date (YYYY-MM-DD) & Time GMT/BST (HH:MM - HH:MM)` (text), `Flow (MW) To GB` (int4), `Flow (MW) From GB` (int4), `Reason For Restriction` (text)

- **164 resources sharing this schema** (e.g. BritNed DA & ID Weekly ITLs 20221116, BritNed DA & ID Weekly ITLs 20221123, BritNed DA & ID Weekly ITLs 20221130, …) (CSV via API, ~15,983 rows combined)
  Fields: `Operational Date (YYYY-MM-DD) & Time GMT/BST (HH:MM - HH:MM)` (text), `Flow (MW) to GB` (int4), `Flow (MW) from GB` (int4), `Reason for restriction` (text)

- **2 resources sharing this schema:** BritNed DA & ID Weekly ITLs 20230913, BritNed DA & ID Weekly ITLs 20260128 (CSV via API, ~193 rows combined)
  Fields: `Operational Date (YYYY-MM-DD) & Time GMT/BST (HH:MM - HH:MM)` (text), `Flow (MW) to GB` (int4), `Flow (MW) from GB` (text), `Reason for restriction` (text)

- **3 resources sharing this schema:** BritNed DA & ID Weekly ITLs 20250416, BritNed DA & ID Weekly ITLs 20250627, BritNed DA & ID Weekly ITLs 20251015 (CSV via API, ~312 rows combined)
  Fields: `Operational Date (YYYY-MM-DD) & Time GMT/BST (HH:MM - HH:MM)` (text), `Flow (MW) to GB` (text), `Flow (MW) from GB` (int4), `Reason for restriction` (text)

### Eleclink

`neso_data/interconnectors/eleclink/` — 2 resource(s)

- **ElecLink NTC Data** (CSV via API, ~19,583 rows)
  Fields: `Data Upload Time (GMT)` (timestamp), `Auction Type` (text), `Operational Period Start Date & Time (GMT)` (timestamp), `Flow (MW) To GB` (int4), `Reason For Restriction To GB` (text), `Flow (MW) From GB` (int4), `Reason For Restriction From GB` (text)

- **Archived ElecLink NTC Data** (CSV via API, ~8,472 rows)
  Fields: `Operational Date` (date), `Auction Type` (text), `Version` (int4), `Hourly Time Period (GMT)` (text), `Flow (MW) To GB` (int4), `Flow (MW) From GB` (int4), `Reason For Reduction` (text)

### Ifa

`neso_data/interconnectors/ifa/` — 2 resource(s)

- **Archived IFA DA & ID Weekly ITLs** (CSV via API, ~11,401 rows)
  Fields: `Operational Date (YYYY-MM-DD) & Time GMT/BST (HH:MM - HH:MM)` (text), `Flow (MW) to GB` (numeric), `Flow (MW) from GB` (numeric), `Reason for restriction` (text)

- **IFA ITL Data** (CSV via API, ~9,022 rows)
  Fields: `Data Upload Time (GMT)` (timestamp), `Auction Type` (text), `Operational Period Start Date & Time (GMT)` (timestamp), `Flow (MW) To GB` (int4), `Reason For Restriction To GB` (text), `Flow (MW) From GB` (int4), `Reason For Restriction From GB` (text)

### Ifa2

`neso_data/interconnectors/ifa2/` — 2 resource(s)

- **Archived IFA2 DA & ID Weekly ITLs** (CSV via API, ~7,680 rows)
  Fields: `Operational Date (YYYY-MM-DD) & Time GMT/BST (HH:MM - HH:MM)` (text), `Flow (MW) to GB` (int4), `Flow (MW) from GB` (int4), `Reason for restriction` (text)

- **IFA2 ITL Data** (CSV via API, ~5,424 rows)
  Fields: `Data Upload Time (GMT)` (timestamp), `Auction Type` (text), `Operational Period Start Date & Time (GMT)` (timestamp), `Flow (MW) To GB` (int4), `Reason For Restriction To GB` (text), `Flow (MW) From GB` (int4), `Reason For Restriction From GB` (text)

### Nemolink

`neso_data/interconnectors/nemolink/` — 4 resource(s)

- **NemoLink NTC Data** (CSV via API, ~11,231 rows)
  Fields: `Data Upload Time (GMT)` (timestamp), `Auction Type` (text), `Operational Period Start Date & Time (GMT)` (timestamp), `Flow (MW) To GB` (int4), `Reason For Restriction To GB` (text), `Flow (MW) From GB` (int4), `Reason For Restriction From GB` (text)

- **Archived NemoLink NTC Data** (CSV via API, ~11,280 rows)
  Fields: `Operational Date` (date), `Auction Type` (text), `Version` (int4), `Hourly Time Period (GMT)` (text), `Flow (MW) To GB` (int4), `Flow (MW) From GB` (int4), `Reason For Reduction` (text)

- **Archived Nemo DA & ID Weekly NTCs** (CSV via API, ~1,344 rows)
  Fields: `Operational Date (YYYY-MM-DD) & Time GMT/BST (HH:MM - HH:MM)` (text), `Flow (MW) to GB` (numeric), `Flow (MW) from GB` (numeric), `Reason For Restriction` (text)

- **NemoLink-Intraday1-20240127-001** (CSV via API, ~24 rows)
  Fields: `Hourly Time Period (GMT)` (text), `Flow (MW) To GB` (int4), `Flow (MW) From GB` (int4), `Reason For Reduction` (text)

### Nsl

`neso_data/interconnectors/nsl/` — 2 resource(s)

- **NSL NTC Data** (CSV via API, ~15,480 rows)
  Fields: `Data Upload Time (GMT)` (timestamp), `Auction Type` (text), `Operational Period Start Date & Time (GMT)` (timestamp), `Flow (MW) To GB` (int4), `Reason For Restriction To GB` (text), `Flow (MW) From GB` (int4), `Reason For Restriction From GB` (text)

- **Archived NSL NTC Data** (CSV via API, ~16,632 rows)
  Fields: `Operational Date` (date), `Auction Type` (text), `Version` (int4), `Hourly Time Period (GMT)` (text), `Flow (MW) To GB` (int4), `Flow (MW) From GB` (int4), `Reason For Reduction` (text)

### Viking

`neso_data/interconnectors/viking/` — 2 resource(s)

- **Viking Link NTC Data** (CSV via API, ~16,295 rows)
  Fields: `Data Upload Time (GMT)` (timestamp), `Auction Type` (text), `Operational Period Start Date & Time (GMT)` (timestamp), `Flow (MW) To GB` (int4), `Reason For Restriction To GB` (text), `Flow (MW) From GB` (int4), `Reason For Restriction From GB` (text)

- **Archived Viking NTC Data** (CSV via API, ~6,456 rows)
  Fields: `Operational Date` (date), `Auction Type` (text), `Version` (int4), `Hourly Time Period (GMT)` (text), `Flow (MW) To GB` (int4), `Flow (MW) From GB` (int4), `Reason For Reduction` (text)


## Network Charges

### AAHEDC (Assistance for Areas with High Electricity Distribution Costs) Tariffs

`neso_data/network-charges/aahedc-tariffs/` — 1 resource(s)

- **Assistance for Areas of High Electricity Distribution Costs (AAHEDC) Tariffs** (CSV via API, ~8 rows)
  Fields: `Publication Type` (text), `Year FY` (int4), `Published Date` (date), `Total Scheme Tariff in p/kwh` (numeric), `Shetland Tariff in p/kwh` (numeric), `AAHEDC tariff excluding the Shetland Assistance Amount in p/kwh` (numeric)

### Gis Boundaries For GB Generation Charging Zones

`neso_data/network-charges/gis-boundaries-for-gb-generation-charging-zones/` — 2 resource(s)

- **GB Generation Charging Zones with ESRI Shape File** (ZIP file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **GB Generation Charging Zones with GeoJSON** (GeoJSON file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Transmission Network Use Of System TNUoS (Transmission Network Use of System) Tariffs

`neso_data/network-charges/transmission-network-use-of-system-tnuos-tariffs/` — 8 resource(s)

- **Non Half-Hourly (NHH) Demand Tariffs** (CSV via API, ~602 rows)
  Fields: `Publication` (text), `Year_FY` (int4), `Published_Date` (date), `Zone_No` (int4), `Zone_Name` (text), `NHH_Zonal_p/kWh` (numeric), `NHH_SGD_Adjustment_p/kWh` (numeric), `NHHTariff(Floored)_p/kWh` (numeric)

- **Half-Hourly (HH) Demand Tariffs** (CSV via API, ~602 rows)
  Fields: `Publication` (text), `Year_FY` (int4), `Published_Date` (date), `Zone_No` (int4), `Zone_Name` (text), `Peak_£/kW` (numeric), `YearRound_£/kW` (numeric), `HH_SGD_Adjustment_£/kW` (numeric), `HHTariff(Floored)_£/kW` (numeric)

- **Embedded Export Tariffs** (CSV via API, ~602 rows)
  Fields: `Publication` (text), `Year_FY` (int4), `Published_Date` (date), `Zone_No` (int4), `Zone_Name` (text), `Locational_£/kW` (numeric), `AGIC_£/kW` (numeric), `PhasedResidual_£/kW` (numeric), `EET(Floored)_£/kW` (numeric)

- **Onshore Local Circuit Tariffs** (CSV via API, ~4,647 rows)
  Fields: `Publication` (text), `Year_FY` (int4), `Published_Date` (date), `Substation_Name` (text), `Tariff_£/kW` (numeric)

- **Onshore Generator Tariffs** (CSV via API, ~1,161 rows)
  Fields: `Publication` (text), `Year_FY` (int4), `Published_Date` (date), `Zone_No` (int4), `Zone_Name` (text), `SystemPeak_£/kW` (numeric), `SharedYearRound_£/kW` (numeric), `NotSharedYearRound_£/kW` (numeric), `Residual_£/kW` (numeric), `SmallGenDiscount_£/kW` (numeric)

- **Local Offshore Generator Tariffs** (CSV via API, ~1,346 rows)
  Fields: `Publication` (text), `Year_FY` (int4), `Published_Date` (date), `OffshoreGenerator` (text), `Substation_£/kW` (numeric), `Circuit_£/kW` (numeric), `ETUoS_£/kW` (numeric)

- **Transmission Demand Residual (TDR) Tariffs** (CSV via API, ~462 rows)
  Fields: `Publication` (text), `Year_FY` (int4), `Published_Date` (date), `TDR Band` (text), `TDR Tariff in Â£/(Site Day)` (numeric), `Notes` (text)

- **Local Substation TNUoS Tariff** (CSV via API, ~84 rows)
  Fields: `Publication` (text), `Year_FY` (int4), `Published_Date` (date), `Voltage` (text), `Sum of TEC at Connecting Substation` (text), `Connection Type` (text), `Tariff` (numeric)


## Plans, Reports & Analysis

### Data Portal Planned Changes Known Issues

`neso_data/plans-reports-analysis/data-portal-planned-changes-known-issues/` — 1 resource(s)

- **Planned Changes and Issues Log** (CSV via API, ~215 rows)
  Fields: `po` (numeric), `Change_Issue_Title` (text), `Description` (text), `Dataset_Specific` (text), `File_Specific` (text), `Status` (text), `Change_DateTime_From` (timestamp), `Change_DateTime_To` (timestamp), `Last_Updated` (timestamp), `Notes` (text)


## Strategic Energy Planning

### SSEP (Strategic Spatial Energy Plan) Onshore Publication Zone Shapefile

`neso_data/strategic-energy-planning/ssep-onshore-publication-zone-shapefile/` — 3 resource(s)

- **Strategic Spatial Energy Plan (SSEP) Onshore Publication Zone Shapefile** (ZIP file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Strategic Spatial Energy Plan (SSEP) Offshore Publication Zone Shapefile** (ZIP file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **Strategic Spatial Energy Plan (SSEP) Economic Zones Shapefile** (ZIP file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)


## System

### ETYS (Electricity Ten Year Statement) GB Transmission System Boundaries

`neso_data/system/etys-gb-transmission-system-boundaries/` — 1 resource(s)

- **ETYS 2024 GB Transmission System Boundaries** (ZIP file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Gis Boundaries For GB DNO (Distribution Network Operator) License Areas

`neso_data/system/gis-boundaries-for-gb-dno-license-areas/` — 6 resource(s)

- **GB DNO Licence Areas 20200506 with ESRI Shape File** (ZIP file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **GB DNO Licence Areas 20200506** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **GB DNO Licence Areas 20200506 with GeoJson** (GeoJSON file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **GB DNO Licence Areas 20240503 with ESRI Shape File** (ZIP file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **GB DNO Licence Areas 20240503 with GeoJson** (GeoJSON file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **GB DNO Licence Areas 20240503** (PNG file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Gis Boundaries For GB Grid Supply Points

`neso_data/system/gis-boundaries-for-gb-grid-supply-points/` — 10 resource(s)

- **GSP - Gnode - Direct Connect - Region Lookup 20181031** (CSV via API, ~380 rows)
  Fields: `ng_id` (numeric), `ggd_id` (numeric), `gnode_id` (numeric), `gnode_name` (text), `gnode_lat` (numeric), `gnode_lon` (numeric), `gsp_id` (numeric), `gsp_name` (text), `gsp_lat` (numeric), `gsp_lon` (numeric), `dc_id` (numeric), `dc_name` (text), `dc_lat` (numeric), `dc_lon` (numeric), `region_id` (numeric), `region_name` (text), `has_pv` (numeric), `pes_id` (numeric), `pes_name` (text)

- **GSP Regions 20181031 with ESRI Shape file** (ZIP file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **GSP Regions 20181031 with GeoJson** (GeoJSON file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **GSP Regions 20220314 (GeoJSON)** (GeoJSON file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **GSP Regions 20220314 (ESRI Shapefile)** (ZIP file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **GSP Regions 20250102** (ZIP file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **GSP Regions 20250109** (ZIP file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **GSP Regions changelog** (TXT file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **GSP Regions 20251204** (ZIP file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **GSP Regions 20260209** (ZIP file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Stability Midterm Y 1 Utilisation Report

`neso_data/system/stability-midterm-y-1-utilisation-report/` — 1 resource(s)

- **Stability midterm (Y-1) utilisation report 25/26** (CSV via API, ~17 rows)
  Fields: `BMU ID` (text), `Inertia (in MVA.s)` (numeric), `Month & Year` (text), `Utilisation Start Datetime` (timestamp), `Utilisation End Datetime` (timestamp), `Hours Utilised` (text)

### Stability Pathfinder Service Information

`neso_data/system/stability-pathfinder-service-information/` — 8 resource(s)

- **4 resources sharing this schema:** Stability Pathfinder Utilisation Report 2023-2024, Stability Pathfinder Utilisation Report 2024-2025, Stability Pathfinder Utilisation Report 2025-2026, Stability Pathfinder Utilisation Report 2026-2027 (CSV via API, ~627,246 rows combined)
  Fields: `UNIT` (text), `Settlement Period Start Date Time` (timestamp), `Settlement Period End Date Time` (timestamp), `Instruction Code` (text), `Instruction Issue Time` (timestamp), `Actual Service Start or Cease Time` (timestamp), `Inertia` (int4)

- **4 resources sharing this schema:** Stability Pathfinder Availability Report 2023-2024, Stability Pathfinder Availability Report 2024-2025, Stability Pathfinder Availability Report 2025-2026, Stability Pathfinder Availability Report 2026-2027 (CSV via API, ~670,583 rows combined)
  Fields: `UNIT` (text), `Settlement Period Start Date Time` (timestamp), `Settlement Period End Date Time` (timestamp), `Availability Flag` (text), `REMARK` (text)

### System Frequency Data

`neso_data/system/system-frequency-data/` — 149 resource(s)

- **137 resources sharing this schema** (e.g. April 2014 - Historic Frequency Data, April 2015 - Historic Frequency Data, April 2016 - Historic Frequency Data, …) (CSV via API, ~313,372,800 rows combined)
  Fields: `dtm` (timestamp), `f` (numeric)

- **11 resources sharing this schema** (e.g. April 2019 - Historic Frequency Data, August 2019 - Historic Frequency Data, December 2019 - Historic Frequency Data, …) (CSV via API, ~23,407,450 rows combined)
  Fields: `dtm` (text), `f` (numeric)

- **February 2014 - Historic Frequency Data** (CSV file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### System Inertia

`neso_data/system/system-inertia/` — 10 resource(s)

- **4 resources sharing this schema:** GB System Inertia - 2017-2018, GB System Inertia - 2018-2019, GB System Inertia - 2019-2020, GB System Inertia - 2020-2021 (CSV via API, ~70,128 rows combined)
  Fields: `Settlement Date` (timestamp), `Settlement Period` (numeric), `Outturn Inertia` (numeric), `Market Provided Inertia` (numeric)

- **GB System Inertia - 2021-2022** (CSV via API, ~17,520 rows)
  Fields: `Settlement Date` (date), `Settlement Period` (numeric), `Outturn Inertia` (numeric), `Market Provided Inertia` (numeric)

- **5 resources sharing this schema:** GB System Inertia - 2022-2023, GB System Inertia - 2023-2024, GB System Inertia - 2024-2025, GB System Inertia - 2025-2026, GB System Inertia - 2026-2027 (CSV via API, ~73,482 rows combined)
  Fields: `Settlement Date` (date), `Settlement Period` (int4), `Outturn Inertia` (int4), `Market Provided Inertia` (int4)

### System Inertia Cost

`neso_data/system/system-inertia-cost/` — 10 resource(s)

- **4 resources sharing this schema:** GB System Inertia Costs 2017, GB System Inertia Costs 2018, GB System Inertia Costs 2019, GB System Inertia Costs 2020 (CSV via API, ~1,461 rows combined)
  Fields: `Settlement Date` (timestamp), `Cost` (numeric)

- **GB System Inertia Costs 2021** (CSV via API, ~361 rows)
  Fields: `Settlement Date` (date), `Cost_per_GVAs` (numeric)

- **5 resources sharing this schema:** GB System Inertia Costs 2022, GB System Inertia Costs 2023, GB System Inertia Costs 2024, GB System Inertia Costs 2025, GB System Inertia Costs 2026 (CSV via API, ~1,460 rows combined)
  Fields: `Settlement Date` (date), `Cost_per_GVAs` (int4)

### System Operating Plan SOP (System Operating Plan)

`neso_data/system/system-operating-plan-sop/` — 3 resource(s)

- **System Operating Plan - Data Table** (CSV via API, ~9,993 rows)
  Fields: `sop_datetime` (timestamp), `report_date` (timestamp), `latest_version` (float8), `latest_status` (text), `cardinal_point` (text), `customer_demand_forcast` (float8), `station_transformer` (float8), `dsbr` (float8), `total_sop_demand` (float8), `standing_reserve_requirement` (float8), `standing_reserve_availability` (float8), `standing_reserve_shortfall` (float8), `standing_reserve_excess` (float8), `standing_res_wind_adj` (float8), `net_positive_regulating_reserve` (float8), `positive_reg_res_wind_adj` (float8), `reserve_for_response` (float8), `total_positive_reserve` (float8), `percentage_of_standing_reserve_excess` (float8), `net_negative_regulating_reserve` (float8), `negative_reg_res_wind_adj` (float8), `negative_response_reserve` (float8), `total_negative_reserve` (float8), `maximum_loss_generation` (float8), `maximum_loss_demand` (float8), `positive_residual` (float8), `imbalance` (float8), `negative_residual` (float8), `sop_report_creation_time_gmt` (timestamp), `sop_d_and_c_time_gmt` (timestamp), `contingency_requirement` (float8), `operating_margin_surplus` (float8), `trigger_level` (float8), `no1_temx` (float8), `no1_teol` (float8), `no1_temi` (float8), `nw1_temx` (float8), `nw1_teol` (float8), `nw1_temi` (float8), `so1_temx` (float8), `so1_teol` (float8), `so1_temi` (float8), `sw1_temx` (float8), `sw1_teol` (float8), `sw1_temi` (float8), `britned_temx` (float8), `britned_teol` (float8), `britned_temi` (float8), `ewic_temx` (float8), `ewic_teol` (float8), `ewic_temi` (float8), `france_temx` (float8), `france_teol` (float8), `france_temi` (float8), `intifa2_temx` (float8), `intifa2_teol` (float8), `intifa2_temi` (float8), `moyle_temx` (float8), `moyle_teol` (float8), `moyle_temi` (float8), `nemo_temx` (float8), `nemo_teol` (float8), `nemo_temi` (float8), `ps_temx` (float8), `ps_teol` (float8), `ps_temi` (float8), `sto_temx` (float8), `sto_teol` (float8), `sto_temi` (float8), `sb_temx` (float8), `sb_teol` (float8), `sb_temi` (float8), `total_temx` (float8), `total_teol` (float8), `total_temi` (float8), `INTNSL_temx` (float8), `INTNSL_teol` (float8), `INTNSL_temi` (float8), `INTELEC_temx` (float8), `INTELEC_teol` (float8), `INTELEC_temi` (float8), `BAT_temx` (float8), `BAT_teol` (int4), `BAT_temi` (int4), `SLR_temx` (int4), `SLR_teol` (int4), `SLR_temi` (int4), `INTGRNL_temx` (int4), `INTGRNL_teol` (int4), `INTGRNL_temi` (int4), `INTVKL_temx` (int4), `INTVKL_teol` (int4), `INTVKL_temi` (int4)

- **Glossary of terms used in System Operating Plan** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

- **An Introduction to System Operator Plans** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)


## Trade Data

### Balancing Services Contract Enactment

`neso_data/trade-data/balancing-services-contract-enactment/` — 6 resource(s)

- **Balancing Service Contract Enactment 21-22 (Pre June 2021)** (CSV via API, ~79 rows)
  Fields: `Record` (text), `Counterparty` (text), `Unit` (text), `Start Time` (date), `End Time` (timestamp), `Volume` (float8), `Price` (float8), `Notes` (text), `Last Updated` (timestamp)

- **4 resources sharing this schema:** Balancing Contract Enactment FY 21-22, Balancing Contract Enactment FY 22-23, Balancing Contract Enactment FY 23-24, Balancing Contract Enactment FY 25-26 (CSV via API, ~81 rows combined)
  Fields: `ID` (text), `StartTime` (timestamp), `EndTime` (timestamp), `Volume` (float8), `Price` (float8), `Cost` (float8), `SO_Flag` (text), `Reason` (text), `AssetID` (text), `CP_Name` (text), `Area` (text), `Note` (text), `Last_Updated` (timestamp)

- **Balancing Contract Enactment (Archived files)** (ZIP file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Historic GTMA (Grid Trade Master Agreement) Grid Trade Master Agreement Trades Data _(cadence hint from name: static/historical reference)_

`neso_data/trade-data/historic-gtma-grid-trade-master-agreement-trades-data/` — 13 resource(s)

- **5 resources sharing this schema:** Historic GTMA Trades Data - Apr 2015 - March 2016, Historic GTMA Trades Data - Apr 2016 - March 2017, Historic GTMA Trades Data - Apr 2017 - March 2018, Historic GTMA Trades Data - Apr 2018 - March 2019, Historic GTMA Trades Data - Apr 2019 - March 2020 (CSV via API, ~51,230 rows combined)
  Fields: `Trade ID` (text), `Start Time` (text), `End Time` (text), `Volume` (numeric), `Price` (numeric), `Cost` (numeric), `SO Flag` (text)

- **2 resources sharing this schema:** Historic GTMA Trades Data - Apr 2020 - March 2021, Historic GTMA Trades Data - Apr 2021 - Mar 2022 (Pre June 2021) (CSV via API, ~63,012 rows combined)
  Fields: `Trade ID` (text), `Start Time` (timestamp), `End Time` (timestamp), `Volume` (numeric), `Price` (numeric), `Cost` (numeric), `SO Flag` (text)

- **6 resources sharing this schema:** Historic GTMA Trades FY 21-22, Historic GTMA Trades FY 22-23, Historic GTMA Trades FY 23-24, Historic GTMA Trades FY 24-25, Historic GTMA Trades FY 25-26, Historic GTMA Trades FY 26-27 (CSV via API, ~223,841 rows combined)
  Fields: `ID` (text), `StartTime` (timestamp), `EndTime` (timestamp), `Volume` (float8), `Price` (float8), `Cost` (float8), `SO_Flag` (text), `Reason` (text), `Note` (text), `Last_Updated` (timestamp)

### Index Linked Contract Volume

`neso_data/trade-data/index-linked-contract-volume/` — 5 resource(s)

- **4 resources sharing this schema:** Index Linked Contract Enactment FY 21-22, Index Linked Contract Enactment FY 22-23, Index Linked Contract Enactment FY 23-24, Index Linked Contract Enactment FY 24-25 (CSV via API, ~16 rows combined)
  Fields: `ID` (text), `StartTime` (timestamp), `EndTime` (timestamp), `Volume` (float8), `Price` (float8), `Cost` (float8), `SO_Flag` (text), `Reason` (text), `AssetID` (text), `CP_Name` (text), `Area` (text), `Note` (text), `Last_Updated` (timestamp)

- **Index Linked Contract Enactment  (Archived files)** (ZIP file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Interconnector Requirement And Auction Summary Data

`neso_data/trade-data/interconnector-requirement-and-auction-summary-data/` — 2 resource(s)

- **Interconnector Requirements and Auction Summary** (CSV via API, ~27,119 rows)
  Fields: `Published DateTime` (timestamp), `Notes` (text), `Auction ID` (text), `Auction Lot ID` (text), `Buy Sell` (text), `Volume Required` (numeric), `Qualified IC` (text), `Start Time` (timestamp), `End Time` (timestamp), `Bid Deadline` (timestamp), `Default Price` (numeric), `Clearing Price` (numeric), `Best Price` (numeric), `VWA Price` (numeric), `Cleared Volume` (numeric), `Total Bid Volume` (numeric), `IFA1 Volume` (numeric), `BN Volume` (numeric), `NEMO Volume` (numeric), `IFA2 Volume` (numeric), `EL Volume` (numeric), `VKL Volume` (numeric), `System Flag` (text)

- **Interconnector trading restrictions for NESO** (PDF file download — not a queryable table; content-type from probe: `text/plain;charset=UTF-8`)

### Super Stable Export Limit Contract Enactment

`neso_data/trade-data/super-stable-export-limit-contract-enactment/` — 6 resource(s)

- **Super Stable Export Limit Contract Enactment 20-21** (CSV via API, ~20 rows)
  Fields: `Record` (int4), `Unit` (text), `Start` (timestamp), `End` (timestamp), `Reduction (MW)` (float8), `Price (£/MW/hr)` (float8)

- **5 resources sharing this schema:** Super Stable Export Limit Contract Enactment FY 21-22, Super Stable Export Limit Contract Enactment FY 22-23, Super Stable Export Limit Contract Enactment FY 23-24, Super Stable Export Limit Contract Enactment FY 24-25, Super Stable Export Limit Contract Enactment FY 25-26 (CSV via API, ~7 rows combined)
  Fields: `ID` (text), `StartTime` (timestamp), `EndTime` (timestamp), `Volume` (float8), `Price` (float8), `Cost` (float8), `SO_Flag` (text), `Reason` (text), `AssetID` (text), `CP_Name` (text), `Area` (text), `Note` (text), `Last_Updated` (timestamp)

### Upcoming Trades

`neso_data/trade-data/upcoming-trades/` — 1 resource(s)

- **Upcoming Trades** (CSV via API, ~0 rows)
  Fields: `ID` (text), `Date` (date), `SP` (int4), `Volume` (float8), `Price` (float8), `Cost` (float8), `SO_Flag` (text), `Reason` (text), `Note` (text), `Last_Updated` (timestamp)


