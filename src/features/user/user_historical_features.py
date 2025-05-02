import polars as pl
from typing import List


def user_history_flags() -> List[pl.Expr]:
    """
    Generate flags indicating whether the user has historical data for price and star rating.

    - **`has_user_price_history`**: Indicates if the user has recorded price history.
    - **`has_user_rating_history`**: Indicates if the user has recorded star rating history.

    These features help determine if we have enough historical data to make personalized predictions.
    """
    return [
        pl.col("user_hist_avg_price")
        .is_not_null()
        .cast(pl.Int8)
        .alias("has_user_price_history"),
        pl.col("user_hist_avg_stars")
        .is_not_null()
        .cast(pl.Int8)
        .alias("has_user_rating_history"),
    ]


def user_vs_hotel_diff_features() -> List[pl.Expr]:
    """
    Calculate the difference between the current hotel features and the user's historical preferences.

    - **`price_diff_vs_user_history`**: Difference between the current hotel price and the user's historical price.
    - **`star_diff_vs_user_history`**: Difference between the current hotel star rating and the user's historical rating.

    These features are useful for assessing **how much the user’s preferences align** with the hotel’s attributes.
    """
    return [
        (
            pl.col("display_price").cast(pl.Float64)
            - pl.col("user_hist_avg_price").cast(pl.Float64)
        ).alias("price_diff_vs_user_history"),
        (
            pl.col("hotel_star_rating").cast(pl.Float64)
            - pl.col("user_hist_avg_stars").cast(pl.Float64)
        ).alias("star_diff_vs_user_history"),
    ]
