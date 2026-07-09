"""
GIE AGSI+ / ALSI / IIP Public Data Collector
=============================================
Fetches all public gas storage (AGSI), LNG (ALSI), and Urgent Market Message
(IIP) data published by Gas Infrastructure Europe.

Coverage
--------
For AGSI and ALSI, data is organised as a tree: EU / Non-EU (/ Additional
Information for ALSI) -> country -> company -> facility. Aggregated
(EU/country/company) and individual (facility) datasets are each their own
historical time series and must be queried separately. This collector
enumerates every node in that tree via the EIC listing endpoint
(/api/about?show=listing) and pulls each node's full history, plus the
unavailability reports and news feed for both platforms, plus every IIP
Urgent Market Message.

Modes
-----
  backfill   Download full history for every entity. Skips entities already
             marked complete in the state file so reruns are safe.
  daily      Re-pull only entries updated since the last run (facility/
             aggregate time series use the `updated` filter). Unavailability,
             news and IIP are always re-pulled in full each run and merged,
             since GIE does not offer an "updated since" filter for those and
             their volume is small relative to the time-series data.

Usage
-----
  python gie_collector.py --mode backfill
  python gie_collector.py --mode daily

Setup
-----
  Create a .env file (next to this script) containing:
    GIE_API_KEY=<your key>

Output
------
  gie_data/
    _state.json                     Per-entity run state.
    agsi/_catalog.json               EIC listing snapshot (companies/facilities).
    agsi/eu.csv, ne.csv               Pan-EU / Non-EU aggregate history.
    agsi/countries/{CC}.csv           Per-country aggregate history.
    agsi/companies/{CC}/{name}.csv    Per-company aggregate history.
    agsi/facilities/{CC}/{co}/{fac}.csv  Per-facility history.
    agsi/unavailability.csv           All AGSI unavailability reports.
    agsi/news.csv                     All AGSI service announcements.
    alsi/...                          Same layout for ALSI (plus ai.csv).
    iip/umm.csv                       All Urgent Market Messages.

Rate limits (per GIE documentation)
------------------------------------
  60 API calls / minute per IP, else a 60s "too many requests" penalty and,
  for repeat offenders, a permanent ban. CALL_INTERVAL below throttles every
  single call (across agsi/alsi/iip combined, since limiting is per-IP) to
  stay comfortably under that.
"""

import argparse
import csv
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv()
API_KEY = os.getenv("GIE_API_KEY")

BASE_URLS = {
    "agsi": "https://agsi.gie.eu/api",
    "alsi": "https://alsi.gie.eu/api",
    "iip": "https://iip.gie.eu/api",
}

OUTPUT_DIR = Path(__file__).parent / "gie_data"
STATE_FILE = OUTPUT_DIR / "_state.json"

# This collector is scoped to specific countries only (per user request: GB*
# post-Brexit UK data, not pre-Brexit "GB" and not the rest of Europe).
# Override with --countries if the scope ever needs to widen.
DEFAULT_COUNTRIES = ["GB*"]

# Seconds between ANY API call (agsi+alsi+iip share one IP-based limit).
# GIE caps at 60 calls/min; this keeps us at ~50/min with margin.
CALL_INTERVAL: float = 1.2
# Max entries per page (facility/unavailability endpoints respect this;
# IIP ignores it and fixes its own page size — handled generically via
# last_page regardless).
PAGE_SIZE: int = 300
HTTP_TIMEOUT: int = 60

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# HTTP session with retry + global throttle
# ---------------------------------------------------------------------------

def make_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=6,
        backoff_factor=5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": "GIE-Collector/1.0"})
    return session


SESSION = make_session()
_last_call: float = 0.0


def _throttle() -> None:
    global _last_call
    wait = CALL_INTERVAL - (time.monotonic() - _last_call)
    if wait > 0:
        time.sleep(wait)
    _last_call = time.monotonic()


RATE_LIMIT_COOLDOWN: float = 65.0  # GIE's documented penalty window is 60s
MAX_RATE_LIMIT_RETRIES: int = 6


