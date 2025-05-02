# src/features/build_features.py

import polars as pl
from pathlib import Path

# Hotel features
from hotel.hotel_entropy import (
    hotel_click_entropy_price_tier,
)  # Modified to work with LazyFrames
from hotel.hotel_rolling_features import hotel_rolling_features
from hotel.location_features import location_score_features

# User features
from user.user_historical_features import (
    user_history_flags,
    user_vs_hotel_diff_features,
)

# Booking features
from booking.booking_features import booking_stats_features, query_level_flags

# Search features
from search.search_context_features import search_context_features
from search.search_temporal_features import (
    search_time_features,
    booking_time_features,
)

# Competitor features
from competitor.competitor_features import (
    competitor_inv_features,
    competitor_rate_features,
    competitor_price_diff_features,
)

from utils.memory_utils import optimize_memory
from utils.load_yaml import load_yaml
from utils.feature_utils import mad_filter, groupwise_mean_imputation


def build_features(lf: pl.LazyFrame) -> pl.LazyFrame:
    """
    Build features using LazyFrame operations throughout the pipeline.

    Parameters:
    -----------
    lf : pl.LazyFrame
        Input LazyFrame with raw data

    Returns:
    --------
    pl.LazyFrame
        LazyFrame with all features added
    """
    print("Starting feature building pipeline in lazy mode...")

    # ============ Step 1: Precompute dependencies ============

    print("[1/7] Creating intermediate time columns...")
    lf = lf.with_columns(
        [
            *search_time_features(),
            *booking_time_features(),  # needs expected_checkin_date
        ]
    )

    # ============ Step 2: Hotel features ============
    print("[2/7] Applying hotel features...")
    lf = lf.with_columns(
        [
            *hotel_rolling_features(window_size=7),  # needs search_date
            *location_score_features(),
        ]
    )

    # ============ Step 3: User features ============
    print("[3/7] Applying user features...")
    lf = lf.with_columns(
        [
            *user_history_flags(),
            *user_vs_hotel_diff_features(),
        ]
    )

    # ============ Step 4: Booking features ============
    print("[4/7] Applying booking features...")
    lf = lf.with_columns(
        [
            *booking_stats_features(),
            *query_level_flags(),
            *booking_time_features(),  # needs expected_checkin_date
        ]
    )

    # ============ Step 5: Search context features ============
    print("[5/7] Applying search context features...")
    lf = lf.with_columns(
        [
            *search_context_features(),
        ]
    )

    # ============ Step 6: Competitor features ============
    print("[6/7] Applying competitor features...")
    lf = lf.with_columns(
        [
            *competitor_inv_features(),
            *competitor_rate_features(),
            *competitor_price_diff_features(),
        ]
    )

    # ============ Step 7: Apply entropy features in lazy mode ============
    print("[7/7] Applying entropy features in lazy mode...")
    lf = hotel_click_entropy_price_tier(
        lf
    )  # Modified version that works with LazyFrames

    print("✅ Feature building pipeline completed (lazy mode).")
    return lf


# ==========================
# Test block for sanity check
# ==========================
if __name__ == "__main__":
    # === CONFIG ===
    DATA_DIR = Path("data")
    RAW_PATH = DATA_DIR / "raw" / "train.csv"
    PROCESSED_PATH = DATA_DIR / "processed" / "features.parquet"
    RENAME_MAP_PATH = Path("src/configs/feature_rename_map.yaml")
    DTYPES_MAP_PATH = Path("src/configs/downcast_dtypes_map.yaml")

    # === PIPELINE START ===
    print("\n[TEST] Running build_features on development subset...\n")

    # Load renaming and dtypes map
    rename_map = load_yaml(RENAME_MAP_PATH)
    dtypes_config = load_yaml(DTYPES_MAP_PATH)
    dtypes = {k: getattr(pl, v) for k, v in dtypes_config.items()}

    # Load raw dataset (lazy, from CSV)
    lf_raw = pl.scan_csv(RAW_PATH, null_values=["NULL"], try_parse_dates=True)
    lf_raw = lf_raw.rename(rename_map, strict=False).cast(dtypes, strict=True)

    # === Preprocessing (MAD Filtering + Imputation) ===
    lf_raw = mad_filter(lf_raw, input_column="display_price", z_thresh=3.5)
    lf_raw = groupwise_mean_imputation(
        lf_raw,
        groupby_cols=["hotel_id"],
        feature_to_impute="display_price_mad_filtered",
    )

    # === Development Sample ===
    lf_dev_sample = lf_raw.limit(100_000)

    # === Feature Engineering ===
    lf_features = build_features(lf_dev_sample)

    # === Collect & Save ===
    print("\n[TEST] Collecting final results...")
    df_features_final = lf_features.collect(engine="gpu")

    print(
        f"\n[INFO] Final dataset: {df_features_final.shape[0]} rows, {df_features_final.shape[1]} columns."
    )

    print("\n[SAVE] Writing final DataFrame to Parquet...")
    df_features_final.write_parquet(PROCESSED_PATH)
    print(f"[✓] Saved to {PROCESSED_PATH.resolve()}")

    # Optional: For large datasets, you could use streaming mode
    # df_features = df_features_lazy.collect(engine="streaming")
