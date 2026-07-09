# GIE AGSI+ / ALSI / IIP — Data Field Reference

Field reference for the CSVs produced by `gie_collector.py`. Grounded in both
the official `GIE_API_documentation_v013.pdf` (6 March 2025) and the live API
responses actually collected — a few fields exist in production that aren't
in the v013 PDF (noted below), and a few documented fields are conditional
on which "level" of the tree a row comes from (EU / country / company /
facility). Units and descriptions below match GIE's own definitions.

## Platforms at a glance

| Platform | Covers | Base URL | Historical range |
|---|---|---|---|
| AGSI | Gas storage (facility/company/country/EU) | `https://agsi.gie.eu/api` | Since 2011-01-01, or facility's operational start |
| ALSI | LNG terminals (facility/company/country/EU) | `https://alsi.gie.eu/api` | Since 2012-01-01, or facility's operational start |
| IIP | Urgent Market Messages (REMIT UMM disclosure) | `https://iip.gie.eu/api` | Since GIE became IIP host; per-message |

Auth is a `x-key: <API key>` header on every request. GIE enforces 60 calls/
minute per account/IP; `gie_collector.py` throttles to ~50/min and backs off
on the documented penalty.

**This collector's scope is GB\* only** (post-Brexit UK, tagged `GB*` by GIE
— distinct from pre-Brexit `GB`, which stopped updating 2020-12-30). Every
GB\*-tagged facility's history here starts **2020-12-31**, not 2011, because
GIE re-coded UK facilities under new EIC codes at Brexit rather than
continuing the old `GB` series.

## Update frequency & lag

| Dataset | Frequency | Lag / publication timing |
|---|---|---|
| AGSI/ALSI facility & aggregate reports | Daily — one row per gas day per entity | Same-day, first published ~19:30 CET for the *previous* gas day, with a second catch-up publication at 23:00 CET for operators who miss the first run |
| AGSI/ALSI unavailability reports | Event-driven (REMIT disclosure) | Published whenever the operator files it — can be days/weeks ahead for planned maintenance, or near-real-time for unplanned outages. No fixed schedule. |
| News / service announcements | Ad hoc | Whenever GIE posts an announcement (data corrections, onboarding changes, etc.) |
| IIP Urgent Market Messages | Event-driven (REMIT UMM disclosure) | Published whenever a market participant/SSO/LSO files it. Revisions to an already-published message appear as new versions (see `prev`, below), not edits in place. |

