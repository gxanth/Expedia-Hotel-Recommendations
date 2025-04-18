# src/features/location_features.py
import polars as pl
from typing import List
from features.utils import standardize_expr, normalize_expr

def location_score_features() -> List[pl.Expr]:
    return [
        normalize_expr("prop_location_score1"),
        normalize_expr("prop_location_score2"),
        (
            (normalize_expr("prop_location_score1") + normalize_expr("prop_location_score2")) / 2
        ).alias("location_score_mean_norm"),

        standardize_expr("prop_location_score1"),
        standardize_expr("prop_location_score2"),
        (
            (standardize_expr("prop_location_score1") + standardize_expr("prop_location_score2")) / 2
        ).alias("location_score_mean_std"),

        (pl.col("prop_location_score1") - pl.col("prop_location_score2")).alias("location_score_diff")
    ]
