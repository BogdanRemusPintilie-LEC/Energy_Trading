#!/usr/bin/env python3
"""
ENTSO-E Transparency Platform — GB Data Collector
==================================================
Fetches every available data category for the GB bidding zone
(EIC: 10YGB----------A) and writes one CSV file per category
into the ./data/ directory.

Usage
-----
    python collector.py                        # backfill YTD + today
    python collector.py --mode backfill        # 2026-01-01 -> now
    python collector.py --mode daily           # yesterday -> now
    python collector.py --dataset load_actual  # single dataset only
    python collector.py --list                 # print all dataset names

Prerequisites
-------------
    pip install -r requirements.txt
    # .env must contain: ENTSOE_API_TOKEN=<your-token>
"""

import argparse
import logging
import os
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

import pandas as pd
import requests
from dotenv import load_dotenv

# ── Bootstrap ─────────────────────────────────────────────────────────────────

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────

API_TOKEN      = os.getenv("ENTSOE_API_TOKEN")
BASE_URL       = "https://web-api.tp.entsoe.eu/api"
OUTPUT_DIR     = Path("data")
BACKFILL_START = datetime(2026, 1, 1, tzinfo=timezone.utc)

# Seconds to sleep between every API call — keep below the platform rate limit
RATE_PAUSE  = 1.2
MAX_RETRIES = 4

# ── EIC area codes ────────────────────────────────────────────────────────────

GB = "10YGB----------A"   # Great Britain

NEIGHBORS: dict[str, str] = {
    "FR": "10YFR-RTE------C",   # France       (IFA, IFA2, ElecLink)
    "BE": "10YBE----------2",   # Belgium       (Nemo Link)
    "NL": "10YNL----------L",   # Netherlands   (BritNed)
    "IE": "10YIE-1001A00010",   # Ireland       (East–West)
    "NO": "10YNO-0--------C",   # Norway        (North Sea Link)
}

# ── Dataset catalogue ─────────────────────────────────────────────────────────
#
# Each entry:
#   name        – CSV filename stem and --dataset key
#   description – human-readable label (logged at startup)
#   params      – fixed API query parameters (token + dates added at call time)
#   chunk_days  – max days per single API request (API-imposed limits vary)

