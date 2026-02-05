#!/usr/bin/env python3
"""
weathersh - minimal terminal weather using Open-Meteo (stdlib only)
"""

import sys
import argparse
from pathlib import Path

from fetch import get_weather_data, geocode_city
from storage import load_default_location, save_default_location, clear_default_location
from output import (
    print_current_weather,
    print_current_daily_forecast,
    print_hourly_forecast,
)


def main():
    parser = argparse.ArgumentParser(
        description="Minimal CLI weather using Open-Meteo",
        epilog="Examples:\n"
        "  weathersh Paris\n"
        '  weathersh "New York"\n'
        "  weathersh --set-default Berlin\n"
        "  weathersh --unit f",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "location",
        nargs="?",
        help="City name (e.g. Paris, 'New York', Berlin DE)",
    )

    parser.add_argument(
        "--unit",
        choices=["c", "f"],
        default="c",
        help="Temperature unit: c (default) or f",
    )

    parser.add_argument(
        "--set-default",
        metavar="CITY",
        help="Save this location as default",
    )

    parser.add_argument(
        "--clear-default",
        action="store_true",
        help="Remove saved default location",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="weathersh 0.1.0",
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "--daily",
        action="store_true",
        help="Show daily forecast (today + next days)",
    )

    group.add_argument(
        "--hourly",
        action="store_true",
        help="Show hourly forecast for next 12–24 hours",
    )

    args = parser.parse_args()

    # Handle special modes first
    if args.clear_default:
        clear_default_location()
        print("Default location cleared.")
        return

    if args.set_default:
        print(f"Looking up '{args.set_default}'...", end="", flush=True)
        try:
            result = geocode_city(args.set_default)
            print("\r" + " " * 80 + "\r", end="", flush=True)  # clear line
            if not result:
                print(f"Could not find location: {args.set_default}", file=sys.stderr)
                return
            save_default_location(result)
            print(f"Default location set to: {result['display_name']}")
        except Exception as e:
            print("\r" + " " * 80 + "\r", end="", flush=True)
            print(f"Failed to set default location: {e}", file=sys.stderr)
        return

    # Determine which location to use
    city_input = None

    if args.location:
        city_input = args.location.strip()
    else:
        default = load_default_location()
        if default:
            # Use the saved name, but try to clean it for better geocoding success
            saved_name = default["display_name"]
            # Remove ", XX" or " XX" at the end if present
            if "," in saved_name:
                city_input = saved_name.split(",", 1)[0].strip()
            elif " " in saved_name:
                parts = saved_name.rsplit(" ", 1)
                if len(parts[1]) <= 3:  # likely country code
                    city_input = parts[0].strip()
                else:
                    city_input = saved_name
            else:
                city_input = saved_name

            print(f"Using saved default: {saved_name}")
        else:
            print("No location given and no default is set.", file=sys.stderr)
            print("Use:  weathersh <city>   or   weathersh --set-default <city>")
            return

    print(f"Fetching weather for {city_input}...", end="", flush=True)

    # Get coordinates
    try:
        geo = geocode_city(city_input)
        if not geo:
            print("\r" + " " * 80 + "\r", end="", flush=True)
            print(f"Location not found: {city_input}", file=sys.stderr)
            return
        weather_data = get_weather_data(geo["lat"], geo["lon"], unit=args.unit)
        print("\r" + " " * 80 + "\r", end="", flush=True)
        if args.daily:
            print_current_daily_forecast(weather_data, geo)
        elif args.hourly:
            print_hourly_forecast(weather_data, geo)
        else:
            print_current_weather(weather_data["current"], geo, args.unit)

    except KeyboardInterrupt:
        print("\rCancelled.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print("\r" + " " * 80 + "\r", end="", flush=True)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)




if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        sys.exit(1)
