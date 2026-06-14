# Mutual Analytics

This repository supports mutual fund analytics through data ingestion, processing, metrics computation, and reporting for the Mutual Analytics project.

## Repository structure

- `data/`
  - `raw/` - inbound source CSVs and fetched NAV history files.
  - `processed/` - cleaned and transformed datasets used by analytics and loaders.
  - `db/` - local SQLite database output for processed tables.
- `scripts/` - pipeline and utility scripts:
  - `run_pipeline.py` - master entry point for pipeline tasks.
  - `live_nav_fetch.py` - fetches NAV history for selected schemes.
  - `load_processed_to_sqlite.py` - loads cleaned processed CSVs into `data/db/bluestock_mf.db`.
  - `etl_pipeline.py` - orchestrates ETL script execution.
  - `compute_metrics.py` - placeholder for computed metrics functions.
  - `recommender.py` - fund recommendation helper and CLI.
- `notebooks/` - exploratory analysis and reporting notebooks.
- `sql/` - schema definition and query examples.
- `dashboard/` - dashboard artifact (`bluestock_mf.pbix`).
- `reports/` - generated analysis and summary outputs.

## Setup

1. Activate the local Python environment:

   ```powershell
   .\mutual\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

## Running the project

### 1. Run the full pipeline

From the repository root:

```powershell
python .\scripts\run_pipeline.py
```

This now defaults to running all available steps.

### 2. Load raw CSVs only

```powershell
python .\scripts\run_pipeline.py --load-raw
```

### 3. Load processed datasets to SQLite

```powershell
python .\scripts\run_pipeline.py --load-processed
```

### 4. Fetch live NAV data

```powershell
python .\scripts\run_pipeline.py --fetch-nav
```

### 5. Use the recommender

```powershell
python .\scripts\recommender.py "Moderate" --top 5
```

## Dashboard

The dashboard file is located at `dashboard/bluestock_mf.pbix` and can be opened in Microsoft Power BI Desktop.

## Notes

- `main.py` loads raw source CSVs into `bluestock_mf.db` at the repository root.
- `scripts/load_processed_to_sqlite.py` loads cleaned processed datasets into `data/db/bluestock_mf.db`.
- `scripts/run_pipeline.py` now defaults to the full pipeline when run without flags.
- `dashboard/bluestock_mf.pbix` is the Power BI dashboard asset.
