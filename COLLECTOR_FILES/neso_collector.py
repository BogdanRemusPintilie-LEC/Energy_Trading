"""
NESO (National Energy System Operator) Public Data Collector
============================================================
Fetches all public GB/UK datasets from the NESO Data Portal API.
No API key required.

Modes
-----
  backfill   Download every resource from scratch. Skips resources already
             marked complete in the state file so reruns are safe.
  daily      Append only new rows (datastore resources) or re-download file
             resources that have changed since the last run.

Usage
-----
  python neso_collector.py --mode backfill
  python neso_collector.py --mode daily

Output
------
  neso_data/
    _catalog.json          Full metadata snapshot of all datasets/resources.
    _state.json            Per-resource run state (row counts, timestamps).
    {org}/{dataset}/{resource}.csv   One CSV per resource.

Rate limits (per NESO documentation)
-------------------------------------
  CKAN metadata API  : 1 request / second
  Datastore API      : 2 requests / minute

  DATASTORE_INTERVAL below can be raised if NESO relax their limits.
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
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "https://api.neso.energy/api/3/action/"
OUTPUT_DIR = Path(__file__).parent / "neso_data"
STATE_FILE = OUTPUT_DIR / "_state.json"
CATALOG_FILE = OUTPUT_DIR / "_catalog.json"

# Seconds between CKAN metadata calls (limit: 1/sec)
CKAN_INTERVAL: float = 1.1
# Seconds between datastore fetch calls (limit: 2/min = 1 per 30s)
DATASTORE_INTERVAL: float = 31.0
# Rows fetched per datastore page
PAGE_SIZE: int = 10_000
# HTTP timeout in seconds
HTTP_TIMEOUT: int = 60

# --- Discovery mode (structure-only, not full data) --------------------
# Rows sampled per resource when running --mode discover
DISCOVER_SAMPLE_ROWS: int = 5
# Seconds between API calls during discovery. Faster than the production
# datastore interval since each call is a tiny sample, not a full page pull.
DISCOVER_INTERVAL: float = 0.5

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(OUTPUT_DIR / "collector.log" if OUTPUT_DIR.exists() else "collector.log"),
    ],
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# HTTP session with retry
# ---------------------------------------------------------------------------

def make_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": "NESO-Collector/1.0"})
    return session


SESSION = make_session()


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


# ---------------------------------------------------------------------------
# CKAN API helpers
# ---------------------------------------------------------------------------

def ckan_get(action: str, params: Optional[Dict] = None) -> Any:
    """Call a CKAN action endpoint and return the result payload."""
    url = urljoin(BASE_URL, action)
    resp = SESSION.get(url, params=params, timeout=HTTP_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"CKAN error on {action}: {data.get('error')}")
    return data["result"]


def fetch_catalog() -> List[Dict]:
    """Return a list of all packages with their full metadata."""
    log.info("Fetching package list…")
    package_ids: List[str] = ckan_get("package_list")
    log.info("Found %d datasets. Fetching metadata for each…", len(package_ids))

    packages = []
    for i, pkg_id in enumerate(package_ids, 1):
        try:
            pkg = ckan_get("package_show", {"id": pkg_id})
            packages.append(pkg)
            log.info("[%d/%d] Catalogued: %s", i, len(package_ids), pkg_id)
        except Exception as exc:
            log.warning("Could not fetch metadata for %s: %s", pkg_id, exc)
        time.sleep(CKAN_INTERVAL)

    log.info("Catalog complete: %d packages retrieved.", len(packages))
    return packages


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def safe_name(name: str) -> str:
    """Strip characters that are invalid in Windows filenames."""
    keep = set(" abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.()")
    return "".join(c if c in keep else "_" for c in name).strip()


def resource_csv_path(org: str, dataset: str, resource_name: str, resource_id: str) -> Path:
    short_id = resource_id[:8]
    filename = f"{safe_name(resource_name)}_{short_id}.csv"
    return OUTPUT_DIR / safe_name(org) / safe_name(dataset) / filename


# ---------------------------------------------------------------------------
# Datastore download
# ---------------------------------------------------------------------------

# Timestamp (time.monotonic) of the last call made to each rate-limited
# endpoint category. Enforced globally so back-to-back resources don't
# burst past the documented limit — see fetch_datastore_page.
_last_call_time: Dict[str, float] = {}


def _throttle(key: str, interval: float) -> None:
    """Block until at least `interval` seconds have passed since the last
    call tagged with `key`, regardless of which resource made that call."""
    last = _last_call_time.get(key, 0.0)
    wait = interval - (time.monotonic() - last)
    if wait > 0:
        time.sleep(wait)
    _last_call_time[key] = time.monotonic()


def fetch_datastore_page(
    resource_id: str,
    offset: int,
    limit: int = PAGE_SIZE,
    interval: float = DATASTORE_INTERVAL,
) -> Tuple[List[Dict], int, List[Dict]]:
    """
    Fetch one page of rows from the datastore.
    Returns (rows, total_count, fields).

    Throttled on every call (not just between pages of the same resource) so
    the datastore rate limit is respected across resource boundaries too.
    """
    _throttle("datastore", interval)
    params = {
        "resource_id": resource_id,
        "limit": limit,
        "offset": offset,
    }
    result = ckan_get("datastore_search", params)
    total = result.get("total", 0)
    rows = result.get("records", [])
    fields = result.get("fields", [])
    return rows, total, fields


def download_datastore_resource(
    resource_id: str,
    csv_path: Path,
    start_offset: int = 0,
    append: bool = False,
) -> int:
    """
    Page through a datastore resource and write rows to csv_path.
    Returns the total number of rows written in this call.
    """
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    rows_written = 0
    offset = start_offset
    fieldnames: Optional[List[str]] = None

    # When appending we need to know existing headers to stay consistent
    if append and csv_path.exists():
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            try:
                fieldnames = next(reader)
            except StopIteration:
                pass

    with open(csv_path, mode, newline="", encoding="utf-8") as f:
        writer: Optional[csv.DictWriter] = None

        while True:
            log.info("  Fetching rows %d–%d from %s", offset, offset + PAGE_SIZE, resource_id)
            rows, total, _fields = fetch_datastore_page(resource_id, offset)

            if not rows:
                break

            if writer is None:
                if fieldnames is None:
                    # Drop internal CKAN columns
                    fieldnames = [k for k in rows[0].keys() if k != "_id"]
                writer = csv.DictWriter(
                    f,
                    fieldnames=fieldnames,
                    extrasaction="ignore",
                    lineterminator="\n",
                )
                if not append or os.path.getsize(csv_path) == 0:
                    writer.writeheader()

            writer.writerows(rows)
            rows_written += len(rows)
            offset += len(rows)

            if offset >= total:
                break

    return rows_written


# ---------------------------------------------------------------------------
# File resource download (non-datastore)
# ---------------------------------------------------------------------------

def download_file_resource(url: str, csv_path: Path) -> bool:
    """
    Download a raw file resource (CSV/Excel/PDF etc.) directly.
    Returns True on success.
    """
    if not url:
        return False
    try:
        log.info("  Downloading file: %s", url)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with SESSION.get(url, timeout=HTTP_TIMEOUT, stream=True) as resp:
            resp.raise_for_status()
            with open(csv_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    f.write(chunk)
        return True
    except Exception as exc:
        log.warning("  File download failed: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Structure discovery (schema/sample only, no bulk download)
# ---------------------------------------------------------------------------

def discover_datastore_structure(resource_id: str) -> Dict[str, Any]:
    """Fetch a small sample from a datastore resource to learn its schema."""
    rows, total, fields = fetch_datastore_page(
        resource_id, 0, limit=DISCOVER_SAMPLE_ROWS, interval=DISCOVER_INTERVAL
    )
    return {
        "total_rows": total,
        "fields": [
            {"id": f.get("id"), "type": f.get("type")}
            for f in fields
            if f.get("id") != "_id"
        ],
        "sample_rows": [
            {k: v for k, v in row.items() if k != "_id"} for row in rows
        ],
    }


def discover_file_structure(url: str) -> Dict[str, Any]:
    """HEAD a raw file resource to learn its type/size without downloading it."""
    if not url:
        return {"error": "no url"}
    _throttle("file_head", DISCOVER_INTERVAL)
    try:
        resp = SESSION.head(url, timeout=HTTP_TIMEOUT, allow_redirects=True)
        return {
            "status_code": resp.status_code,
            "content_type": resp.headers.get("Content-Type"),
            "content_length": resp.headers.get("Content-Length"),
        }
    except Exception as exc:
        return {"error": str(exc)}


def run_discover(time_budget_seconds: float = 900.0) -> None:
    """
    Walk the full catalog and record each resource's structure (field names/
    types + a few sample rows for datastore resources; content-type/size for
    file resources) without downloading full data. Bounded by a wall-clock
    time budget so it stays quick to run.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()

    if CATALOG_FILE.exists():
        log.info("Loading cached catalog…")
        with open(CATALOG_FILE, encoding="utf-8") as f:
            packages = json.load(f)
    else:
        packages = fetch_catalog()
        with open(CATALOG_FILE, "w", encoding="utf-8") as f:
            json.dump(packages, f, indent=2, default=str)

    total_resources = sum(len(p.get("resources", [])) for p in packages)

    report_path = OUTPUT_DIR / "_structure_report.json"
    already: Dict[str, Dict[str, Any]] = {}
    if report_path.exists():
        with open(report_path, encoding="utf-8") as f:
            prior = json.load(f)
        for entry in prior.get("resources", []):
            already[entry["resource_id"]] = entry
        log.info("Resuming discovery — %d resources already sampled.", len(already))

    log.info(
        "Discovering structure for %d resources across %d datasets (budget=%ds)…",
        total_resources, len(packages), time_budget_seconds,
    )

    report: List[Dict[str, Any]] = list(already.values())
    new_this_run = 0
    processed = len(already)
    ran_out_of_time = False

    for pkg in packages:
        if ran_out_of_time:
            break
        dataset_name = pkg.get("name", "unknown")
        org_name = (pkg.get("organization", {}) or {}).get("name", "ungrouped")

        for resource in pkg.get("resources", []):
            resource_id = resource.get("id", "")
            if resource_id in already:
                continue

            if time.monotonic() - start > time_budget_seconds:
                ran_out_of_time = True
                break

            processed += 1
            resource_name = resource.get("name") or resource_id
            datastore_active = resource.get("datastore_active", False)
            log.info(
                "[%d/%d] %s / %s / %s",
                processed, total_resources, org_name, dataset_name, resource_name,
            )

            entry: Dict[str, Any] = {
                "org": org_name,
                "dataset": dataset_name,
                "resource_id": resource_id,
                "resource_name": resource_name,
                "format": resource.get("format"),
                "datastore_active": datastore_active,
            }
            try:
                if datastore_active:
                    entry["structure"] = discover_datastore_structure(resource_id)
                else:
                    entry["structure"] = discover_file_structure(resource.get("url", ""))
            except Exception as exc:
                entry["structure"] = {"error": str(exc)}
            report.append(entry)
            new_this_run += 1

    skipped = total_resources - len(report)
    if skipped:
        log.warning(
            "Time budget reached — %d/%d resources not yet sampled.",
            skipped, total_resources,
        )

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "generated": now_iso(),
                "resources_total": total_resources,
                "resources_discovered": len(report),
                "resources_skipped_time_budget": skipped,
                "resources": report,
            },
            f,
            indent=2,
            default=str,
        )
    log.info(
        "Structure discovery complete: %d/%d resources sampled. Report: %s",
        len(report), total_resources, report_path,
    )