DATASETS: list[dict] = [

    # ── Load ──────────────────────────────────────────────────────────────────
    {
        "name": "load_actual",
        "description": "Actual Total Load",
        "params": {"documentType": "A65", "processType": "A16",
                   "outBiddingZone_Domain": GB},
        "chunk_days": 365,
    },
    {
        "name": "load_forecast_da",
        "description": "Day-Ahead Total Load Forecast",
        "params": {"documentType": "A65", "processType": "A01",
                   "outBiddingZone_Domain": GB},
        "chunk_days": 365,
    },
    {
        "name": "load_forecast_week",
        "description": "Week-Ahead Total Load Forecast",
        "params": {"documentType": "A65", "processType": "A31",
                   "outBiddingZone_Domain": GB},
        "chunk_days": 365,
    },
    {
        "name": "load_forecast_month",
        "description": "Month-Ahead Total Load Forecast",
        "params": {"documentType": "A65", "processType": "A32",
                   "outBiddingZone_Domain": GB},
        "chunk_days": 365,
    },
    {
        "name": "load_forecast_year",
        "description": "Year-Ahead Total Load Forecast",
        "params": {"documentType": "A65", "processType": "A33",
                   "outBiddingZone_Domain": GB},
        "chunk_days": 365,
    },

    # ── Generation ────────────────────────────────────────────────────────────
    {
        "name": "generation_actual_per_type",
        "description": "Actual Generation per Production Type",
        "params": {"documentType": "A75", "processType": "A16",
                   "in_Domain": GB},
        "chunk_days": 365,
    },
    {
        "name": "generation_actual_per_unit",
        "description": "Actual Generation per Production Unit (slow: 1 call/day)",
        "params": {"documentType": "A73", "processType": "A16",
                   "in_Domain": GB},
        "chunk_days": 1,    # hard API limit — one day per request
    },
    {
        "name": "generation_forecast_da",
        "description": "Day-Ahead Aggregated Generation Forecast",
        "params": {"documentType": "A71", "processType": "A01",
                   "in_Domain": GB},
        "chunk_days": 365,
    },
    {
        "name": "generation_forecast_wind_solar",
        "description": "Wind and Solar Generation Forecast",
        "params": {"documentType": "A69", "processType": "A01",
                   "in_Domain": GB},
        "chunk_days": 365,
    },
    {
        "name": "generation_capacity_aggregated",
        "description": "Installed Generation Capacity Aggregated per Type",
        "params": {"documentType": "A68", "processType": "A33",
                   "in_Domain": GB},
        "chunk_days": 365,
    },
    {
        "name": "generation_capacity_per_unit",
        "description": "Installed Generation Capacity per Unit",
        "params": {"documentType": "A71", "processType": "A33",
                   "in_Domain": GB},
        "chunk_days": 365,
    },

    # ── Prices ────────────────────────────────────────────────────────────────
    {
        "name": "prices_day_ahead",
        "description": "Day-Ahead Market Clearing Prices",
        "params": {"documentType": "A44",
                   "in_Domain": GB, "out_Domain": GB},
        "chunk_days": 365,
    },

    # ── Balancing ─────────────────────────────────────────────────────────────
    {
        "name": "balancing_imbalance_prices",
        "description": "Imbalance Prices",
        "params": {"documentType": "A85", "businessType": "B33",
                   "controlArea_Domain": GB},
        "chunk_days": 31,
    },
    {
        "name": "balancing_imbalance_volume",
        "description": "Imbalance Volumes",
        "params": {"documentType": "A86", "businessType": "B33",
                   "controlArea_Domain": GB},
        "chunk_days": 31,
    },
    {
        "name": "balancing_activated_energy",
        "description": "Activated Balancing Energy",
        "params": {"documentType": "A83",
                   "controlArea_Domain": GB},
        "chunk_days": 31,
    },
    {
        "name": "balancing_bids_aggregated",
        "description": "Aggregated Balancing Energy Bids",
        "params": {"documentType": "A24",
                   "controlArea_Domain": GB},
        "chunk_days": 1,
    },
    {
        "name": "balancing_cross_border",
        "description": "Cross-Border Balancing",
        "params": {"documentType": "A26",
                   "acquiring_Domain": GB, "connecting_Domain": GB},
        "chunk_days": 31,
    },
    {
        "name": "balancing_procured_reserves",
        "description": "Amount of Procured Reserves",
        "params": {"documentType": "A95",
                   "controlArea_Domain": GB},
        "chunk_days": 31,
    },

    # ── Congestion management ─────────────────────────────────────────────────
    {
        "name": "congestion_redispatch",
        "description": "Redispatching",
        "params": {"documentType": "A93", "businessType": "A46",
                   "in_Domain": GB},
        "chunk_days": 365,
    },
    {
        "name": "congestion_countertrading",
        "description": "Countertrading",
        "params": {"documentType": "A91",
                   "in_Domain": GB, "out_Domain": GB},
        "chunk_days": 365,
    },
    {
        "name": "congestion_costs",
        "description": "Costs of Congestion Management",
        "params": {"documentType": "A92",
                   "in_Domain": GB, "out_Domain": GB},
        "chunk_days": 365,
    },

    # ── Outages ───────────────────────────────────────────────────────────────
    {
        "name": "outages_generation_planned",
        "description": "Planned Unavailability of Generation Units",
        "params": {"documentType": "A77",
                   "biddingZone_Domain": GB},
        "chunk_days": 365,
    },
    {
        "name": "outages_generation_forced",
        "description": "Forced Unavailability of Generation Units",
        "params": {"documentType": "A78",
                   "biddingZone_Domain": GB},
        "chunk_days": 365,
    },
    {
        "name": "outages_production_planned",
        "description": "Planned Unavailability of Production Units (aggregated)",
        "params": {"documentType": "A80",
                   "biddingZone_Domain": GB},
        "chunk_days": 365,
    },
    {
        "name": "outages_transmission_planned",
        "description": "Planned Unavailability of Transmission",
        "params": {"documentType": "A79",
                   "in_Domain": GB, "out_Domain": GB},
        "chunk_days": 365,
    },
    {
        "name": "outages_offshore_grid",
        "description": "Planned Unavailability of Offshore Grid Infrastructure",
        "params": {"documentType": "A90",
                   "biddingZone_Domain": GB},
        "chunk_days": 365,
    },

    # ── Capacity & net position ───────────────────────────────────────────────
    {
        "name": "net_position_gb",
        "description": "Net Position GB (scheduled net export)",
        "params": {"documentType": "A25", "businessType": "B09",
                   "in_Domain": GB, "out_Domain": GB},
        "chunk_days": 365,
    },
]

