"""
Network and Open-Meteo API interaction
"""

import json
import sys
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Optional


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_json(url: str) -> dict:
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


def geocode_city(name: str) -> Optional[Dict]:
    """
    Search for city and return best match with lat/lon and display name
    Returns None if nothing useful found
    """
    params = {"name": name, "count": 1, "language": "en", "format": "json"}
    query = urllib.parse.urlencode(params)
    url = f"{GEOCODING_URL}?{query}"

    data = fetch_json(url)

    results = data.get("results", [])
    if not results:
        return None

    best = results[0]

    return {
        "lat": best["latitude"],
        "lon": best["longitude"],
        "display_name": f"{best.get('name', 'Unknown')}, {best.get('country_code', '?')}",
    }


def get_current_weather(lat: float, lon: float, unit: str = "c") -> dict:
    """
    Get current weather conditions
    """
    temperature_unit = "celsius" if unit == "c" else "fahrenheit"

    params = {
        "latitude": str(lat),
        "longitude": str(lon),
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,"
        "weather_code,wind_speed_10m,wind_direction_10m",
        "temperature_unit": temperature_unit,
        "wind_speed_unit": "kmh",
        "timezone": "auto",
        "forecast_days": 1,  # we only need today
    }

    query = urllib.parse.urlencode(params)
    url = f"{FORECAST_URL}?{query}"

    data = fetch_json(url)

    current = data.get("current", {})
    if not current:
        raise ValueError("No current weather data in response")

    return {
        "temperature": current.get("temperature_2m"),
        "feels_like": current.get("apparent_temperature"),
        "humidity": current.get("relative_humidity_2m"),
        "wind_speed": current.get("wind_speed_10m"),
        "wind_direction": current.get("wind_direction_10m"),
        "weather_code": current.get("weather_code"),
        "time": current.get("time"),  # ISO time string
        "unit": unit,
    }
