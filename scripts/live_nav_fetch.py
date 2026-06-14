"""Fetch NAV history for selected mutual fund schemes and save raw NAV CSV files."""

import time
from pathlib import Path
from typing import Dict, List

import pandas as pd
import requests

SCHEMES: Dict[str, str] = {
    "hdfc_top100": "125497",
    "sbi_bluechip": "119551",
    "icici_bluechip": "120503",
    "nippon_large_cap": "118632",
    "axis_bluechip": "119092",
    "kotak_bluechip": "120841",
}

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "data" / "raw" / "nav_data"


def fetch_scheme_nav(scheme_name: str, scheme_code: str) -> pd.DataFrame:
    """Fetch NAV history for a single mutual fund scheme."""
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    for attempt in range(3):
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return pd.DataFrame(response.json()["data"])
    raise RuntimeError(f"Unable to fetch NAV data for {scheme_name}")


def save_nav_csv(scheme_name: str, nav_df: pd.DataFrame) -> Path:
    """Save NAV history DataFrame to the raw nav_data folder."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    file_path = OUTPUT_DIR / f"{scheme_name}.csv"
    nav_df.to_csv(file_path, index=False)
    return file_path


def main() -> int:
    """Fetch NAV data for all predefined schemes."""
    successful_schemes: List[str] = []
    failed_schemes: List[str] = []

    for scheme_name, scheme_code in SCHEMES.items():
        try:
            nav_df = fetch_scheme_nav(scheme_name, scheme_code)
            save_nav_csv(scheme_name, nav_df)
            successful_schemes.append(scheme_name)
        except Exception:
            failed_schemes.append(scheme_name)

    print("NAV fetch completed.")
    print(f"Successful downloads: {len(successful_schemes)}")
    print(f"Failed downloads: {len(failed_schemes)}")

    return 0 if not failed_schemes else 1


if __name__ == "__main__":
    raise SystemExit(main())