# Cross-border datasets — one set of entries per interconnector
for _neighbor, _eic in NEIGHBORS.items():
    _n = _neighbor.lower()
    DATASETS += [
        # Physical cross-border flows (both directions)
        {
            "name": f"flows_gb_to_{_n}",
            "description": f"Physical Cross-Border Flows: GB -> {_neighbor}",
            "params": {"documentType": "A11",
                       "in_Domain": _eic, "out_Domain": GB},
            "chunk_days": 365,
        },
        {
            "name": f"flows_{_n}_to_gb",
            "description": f"Physical Cross-Border Flows: {_neighbor} -> GB",
            "params": {"documentType": "A11",
                       "in_Domain": GB, "out_Domain": _eic},
            "chunk_days": 365,
        },
        # Scheduled commercial exchanges (day-ahead)
        {
            "name": f"scheduled_exports_gb_{_n}",
            "description": f"Scheduled Commercial Exchanges: GB -> {_neighbor}",
            "params": {"documentType": "A09", "businessType": "A01",
                       "in_Domain": _eic, "out_Domain": GB},
            "chunk_days": 365,
        },
        {
            "name": f"scheduled_imports_gb_{_n}",
            "description": f"Scheduled Commercial Exchanges: {_neighbor} -> GB",
            "params": {"documentType": "A09", "businessType": "A01",
                       "in_Domain": GB, "out_Domain": _eic},
            "chunk_days": 365,
        },
        # Net Transfer Capacity (both directions)
        {
            "name": f"ntc_export_gb_{_n}",
            "description": f"Net Transfer Capacity (NTC) GB -> {_neighbor}",
            "params": {"documentType": "A61", "businessType": "B08",
                       "in_Domain": _eic, "out_Domain": GB},
            "chunk_days": 365,
        },
        {
            "name": f"ntc_import_gb_{_n}",
            "description": f"Net Transfer Capacity (NTC) {_neighbor} -> GB",
            "params": {"documentType": "A61", "businessType": "B08",
                       "in_Domain": GB, "out_Domain": _eic},
            "chunk_days": 365,
        },
        # Already Allocated Capacity
        {
            "name": f"atc_export_gb_{_n}",
            "description": f"Already Allocated Capacity (ATC) GB -> {_neighbor}",
            "params": {"documentType": "A61", "businessType": "B07",
                       "in_Domain": _eic, "out_Domain": GB},
            "chunk_days": 365,
        },
        {
            "name": f"atc_import_gb_{_n}",
            "description": f"Already Allocated Capacity (ATC) {_neighbor} -> GB",
            "params": {"documentType": "A61", "businessType": "B07",
                       "in_Domain": GB, "out_Domain": _eic},
            "chunk_days": 365,
        },
        # Explicit capacity allocations — day-ahead auction (both directions)
        {
            "name": f"cap_alloc_da_gb_to_{_n}",
            "description": f"Explicit Day-Ahead Capacity Allocation: GB -> {_neighbor}",
            "params": {"documentType": "A25",
                       "contract_MarketAgreement.Type": "A01",
                       "in_Domain": _eic, "out_Domain": GB},
            "chunk_days": 365,
        },
        {
            "name": f"cap_alloc_da_{_n}_to_gb",
            "description": f"Explicit Day-Ahead Capacity Allocation: {_neighbor} -> GB",
            "params": {"documentType": "A25",
                       "contract_MarketAgreement.Type": "A01",
                       "in_Domain": GB, "out_Domain": _eic},
            "chunk_days": 365,
        },
        # Explicit capacity allocations — weekly auction
        {
            "name": f"cap_alloc_week_gb_to_{_n}",
            "description": f"Explicit Weekly Capacity Allocation: GB -> {_neighbor}",
            "params": {"documentType": "A25",
                       "contract_MarketAgreement.Type": "A02",
                       "in_Domain": _eic, "out_Domain": GB},
            "chunk_days": 365,
        },
        {
            "name": f"cap_alloc_week_{_n}_to_gb",
            "description": f"Explicit Weekly Capacity Allocation: {_neighbor} -> GB",
            "params": {"documentType": "A25",
                       "contract_MarketAgreement.Type": "A02",
                       "in_Domain": GB, "out_Domain": _eic},
            "chunk_days": 365,
        },
        # Explicit capacity allocations — monthly auction
        {
            "name": f"cap_alloc_month_gb_to_{_n}",
            "description": f"Explicit Monthly Capacity Allocation: GB -> {_neighbor}",
            "params": {"documentType": "A25",
                       "contract_MarketAgreement.Type": "A03",
                       "in_Domain": _eic, "out_Domain": GB},
            "chunk_days": 365,
        },
        {
            "name": f"cap_alloc_month_{_n}_to_gb",
            "description": f"Explicit Monthly Capacity Allocation: {_neighbor} -> GB",
            "params": {"documentType": "A25",
                       "contract_MarketAgreement.Type": "A03",
                       "in_Domain": GB, "out_Domain": _eic},
            "chunk_days": 365,
        },
        # Explicit capacity allocations — yearly auction
        {
            "name": f"cap_alloc_year_gb_to_{_n}",
            "description": f"Explicit Yearly Capacity Allocation: GB -> {_neighbor}",
            "params": {"documentType": "A25",
                       "contract_MarketAgreement.Type": "A04",
                       "in_Domain": _eic, "out_Domain": GB},
            "chunk_days": 365,
        },
        {
            "name": f"cap_alloc_year_{_n}_to_gb",
            "description": f"Explicit Yearly Capacity Allocation: {_neighbor} -> GB",
            "params": {"documentType": "A25",
                       "contract_MarketAgreement.Type": "A04",
                       "in_Domain": GB, "out_Domain": _eic},
            "chunk_days": 365,
        },
        # Congestion income per interconnector border
        {
            "name": f"congestion_income_gb_to_{_n}",
            "description": f"Congestion Income: GB -> {_neighbor}",
            "params": {"documentType": "A92",
                       "in_Domain": _eic, "out_Domain": GB},
            "chunk_days": 365,
        },
        {
            "name": f"congestion_income_{_n}_to_gb",
            "description": f"Congestion Income: {_neighbor} -> GB",
            "params": {"documentType": "A92",
                       "in_Domain": GB, "out_Domain": _eic},
            "chunk_days": 365,
        },
    ]

