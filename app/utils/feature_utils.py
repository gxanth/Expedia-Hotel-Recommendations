from pathlib import Path
import polars as pl
import numpy as np
import re
from typing import List, Dict
from collections import defaultdict
import yaml
from pathlib import Path
from app.utils.data_loader import load_config, load_table_styles


# -----------------------------
# 1. Dummy Data Generator
# -----------------------------
def generate_dummy_feature_data(seed: int = 42) -> pl.LazyFrame:
    """
    Generate dummy Expedia-style feature data.

    Returns:
        pl.LazyFrame: Polars lazy dataframe with numeric feature variants.
    """
    np.random.seed(seed)
    df = pl.DataFrame(
        {
            "price_usd": np.random.normal(120, 25, 1000),
            "log_price_usd": np.log1p(np.random.normal(120, 25, 1000)),
            "price_usd_norm": np.random.beta(2, 5, 1000),
            "visitor_hist_adr_usd": np.random.normal(100, 20, 1000),
            "log_visitor_hist_adr_usd": np.log1p(np.random.normal(100, 20, 1000)),
            "prop_review_score": np.clip(np.random.normal(4.2, 0.6, 1000), 1.0, 5.0),
            "target": np.random.choice([0, 1, 5], 1000, p=[0.3, 0.3, 0.4]),
        }
    )
    return df.lazy()


def generate_and_save_dummy(
    path: Path = Path("data/processed/dummy_expedia.parquet"), seed: int = 42
) -> None:
    """
    Generate dummy data and save to Parquet file.

    Args:
        path (Path): Output path.
        seed (int): Random seed.
    """
    lf = generate_dummy_feature_data(seed)
    df = lf.collect()
    path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(str(path))
    print(f"✅ Dummy dataset saved to: {path.resolve()}")


# ------------------------------
# 2. Generate Feature Summary
# ------------------------------


def generate_feature_summary(df: pl.LazyFrame, features: list[str]) -> pl.DataFrame:
    """
    Compute rounded summary statistics for a list of numeric features in a Polars LazyFrame.

    Args:
        df (pl.LazyFrame): The input lazy Polars dataframe
        features (list): The feature columns to summarize

    Returns:
        pl.DataFrame: Rounded summary statistics per feature
    """
    summary = pl.concat(
        [
            df.select(
                [
                    pl.lit(col).alias("feature"),  # column name
                    pl.col(col)
                    .mean()
                    .cast(pl.Float64)
                    .round(3)
                    .alias("mean"),  # average
                    pl.col(col)
                    .std()
                    .cast(pl.Float64)
                    .round(3)
                    .alias("std"),  # standard deviation
                    pl.col(col).min().cast(pl.Float64).round(3).alias("min"),  # minimum
                    pl.col(col).max().cast(pl.Float64).round(3).alias("max"),  # maximum
                    (pl.col(col).is_null().sum() / pl.len())
                    .round(3)
                    .alias("null_pct"),  # percent null
                    ((pl.col(col) == 0).sum() / pl.len())
                    .round(3)
                    .alias("zero_pct"),  # percent zeros
                    (
                        (
                            0.6745
                            * (pl.col(col) - pl.col(col).median())
                            / (pl.col(col).abs().median() + 1e-6)
                        ).abs()
                        > 3.0
                    )
                    .sum()
                    .alias("outlier_count"),  # MAD outliers
                    pl.col(col).n_unique().alias("n_unique"),  # number of unique values
                    pl.col(col)
                    .skew()
                    .round(3)
                    .alias("skew"),  # skewness using built-in method
                    pl.col(col)
                    .kurtosis()
                    .round(3)
                    .alias("kurt"),  # kurtosis using built-in method
                ]
            )
            for col in features
        ]
    ).collect()

    return summary


# -----------------------------
# 3. Feature Variant Grouping (Regex-based)
# -----------------------------
def find_feature_variants_regex(columns: List[str]) -> Dict[str, List[str]]:
    """
    Group columns by base feature using regex patterns to remove prefixes/suffixes.

    Args:
        columns (List[str]): List of column names from the dataset.

    Returns:
        Dict[str, List[str]]: Base feature -> list of all its variants.
    """
    variant_map = defaultdict(
        list
    )  # automatically starts new base group with empty list

    # This pattern:
    # - skips known prefixes like log_/sqrt_/bin_
    # - skips known suffixes like _norm/_zscore
    pattern = re.compile(
        r"^(?:log_|sqrt_|zscore_|bin_)?(.*?)(?:_norm|_mad_filtered|_bin|_zscore)?$"
    )

    for col in columns:
        match = pattern.match(col)
        if match:
            base = match.group(1)  # capture the central feature name
            variant_map[base].append(col)  # group the original name under the base

    return dict(variant_map)
