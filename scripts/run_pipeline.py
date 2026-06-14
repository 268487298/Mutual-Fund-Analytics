"""Master pipeline script for Mutual Analytics."""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List

ROOT_DIR = Path(__file__).resolve().parent
REPO_ROOT = ROOT_DIR.parent
MAIN_SCRIPT = REPO_ROOT / "main.py"
LOAD_PROCESSED_SCRIPT = ROOT_DIR / "load_processed_to_sqlite.py"
LIVE_NAV_SCRIPT = ROOT_DIR / "live_nav_fetch.py"


def run_command(command: List[str]) -> int:
    """Run a subprocess command and return the exit code."""
    result = subprocess.run(command, cwd=REPO_ROOT)
    return result.returncode


def run_raw_ingestion() -> int:
    """Run the raw CSV ingestion script."""
    return run_command([sys.executable, str(MAIN_SCRIPT)])


def run_processed_load() -> int:
    """Load cleaned processed datasets into the database."""
    return run_command([sys.executable, str(LOAD_PROCESSED_SCRIPT)])


def run_nav_fetch() -> int:
    """Fetch live NAV files for the configured schemes."""
    return run_command([sys.executable, str(LIVE_NAV_SCRIPT)])


def main() -> int:
    """Parse pipeline arguments and execute selected tasks."""
    parser = argparse.ArgumentParser(
        description="Run Mutual Analytics pipeline tasks."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all available pipeline tasks.",
    )
    parser.add_argument(
        "--load-raw",
        action="store_true",
        help="Load raw CSV datasets into the root SQLite database.",
    )
    parser.add_argument(
        "--load-processed",
        action="store_true",
        help="Load cleaned processed datasets into data/db/bluestock_mf.db.",
    )
    parser.add_argument(
        "--fetch-nav",
        action="store_true",
        help="Fetch live NAV history for configured schemes.",
    )
    args = parser.parse_args()

    if not any([args.all, args.load_raw, args.load_processed, args.fetch_nav]):
        args.all = True

    tasks = []
    if args.all or args.load_raw:
        tasks.append(run_raw_ingestion)
    if args.all or args.load_processed:
        tasks.append(run_processed_load)
    if args.all or args.fetch_nav:
        tasks.append(run_nav_fetch)

    for task in tasks:
        exit_code = task()
        if exit_code != 0:
            return exit_code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
