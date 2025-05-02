import polars as pl
from typing import List
import holidays
from datetime import datetime

# Pre-load holidays for relevant years (adjust range as needed)
START_YEAR = 2012
END_YEAR = 2015
us_holidays = holidays.country_holidays("US", years=range(START_YEAR, END_YEAR + 1))
holiday_dates = list(us_holidays.keys())


def _is_holiday_expr(date_col: str, country: str = "US") -> pl.Expr:
    """
    Generate a feature indicating whether a given date is a holiday.
    """
    return (
        pl.col(date_col)
        .cast(pl.Date)
        .is_in(holiday_dates)
        .cast(pl.Int8)
        .alias(f"{date_col}_is_holiday")
    )


def search_time_features() -> List[pl.Expr]:
    """
    Features from search timestamp:
    - Basic date parts
    - Time of day bucket
    - Weekend and holiday indicator
    - Search date (used in rolling ops)
    """
    return [
        pl.col("search_timestamp").dt.hour().alias("search_hour"),
        pl.col("search_timestamp").dt.weekday().alias("search_day_of_week"),
        pl.col("search_timestamp").dt.week().alias("search_week"),
        pl.col("search_timestamp").dt.month().alias("search_month"),
        pl.col("search_timestamp").dt.year().alias("search_year"),
        pl.col("search_timestamp").dt.date().alias("search_date"),
        (pl.col("search_timestamp").dt.weekday().is_in([5, 6]))
        .cast(pl.Int8)
        .alias("is_weekend_search"),
        _is_holiday_expr("search_timestamp", country="US"),
        (
            pl.when(pl.col("search_timestamp").dt.hour().is_between(0, 5))
            .then(pl.lit("night"))
            .when(pl.col("search_timestamp").dt.hour().is_between(6, 11))
            .then(pl.lit("morning"))
            .when(pl.col("search_timestamp").dt.hour().is_between(12, 17))
            .then(pl.lit("afternoon"))
            .otherwise(pl.lit("evening"))
            .alias("search_time_of_day")
        ),
    ]


def booking_time_features() -> List[pl.Expr]:
    expected_checkin_expr = (
        pl.col("search_timestamp") + pl.duration(days=pl.col("days_until_checkin"))
    ).dt.date()

    return [
        expected_checkin_expr.alias("expected_checkin_date"),
        expected_checkin_expr.dt.weekday().alias("checkin_day_of_week"),
        expected_checkin_expr.dt.day().alias("checkin_day_of_month"),
        expected_checkin_expr.dt.month().alias("checkin_month"),
        expected_checkin_expr.dt.weekday()
        .is_in([5, 6])
        .cast(pl.Int8)
        .alias("checkin_is_weekend"),
        expected_checkin_expr.is_in(holiday_dates)
        .cast(pl.Int8)
        .alias("expected_checkin_date_is_holiday"),
    ]


__all__ = [
    "search_time_features",
    "booking_time_features",
]
