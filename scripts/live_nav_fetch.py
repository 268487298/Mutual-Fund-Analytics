import requests
import pandas as pd
from pathlib import Path
import time

# Mutual Fund Schemes
schemes = {
    "hdfc_top100": "125497",
    "sbi_bluechip": "119551",
    "icici_bluechip": "120503",
    "nippon_large_cap": "118632",
    "axis_bluechip": "119092",
    "kotak_bluechip": "120841",
}

# Create output folder
output_dir = Path("data/raw/nav_data")
output_dir.mkdir(parents=True, exist_ok=True)

successful_schemes = []
failed_schemes = []

print("Fetching NAV data...\n")

for scheme_name, scheme_code in schemes.items():

    url = f"https://api.mfapi.in/mf/{scheme_code}"

    try:
        # Retry up to 3 times
        for attempt in range(3):
            try:
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                break
            except Exception:
                if attempt < 2:
                    print(f"Retrying {scheme_name} (Attempt {attempt + 2}/3)...")
                    time.sleep(2)
                else:
                    raise

        data = response.json()

        # Convert NAV history to DataFrame
        nav_df = pd.DataFrame(data["data"])

        # Save CSV
        file_path = output_dir / f"{scheme_name}.csv"
        nav_df.to_csv(file_path, index=False)

        successful_schemes.append(scheme_name)

        print(f"✓ {scheme_name} saved successfully")
        print(f"  Rows: {len(nav_df)}")
        print(f"  File: {file_path}\n")

    except Exception as e:
        failed_schemes.append(scheme_name)

        print(f"✗ Error fetching {scheme_name}")
        print(f"  Reason: {e}\n")

print("=" * 50)
print("DOWNLOAD SUMMARY")
print("=" * 50)

print(f"\nSuccessful Downloads: {len(successful_schemes)}")
for scheme in successful_schemes:
    print(f"✓ {scheme}")

print(f"\nFailed Downloads: {len(failed_schemes)}")
for scheme in failed_schemes:
    print(f"✗ {scheme}")

print("\nProcess Completed.")
