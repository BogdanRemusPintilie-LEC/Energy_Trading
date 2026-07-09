import requests
import pandas as pd
import datetime as dt
import os
import gzip
import json
import time

# Constants
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
API_KEY = "aef4e5249b8843ca1c567108af2766d7"
CSV_FILE = 'weather_data.csv'
CITY_LIST_FILE = 'city.list.json.gz'
CITY_LIST_URL = 'http://bulk.openweathermap.org/sample/city.list.json.gz'
PROGRESS_FILE = 'weather_progress.txt'

# Free tier: 60 calls/min. Set to 62 to stay safely under.
CALLS_PER_MINUTE = 60
SLEEP_BETWEEN_CALLS = 60.0 / CALLS_PER_MINUTE  # ~1 second

BATCH_SIZE = 100  # Write to CSV every N successful records


def kelvin_to_celsius(kelvin):
    return round(kelvin - 273.15, 2)


def download_city_list():
    print("Downloading city list from OpenWeatherMap...")
    r = requests.get(CITY_LIST_URL, stream=True, timeout=60)
    r.raise_for_status()
    with open(CITY_LIST_FILE, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Saved to {CITY_LIST_FILE}")


def load_city_ids():
    if not os.path.exists(CITY_LIST_FILE):
        download_city_list()
    print("Loading city list (UK only)...")
    with gzip.open(CITY_LIST_FILE, 'rt', encoding='utf-8') as f:
        cities = json.load(f)
    ids = [c['id'] for c in cities if c.get('country') == 'GB']
    print(f"Total UK cities: {len(ids):,}")
    return ids


def load_progress():
    """Return the last successfully processed city ID index (0-based), or -1."""
    if not os.path.exists(PROGRESS_FILE):
        return -1
    with open(PROGRESS_FILE, 'r') as f:
        content = f.read().strip()
    return int(content) if content else -1


def save_progress(index):
    with open(PROGRESS_FILE, 'w') as f:
        f.write(str(index))


def fetch_weather_by_id(city_id):
    url = BASE_URL + f"appid={API_KEY}&id={city_id}"
    try:
        r = requests.get(url, timeout=10).json()
    except requests.RequestException as e:
        print(f"  Request error for ID {city_id}: {e}")
        return None

    if r.get('cod') != 200:
        # 404 = city not found (stale ID), skip silently; log others
        if r.get('cod') != 404:
            print(f"  API error for ID {city_id}: {r.get('message', 'unknown')}")
        return None

    main         = r.get('main', {})
    wind         = r.get('wind', {})
    clouds       = r.get('clouds', {})
    sys_data     = r.get('sys', {})
    coord        = r.get('coord', {})
    weather_list = r.get('weather', [{}])
    weather      = weather_list[0] if weather_list else {}

    return {
        'datetime':              dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'city':                  r.get('name'),
        'country':               sys_data.get('country'),
        'latitude':              coord.get('lat'),
        'longitude':             coord.get('lon'),
        'timezone_offset_sec':   r.get('timezone'),
        'city_id':               r.get('id'),
        'weather_id':            weather.get('id'),
        'weather_main':          weather.get('main'),
        'weather_description':   weather.get('description'),
        'weather_icon':          weather.get('icon'),
        'temp_celsius':          kelvin_to_celsius(main['temp']) if 'temp' in main else None,
        'feels_like_celsius':    kelvin_to_celsius(main['feels_like']) if 'feels_like' in main else None,
        'temp_min_celsius':      kelvin_to_celsius(main['temp_min']) if 'temp_min' in main else None,
        'temp_max_celsius':      kelvin_to_celsius(main['temp_max']) if 'temp_max' in main else None,
        'pressure_hpa':          main.get('pressure'),
        'humidity_pct':          main.get('humidity'),
        'sea_level_hpa':         main.get('sea_level'),
        'grnd_level_hpa':        main.get('grnd_level'),
        'visibility_m':          r.get('visibility'),
        'wind_speed_mps':        wind.get('speed'),
        'wind_direction_deg':    wind.get('deg'),
        'wind_gust_mps':         wind.get('gust'),
        'cloud_cover_pct':       clouds.get('all'),
        'rain_1h_mm':            r.get('rain', {}).get('1h'),
        'rain_3h_mm':            r.get('rain', {}).get('3h'),
        'snow_1h_mm':            r.get('snow', {}).get('1h'),
        'snow_3h_mm':            r.get('snow', {}).get('3h'),
        'sunrise_utc':           dt.datetime.utcfromtimestamp(sys_data['sunrise']).strftime('%Y-%m-%d %H:%M:%S') if sys_data.get('sunrise') else None,
        'sunset_utc':            dt.datetime.utcfromtimestamp(sys_data['sunset']).strftime('%Y-%m-%d %H:%M:%S') if sys_data.get('sunset') else None,
        'data_timestamp_utc':    dt.datetime.utcfromtimestamp(r['dt']).strftime('%Y-%m-%d %H:%M:%S') if r.get('dt') else None,
    }


def flush_batch(batch, write_header):
    df = pd.DataFrame(batch)
    df.to_csv(CSV_FILE, index=False, mode='a', header=write_header)
    return False  # header already written after first flush


def main():
    city_ids = load_city_ids()
    total = len(city_ids)

    last_index = load_progress()
    start_index = last_index + 1

    if start_index > 0:
        print(f"Resuming from index {start_index:,} / {total:,} ({start_index/total*100:.1f}% done)")
    else:
        print(f"Starting fresh run over {total:,} cities.")

    write_header = not os.path.exists(CSV_FILE) or start_index == 0
    batch = []
    fetched = 0
    errors = 0

    for i in range(start_index, total):
        city_id = city_ids[i]
        data = fetch_weather_by_id(city_id)

        if data:
            batch.append(data)
            fetched += 1
        else:
            errors += 1

        # Flush batch to disk
        if len(batch) >= BATCH_SIZE:
            write_header = flush_batch(batch, write_header)
            batch = []
            save_progress(i)
            print(f"  [{i+1:,}/{total:,}] Fetched: {fetched:,}  Errors/skipped: {errors:,}")

        time.sleep(SLEEP_BETWEEN_CALLS)

    # Final flush
    if batch:
        flush_batch(batch, write_header)

    save_progress(total - 1)
    print(f"\nDone. {fetched:,} cities written to {CSV_FILE}. {errors:,} skipped/errored.")


if __name__ == '__main__':
    main()
