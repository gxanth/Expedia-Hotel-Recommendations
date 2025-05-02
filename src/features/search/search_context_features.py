import polars as pl
from typing import List


def search_context_features() -> List[pl.Expr]:
    """
    Create booking-related statistical features using when-then-otherwise pattern.

    Returns:
        List of Polars expressions for booking features
    """
    return [
        # Total number of guests
        (pl.col("num_adults") + pl.col("num_children")).alias("total_guests"),
        # Stay duration bucket using when-then-otherwise
        pl.when(pl.col("stay_duration") < 2)
        .then(pl.lit("short"))
        .when(pl.col("stay_duration") < 5)
        .then(pl.lit("medium"))
        .otherwise(pl.lit("long"))
        .alias("stay_duration_bucket"),
        # Booking window bucket using when-then-otherwise
        pl.when(pl.col("days_until_checkin") < 3)
        .then(pl.lit("last_minute"))
        .when(pl.col("days_until_checkin") < 14)
        .then(pl.lit("short_term"))
        .otherwise(pl.lit("long_term"))
        .alias("days_until_checkin_bucket"),
        # Room-to-guest ratio (with safe division)
        (
            pl.col("num_rooms")
            / (pl.col("num_adults") + pl.col("num_children")).clip(1, None)
        ).alias("room_to_guest_ratio"),
    ]
