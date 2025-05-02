# src/features/build_features.py
import polars as pl
from pathlib import Path
from features.booking_features import all_booking_features
from features.location_features import location_features
from features.user_historical_features import all_user_history_features
from features.temporal_features import all_temporal_features
from features.competitor_features import all_competitor_features
from features.desirability_features import all_desirability_features
from features.hotel_entropy import hotel_click_entropy_price_tier
from features.rolling_features import hotel_rolling_features
from features.search_context_features import search_context_features
from features.imputation_module import (
    optimized_groupwise_median_imputation,
    optimized_mean_imputation,
    optimized_median_imputation
)
from features.outlier_detection import apply_mad_outlier_filter

def build_feature_pipeline(df: pl.LazyFrame, debug: bool = True, filter_outliers: bool = True) -> pl.LazyFrame:
    if debug: print("🚧 Starting feature pipeline...")

    # 1. Optional: Filter outliers on *_usd columns
    if filter_outliers:
        if debug: print("⚠️  Applying MAD-based outlier filtering to USD columns...")
        usd_columns = [
            "price_usd",
            "visitor_hist_adr_usd",
            "prop_log_historical_price",
            "gross_bookings_usd"
        ]
        df = apply_mad_outlier_filter(df, columns=usd_columns, threshold=3.0)

    # 2. Imputation
    if debug: print("🔧 Imputing missing values...")
    df = optimized_groupwise_median_imputation(df, group_col="prop_id", target_cols=["prop_review_score", "prop_log_historical_price"])
    df = optimized_mean_imputation(df, ["visitor_hist_adr_usd"])
    df = optimized_median_imputation(df, ["orig_destination_distance"])

    # 3. Feature Expressions
    if debug: print("➕ Adding expression-based features...")
    df = df.with_columns([
        *all_booking_features(),
        *all_user_history_features(),
        *location_features(),
        *all_temporal_features(),
        *all_competitor_features(),
        *all_desirability_features(),
        *search_context_features(),
        *hotel_rolling_features()
    ])

    # 4. DataFrame-Level Features
    if debug: print("📊 Adding aggregated features...")
    df = hotel_click_entropy_price_tier(df)

    if debug: print("✅ Feature pipeline complete (lazy mode).")
    return df

def save_feature_matrix(df: pl.LazyFrame, output_path: Path = Path("data/processed/features_output.parquet"), debug: bool = True):
    if debug: print(f"💾 Saving output to {output_path}...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.collect().write_parquet(output_path)
    if debug: print("✅ Done.")

if __name__ == "__main__":
    raw_path = Path("data/raw/train.csv")
    if not raw_path.exists():
        raise FileNotFoundError(f"❌ Raw data not found at {raw_path}")

    print("📥 Loading raw data...")
    raw_df = pl.read_csv(raw_path).lazy()

    processed_df = build_feature_pipeline(raw_df, debug=True, filter_outliers=True)
    save_feature_matrix(processed_df, Path("data/processed/features_output.parquet"), debug=True)
