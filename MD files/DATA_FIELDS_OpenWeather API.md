# OpenWeatherMap — Data Field Reference

Field reference for `weather_data.csv`, produced by `OpenWeather API.py`.

## Overview

| | |
|---|---|
| Endpoint | `GET https://api.openweathermap.org/data/2.5/weather` (Current Weather Data, "2.5" free tier) |
| Auth | `appid` query parameter (API key) |
| Scope | Every city tagged `country: "GB"` in OpenWeatherMap's bulk city list — this includes mainland UK **and** the British Sovereign Base Areas in Cyprus (Akrotiri/Dhekelia, e.g. "Xylotymbou", "Episkopi"), since OpenWeatherMap codes those `GB` too. Worth filtering out if you want UK-only. |
| Rate limit | Free tier: 60 calls/min. The collector paces at ~1 call/sec (`SLEEP_BETWEEN_CALLS = 60/60`) |
| Coverage model | **Not a time series.** Each run takes one live snapshot per city, appending one row per city to the CSV. Re-running the script captures a fresh round of snapshots (progress-tracked via `weather_progress.txt`, so a run can be resumed if interrupted) — it does not backfill history, since the free "Current Weather" endpoint has no historical/forecast capability. |
| Lag | None beyond network latency — `data_timestamp_utc` reflects the provider's last observation/model update for that city, typically within the last ~10 minutes |

## Fields

| Field | Unit | Description |
|---|---|---|
| `datetime` | local timestamp | When *this collector* fetched the row (not a weather timestamp) |
| `city` | text | City name as OpenWeatherMap has it |
| `country` | ISO code | Country code from OpenWeatherMap's city list — `GB` here also includes the Cyprus base areas (see above) |
| `latitude` / `longitude` | decimal degrees | City coordinates |
| `timezone_offset_sec` | seconds | Shift from UTC for the city's local time |
| `city_id` | id | OpenWeatherMap's internal city ID (used as the API lookup key) |
| `weather_id` | code | OpenWeatherMap condition code (e.g. 800 = clear sky) |
| `weather_main` | text | Short condition group (Clear, Clouds, Rain, …) |
| `weather_description` | text | Longer human-readable condition text |
| `weather_icon` | code | Icon identifier for the condition |
| `temp_celsius` | °C | Current temperature (converted from the API's native Kelvin) |
| `feels_like_celsius` | °C | Perceived temperature accounting for humidity/wind |
| `temp_min_celsius` / `temp_max_celsius` | °C | Min/max observed temperature in the current data window (city-area variation, not a forecast range) |
| `pressure_hpa` | hPa | Atmospheric pressure at sea level (default) |
| `humidity_pct` | % | Relative humidity |
| `sea_level_hpa` | hPa | Pressure reduced to sea level, if provided |
| `grnd_level_hpa` | hPa | Pressure at ground/station level, if provided |
| `visibility_m` | metres | Visibility distance (capped at 10,000 m by the API) |
| `wind_speed_mps` | m/s | Wind speed |
| `wind_direction_deg` | degrees | Wind direction (meteorological, 0°=N) |
| `wind_gust_mps` | m/s | Wind gust speed, if reported |
| `cloud_cover_pct` | % | Cloudiness |
| `rain_1h_mm` / `rain_3h_mm` | mm | Rain volume in the last 1h / 3h, if any fell |
| `snow_1h_mm` / `snow_3h_mm` | mm | Snow volume in the last 1h / 3h, if any fell |
| `sunrise_utc` / `sunset_utc` | UTC datetime | Sunrise/sunset time for this city on the day of the observation |
| `data_timestamp_utc` | UTC datetime | Timestamp of the underlying weather observation/model run — this is the field to treat as "as-of" time, not `datetime` |

## Note on the API key

The key is currently hardcoded in `OpenWeather API.py` (`API_KEY = "aef4e..."`) rather than loaded from `.env` like the other collectors in this folder. Flagging for awareness, not changed here since it wasn't part of this task.
