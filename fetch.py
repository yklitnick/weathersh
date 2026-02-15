"""
Network and Open-Meteo API interaction
"""

import json
import sys
import asyncio
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Optional


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def _fetch_json_sync(url: str) -> dict:
    """Fetch JSON from URL with timeout and basic error handling"""
    req = urllib.request.Request(
        url, headers={"User-Agent": "weathersh/0.1 (CLI tool)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            if response.getcode() != 200:
                raise ValueError(f"HTTP {response.getcode()}")
            data = response.read()
            return json.loads(data)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP error {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e.reason}")
    except json.JSONDecodeError:
        raise RuntimeError("Invalid JSON response from server")
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}")


async def fetch_json(url: str) -> dict:
    """Fetch JSON from URL with timeout and basic error handling (async)"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _fetch_json_sync, url)


async def geocode_city(name: str) -> Optional[Dict]:
    """
    Search for city and return best match with lat/lon and display name
    Returns None if nothing useful found
    """
    params = {"name": name, "count": 1, "language": "en", "format": "json"}
    query = urllib.parse.urlencode(params)
    url = f"{GEOCODING_URL}?{query}"

    data = await fetch_json(url)

    results = data.get("results", [])
    if not results:
        return None

    best = results[0]

    return {
        "lat": best["latitude"],
        "lon": best["longitude"],
        "display_name": f"{best.get('name', 'Unknown')}, {best.get('country_code', '?')}",
    }


async def get_weather_data(lat: float, lon: float, unit: str = "c") -> dict:
    """
    Fetch current + daily + hourly weather data from Open-Meteo
    """
    temperature_unit = "celsius" if unit == "c" else "fahrenheit"

    params = {
        # Current
        "current": (
            "temperature_2m,"
            "apparent_temperature,"
            "relative_humidity_2m,"
            "weather_code,"
            "wind_speed_10m,"
            "wind_direction_10m,"
            "precipitation_probability"
        ),
        # Daily forecast
        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "apparent_temperature_max,"
            "apparent_temperature_min,"
            "precipitation_sum,"
            "precipitation_probability_max,"
            "wind_speed_10m_max"
        ),
        # Hourly (next 24 hours)
        "hourly": (
            "temperature_2m,weather_code,precipitation_probability,precipitation"
        ),
        "temperature_unit": temperature_unit,
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
        "timezone": "auto",
        "forecast_days": 7,  # up to 7 days
        "forecast_hours": 24,  # next 24 hours
        "latitude": str(lat),
        "longitude": str(lon),
    }

    query = urllib.parse.urlencode(params)
    url = f"{FORECAST_URL}?{query}"

    data = await fetch_json(url)

    # Basic validation
    if "current" not in data or "daily" not in data or "hourly" not in data:
        raise ValueError("Incomplete weather data received")

    return {
        "current": data["current"],
        "daily": data["daily"],
        "hourly": data["hourly"],
        "unit": unit,
    }