def _embedded_error_code(data: Any) -> Optional[int]:
    """GIE's backend doesn't always answer errors with a real HTTP status —
    sometimes it's HTTP 200 with a body like
    {"type":"ClientException","code":429,...} and no "data"/"last_page" keys.
    Detect that shape and return the embedded code, or None if this isn't one."""
    if (
        isinstance(data, dict)
        and "code" in data
        and "message" in data
        and "data" not in data
        and "last_page" not in data
    ):
        return data.get("code")
    return None


def api_get(platform: str, path: str, params: Optional[Dict] = None) -> Dict:
    """Call a GIE endpoint (agsi/alsi/iip) and return the parsed JSON body.

    Only an embedded code of 429 is treated as transient (rate limit) and
    retried with a cooldown. Any other embedded error code (e.g. 400 — seen
    in practice on some IIP filter combinations regardless of retries) is
    raised immediately since retrying it can't possibly help."""
    if not API_KEY:
        raise RuntimeError("GIE_API_KEY is not set (create a .env file).")
    url = BASE_URLS[platform] + path
    for attempt in range(1, MAX_RATE_LIMIT_RETRIES + 1):
        _throttle()
        resp = SESSION.get(
            url, params=params, headers={"x-key": API_KEY}, timeout=HTTP_TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()
        code = _embedded_error_code(data)
        if code is None:
            return data
        if code != 429:
            raise RuntimeError(f"GIE returned embedded error {code} for {url} params={params}: {data.get('message')}")
        log.warning(
            "  Rate-limited (embedded 429), cooling down %.0fs (attempt %d/%d)",
            RATE_LIMIT_COOLDOWN, attempt, MAX_RATE_LIMIT_RETRIES,
        )
        time.sleep(RATE_LIMIT_COOLDOWN)
    raise RuntimeError(f"Persistent rate limiting on {url} after {MAX_RATE_LIMIT_RETRIES} retries")


# ---------------------------------------------------------------------------
# State helpers
# ---------------------------------------------------------------------------

def load_state() -> Dict[str, Any]:
    if STATE_FILE.exists():
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state: Dict[str, Any]) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, default=str)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def today_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Path / name helpers
# ---------------------------------------------------------------------------

def safe_name(name: str) -> str:
    keep = set(" abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.()")
    return "".join(c if c in keep else "_" for c in (name or "")).strip() or "unknown"


# ---------------------------------------------------------------------------
# Generic row flattening + CSV upsert
# ---------------------------------------------------------------------------

def flatten_row(row: Dict, parent_key: str = "") -> Dict[str, Any]:
    """Flatten nested dicts into dotted columns; JSON-encode lists (their
    length/shape varies row to row, so they don't map to fixed columns)."""
    out: Dict[str, Any] = {}
    for k, v in row.items():
        key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict):
            out.update(flatten_row(v, key))
        elif isinstance(v, list):
            out[key] = json.dumps(v, default=str) if v else ""
        else:
            out[key] = v
    return out


