import polars as pl
from typing import List

def hotel_rolling_features(window_size: int = 10) -> List[pl.Expr]:
    return [
        pl.col("price_usd")
        .rolling_mean_by(
            "date", 
            window_size=f"{window_size}i", 
            by="prop_id"
        )
        .alias("rolling_mean_price"),

        pl.col("price_usd")
        .rolling_std_by(
            "date", 
            window_size=f"{window_size}i", 
            by="prop_id"
        )
        .alias("rolling_std_price"),

        pl.col("click_bool")
        .rolling_mean_by(
            "date", 
            window_size=f"{window_size}i", 
            by="prop_id"
        )
        .alias("rolling_click_rate")
    ]