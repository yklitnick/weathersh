# weathersh – Minimal CLI Weather

A very simple, dependency-free command-line weather tool that uses only the Python standard library and the free Open-Meteo API.

## Features (current version)

- Shows current weather conditions
- Remembers your default location
- Supports °C and °F
- No external packages required

## Requirements

- Python 3.8 or newer

## Installation

1. Clone or download this repository

```bash
git clone https://github.com/yklitnick/weathersh.git
cd weathersh
```

2. Make the script executable (Linux/macOS):

```bash
chmod +x weathersh.py
```

Or just run it directly with python:

```bash
python weathersh.py [options]
```

## Recommended: add alias or symlink

```bash
# Option A – alias in ~/.bashrc or ~/.zshrc
alias wth='python3 /path/to/weathersh/weathersh.py'

# Option B – symlink to ~/bin (if you have it in PATH)
ln -s /path/to/weathersh/weathersh.py ~/bin/wth
```

## Usage

```bash
# Show current weather
weathersh Paris
weathersh "New York"
weathersh Berlin

# Use Fahrenheit
weathersh Berlin --unit f

# Set default location
weathersh --set-default "London,GB"

# Use default location
weathersh

# Clear default
weathersh --clear-default

# Help
weathersh --help
```

## Examples

```bash
$ weathersh Paris
Paris, FR                            14:35
─────────────────────────────────────────────
Weather      Light rain
Temperature  12.4 °C
Feels like   11.1 °C
Humidity     88%
Wind         19 km/h SSW

Updated      just now
```