# ---------------------------------------------------------------------------
# Per-resource dispatcher
# ---------------------------------------------------------------------------

def process_resource(
    resource: Dict,
    dataset_name: str,
    org_name: str,
    state: Dict,
    mode: str,
) -> None:
    resource_id = resource.get("id", "")
    resource_name = resource.get("name") or resource.get("description") or resource_id
    datastore_active = resource.get("datastore_active", False)
    file_url = resource.get("url", "")
    fmt = (resource.get("format") or "").upper()

    csv_path = resource_csv_path(org_name, dataset_name, resource_name, resource_id)
    entry = state.get(resource_id, {})

    # ------------------------------------------------------------------
    # Backfill: skip if already complete
    # ------------------------------------------------------------------
    if mode == "backfill" and entry.get("status") == "complete":
        log.info("  Skipping (already complete): %s", resource_name)
        return

    # ------------------------------------------------------------------
    # Datastore resource
    # ------------------------------------------------------------------
    if datastore_active:
        start_offset = 0
        append = False

        if mode == "daily" and entry.get("status") == "complete":
            start_offset = entry.get("last_row_count", 0)
            append = True
            log.info(
                "  Daily append from row %d: %s", start_offset, resource_name
            )
        else:
            log.info("  Downloading datastore resource: %s", resource_name)

        try:
            rows_written = download_datastore_resource(
                resource_id, csv_path, start_offset=start_offset, append=append
            )
            prev = entry.get("last_row_count", 0) if append else 0
            state[resource_id] = {
                "status": "complete",
                "last_row_count": prev + rows_written,
                "last_run": now_iso(),
                "file_path": str(csv_path.relative_to(OUTPUT_DIR)),
                "dataset": dataset_name,
                "resource_name": resource_name,
                "type": "datastore",
            }
            log.info("  Done: %d rows (+%d new)", prev + rows_written, rows_written)
        except Exception as exc:
            log.error("  Datastore download failed for %s: %s", resource_name, exc)
            state[resource_id] = {**entry, "status": "error", "last_error": str(exc), "last_run": now_iso()}

    # ------------------------------------------------------------------
    # File resource (non-datastore)
    # ------------------------------------------------------------------
    else:
        # In daily mode re-download file resources regardless (no row tracking)
        if not file_url:
            log.warning("  No URL for resource: %s", resource_name)
            return

        # Use the resource format as the file extension where possible
        ext = f".{fmt.lower()}" if fmt and fmt not in ("", "OTHER") else ".csv"
        file_path = csv_path.with_suffix(ext)

        log.info("  Downloading file resource (%s): %s", fmt or "unknown", resource_name)
        ok = download_file_resource(file_url, file_path)
        if ok:
            state[resource_id] = {
                "status": "complete",
                "last_run": now_iso(),
                "file_path": str(file_path.relative_to(OUTPUT_DIR)),
                "dataset": dataset_name,
                "resource_name": resource_name,
                "type": "file",
                "format": fmt,
            }
        else:
            state[resource_id] = {**entry, "status": "error", "last_run": now_iso()}


