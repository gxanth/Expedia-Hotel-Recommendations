import polars as pl
from typing import List


def hotel_rolling_features(window_size: int = 7) -> List[pl.Expr]:
    """
    Return a list of expressions for rolling features (mean, std, click rate)
    based on search timestamp over a window of days.
    """
    return [
        pl.col("display_price")
        .rolling_mean_by(by="search_timestamp", window_size=f"{window_size}d")
        .over("hotel_id")
        .alias("rolling_mean_price"),
        pl.col("display_price")
        .rolling_std_by(by="search_timestamp", window_size=f"{window_size}d")
        .over("hotel_id")
        .alias("rolling_std_price"),
        pl.col("was_clicked")
        .rolling_mean_by(by="search_timestamp", window_size=f"{window_size}d")
        .over("hotel_id")
        .alias("rolling_click_rate"),
    ]
