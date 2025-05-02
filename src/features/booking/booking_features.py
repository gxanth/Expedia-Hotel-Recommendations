import polars as pl
from typing import List


def booking_stats_features() -> List[pl.Expr]:
    """
    Generate booking-related statistics features for hotels:
    - **`click_prob`**: Probability of clicking on a hotel (clicks per hotel divided by total searches).
    - **`booking_prob`**: Probability of booking a hotel (bookings per hotel divided by total searches).
    - **`hotel_avg_position`**: The average position of a hotel in search results.
    - **`hotel_position_std`**: The standard deviation of the hotel's position in search results.

    These features help the model understand how well a hotel performs in terms of user engagement (clicks and bookings)
    and how its position in search results affects user behavior.
    """
    return [
        # Click probability (clicks per hotel divided by total searches)
        (
            pl.col("was_clicked").sum().over("hotel_id") / pl.count().over("hotel_id")
        ).alias("click_prob"),
        # Booking probability (bookings per hotel divided by total searches)
        (
            pl.col("was_booked").sum().over("hotel_id") / pl.count().over("hotel_id")
        ).alias("booking_prob"),
        # Average position of the hotel
        pl.col("display_position").mean().over("hotel_id").alias("hotel_avg_position"),
        # Standard deviation of hotel position
        pl.col("display_position").std().over("hotel_id").alias("hotel_position_std"),
    ]


def query_level_flags() -> List[pl.Expr]:
    """
    Generate flags indicating query-level characteristics:
    - **`query_contains_missing_position`**: Flag indicating if any search query contains a missing hotel position.

    This feature is useful to track whether there are missing ranking positions for any hotel in a search query.
    """
    return [
        # Flag for missing hotel position in the query
        pl.col("display_position")
        .is_null()
        .any()
        .over("search_id")
        .cast(pl.Int8)
        .alias("query_contains_missing_position")
    ]
