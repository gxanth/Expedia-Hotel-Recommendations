# src/features/competitor_features.py
import polars as pl
from typing import List


def competitor_rate_features() -> List[pl.Expr]:
    comp_rate_cols = [f"comp{i}_rate" for i in range(1, 9)]

    return [
        pl.sum_horizontal(
            [pl.col(col).eq(1).cast(pl.Int8) for col in comp_rate_cols]
        ).alias("num_comp_cheaper"),
        pl.sum_horizontal(
            [pl.col(col).eq(0).cast(pl.Int8) for col in comp_rate_cols]
        ).alias("num_comp_same_price"),
        pl.sum_horizontal(
            [pl.col(col).eq(-1).cast(pl.Int8) for col in comp_rate_cols]
        ).alias("num_comp_more_expensive"),
        pl.sum_horizontal(
            [pl.col(col).is_not_null().cast(pl.Int8) for col in comp_rate_cols]
        ).alias("num_valid_comp_rate"),
    ]


def competitor_inv_features() -> List[pl.Expr]:
    comp_inv_cols = [f"comp{i}_inv" for i in range(1, 9)]

    return [
        pl.sum_horizontal(
            [pl.col(col).eq(1).cast(pl.Int8) for col in comp_inv_cols]
        ).alias("num_competitor_unavailable"),
        pl.sum_horizontal(
            [pl.col(col).is_not_null().cast(pl.Int8) for col in comp_inv_cols]
        ).alias("num_valid_comp_inv"),
    ]


def competitor_price_diff_features() -> List[pl.Expr]:
    comp_pct_cols = [f"comp{i}_rate_percent_diff" for i in range(1, 9)]

    return [
        pl.mean_horizontal([pl.col(c).cast(pl.Float64) for c in comp_pct_cols]).alias(
            "mean_comp_price_diff_pct"
        ),
        pl.max_horizontal([pl.col(c).cast(pl.Float64) for c in comp_pct_cols]).alias(
            "max_comp_price_diff_pct"
        ),
    ]


__all__ = [
    "competitor_rate_features",
    "competitor_inv_features",
    "competitor_price_diff_features",
]
