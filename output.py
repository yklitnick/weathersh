"""
Minimal terminal output formatting
"""

from typing import Dict
import datetime
import sys


WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Light snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Light rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Light snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with light hail",
    99: "Thunderstorm with heavy hail",
}


def get_weather_description(code: int) -> str:
    return WMO_WEATHER_CODES.get(code, "Unknown")


def format_wind_direction(degrees: float) -> str:
    directions = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]
    idx = int((degrees + 11.25) // 22.5) % 16
    return directions[idx]


def print_current_weather(weather: Dict, geo: Dict, unit: str) -> None:
    temp_unit = "°C" if unit == "c" else "°F"
    temp = weather["temperature"]
    feels_like = weather["feels_like"]
    wind_speed = weather["wind_speed"]
    wind_dir = format_wind_direction(weather["wind_direction"])
    desc = get_weather_description(weather["weather_code"])

    # Try to make time human-friendly
    try:
        dt = datetime.datetime.fromisoformat(weather["time"].replace("Z", "+00:00"))
        time_str = dt.strftime("%H:%M")
    except Exception:
        time_str = weather["time"]

    print(f"{geo['display_name']:<30} {time_str}")
    print("─" * 45)

    print(f"Weather      {desc}")
    print(f"Temperature  {temp:.1f} {temp_unit}")
    print(f"Feels like   {feels_like:.1f} {temp_unit}")
    print(f"Humidity     {weather['humidity']}%")
    print(f"Wind         {wind_speed:.0f} km/h {wind_dir}")

    print()
    print("Updated      just now")
    print()
