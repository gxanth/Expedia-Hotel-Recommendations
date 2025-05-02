import polars as pl
from typing import List
from utils.feature_utils import standardize_expr, normalize_expr


def location_score_features() -> List[pl.Expr]:
    """
    Return a list of location-based feature expressions for hotels.
    """
    return [
        normalize_expr("location_score_primary"),
        normalize_expr("location_score_secondary"),
        (
            (
                normalize_expr("location_score_primary")
                + normalize_expr("location_score_secondary")
            )
            / 2
        ).alias("location_score_mean_norm"),
        standardize_expr("location_score_primary"),
        standardize_expr("location_score_secondary"),
        (
            (
                standardize_expr("location_score_primary")
                + standardize_expr("location_score_secondary")
            )
            / 2
        ).alias("location_score_mean_std"),
        (pl.col("location_score_primary") - pl.col("location_score_secondary")).alias(
            "location_score_diff"
        ),
    ]