DATASETS_BY_NAME: dict[str, dict] = {d["name"]: d for d in DATASETS}

# ── XML parsing ───────────────────────────────────────────────────────────────

_NS_DECL_RE = re.compile(r'\s+xmlns(?::\w+)?="[^"]*"')
_NS_PFX_RE  = re.compile(r'<(/?)[\w][\w.-]*:')

_RESOLUTION_MAP: dict[str, timedelta] = {
    "PT15M": timedelta(minutes=15),
    "PT30M": timedelta(minutes=30),
    "PT60M": timedelta(hours=1),
    "P1D":   timedelta(days=1),
    "P1W":   timedelta(weeks=1),
    "P1M":   timedelta(days=30),
    "P1Y":   timedelta(days=365),
}


def _strip_ns(xml_text: str) -> str:
    """Strip all XML namespace declarations and prefixes for simple tag access."""
    xml_text = _NS_DECL_RE.sub("", xml_text)
    xml_text = _NS_PFX_RE.sub(r"<\1", xml_text)
    return xml_text


def _parse_dt(s: str) -> datetime:
    """Parse ENTSO-E ISO-8601 datetime string to a UTC-aware datetime."""
    s = s.strip().rstrip("Z")
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    raise ValueError(f"Unparseable datetime: {s!r}")


