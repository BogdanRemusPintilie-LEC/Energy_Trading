"""
Elexon BMRS Insights Solution API — GB/UK Data Collector
Base URL: https://data.elexon.co.uk/bmrs/api/v1
No API key required. Public data.

Endpoint coverage (sourced from live Swagger at /swagger/v1/swagger.json):
  - 87 /datasets/* endpoints
  - 60+ opinionated endpoints: demand, forecast, generation, balancing,
    settlement, remit, system, lss, soso, lolpdrm, saa
  - 12 data-status/* endpoints
  - 6 reference/* endpoints

Usage:
  # Rolling window — last 24 hours
  python bmrs_collector.py --mode rolling

  # Full YTD backfill (2026-01-01 to today)
  python bmrs_collector.py --mode backfill

  # Custom date range
  python bmrs_collector.py --mode backfill --from 2026-03-01 --to 2026-06-01

  # Specific datasets only
  python bmrs_collector.py --mode rolling --datasets FUELINST FREQ WINDFOR

  # Skip slow period-granular settlement endpoints (recommended for large backfills)
  python bmrs_collector.py --mode backfill --skip-period-granular
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import logging
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"
CHUNK_DAYS = 7           # Days per request for range endpoints
RETRY_ATTEMPTS = 5
RETRY_BACKOFF_BASE = 2   # seconds; doubles each retry
REQUEST_DELAY = 0.3      # polite inter-request pause (seconds)
BACKFILL_START = date(2026, 1, 1)
SETTLEMENT_PERIODS = range(1, 51)   # GB has up to 50 half-hourly periods per day
BID_OFFER_TYPES = ["BID", "OFFER"]
# Recent triad seasons to collect for path-param triad endpoints
TRIAD_SEASONS = ["2023-24", "2024-25", "2025-26"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("bmrs")


# ---------------------------------------------------------------------------
# Endpoint catalogue
#
# Endpoint types:
#   "range"              → ?from=YYYY-MM-DD&to=YYYY-MM-DD  (chunked weekly)
#   "settlement_date_qp" → ?settlementDate=YYYY-MM-DD      (query param, iterate by day)
#   "settlement_date_pp" → /{settlementDate}               (path param, iterate by day)
#   "settlement_bo_date" → /{bidOffer}/{settlementDate}    (iterate BID/OFFER × day)
#   "settlement_period"  → /{settlementDate}/{settlementPeriod}  (iterate day × 1-50)
#   "settlement_bo_period" → /{bidOffer}/{settlementDate}/{settlementPeriod}
#   "triad_season"       → /{triadSeason}                  (iterate TRIAD_SEASONS)
#   "static"             → no date params, fetched once
# ---------------------------------------------------------------------------

# --- /datasets/* (all use from/to range) -----------------------------------

DATASET_ENDPOINTS: list[dict[str, Any]] = [
    # Generation
    {"name": "AGPT"},         # Actual Aggregated Generation Per Type
    {"name": "B1610"},        # Actual Generation Output Per Generation Unit
    {"name": "AGWS"},         # Actual or Estimated Wind & Solar Generation
    {"name": "BOALF"},        # Bid Offer Acceptance Level Final
    {"name": "FOU2T14D"},     # Generation forecast 2–14 day
    {"name": "FOU2T3YW"},     # Generation forecast 3-year weekly
    {"name": "FUELINST"},     # Instantaneous generation by fuel type
    {"name": "FUELHH"},       # Half-hourly generation by fuel type
    {"name": "INDGEN"},       # Indicated generation
    {"name": "WINDFOR"},      # Wind generation forecast
    {"name": "UOU2T14D"},     # Unplanned availability forecast 2–14 day
    {"name": "UOU2T3YW"},     # Unplanned availability forecast 3-year weekly
    # Demand
    {"name": "INDDEM"},       # Indicated demand
    {"name": "IMBALNGC"},     # Indicated imbalance (NGC)
    {"name": "INDO"},         # Indicated national demand outturn
    {"name": "INDOD"},        # Indicated outturn demand
    {"name": "ITSDO"},        # Initial transmission system demand outturn
    {"name": "NDF"},          # National demand forecast
    {"name": "NDFD"},         # National demand forecast day-ahead
    {"name": "NDFW"},         # National demand forecast week-ahead
    {"name": "NOU2T14D"},     # Demand forecast 2–14 day
    {"name": "NOU2T3YW"},     # Demand forecast 3-year weekly
    {"name": "TSDF"},         # Transmission system demand forecast
    {"name": "TSDFD"},        # TSDF day-ahead
    {"name": "TSDFW"},        # TSDF week-ahead
    # Balancing & imbalance
    {"name": "BOD"},          # Bid Offer Data
    {"name": "DISBSAD"},      # Balancing Services Adjustment Data
    {"name": "MID"},          # Market Index Data
    {"name": "NETBSAD"},      # Net Balancing Services Adjustment Data
    {"name": "NONBM"},        # Non-BM Balancing Services
    {"name": "QAS"},          # Balancing Services Volume
    # Physical / dynamic
    {"name": "MILS"},         # Stable Import Limit per BMU
    {"name": "MELS"},         # Stable Export Limit per BMU
    {"name": "MDP"},          # Market Demand Price
    {"name": "MDV"},          # Market Demand Volume
    {"name": "MDB"},          # Maximum Delivery Block
    {"name": "MDO"},          # Maximum Delivery Duration
    {"name": "MELNGC"},       # Day-ahead margin (NGC)
    {"name": "MNZT"},         # Minimum Non-Zero Time
    {"name": "MZT"},          # Minimum Zero Time
    {"name": "NDZ"},          # Notice to Deviate from Zero
    {"name": "NTB"},          # Notice to Deliver Bids
    {"name": "NTO"},          # Notice to Deliver Offers
    {"name": "OCNMF3Y"},      # Operational Cancelled Network Model Forecast 3Y
    {"name": "OCNMF3Y2"},     # OCNM Forecast 3Y (version 2)
    {"name": "OCNMFD"},       # OCNM Forecast Day
    {"name": "OCNMFD2"},      # OCNM Forecast Day (version 2)
    {"name": "PN"},           # Physical Notifications
    {"name": "QPN"},          # Quiescent Physical Notifications
    {"name": "RDRE"},         # Run Down Rate Export
    {"name": "RDRI"},         # Run Down Rate Import
    {"name": "RURE"},         # Run Up Rate Export
    {"name": "RURI"},         # Run Up Rate Import
    {"name": "SEL"},          # Stable Export Limit
    {"name": "SIL"},          # Stable Import Limit
    # Interconnectors & transfers
    {"name": "IGCA"},         # Interconnector Allocation
    {"name": "IGCPU"},        # Interconnector Power & Usage
    {"name": "ATL"},          # Actual Transfer Levels
    {"name": "DATL"},         # Day-Ahead Transfer Levels
    {"name": "MATL"},         # Market Accepted Transfer Levels
    {"name": "WATL"},         # Weekly Accepted Transfer Levels
    {"name": "YATL"},         # Year-Ahead Transfer Levels
    # Availability
    {"name": "ABUC"},         # Actual Balancing Unconstrained Capacity
    {"name": "AOBE"},         # Actual Or Best Estimate Availability
    {"name": "BEB"},          # Best Estimated Balance
    {"name": "CBS"},          # Capacity Below Stable Limit
    {"name": "CCM"},          # Capacity Contracted for Mandatory Services
    {"name": "DAG"},          # Day-Ahead Generating Plant Availability
    {"name": "DCI"},          # De-rated Capacity Index
    {"name": "DGWS"},         # De-rated Generating plant availability (wind & solar)
    {"name": "FEIB"},         # Final Energy Imbalance and Balancing Services
    {"name": "LOLPDRM"},      # Loss of Load Probability / De-rated Margin
    {"name": "PBC"},          # Plant Balance Contribution
    {"name": "PPBR"},         # Plant Physical Balance Reserve
    {"name": "RZDF"},         # Reserve Zone Demand Forecast
    {"name": "RZDR"},         # Reserve Zone De-rated Reserve
    {"name": "SOSO"},         # So-So Offers
    # Settlements & cash flows
    {"name": "CDN"},          # Credit Default Notice
    {"name": "REMIT"},        # REMIT data (dataset endpoint)
    {"name": "TUDM"},         # Total Unconstrained Daily Margin
    {"name": "YAFM"},         # Year-Ahead Forecast Margin
    # System / misc
    {"name": "FREQ"},         # System Frequency
    {"name": "TEMP"},         # Temperature
    {"name": "SYSWARN"},      # System Warnings
]

# --- Opinionated range endpoints (from/to) ----------------------------------

RANGE_OPINIONATED_ENDPOINTS: list[dict[str, Any]] = [
    # Balancing non-BM
    {"name": "DISBSAD_SUMMARY",      "path": "/balancing/nonbm/disbsad/summary"},
    {"name": "NETBSAD_RANGE",        "path": "/balancing/nonbm/netbsad"},
    {"name": "NONBM_STOR",           "path": "/balancing/nonbm/stor"},
    {"name": "NONBM_VOLUMES",        "path": "/balancing/nonbm/volumes"},
    {"name": "MARKET_INDEX_PRICE",   "path": "/balancing/pricing/market-index"},
    {"name": "SETTLEMENT_NOTICES",   "path": "/balancing/settlement/default-notices"},
    # Demand (opinionated views)
    {"name": "DEMAND_OUTTURN",           "path": "/demand/outturn"},
    {"name": "DEMAND_OUTTURN_DAILY",     "path": "/demand/outturn/daily"},
    {"name": "DEMAND_OUTTURN_SUMMARY",   "path": "/demand/outturn/summary"},
    {"name": "DEMAND_ACTUAL_TOTAL",      "path": "/demand/actual/total"},
    {"name": "DEMAND_TOTAL_ACTUAL",      "path": "/demand/total/actual"},
    {"name": "DEMAND_SUMMARY",           "path": "/demand/summary"},
    {"name": "DEMAND_PEAK",              "path": "/demand/peak"},
    {"name": "DEMAND_PEAK_INDICATIVE",   "path": "/demand/peak/indicative"},
    {"name": "DEMAND_TRIAD",             "path": "/demand/peak/triad"},
    {"name": "DEMAND_RESTORATION_ZONE",  "path": "/demand/by-restoration-zone/restored/submissions"},
    # Forecast — availability
    {"name": "FCST_AVAIL_DAILY",         "path": "/forecast/availability/daily"},
    {"name": "FCST_AVAIL_DAILY_EVOL",    "path": "/forecast/availability/daily/evolution"},
    {"name": "FCST_AVAIL_DAILY_HIST",    "path": "/forecast/availability/daily/history"},
    {"name": "FCST_AVAIL_WEEKLY",        "path": "/forecast/availability/weekly"},
    {"name": "FCST_AVAIL_WEEKLY_EVOL",   "path": "/forecast/availability/weekly/evolution"},
    {"name": "FCST_AVAIL_WEEKLY_HIST",   "path": "/forecast/availability/weekly/history"},
    # Forecast — demand
    {"name": "FCST_DEMAND_DAILY",        "path": "/forecast/demand/daily"},
    {"name": "FCST_DEMAND_DAILY_EVOL",   "path": "/forecast/demand/daily/evolution"},
    {"name": "FCST_DEMAND_DAILY_HIST",   "path": "/forecast/demand/daily/history"},
    {"name": "FCST_DEMAND_DA",           "path": "/forecast/demand/day-ahead"},
    {"name": "FCST_DEMAND_DA_EVOL",      "path": "/forecast/demand/day-ahead/evolution"},
    {"name": "FCST_DEMAND_DA_HIST",      "path": "/forecast/demand/day-ahead/history"},
    {"name": "FCST_DEMAND_DA_PEAK",      "path": "/forecast/demand/day-ahead/peak"},
    {"name": "FCST_DEMAND_TOTAL_DA",     "path": "/forecast/demand/total/day-ahead"},
    {"name": "FCST_DEMAND_TOTAL_WA",     "path": "/forecast/demand/total/week-ahead"},
    {"name": "FCST_DEMAND_WEEKLY",       "path": "/forecast/demand/weekly"},
    {"name": "FCST_DEMAND_WEEKLY_EVOL",  "path": "/forecast/demand/weekly/evolution"},
    {"name": "FCST_DEMAND_WEEKLY_HIST",  "path": "/forecast/demand/weekly/history"},
    # Forecast — generation
    {"name": "FCST_GEN_DA",              "path": "/forecast/generation/day-ahead"},
    {"name": "FCST_GEN_WIND",            "path": "/forecast/generation/wind"},
    {"name": "FCST_GEN_WIND_SOLAR_DA",   "path": "/forecast/generation/wind-and-solar/day-ahead"},
    {"name": "FCST_GEN_WIND_EVOL",       "path": "/forecast/generation/wind/evolution"},
    {"name": "FCST_GEN_WIND_HIST",       "path": "/forecast/generation/wind/history"},
    {"name": "FCST_GEN_WIND_PEAK",       "path": "/forecast/generation/wind/peak"},
    # Forecast — indicated / margin / surplus / system
    {"name": "FCST_INDICATED_DA",        "path": "/forecast/indicated/day-ahead"},
    {"name": "FCST_INDICATED_DA_EVOL",   "path": "/forecast/indicated/day-ahead/evolution"},
    {"name": "FCST_INDICATED_DA_HIST",   "path": "/forecast/indicated/day-ahead/history"},
    {"name": "FCST_MARGIN_DAILY",        "path": "/forecast/margin/daily"},
    {"name": "FCST_MARGIN_DAILY_EVOL",   "path": "/forecast/margin/daily/evolution"},
    {"name": "FCST_MARGIN_DAILY_HIST",   "path": "/forecast/margin/daily/history"},
    {"name": "FCST_MARGIN_WEEKLY",       "path": "/forecast/margin/weekly"},
    {"name": "FCST_MARGIN_WEEKLY_EVOL",  "path": "/forecast/margin/weekly/evolution"},
    {"name": "FCST_MARGIN_WEEKLY_HIST",  "path": "/forecast/margin/weekly/history"},
    {"name": "FCST_SURPLUS_DAILY",       "path": "/forecast/surplus/daily"},
    {"name": "FCST_SURPLUS_DAILY_EVOL",  "path": "/forecast/surplus/daily/evolution"},
    {"name": "FCST_SURPLUS_DAILY_HIST",  "path": "/forecast/surplus/daily/history"},
    {"name": "FCST_SURPLUS_WEEKLY",      "path": "/forecast/surplus/weekly"},
    {"name": "FCST_SURPLUS_WEEKLY_EVOL", "path": "/forecast/surplus/weekly/evolution"},
    {"name": "FCST_SURPLUS_WEEKLY_HIST", "path": "/forecast/surplus/weekly/history"},
    {"name": "FCST_LOLP",                "path": "/forecast/system/loss-of-load"},
    # Generation (opinionated)
    {"name": "GEN_ACTUAL_PER_TYPE",      "path": "/generation/actual/per-type"},
    {"name": "GEN_ACTUAL_PER_TYPE_DAY",  "path": "/generation/actual/per-type/day-total"},
    {"name": "GEN_ACTUAL_WIND_SOLAR",    "path": "/generation/actual/per-type/wind-and-solar"},
    {"name": "GEN_OUTTURN",              "path": "/generation/outturn"},
    {"name": "GEN_OUTTURN_HH_INTERCON",  "path": "/generation/outturn/halfHourlyInterconnector"},
    {"name": "GEN_OUTTURN_INTERCON",     "path": "/generation/outturn/interconnectors"},
    {"name": "GEN_OUTTURN_SUMMARY",      "path": "/generation/outturn/summary"},
    # LOLPDRM, LSS, SOSO
    {"name": "LOLPDRM_EVOL",            "path": "/lolpdrm/forecast/evolution"},
    {"name": "LSS_LOAD_SHAPE_PERIOD",   "path": "/lss/load-shape-period"},
    {"name": "LSS_LOAD_SHAPE_TOTALS",   "path": "/lss/load-shape-totals"},
    {"name": "SOSO_PRICES",             "path": "/soso/prices"},
    # REMIT (opinionated)
    {"name": "REMIT_BY_EVENT",          "path": "/remit/list/by-event"},
    {"name": "REMIT_BY_PUBLISH",        "path": "/remit/list/by-publish"},
    {"name": "REMIT_REVISIONS",         "path": "/remit/revisions"},
    # System
    {"name": "SYSTEM_DCI",              "path": "/system/demand-control-instructions"},
    {"name": "SYSTEM_FREQ",             "path": "/system/frequency"},
    {"name": "SYSTEM_WARNINGS",         "path": "/system/warnings"},
    {"name": "TEMPERATURE",             "path": "/temperature"},
]

# --- Settlement date query-param endpoints (iterate day by day) -------------
# These accept ?settlementDate=YYYY-MM-DD and return all periods for that day.

SETTLEMENT_DATE_QP_ENDPOINTS: list[dict[str, Any]] = [
    {"name": "DYNAMIC_ALL",              "path": "/balancing/dynamic/all"},
    {"name": "DYNAMIC_PARAMS_ALL",       "path": "/balancing/dynamic/dynamicParameters/all"},
    {"name": "DYNAMIC_RATES_ALL",        "path": "/balancing/dynamic/rates/all"},
    {"name": "PHYSICAL_ALL",             "path": "/balancing/physical/all"},
    {"name": "BID_OFFER_ALL",            "path": "/balancing/bid-offer/all"},
    {"name": "ACCEPTANCES_ALL",          "path": "/balancing/acceptances/all"},
    {"name": "DISBSAD_DETAILS",          "path": "/balancing/nonbm/disbsad/details"},
]

# --- Settlement path-param endpoints: /{settlementDate} (iterate by day) ----

SETTLEMENT_DATE_PP_ENDPOINTS: list[dict[str, Any]] = [
    {"name": "SETTLEMENT_MARKET_DEPTH", "path": "/balancing/settlement/market-depth/{settlementDate}"},
    {"name": "SETTLEMENT_MESSAGES",     "path": "/balancing/settlement/messages/{settlementDate}"},
    {"name": "SETTLEMENT_SYS_PRICES",   "path": "/balancing/settlement/system-prices/{settlementDate}"},
    {"name": "SAA_EXEMPT_VOLUME",       "path": "/saa/datasets/total-exempt-volume/{settlementDate}"},
]

# --- Settlement path-param: /{bidOffer}/{settlementDate} --------------------
# Iterated for each of BID_OFFER_TYPES × each day in range.

SETTLEMENT_BO_DATE_ENDPOINTS: list[dict[str, Any]] = [
    {"name": "SETTLEMENT_ACCEPT_VOLS",  "path": "/balancing/settlement/acceptance/volumes/all/{bidOffer}/{settlementDate}"},
    {"name": "SETTLEMENT_INDIC_CF",     "path": "/balancing/settlement/indicative/cashflows/all/{bidOffer}/{settlementDate}"},
    {"name": "SETTLEMENT_INDIC_VOLS",   "path": "/balancing/settlement/indicative/volumes/all/{bidOffer}/{settlementDate}"},
]

# --- Settlement path-param: /{settlementDate}/{settlementPeriod} ------------
# Iterated for each day × each period 1-50.
# WARNING: for backfill this is ~8,850 requests per endpoint. Use
# --skip-period-granular to omit these during large backfills.

SETTLEMENT_PERIOD_PP_ENDPOINTS: list[dict[str, Any]] = [
    {"name": "SETTLEMENT_SUMMARY",      "path": "/balancing/settlement/summary/{settlementDate}/{settlementPeriod}"},
    {"name": "SETTLEMENT_ACCEPT_ALL",   "path": "/balancing/settlement/acceptances/all/{settlementDate}/{settlementPeriod}"},
]

# --- Settlement path-param: /{bidOffer}/{settlementDate}/{settlementPeriod} -
# Iterated for BID/OFFER × each day × each period. Even more requests.

SETTLEMENT_BO_PERIOD_ENDPOINTS: list[dict[str, Any]] = [
    {"name": "SETTLEMENT_STACK",        "path": "/balancing/settlement/stack/all/{bidOffer}/{settlementDate}/{settlementPeriod}"},
]

# --- Triad season endpoints: /{triadSeason} ---------------------------------
# Fetched for each season in TRIAD_SEASONS.

TRIAD_SEASON_ENDPOINTS: list[dict[str, Any]] = [
    {"name": "DEMAND_PEAK_INDIC_OPS",   "path": "/demand/peak/indicative/operational/{triadSeason}"},
    {"name": "DEMAND_PEAK_INDIC_SETT",  "path": "/demand/peak/indicative/settlement/{triadSeason}"},
]

# --- Static endpoints (fetched once, no date params) ------------------------

STATIC_ENDPOINTS: list[dict[str, Any]] = [
    # Reference data
    {"name": "REF_BMUNITS",             "path": "/reference/bmunits/all"},
    {"name": "REF_INTERCONNECTORS",     "path": "/reference/interconnectors/all"},
    {"name": "REF_FUELTYPES",           "path": "/reference/fueltypes/all"},
    {"name": "REF_REMIT_ASSETS",        "path": "/reference/remit/assets/all"},
    {"name": "REF_REMIT_FUELTYPES",     "path": "/reference/remit/fueltypes/all"},
    {"name": "REF_REMIT_PARTICIPANTS",  "path": "/reference/remit/participants/all"},
    # Latest/current snapshots
    {"name": "DATASETS_METADATA",       "path": "/datasets/metadata/latest"},
    {"name": "ACCEPTANCES_LATEST",      "path": "/balancing/acceptances/all/latest"},
    {"name": "GEN_OUTTURN_CURRENT",     "path": "/generation/outturn/current"},
    {"name": "GEN_OUTTURN_FUELINSTHHCUR","path": "/generation/outturn/FUELINSTHHCUR"},
    {"name": "DEMAND_ROLLING",          "path": "/demand/rollingSystemDemand"},
    {"name": "FCST_DEMAND_DA_EARLIEST", "path": "/forecast/demand/day-ahead/earliest"},
    {"name": "FCST_DEMAND_DA_LATEST",   "path": "/forecast/demand/day-ahead/latest"},
    {"name": "FCST_DEMAND_WA_LATEST",   "path": "/forecast/demand/total/week-ahead/latest"},
    {"name": "FCST_WIND_EARLIEST",      "path": "/forecast/generation/wind/earliest"},
    {"name": "FCST_WIND_LATEST",        "path": "/forecast/generation/wind/latest"},
]

# --- Data-status endpoints (fetch once, return latest availability status) --

DATA_STATUS_ENDPOINTS: list[dict[str, Any]] = [
    {"name": "STATUS_BOALF",    "path": "/data-status/BOALF"},
    {"name": "STATUS_BOAV",     "path": "/data-status/BOAV"},
    {"name": "STATUS_BOD",      "path": "/data-status/BOD"},
    {"name": "STATUS_DISBSAD",  "path": "/data-status/DISBSAD"},
    {"name": "STATUS_DISEBSP",  "path": "/data-status/DISEBSP"},
    {"name": "STATUS_DISPTAV",  "path": "/data-status/DISPTAV"},
    {"name": "STATUS_EBOCF",    "path": "/data-status/EBOCF"},
    {"name": "STATUS_FREQ",     "path": "/data-status/FREQ"},
    {"name": "STATUS_ISPSTACK", "path": "/data-status/ISPSTACK"},
    {"name": "STATUS_NETBSAD",  "path": "/data-status/NETBSAD"},
    {"name": "STATUS_PN",       "path": "/data-status/PN"},
    {"name": "STATUS_REMIT",    "path": "/data-status/REMIT"},
]


# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------

SESSION = requests.Session()
SESSION.headers.update({"Accept": "text/csv, application/json"})


def _get(url: str, params: dict) -> requests.Response | None:
    """GET with exponential-backoff retry on 429 / 5xx."""
    for attempt in range(RETRY_ATTEMPTS):
        try:
            resp = SESSION.get(url, params=params, timeout=30)
        except requests.RequestException as exc:
            log.warning("Network error (attempt %d/%d): %s", attempt + 1, RETRY_ATTEMPTS, exc)
            time.sleep(RETRY_BACKOFF_BASE ** attempt)
            continue

        if resp.status_code == 200:
            return resp
        if resp.status_code == 429:
            wait = RETRY_BACKOFF_BASE ** (attempt + 2)
            log.warning("Rate limited — sleeping %ds (attempt %d/%d)", wait, attempt + 1, RETRY_ATTEMPTS)
            time.sleep(wait)
        elif resp.status_code in (400, 404, 422):
            log.debug("HTTP %d — %s %s — skipping", resp.status_code, url, params)
            return None
        else:
            log.warning("HTTP %d (attempt %d/%d) — %s", resp.status_code, attempt + 1, RETRY_ATTEMPTS, url)
            time.sleep(RETRY_BACKOFF_BASE ** attempt)

    log.error("All %d attempts failed — %s", RETRY_ATTEMPTS, url)
    return None


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------

def _parse_response(resp: requests.Response, label: str) -> list[dict]:
    """Parse CSV or JSON response into a list of row dicts."""
    text = resp.text.strip()
    if not text:
        return []

    content_type = resp.headers.get("Content-Type", "")

    # Try CSV
    if "text/csv" in content_type:
        try:
            reader = csv.DictReader(io.StringIO(text))
            return list(reader)
        except Exception:
            pass

    # Try JSON
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return [_flatten(r) for r in data]
        if isinstance(data, dict):
            for key in ("data", "items", "results", "records"):
                if key in data and isinstance(data[key], list):
                    return [_flatten(r) for r in data[key]]
            return [_flatten(data)]
    except Exception:
        pass

    # Last resort: try CSV parse regardless of content-type
    try:
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        if rows:
            return rows
    except Exception:
        pass

    log.warning("Could not parse response for %s — content-type: %s", label, content_type)
    return []


def _flatten(obj: Any, prefix: str = "") -> dict:
    """Flatten a nested JSON object into a flat dict with dot-separated keys."""
    out: dict = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            full_key = f"{prefix}{k}" if not prefix else f"{prefix}.{k}"
            if isinstance(v, (dict, list)):
                out.update(_flatten(v, full_key))
            else:
                out[full_key] = v
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(_flatten(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = obj
    return out


# ---------------------------------------------------------------------------
# CSV writer
# ---------------------------------------------------------------------------

def _append_csv(dest: Path, rows: list[dict]) -> int:
    """Append rows to a CSV; writes header only on first write. Returns row count."""
    if not rows:
        return 0
    dest.parent.mkdir(parents=True, exist_ok=True)
    write_header = not dest.exists() or dest.stat().st_size == 0
    fieldnames = list(rows[0].keys())
    with dest.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def _overwrite_csv(dest: Path, rows: list[dict]) -> int:
    """Overwrite a CSV file (used for static/reference data)."""
    if dest.exists():
        dest.unlink()
    return _append_csv(dest, rows)


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def _date_chunks(start: date, end: date, chunk_days: int = CHUNK_DAYS):
    cursor = start
    while cursor <= end:
        chunk_end = min(cursor + timedelta(days=chunk_days - 1), end)
        yield cursor, chunk_end
        cursor = chunk_end + timedelta(days=1)


def _days_in_range(start: date, end: date):
    cursor = start
    while cursor <= end:
        yield cursor
        cursor += timedelta(days=1)


# ---------------------------------------------------------------------------
# Collectors
# ---------------------------------------------------------------------------

def collect_range(name: str, url: str, start: date, end: date, out_dir: Path) -> int:
    dest = out_dir / f"{name}.csv"
    total = 0
    for chunk_start, chunk_end in _date_chunks(start, end):
        params = {"from": chunk_start.isoformat(), "to": chunk_end.isoformat(), "format": "csv"}
        resp = _get(url, params)
        time.sleep(REQUEST_DELAY)
        if resp is None:
            continue
        rows = _parse_response(resp, name)
        total += _append_csv(dest, rows)
    return total


def collect_settlement_date_qp(name: str, url: str, start: date, end: date, out_dir: Path) -> int:
    """Iterate by day; sends ?settlementDate=YYYY-MM-DD."""
    dest = out_dir / f"{name}.csv"
    total = 0
    for day in _days_in_range(start, end):
        params = {"settlementDate": day.isoformat(), "format": "csv"}
        resp = _get(url, params)
        time.sleep(REQUEST_DELAY)
        if resp is None:
            continue
        total += _append_csv(dest, _parse_response(resp, name))
    return total


def collect_settlement_date_pp(name: str, path_template: str, start: date, end: date, out_dir: Path) -> int:
    """Iterate by day; substitutes {settlementDate} in path."""
    dest = out_dir / f"{name}.csv"
    total = 0
    for day in _days_in_range(start, end):
        url = BASE_URL + path_template.replace("{settlementDate}", day.isoformat())
        resp = _get(url, {"format": "csv"})
        time.sleep(REQUEST_DELAY)
        if resp is None:
            continue
        total += _append_csv(dest, _parse_response(resp, name))
    return total


def collect_settlement_bo_date(name: str, path_template: str, start: date, end: date, out_dir: Path) -> int:
    """Iterate by BID/OFFER × day; substitutes {bidOffer} and {settlementDate}."""
    dest = out_dir / f"{name}.csv"
    total = 0
    for bo in BID_OFFER_TYPES:
        for day in _days_in_range(start, end):
            url = BASE_URL + path_template.replace("{bidOffer}", bo).replace("{settlementDate}", day.isoformat())
            resp = _get(url, {"format": "csv"})
            time.sleep(REQUEST_DELAY)
            if resp is None:
                continue
            total += _append_csv(dest, _parse_response(resp, name))
    return total


def collect_settlement_period_pp(name: str, path_template: str, start: date, end: date, out_dir: Path) -> int:
    """Iterate by day × settlement period 1-50."""
    dest = out_dir / f"{name}.csv"
    total = 0
    days = list(_days_in_range(start, end))
    log.info("             (period-granular: %d days × 50 periods = %d requests)",
             len(days), len(days) * 50)
    for day in days:
        for sp in SETTLEMENT_PERIODS:
            url = BASE_URL + path_template.replace("{settlementDate}", day.isoformat()).replace(
                "{settlementPeriod}", str(sp))
            resp = _get(url, {"format": "csv"})
            time.sleep(REQUEST_DELAY)
            if resp is None:
                continue
            total += _append_csv(dest, _parse_response(resp, name))
    return total


def collect_settlement_bo_period(name: str, path_template: str, start: date, end: date, out_dir: Path) -> int:
    """Iterate by BID/OFFER × day × settlement period 1-50."""
    dest = out_dir / f"{name}.csv"
    total = 0
    days = list(_days_in_range(start, end))
    log.info("             (bo-period-granular: 2 × %d days × 50 periods = %d requests)",
             len(days), len(days) * 50 * 2)
    for bo in BID_OFFER_TYPES:
        for day in days:
            for sp in SETTLEMENT_PERIODS:
                url = BASE_URL + path_template.replace("{bidOffer}", bo).replace(
                    "{settlementDate}", day.isoformat()).replace("{settlementPeriod}", str(sp))
                resp = _get(url, {"format": "csv"})
                time.sleep(REQUEST_DELAY)
                if resp is None:
                    continue
                total += _append_csv(dest, _parse_response(resp, name))
    return total


def collect_triad_season(name: str, path_template: str, out_dir: Path) -> int:
    dest = out_dir / f"{name}.csv"
    if dest.exists():
        dest.unlink()
    total = 0
    for season in TRIAD_SEASONS:
        url = BASE_URL + path_template.replace("{triadSeason}", season)
        resp = _get(url, {"format": "csv"})
        time.sleep(REQUEST_DELAY)
        if resp is None:
            continue
        total += _append_csv(dest, _parse_response(resp, name))
    return total


def collect_static(name: str, url: str, out_dir: Path) -> int:
    resp = _get(url, {"format": "csv"})
    time.sleep(REQUEST_DELAY)
    if resp is None:
        return 0
    rows = _parse_response(resp, name)
    return _overwrite_csv(out_dir / f"{name}.csv", rows)


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run(
    start: date,
    end: date,
    out_dir: Path,
    filter_names: set[str] | None = None,
    skip_period_granular: bool = False,
):
    out_dir.mkdir(parents=True, exist_ok=True)
    log.info("BMRS data collection  %s → %s  →  %s/", start, end, out_dir)
    if skip_period_granular:
        log.info("(--skip-period-granular: omitting period-level settlement endpoints)")

    def _want(name: str) -> bool:
        return filter_names is None or name in filter_names

    summary: list[tuple[str, int]] = []

    def _record(name: str, n: int, label: str = ""):
        summary.append((name, n))
        log.info("%-40s  %d rows", f"[{label or 'done'}] {name}", n)

    # 1. Dataset endpoints (all use from/to)
    log.info("--- /datasets/* ---")
    for ep in DATASET_ENDPOINTS:
        name = ep["name"]
        if not _want(name):
            continue
        log.info("  collecting %s ...", name)
        n = collect_range(name, f"{BASE_URL}/datasets/{name}", start, end, out_dir)
        _record(name, n, "dataset")

    # 2. Opinionated range endpoints
    log.info("--- opinionated range ---")
    for ep in RANGE_OPINIONATED_ENDPOINTS:
        if not _want(ep["name"]):
            continue
        log.info("  collecting %s ...", ep["name"])
        n = collect_range(ep["name"], BASE_URL + ep["path"], start, end, out_dir)
        _record(ep["name"], n, "range")

    # 3. Settlement date query-param (iterate by day)
    log.info("--- settlement-date (query param) ---")
    for ep in SETTLEMENT_DATE_QP_ENDPOINTS:
        if not _want(ep["name"]):
            continue
        log.info("  collecting %s ...", ep["name"])
        n = collect_settlement_date_qp(ep["name"], BASE_URL + ep["path"], start, end, out_dir)
        _record(ep["name"], n, "settlement-qp")

    # 4. Settlement date path-param (iterate by day)
    log.info("--- settlement-date (path param) ---")
    for ep in SETTLEMENT_DATE_PP_ENDPOINTS:
        if not _want(ep["name"]):
            continue
        log.info("  collecting %s ...", ep["name"])
        n = collect_settlement_date_pp(ep["name"], ep["path"], start, end, out_dir)
        _record(ep["name"], n, "settlement-pp")

    # 5. BID/OFFER × date path-param
    log.info("--- bid-offer × date (path param) ---")
    for ep in SETTLEMENT_BO_DATE_ENDPOINTS:
        if not _want(ep["name"]):
            continue
        log.info("  collecting %s ...", ep["name"])
        n = collect_settlement_bo_date(ep["name"], ep["path"], start, end, out_dir)
        _record(ep["name"], n, "bo-date")

    # 6. Period-granular endpoints (day × 1-50)
    if not skip_period_granular:
        log.info("--- settlement-period (path param) ---")
        for ep in SETTLEMENT_PERIOD_PP_ENDPOINTS:
            if not _want(ep["name"]):
                continue
            log.info("  collecting %s ...", ep["name"])
            n = collect_settlement_period_pp(ep["name"], ep["path"], start, end, out_dir)
            _record(ep["name"], n, "period-pp")

        log.info("--- bid-offer × period (path param) ---")
        for ep in SETTLEMENT_BO_PERIOD_ENDPOINTS:
            if not _want(ep["name"]):
                continue
            log.info("  collecting %s ...", ep["name"])
            n = collect_settlement_bo_period(ep["name"], ep["path"], start, end, out_dir)
            _record(ep["name"], n, "bo-period")
    else:
        skipped = [ep["name"] for ep in SETTLEMENT_PERIOD_PP_ENDPOINTS + SETTLEMENT_BO_PERIOD_ENDPOINTS]
        log.info("Skipped period-granular endpoints: %s", ", ".join(skipped))

    # 7. Triad season endpoints
    log.info("--- triad seasons ---")
    for ep in TRIAD_SEASON_ENDPOINTS:
        if not _want(ep["name"]):
            continue
        log.info("  collecting %s ...", ep["name"])
        n = collect_triad_season(ep["name"], ep["path"], out_dir)
        _record(ep["name"], n, "triad")

    # 8. Static / latest snapshots
    log.info("--- static / reference ---")
    for ep in STATIC_ENDPOINTS:
        if not _want(ep["name"]):
            continue
        log.info("  collecting %s ...", ep["name"])
        n = collect_static(ep["name"], BASE_URL + ep["path"], out_dir)
        _record(ep["name"], n, "static")

    # 9. Data-status endpoints
    log.info("--- data-status ---")
    for ep in DATA_STATUS_ENDPOINTS:
        if not _want(ep["name"]):
            continue
        log.info("  collecting %s ...", ep["name"])
        n = collect_static(ep["name"], BASE_URL + ep["path"], out_dir)
        _record(ep["name"], n, "status")

    # Summary table
    log.info("")
    log.info("=== Collection complete ===")
    log.info("%-42s  %s", "Endpoint", "Rows")
    log.info("-" * 55)
    grand_total = 0
    for name, n in summary:
        log.info("%-42s  %d", name, n)
        grand_total += n
    log.info("-" * 55)
    log.info("%-42s  %d", "TOTAL", grand_total)
    log.info("%d endpoints collected, output in %s/", len(summary), out_dir)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def main():
    parser = argparse.ArgumentParser(
        description="Elexon BMRS Insights API — comprehensive GB/UK data collector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--mode", choices=["rolling", "backfill"], required=True,
        help="'rolling' = last 24 h; 'backfill' = 2026-01-01 to today (or --from/--to)",
    )
    parser.add_argument("--from", dest="date_from", metavar="YYYY-MM-DD",
                        help="Start date override (backfill mode)")
    parser.add_argument("--to",   dest="date_to",   metavar="YYYY-MM-DD",
                        help="End date override (default: today)")
    parser.add_argument("--out", default="output", metavar="DIR",
                        help="Output directory for CSV files (default: ./output)")
    parser.add_argument("--datasets", nargs="+", metavar="NAME",
                        help="Collect only these named endpoints")
    parser.add_argument(
        "--skip-period-granular", action="store_true",
        help="Skip endpoints that iterate by settlement period (recommended for large backfills "
             "— these generate 8,850+ requests per endpoint)",
    )
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show per-chunk debug logging")

    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.DEBUG)

    today = date.today()

    if args.mode == "rolling":
        start = today - timedelta(days=1)
        end = today
    else:
        start = _parse_date(args.date_from) if args.date_from else BACKFILL_START
        end = _parse_date(args.date_to) if args.date_to else today

    if start > end:
        parser.error(f"--from {start} is after --to {end}")

    days = (end - start).days + 1
    log.info("Date range: %s → %s (%d days)", start, end, days)
    if days > 30 and not args.skip_period_granular:
        log.warning(
            "Backfill > 30 days detected. Period-granular settlement endpoints will make "
            "%d+ requests and may take several hours. Use --skip-period-granular to skip them.",
            days * 50 * 3,
        )

    run(
        start=start,
        end=end,
        out_dir=Path(args.out),
        filter_names=set(args.datasets) if args.datasets else None,
        skip_period_granular=args.skip_period_granular,
    )


if __name__ == "__main__":
    main()
