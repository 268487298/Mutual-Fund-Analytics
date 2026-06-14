"""Recommender support for mutual fund schemes based on Sharpe ratio and risk appetite."""

from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

DATA_DIR = Path("data/processed")
PERFORMANCE_FILE = DATA_DIR / "clean_scheme_performance.csv"
RISK_GRADE_MAP = {
    "low": "Low",
    "moderate": "Moderate",
    "medium": "Moderate",
    "high": "High",
    "very high": "Very High",
    "very_high": "Very High",
    "veryhigh": "Very High",
}
RECOMMENDATION_COLUMNS = [
    "amfi_code",
    "scheme_name",
    "fund_house",
    "category",
    "plan",
    "return_1yr_pct",
    "return_3yr_pct",
    "return_5yr_pct",
    "sharpe_ratio",
    "aum_crore",
    "expense_ratio_pct",
    "risk_grade",
]


def load_scheme_performance(path: Path = PERFORMANCE_FILE) -> pd.DataFrame:
    """Load the cleaned scheme performance file into a pandas DataFrame."""
    if not path.exists():
        raise FileNotFoundError(f"Performance file not found: {path}")

    df = pd.read_csv(path)
    if "risk_grade" not in df.columns:
        raise ValueError("Expected 'risk_grade' column in scheme performance data.")
    if "sharpe_ratio" not in df.columns:
        raise ValueError("Expected 'sharpe_ratio' column in scheme performance data.")

    df["risk_grade"] = df["risk_grade"].astype(str).str.strip()
    return df


def normalize_risk_grade(risk_appetite: str) -> str:
    """Normalize user-supplied risk appetite values to canonical risk grades."""
    if not isinstance(risk_appetite, str):
        raise TypeError("risk_appetite must be a string")

    normalized = risk_appetite.strip().lower()
    if normalized not in RISK_GRADE_MAP:
        raise ValueError(
            "Unsupported risk appetite. Use one of: Low, Moderate, High, Very High."
        )
    return RISK_GRADE_MAP[normalized]


def recommend_top_funds_by_sharpe(
    risk_appetite: str,
    n: int = 3,
    category: Optional[str] = None,
    plan: Optional[str] = None,
    min_aum_crore: float = 0.0,
    performance_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Return the top funds by Sharpe ratio for a matching risk grade."""
    if performance_df is None:
        performance_df = load_scheme_performance()

    risk_grade = normalize_risk_grade(risk_appetite)
    df = performance_df.copy()
    df["risk_grade_normalized"] = df["risk_grade"].astype(str).str.strip().str.lower()

    df = df[df["risk_grade_normalized"] == risk_grade.lower()]
    if category is not None:
        df = df[df["category"].astype(str).str.strip().str.lower() == category.strip().lower()]
    if plan is not None:
        df = df[df["plan"].astype(str).str.strip().str.lower() == plan.strip().lower()]

    df = df[df["aum_crore"].fillna(0) >= float(min_aum_crore)]
    df = df.dropna(subset=["sharpe_ratio"])
    df = df.sort_values(by="sharpe_ratio", ascending=False)

    result_columns = [col for col in RECOMMENDATION_COLUMNS if col in df.columns]
    return df.loc[:, result_columns].head(max(1, int(n))).reset_index(drop=True)


def format_recommendations(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Convert recommendation DataFrame to a list of dictionaries for display or APIs."""
    if df.empty:
        return []
    return df.to_dict(orient="records")


def main() -> int:
    """Run the recommender CLI for the current performance CSV."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Recommend top mutual fund schemes by Sharpe ratio for a given risk appetite."
    )
    parser.add_argument(
        "risk_appetite",
        type=str,
        help="Investor risk appetite: Low, Moderate, High, or Very High.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=3,
        help="Number of top recommendations to return.",
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Optional fund category filter.",
    )
    parser.add_argument(
        "--plan",
        type=str,
        default=None,
        help="Optional plan filter (e.g. Direct, Regular).",
    )
    parser.add_argument(
        "--min-aum",
        type=float,
        default=0.0,
        help="Optional minimum AUM in crores for eligible funds.",
    )
    parser.add_argument(
        "--data-file",
        type=Path,
        default=PERFORMANCE_FILE,
        help="Path to the cleaned scheme performance CSV file.",
    )
    args = parser.parse_args()

    performance = load_scheme_performance(args.data_file)
    recommendations = recommend_top_funds_by_sharpe(
        risk_appetite=args.risk_appetite,
        n=args.top,
        category=args.category,
        plan=args.plan,
        min_aum_crore=args.min_aum,
        performance_df=performance,
    )

    if recommendations.empty:
        print("No matching funds found for the specified criteria.")
        return 0
    print(recommendations.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