def parse_xml(xml_text: str) -> pd.DataFrame:
    """
    Parse any ENTSO-E API response into a flat DataFrame.

    Every TimeSeries/Period/Point is expanded into one row with:
      - timestamp_utc  : the point's UTC timestamp (ISO-8601 string)
      - all metadata fields from the TimeSeries element
      - all value fields from the Point element (quantity, price.amount, …)
    """
    try:
        root = ET.fromstring(_strip_ns(xml_text))
    except ET.ParseError as exc:
        log.error("XML parse error: %s", exc)
        return pd.DataFrame()

    # Acknowledgement = API-level error / no data
    if root.tag.split("}")[-1] == "Acknowledgement_MarketDocument":
        reason_el = root.find(".//Reason/text")
        log.debug("API acknowledgement (no data): %s",
                  reason_el.text if reason_el is not None else "unknown reason")
        return pd.DataFrame()

    rows: list[dict] = []

    for ts in root.iter("TimeSeries"):
        # Collect flat metadata from all direct children except Period
        meta: dict[str, str] = {}
        for child in ts:
            if child.tag == "Period":
                continue
            if len(child) == 0:
                meta[child.tag] = child.text or ""
            else:
                for sub in child:
                    if len(sub) == 0:
                        meta[f"{child.tag}_{sub.tag}"] = sub.text or ""

        for period in ts.findall("Period"):
            # timeInterval/start (preferred) or start directly under Period
            ti        = period.find("timeInterval")
            start_el  = (ti.find("start") if ti is not None
                         else period.find("start"))
            res_el    = period.find("resolution")

            if start_el is None or res_el is None:
                log.debug("Period missing timeInterval/start or resolution — skipping")
                continue

            try:
                t0  = _parse_dt(start_el.text)
            except ValueError as exc:
                log.debug("Bad period start: %s", exc)
                continue

            res = _RESOLUTION_MAP.get(res_el.text.strip(),
                                      timedelta(hours=1))

            for point in period.findall("Point"):
                pos_el = point.find("position")
                if pos_el is None:
                    continue
                ts_val = t0 + res * (int(pos_el.text) - 1)

                row: dict[str, str] = {
                    "timestamp_utc": ts_val.isoformat(),
                    **meta,
                }
                for c in point:
                    if c.tag != "position":
                        row[c.tag] = c.text or ""
                rows.append(row)

    return pd.DataFrame(rows) if rows else pd.DataFrame()


# ── API client ────────────────────────────────────────────────────────────────

