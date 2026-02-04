"""
Storage of default location (very simple file-based approach)
"""

from pathlib import Path
import sys
from typing import Optional, Dict

CONFIG_DIR = Path.home() / ".config" / "weathersh"
CONFIG_FILE = CONFIG_DIR / "default_location.txt"


def ensure_config_dir() -> None:
    """Create config directory if it doesn't exist"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_default_location() -> Optional[Dict]:
    """
    Returns None if no default exists or file is invalid
    Returns dict with lat, lon, display_name
    """
    if not CONFIG_FILE.is_file():
        return None

    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        if len(lines) < 3:
            return None

        lat = float(lines[0])
        lon = float(lines[1])
        name = lines[2]

        return {"lat": lat, "lon": lon, "display_name": name}
    except (ValueError, OSError):
        return None


def save_default_location(location: Dict) -> None:
    """Save lat, lon, display_name"""
    ensure_config_dir()

    content = f"{location['lat']}\n{location['lon']}\n{location['display_name']}\n"

    try:
        with CONFIG_FILE.open("w", encoding="utf-8") as f:
            f.write(content)
    except OSError as e:
        print(f"Warning: Could not save default location: {e}", file=sys.stderr)


def clear_default_location() -> None:
    """Remove the default location file if it exists"""
    if CONFIG_FILE.exists():
        try:
            CONFIG_FILE.unlink()
        except OSError:
            pass