Data quality on every AGSI/ALSI row is flagged via `status`: `E` (estimated),
`C` (confirmed), or `N` (no data reported yet — often the case for the most
recent 1–2 days before an operator's report lands).

## File layout

```
gie_data/
  agsi/countries/GB_.csv                 <- GB* aggregate (all UK storage combined)
  agsi/companies/GB_/{company}.csv       <- one row per gas day, per company
  agsi/facilities/GB_/{company}/{facility}.csv   <- one row per gas day, per facility
  agsi/unavailability.csv                <- REMIT unavailability notices
  agsi/news.csv                          <- GIE service announcements (GB*-relevant only)
  alsi/...                               <- same layout, for LNG
  iip/umm.csv                            <- Urgent Market Messages (GB*-relevant only)
```

Every CSV also carries a **`_key`** column — a synthetic column the collector
adds itself (not part of the GIE API) to detect and merge corrections across
runs. It's safe to ignore for analysis.

Nested API objects (e.g. `country`, `inventory`, `message`) are flattened
into dotted columns (`country.name`, `country.code`, …). Fields that are
JSON *arrays* with variable shape (`info`, `entities`, `marketParticipant`,
`balancingZone`, `prev`) are stored as JSON-encoded strings in a single
column rather than flattened, since their length varies row to row.

---

## AGSI — storage facility / aggregate report fields

One row per gas day. Applies to the country, company, and facility CSVs (the
EU/Non-EU aggregate rows aren't collected in this GB\*-scoped build, but use
the same shape).

| Field | Scope | Unit | Description |
|---|---|---|---|
| `name` | all | – | Display name of the entity this row is for (country/company/facility) |
| `code` | all | – | EIC or short code of the entity |
| `url` | all | – | URL path fragment used by AGSI for direct linking |
| `longitude` | facility only | decimal degrees | Facility longitude |
| `latitude` | facility only | decimal degrees | Facility latitude |
| `type` | facility only | – | Facility type: `DSR` Depleted Field, `ASR` Aquifer, `ASF` Salt Cavern, `SRC` Rock Cavern, `GRP` Virtual Storage Group |
| `publication_link` | company only | URL | Link to the company's own website |
| `transparency_template` | company only | URL | Link to the company's REMIT transparency template |
| `updatedAt` | all | datetime | Timestamp this specific row was last touched/corrected |
| `gasDayStart` | all | date | The gas day this row reports on — this is the row's primary date key |
| `gasDayEnd` | all | date | End of the gas day window (observed live; not listed in the v013 PDF) |
| `gasInStorage` | all | TWh | Total gas in storage at end of the gas day (4-digit accuracy) |
| `consumption` | country/EU/NE only | TWh | Estimated national gas consumption for the day |
| `consumptionFull` | country/EU/NE only | % | Storage-covered share of that day's consumption |
| `injection` | all | GWh/d | Gas injected into storage during the gas day |
| `withdrawal` | all | GWh/d | Gas withdrawn from storage during the gas day |
| `netWithdrawal` | all | GWh/d | `withdrawal − injection` for the gas day |
| `workingGasVolume` | all | TWh | Technical/working gas capacity (max storable) |
| `injectionCapacity` | all | GWh/d | Maximum technical injection rate |
| `withdrawalCapacity` | all | GWh/d | Maximum technical withdrawal rate |
| `contractedCapacity` | company/facility only | TWh | Capacity contracted out to users |
| `availableCapacity` | company/facility only | TWh | Technical capacity not yet contracted, still available |
| `coveredCapacity` | country/EU/NE only | % | Share of national/regional capacity covered by reporting operators |
| `status` | all | E/C/N | Estimated / Confirmed / No data |
| `trend` | all | +/− | Sign of `(injection − withdrawal) / workingGasVolume` |
| `full` | all | % | Fill level: `gasInStorage / workingGasVolume` |
| `info` | all | JSON array | Linked Service Announcement(s), if any apply to this row |

## AGSI — unavailability report fields

One row per REMIT unavailability notice (not per gas day — these are
event records, so a single multi-day outage is one row, not one per day).

| Field | Unit | Description |
|---|---|---|
| `published` | datetime | When the operator submitted this notice |
| `country.name` / `country.code` | – | Country of the affected facility |
| `company.name` / `company.eic` | – | Reporting operator |
| `facility.name` / `facility.eic` | – | Affected storage facility |
| `start` | datetime | Start of the unavailability window |
| `end` | datetime | End of the unavailability window |
| `volume` | TWh | Unavailable storage volume (3-digit accuracy) |
| `injection` | GWh/d | Unavailable injection capacity (1-digit accuracy) |
| `withdrawal` | GWh/d | Unavailable withdrawal capacity (1-digit accuracy) |
| `description` | text | Free-text explanation from the operator |
| `end_flag` | Estimated/Confirmed | Whether the `end` date is firm or an estimate |
| `type` | Planned/Unplanned | Whether the outage was scheduled or a forced/unplanned event |

---

## ALSI — LNG facility / aggregate report fields

Same "one row per gas day" model as AGSI, with LNG-specific measures.

| Field | Scope | Unit | Description |
|---|---|---|---|
| `name` | all | – | Display name of the entity |
| `code` | all | – | EIC or short code |
| `url` | all | – | URL path fragment for direct linking |
| `longitude` / `latitude` | facility only | decimal degrees | Terminal coordinates |
| `type` | facility only | – | `FSRU` Floating Storage Regasification Unit, `LAND` Land-based terminal |
| `publication_link` / `transparency_template` | company only | URL | Company website / REMIT transparency template |
| `updatedAt` | all | datetime | Last-touched timestamp for this row |
| `gasDayStart` / `gasDayEnd` | all | date | Gas day this row covers (primary date key) |
| `inventory.lng` | all | 10³ m³ LNG | LNG in tanks at end of gas day |
| `inventory.gwh` | all | GWh (approx.) | Same inventory, converted to energy units |
| `sendOut` | all | GWh/d | Gas sent out of the terminal (regasified) during the gas day |
| `dtmi.lng` | all | 10³ m³ LNG | Declared Total Maximum Inventory — LNG storage capacity |
| `dtmi.gwh` | all | GWh (approx.) | DTMI in energy units |
| `dtrs` | all | GWh/d | Declared Total Reference Send-out — technical send-out capacity |
| `contractedCapacity` | company/facility only | GWh/d | Send-out capacity contracted to users |
| `availableCapacity` | company/facility only | GWh/d | Technical capacity not yet contracted |
| `coveredCapacity` | country/EU/NE/AI only | % | Share of national/regional capacity covered by reporting operators |
| `status` | all | E/C/N | Estimated / Confirmed / No data |
| `info` | all | JSON array | Linked Service Announcement(s), if any |

## ALSI — unavailability report fields

Same event-record model as AGSI's unavailability, one row per notice.

| Field | Unit | Description |
|---|---|---|
| `published` | datetime | When the operator submitted this notice |
| `country.name` / `country.code` | – | Country of the affected terminal |
| `company.name` / `company.eic` | – | Reporting operator |
| `facility.name` / `facility.eic` | – | Affected LNG terminal |
| `start` / `end` | datetime | Unavailability window |
| `capacity` | GWh/d | Unavailable send-out capacity (3-digit accuracy) |
| `description` | text | Free-text explanation |
| `end_flag` | Estimated/Confirmed | Firmness of the `end` date |
| `type` | Planned/Unplanned | Scheduled vs. forced outage |

---

## News / service announcements (shared AGSI + ALSI shape)

One row per announcement. Not paginated by GIE — always returned in full.

| Field | Unit | Description |
|---|---|---|
| `url` | id | Numeric ID; append as `?url=<id>` to link directly to this item |
| `start_at` | datetime | When the announcement/situation begins applying |
| `end_at` | datetime / null | When it stops applying, if it has an end |
| `title` | text | Headline |
| `summary` | text | Short summary (often blank) |
| `details` | HTML text | Full announcement body |
| `entities` | JSON array | Countries/companies/facilities the announcement pertains to (`{name, image}` per entry) |

---

## IIP — Urgent Market Message (UMM) fields

One row per REMIT Urgent Market Message. `iip/umm.csv` is empty in this GB\*
build — confirmed (not a bug): none of the 6 GB\* companies have filed any
UMMs through GIE's IIP, consistent with post-Brexit UK REMIT reporting not
routing through GIE. Schema below reflects the general shape seen on
non-UK messages.

| Field | Unit | Description |
|---|---|---|
| `submitted` | datetime | When the reporting entity filed this message |
| `reportingEntity.name` / `.code` / `.type` | – | The SSO/LSO/TSO that filed the report; `reportingEntityString` is the same info pre-joined into one string |
| `message.messageId` | id | Message identifier, includes a version suffix (revisions get a new ID) |
| `message.messageType` | text | e.g. "Injection unavailability", "Storage facility unavailability" |
| `message.reportType` | text | `unavailabilityOfGasFacilitiesReport` (Gas) or Other Market Information |
| `message.unavailabilityType` | Planned/Unplanned/null | Null for non-Gas report types |
| `status` | Active/Inactive/Dismissed | Current status of this UMM |
| `from` / `to` | datetime | Unavailability window |
| `duration` | text | Human-readable duration, e.g. "4 days" |
| `marketParticipant` | JSON array | Affected market participant(s) (`{code, name}`); `marketParticipantString` is the pre-joined string |
| `asset.name` / `.code` | – | Specific affected asset/unit; `assetString` is the pre-joined string |
| `direction` | Entry/Exit | Which flow direction is affected |
| `unavailable.capacity` / `.unit` | float / text (usually GWh/d) | Unavailable capacity; `unavailableString` pre-joins both |
| `available.capacity` / `.unit` | float / text | Remaining available capacity; `availableString` pre-joins both |
| `technical.capacity` / `.unit` | float / text | Full technical capacity; `technicalString` pre-joins both |
| `balancingZone` | JSON array | Balancing zone(s) affected (`{code, name}`); `balancingZoneString` is the pre-joined string |
| `unavailabilityReason` | text | Operator's stated reason (e.g. "Maintenance of compressor unit") |
| `remarks` | text | Additional free-text remarks |
| `published` | datetime | Display timestamp on iip.gie.eu — distinct from `submitted` |
| `rss` | base64 string | The complete underlying REMIT XML report |
| `prev` | JSON array | Prior version(s) of this same message, in order, if this UMM has been revised |
