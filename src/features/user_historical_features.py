# src/features/user_history_features.py
import polars as pl
from typing import List

def user_history_flags() -> List[pl.Expr]:
    return [
        pl.col("visitor_hist_adr_usd").is_not_null().cast(pl.Int8).alias("has_user_price_history"),
        pl.col("visitor_hist_starrating").is_not_null().cast(pl.Int8).alias("has_user_rating_history")
    ]

def user_vs_hotel_diff_features() -> List[pl.Expr]:
    return [
        (pl.col("price_usd") - pl.col("visitor_hist_adr_usd")).alias("price_diff_vs_user_history"),
        (pl.col("prop_starrating") - pl.col("visitor_hist_starrating")).alias("star_diff_vs_user_history")
    ]

def all_user_history_features() -> List[pl.Expr]:
    return user_history_flags() + user_vs_hotel_diff_features()
