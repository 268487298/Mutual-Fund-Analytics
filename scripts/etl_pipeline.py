"""Utility module for running ETL steps in the Mutual Analytics project."""

import subprocess
import sys
from pathlib import Path
from typing import List

ROOT_DIR = Path(__file__).resolve().parent
MAIN_SCRIPT = ROOT_DIR.parent / "main.py"
LOAD_PROCESSED_SCRIPT = ROOT_DIR / "scripts" / "load_processed_to_sqlite.py"
FETCH_NAV_SCRIPT = ROOT_DIR / "scripts" / "live_nav_fetch.py"


def run_script(script_path: Path, args: List[str] = None) -> int:
    """Execute a Python script in the repository root environment."""
    if args is None:
        args = []
    command = [sys.executable, str(script_path)] + args
    result = subprocess.run(command, cwd=ROOT_DIR.parent)
    return result.returncode


def main() -> int:
    """Run the raw and processed ETL scripts sequentially."""
    exit_codes = []
    exit_codes.append(run_script(MAIN_SCRIPT))
    exit_codes.append(run_script(LOAD_PROCESSED_SCRIPT))
    return max(exit_codes)


if __name__ == "__main__":
    raise SystemExit(main())