# ---------------------------------------------------------------------------
# Main run
# ---------------------------------------------------------------------------

def run(mode: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Re-configure file log handler now that the output dir exists
    for h in log.handlers:
        if isinstance(h, logging.FileHandler):
            log.removeHandler(h)
    log.addHandler(logging.FileHandler(OUTPUT_DIR / "collector.log"))

    log.info("=" * 60)
    log.info("NESO Collector  mode=%s  started=%s", mode, now_iso())
    log.info("=" * 60)

    state = load_state()

    # ------------------------------------------------------------------
    # Step 1: fetch / refresh catalog
    # ------------------------------------------------------------------
    if mode == "backfill" or not CATALOG_FILE.exists():
        packages = fetch_catalog()
        with open(CATALOG_FILE, "w", encoding="utf-8") as f:
            json.dump(packages, f, indent=2, default=str)
        log.info("Catalog saved to %s", CATALOG_FILE)
    else:
        log.info("Loading cached catalog for daily run…")
        with open(CATALOG_FILE, encoding="utf-8") as f:
            packages = json.load(f)

    # ------------------------------------------------------------------
    # Step 2: process each resource
    # ------------------------------------------------------------------
    total_resources = sum(len(p.get("resources", [])) for p in packages)
    log.info("Processing %d resources across %d datasets…", total_resources, len(packages))

    processed = 0
    for pkg in packages:
        dataset_name = pkg.get("name", "unknown")
        org_name = (
            pkg.get("organization", {}) or {}
        ).get("name", "ungrouped")
        resources = pkg.get("resources", [])

        for resource in resources:
            processed += 1
            resource_name = resource.get("name") or resource.get("id", "")
            log.info(
                "[%d/%d] %s / %s / %s",
                processed,
                total_resources,
                org_name,
                dataset_name,
                resource_name,
            )
            process_resource(resource, dataset_name, org_name, state, mode)
            save_state(state)  # persist after every resource

    # ------------------------------------------------------------------
    # Step 3: summary
    # ------------------------------------------------------------------
    complete = sum(1 for v in state.values() if v.get("status") == "complete")
    errors = sum(1 for v in state.values() if v.get("status") == "error")
    log.info("=" * 60)
    log.info(
        "Run complete. complete=%d  errors=%d  total_seen=%d",
        complete,
        errors,
        len(state),
    )
    log.info("Output directory: %s", OUTPUT_DIR.resolve())
    log.info("=" * 60)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download all public NESO GB/UK energy data to CSV."
    )
    parser.add_argument(
        "--mode",
        choices=["backfill", "daily", "discover"],
        required=True,
        help=(
            "backfill: full download from scratch (skips already-complete resources). "
            "daily: append new rows / re-download files since last run. "
            "discover: sample every resource's structure (fields + a few rows) "
            "without downloading full data — bounded by --minutes."
        ),
    )
    parser.add_argument(
        "--minutes",
        type=float,
        default=15.0,
        help="Time budget in minutes for --mode discover (default: 15).",
    )
    args = parser.parse_args()
    if args.mode == "discover":
        run_discover(time_budget_seconds=args.minutes * 60.0)
    else:
        run(args.mode)