def upsert_csv(csv_path: Path, new_rows: List[Dict], key_fn: Callable[[Dict], str]) -> int:
    """Merge new_rows into csv_path, keyed by key_fn(raw_row). Existing rows
    with a matching key are overwritten (handles GIE data corrections);
    everything else is preserved. Returns the total row count after merge."""
    existing: Dict[str, Dict[str, Any]] = {}
    if csv_path.exists():
        with open(csv_path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                existing[row.get("_key", "")] = row

    for raw in new_rows:
        flat = flatten_row(raw)
        flat["_key"] = key_fn(raw)
        existing[flat["_key"]] = flat

    fieldnames: List[str] = []
    seen = {"_key"}
    for row in existing.values():
        for k in row.keys():
            if k not in seen:
                seen.add(k)
                fieldnames.append(k)
    fieldnames.append("_key")

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for key in sorted(existing.keys()):
            writer.writerow(existing[key])
    return len(existing)


def nested_id(field: Any) -> str:
    """Pull an eic/code identifier out of a nested dict or a one-item list of
    dicts — GIE returns country/company/facility sub-objects as either,
    depending on endpoint and platform."""
    if isinstance(field, list) and field:
        field = field[0]
    if isinstance(field, dict):
        return str(field.get("eic") or field.get("code") or field.get("name") or "")
    return str(field or "")


# ---------------------------------------------------------------------------
# Entity discovery (EIC listing -> full tree of queryable nodes)
# ---------------------------------------------------------------------------

def fetch_listing(platform: str) -> List[Dict]:
    log.info("[%s] Fetching EIC listing…", platform.upper())
    listing = api_get(platform, "/about", {"show": "listing"})
    catalog_path = OUTPUT_DIR / platform / "_catalog.json"
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(listing, f, indent=2, default=str)
    return listing


def build_entities(platform: str, listing: List[Dict], only_countries: Optional[List[str]] = None) -> List[Dict]:
    """Enumerate every node of the EU/NE(/AI) -> country -> company ->
    facility tree as an independent queryable entity.

    If only_countries is given, the EU/NE/AI pan-European aggregates are
    skipped entirely (they blend in every other country, so they're not
    specific to the requested one(s)) and only matching country/company/
    facility nodes are kept."""
    entities: List[Dict] = []
    country_filter = set(only_countries) if only_countries else None

    if country_filter is None:
        types = ["eu", "ne"] + (["ai"] if platform == "alsi" else [])
        for t in types:
            entities.append({"level": "type", "key": f"type_{t}", "params": {"type": t}})

    countries = sorted({c["country"] for c in listing if c.get("country")})
    if country_filter is not None:
        countries = [cc for cc in countries if cc in country_filter]
    for cc in countries:
        entities.append({
            "level": "country", "key": f"country_{cc}",
            "params": {"country": cc}, "country": cc,
        })

    for company in listing:
        cc = company.get("country")
        c_eic = company.get("eic")
        c_name = company.get("name") or c_eic
        if not (cc and c_eic):
            continue
        if country_filter is not None and cc not in country_filter:
            continue
        entities.append({
            "level": "company", "key": f"company_{cc}_{c_eic}",
            "params": {"country": cc, "company": c_eic},
            "country": cc, "company_eic": c_eic, "company_name": c_name,
        })
        for fac in company.get("facilities", []):
            f_eic = fac.get("eic")
            f_name = fac.get("name") or f_eic
            if not f_eic:
                continue
            entities.append({
                "level": "facility", "key": f"facility_{cc}_{c_eic}_{f_eic}",
                "params": {"country": cc, "company": c_eic, "facility": f_eic},
                "country": cc, "company_eic": c_eic, "company_name": c_name,
                "facility_eic": f_eic, "facility_name": f_name,
            })

    return entities


def entity_csv_path(platform: str, entity: Dict) -> Path:
    base = OUTPUT_DIR / platform
    level = entity["level"]
    if level == "type":
        return base / f"{entity['params']['type']}.csv"
    if level == "country":
        return base / "countries" / f"{safe_name(entity['country'])}.csv"
    if level == "company":
        short_eic = entity["company_eic"][:8]
        return base / "companies" / safe_name(entity["country"]) / f"{safe_name(entity['company_name'])}_{short_eic}.csv"
    if level == "facility":
        short_eic = entity["facility_eic"][:8]
        return (
            base / "facilities" / safe_name(entity["country"]) / safe_name(entity["company_name"])
            / f"{safe_name(entity['facility_name'])}_{short_eic}.csv"
        )
    raise ValueError(f"Unknown entity level: {level}")


# ---------------------------------------------------------------------------
# Fetchers
# ---------------------------------------------------------------------------

def fetch_entity_history(platform: str, entity: Dict, mode: str, state: Dict) -> None:
    """Pull an entity's (type/country/company/facility) full daily history,
    or just what changed since the last run in daily mode."""
    state_key = f"{platform}:{entity['key']}"
    entry = state.get(state_key, {})
    csv_path = entity_csv_path(platform, entity)

    if mode == "backfill" and entry.get("status") == "complete":
        log.info("  Skipping (complete): %s", state_key)
        return

    params = dict(entity["params"])
    params["size"] = PAGE_SIZE
    if mode == "daily" and entry.get("status") == "complete" and entry.get("last_run_date"):
        params["updated"] = entry["last_run_date"]

    page = 1
    rows: List[Dict] = []
    try:
        while True:
            params["page"] = page
            data = api_get(platform, "", params)
            last_page = data.get("last_page", 1)
            page_rows = data.get("data", [])
            rows.extend(page_rows)
            log.info("  [%s] page %d/%d (+%d rows)", state_key, page, last_page, len(page_rows))
            if page >= last_page or not page_rows:
                break
            page += 1
    except Exception as exc:
        log.error("  Failed %s: %s", state_key, exc)
        state[state_key] = {**entry, "status": "error", "last_error": str(exc), "last_run": now_iso()}
        return

    total = upsert_csv(csv_path, rows, key_fn=lambda r: str(r.get("gasDayStart", "")))
    state[state_key] = {
        "status": "complete",
        "last_run": now_iso(),
        "last_run_date": today_str(),
        "row_count": total,
        "new_rows_this_run": len(rows),
        "file_path": str(csv_path.relative_to(OUTPUT_DIR)),
    }
    log.info("  Done: %s -> %d total rows (%d fetched this run)", state_key, total, len(rows))


def fetch_full_list(
    platform: str,
    path: str,
    csv_path: Path,
    key_fn: Callable[[Dict], str],
    state: Dict,
    state_key: str,
    extra_params: Optional[Dict] = None,
    row_filter: Optional[Callable[[Dict], bool]] = None,
) -> None:
    """Fully paginate a list endpoint (unavailability/news/IIP) and merge the
    result into csv_path. Always run in full (see module docstring).

    row_filter, if given, drops rows client-side after fetching — used where
    GIE has no server-side filter param that scopes tightly enough (news)."""
    params = dict(extra_params or {})
    params["size"] = PAGE_SIZE
    page = 1
    rows: List[Dict] = []
    try:
        while True:
            params["page"] = page
            data = api_get(platform, path, params)
            last_page = data.get("last_page", 1)
            page_rows = data.get("data", [])
            rows.extend(page_rows)
            log.info("  [%s] page %d/%d (+%d rows)", state_key, page, last_page, len(page_rows))
            if page >= last_page or not page_rows:
                break
            page += 1
    except Exception as exc:
        log.error("  Failed %s: %s", state_key, exc)
        state[state_key] = {"status": "error", "last_error": str(exc), "last_run": now_iso()}
        return

    fetched = len(rows)
    if row_filter is not None:
        rows = [r for r in rows if row_filter(r)]
        log.info("  [%s] %d/%d rows matched scope filter", state_key, len(rows), fetched)

    total = upsert_csv(csv_path, rows, key_fn=key_fn)
    state[state_key] = {
        "status": "complete",
        "last_run": now_iso(),
        "row_count": total,
        "new_rows_this_run": len(rows),
        "file_path": str(csv_path.relative_to(OUTPUT_DIR)),
    }
    log.info("  Done: %s -> %d total rows (%d fetched this run)", state_key, total, len(rows))


# ---------------------------------------------------------------------------
# Main run
# ---------------------------------------------------------------------------

def _news_scope_filter(relevant_names: set) -> Callable[[Dict], bool]:
    needles = {n.lower() for n in relevant_names if n}

    def _matches(row: Dict) -> bool:
        for ent in row.get("entities", []) or []:
            name = (ent.get("name") or "").lower()
            if any(needle in name or name in needle for needle in needles if needle):
                return True
        return False

    return _matches


def run(mode: str, countries: Optional[List[str]] = None) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    log.addHandler(logging.FileHandler(OUTPUT_DIR / "collector.log"))

    if not API_KEY:
        log.error("GIE_API_KEY is not set. Create a .env file with: GIE_API_KEY=<your key>")
        sys.exit(1)

    scope_label = ",".join(countries) if countries else "ALL (pan-European)"
    log.info("=" * 60)
    log.info("GIE Collector  mode=%s  countries=%s  started=%s", mode, scope_label, now_iso())
    log.info("=" * 60)

    state = load_state()
    relevant_names: set = set(countries or [])
    iip_participant_eics: List[str] = []

    for platform in ("agsi", "alsi"):
        listing = fetch_listing(platform)
        entities = build_entities(platform, listing, only_countries=countries)
        log.info("[%s] %d companies, %d entities in scope to process",
                  platform.upper(), len(listing), len(entities))

        for i, entity in enumerate(entities, 1):
            log.info("[%s %d/%d] %s", platform.upper(), i, len(entities), entity["key"])
            fetch_entity_history(platform, entity, mode, state)
            save_state(state)
            if entity.get("company_name"):
                relevant_names.add(entity["company_name"])
            if entity.get("facility_name"):
                relevant_names.add(entity["facility_name"])
            if entity.get("company_eic"):
                iip_participant_eics.append(entity["company_eic"])

        log.info("[%s] Fetching unavailability reports…", platform.upper())
        unavail_key_fn = lambda r: "|".join([
            nested_id(r.get("company")), nested_id(r.get("facility")),
            str(r.get("start", "")), str(r.get("end", "")), str(r.get("published", "")),
        ])
        for cc in (countries or [None]):
            fetch_full_list(
                platform, "/unavailability",
                OUTPUT_DIR / platform / "unavailability.csv",
                key_fn=unavail_key_fn,
                state=state, state_key=f"{platform}:unavailability:{cc or 'all'}",
                extra_params={"country": cc} if cc else None,
            )
            save_state(state)

        log.info("[%s] Fetching news…", platform.upper())
        fetch_full_list(
            platform, "/news",
            OUTPUT_DIR / platform / "news.csv",
            key_fn=lambda r: str(r.get("url", "")),
            state=state, state_key=f"{platform}:news",
            row_filter=_news_scope_filter(relevant_names) if countries else None,
        )
        save_state(state)

    log.info("[IIP] Fetching Urgent Market Messages…")
    if countries and iip_participant_eics:
        # No server-side "country" filter on IIP, and its "asset" filter is
        # broken server-side (returns HTTP 400 for any value, including
        # known-good EICs — confirmed independent of this collector).
        # "reportingEntity" (company-level) works reliably, so scope by the
        # in-scope companies' EICs instead.
        for eic in sorted(set(iip_participant_eics)):
            fetch_full_list(
                "iip", "",
                OUTPUT_DIR / "iip" / "umm.csv",
                key_fn=lambda r: str((r.get("message") or {}).get("messageId", "")) or str(r.get("submitted", "")),
                state=state, state_key=f"iip:umm:{eic}",
                extra_params={"reportingEntity": eic},
            )
            save_state(state)
    else:
        fetch_full_list(
            "iip", "",
            OUTPUT_DIR / "iip" / "umm.csv",
            key_fn=lambda r: str((r.get("message") or {}).get("messageId", "")) or str(r.get("submitted", "")),
            state=state, state_key="iip:umm",
        )
        save_state(state)

    complete = sum(1 for v in state.values() if v.get("status") == "complete")
    errors = sum(1 for v in state.values() if v.get("status") == "error")
    log.info("=" * 60)
    log.info("Run complete. complete=%d  errors=%d  total_tracked=%d", complete, errors, len(state))
    log.info("Output directory: %s", OUTPUT_DIR.resolve())
    log.info("=" * 60)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download all public GIE AGSI/ALSI/IIP data to CSV."
    )
    parser.add_argument(
        "--mode",
        choices=["backfill", "daily"],
        required=True,
        help=(
            "backfill: full history download from scratch (skips already-complete entities). "
            "daily: pull only records updated since the last run for time series; "
            "unavailability/news/IIP are always fully re-pulled and merged."
        ),
    )
    parser.add_argument(
        "--countries",
        default=",".join(DEFAULT_COUNTRIES),
        help=(
            "Comma-separated country codes to scope to (e.g. GB*,DE). "
            "Pass ALL to disable scoping and pull every country plus the "
            "EU/Non-EU/AI aggregates. Default: %(default)s"
        ),
    )
    args = parser.parse_args()
    countries = None if args.countries.strip().upper() == "ALL" else [
        c.strip() for c in args.countries.split(",") if c.strip()
    ]
    run(args.mode, countries=countries)