def fetch_chunk(params: dict, start: datetime, end: datetime) -> pd.DataFrame:
    """
    Call the ENTSO-E REST API for one time window and return a parsed DataFrame.
    Retries on transient errors; returns empty DataFrame on 400 (no data).
    """
    qs: dict[str, str] = {
        "securityToken": API_TOKEN,
        "periodStart":   start.strftime("%Y%m%d%H%M"),
        "periodEnd":     end.strftime("%Y%m%d%H%M"),
        **params,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(BASE_URL, params=qs, timeout=60)
        except requests.RequestException as exc:
            log.warning("Network error (attempt %d/%d): %s",
                        attempt, MAX_RETRIES, exc)
            time.sleep(2 ** attempt)
            continue

        if resp.status_code == 200:
            return parse_xml(resp.text)

        if resp.status_code == 400:
            # 400 means the endpoint exists but has no data for this window
            log.debug("400 — no data for %s -> %s", start.date(), end.date())
            return pd.DataFrame()

        if resp.status_code == 429:
            wait = 60
            log.warning("Rate limited; sleeping %ds before retry", wait)
            time.sleep(wait)
            continue

        log.warning("HTTP %d on attempt %d/%d: %s",
                    resp.status_code, attempt, MAX_RETRIES,
                    resp.text[:300])
        time.sleep(2 ** attempt)

    log.error("All retries exhausted for period %s -> %s", start.date(), end.date())
    return pd.DataFrame()


# ── Date chunking ─────────────────────────────────────────────────────────────

def date_chunks(start: datetime, end: datetime, chunk_days: int):
    """Yield (chunk_start, chunk_end) pairs covering [start, end)."""
    cursor = start
    delta  = timedelta(days=chunk_days)
    while cursor < end:
        yield cursor, min(cursor + delta, end)
        cursor += delta


# ── CSV persistence ───────────────────────────────────────────────────────────

def save_csv(df: pd.DataFrame, name: str) -> None:
    """
    Append df rows to data/<name>.csv, deduplicating across all columns.
    Creates the file (with header) if it does not exist.
    """
    if df.empty:
        return

    path = OUTPUT_DIR / f"{name}.csv"
    df   = df.astype(str)

    if path.exists():
        existing = pd.read_csv(path, dtype=str)
        combined = pd.concat([existing, df], ignore_index=True)
        combined.drop_duplicates(inplace=True)
    else:
        combined = df

    combined.to_csv(path, index=False)


# ── Collector core ────────────────────────────────────────────────────────────

def collect(dataset: dict, start: datetime, end: datetime) -> None:
    """Fetch all chunks for one dataset and persist to CSV."""
    name        = dataset["name"]
    description = dataset.get("description", name)
    params      = dataset["params"]
    chunk_days  = dataset["chunk_days"]

    chunks  = list(date_chunks(start, end, chunk_days))
    n_total = len(chunks)
    rows_written = 0

    log.info("[%s] %s", name, description)
    log.info("  window: %s -> %s  (%d API calls)",
             start.date(), end.date(), n_total)

    for i, (cs, ce) in enumerate(chunks, 1):
        df = fetch_chunk(params, cs, ce)
        if not df.empty:
            save_csv(df, name)
            rows_written += len(df)
            log.info("  chunk %3d/%d  %s -> %s  +%d rows",
                     i, n_total, cs.date(), ce.date(), len(df))
        time.sleep(RATE_PAUSE)

    log.info("  -> %d rows written to data/%s.csv\n", rows_written, name)


def run(datasets: list[dict], start: datetime, end: datetime) -> None:
    """Collect all datasets for the given time window."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    for ds in datasets:
        collect(ds, start, end)


# ── CLI entry point ───────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="ENTSO-E Transparency Platform — GB data collector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python collector.py                        # full backfill + daily update
  python collector.py --mode backfill        # YTD from 2026-01-01
  python collector.py --mode daily           # yesterday only (for cron)
  python collector.py --dataset prices_day_ahead
  python collector.py --list                 # show all dataset names
        """,
    )
    p.add_argument(
        "--mode",
        choices=["backfill", "daily", "both"],
        default="both",
        help=(
            "backfill: 2026-01-01 -> now | "
            "daily: yesterday -> now | "
            "both: backfill (default)"
        ),
    )
    p.add_argument(
        "--dataset",
        metavar="NAME",
        help="Collect a single named dataset instead of all",
    )
    p.add_argument(
        "--list",
        action="store_true",
        help="Print all available dataset names and exit",
    )
    return p


def main() -> None:
    args = build_parser().parse_args()

    if args.list:
        print(f"\n{'Name':<45}  Description")
        print("-" * 90)
        for ds in DATASETS:
            print(f"  {ds['name']:<43}  {ds.get('description', '')}")
        print(f"\nTotal: {len(DATASETS)} datasets\n")
        return

    if not API_TOKEN:
        raise SystemExit(
            "ERROR: ENTSOE_API_TOKEN is not set.\n"
            "Create a .env file with:  ENTSOE_API_TOKEN=<your-token>"
        )

    now       = datetime.now(tz=timezone.utc).replace(
                    hour=0, minute=0, second=0, microsecond=0)
    yesterday = now - timedelta(days=1)

    if args.dataset:
        if args.dataset not in DATASETS_BY_NAME:
            raise SystemExit(
                f"Unknown dataset: {args.dataset!r}\n"
                f"Run  python collector.py --list  to see all names."
            )
        datasets = [DATASETS_BY_NAME[args.dataset]]
    else:
        datasets = DATASETS

    log.info("ENTSO-E GB Collector  |  %d dataset(s)  |  mode=%s",
             len(datasets), args.mode)
    log.info("Output directory: %s", OUTPUT_DIR.resolve())

    if args.mode in ("backfill", "both"):
        log.info("=== BACKFILL: %s -> %s ===", BACKFILL_START.date(), now.date())
        run(datasets, BACKFILL_START, now)

    # 'daily' is its own distinct window; useful for cron (--mode daily)
    # 'both' already covers yesterday inside the backfill window, so skip
    if args.mode == "daily":
        log.info("=== DAILY UPDATE: %s -> %s ===", yesterday.date(), now.date())
        run(datasets, yesterday, now)

    log.info("All done. CSVs are in: %s", OUTPUT_DIR.resolve())


if __name__ == "__main__":
    main()
