#!/usr/bin/env python3
"""
weathersh - minimal terminal weather using Open-Meteo (stdlib only)
"""

import sys
import argparse
from pathlib import Path

from fetch import get_current_weather, geocode_city
from storage import load_default_location, save_default_location, clear_default_location
from output import print_current_weather


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

    args = parser.parse_args()

    # Handle special modes first
    if args.clear_default:
        clear_default_location()
        print("Default location cleared.")
        return

    if args.set_default:
        # We will geocode and save coordinates + name
        try:
            result = geocode_city(args.set_default)
            if not result:
                print(
                    f"Error: Could not find location '{args.set_default}'",
                    file=sys.stderr,
                )
                return
            save_default_location(result)
            print(f"Default location set to: {result['display_name']}")
        except Exception as e:
            print(f"Error setting default: {e}", file=sys.stderr)
        return

    # Determine which location to use
    city_input = None

    if args.location:
        city_input = args.location
    else:
        default = load_default_location()
        if default:
            city_input = default["display_name"]
            print(f"Using saved location: {city_input}")
        else:
            print("No location provided and no default set.", file=sys.stderr)
            print("Run with a city name or use --set-default CITY", file=sys.stderr)
            return

    # Get coordinates
    try:
        geo = geocode_city(city_input)
        if not geo:
            print(f"Could not find location: {city_input}", file=sys.stderr)
            return
    except Exception as e:
        print(f"Geocoding error: {e}", file=sys.stderr)
        return

    # Fetch weather
    try:
        weather = get_current_weather(geo["lat"], geo["lon"], unit=args.unit)
    except Exception as e:
        print(f"Error fetching weather: {e}", file=sys.stderr)
        return

    # Show result
    print_current_weather(weather, geo, args.unit)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        sys.exit(1)
