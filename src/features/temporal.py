# temporal.py

import polars as pl
import holidays # type: ignore


def create_search_temp_features(
    df: pl.DataFrame, 
    datetime_col: str = "date_time"
) -> pl.DataFrame:
    """
    Extracts search-time temporal features (month, day, hour, weekday, etc.) 
    from the specified datetime column.

    Args:
        df (pl.DataFrame): The input DataFrame.
        datetime_col (str): The name of the datetime column containing search timestamps.

    Returns:
        pl.DataFrame: A new DataFrame with added columns:
            - srch_month (int)
            - srch_day_of_month (int)
            - srch_hour (int)
            - srch_day_of_week (int; Monday=0, Sunday=6)
            - srch_weekend_bool (0 or 1)
            - srch_date (date type, truncated to day)
    """
    return df.with_columns(
        srch_month=pl.col(datetime_col).dt.month(),
        srch_day_of_month=pl.col(datetime_col).dt.day(),
        srch_hour=pl.col(datetime_col).dt.hour(),
        srch_day_of_week=pl.col(datetime_col).dt.weekday(),
        srch_weekend_bool=(pl.col(datetime_col).dt.weekday() >= 5).cast(pl.Int8),
        srch_date=pl.col(datetime_col).dt.date()
    )


def create_booking_temp_features(df: pl.DataFrame) -> pl.DataFrame:
    """
    Extracts booking-time features (month, day, weekday, etc.) 
    from a hypothetical booking date, calculated as srch_date + srch_booking_window.

    The DataFrame must already contain:
        - 'srch_date': a date or datetime column indicating the search date
        - 'srch_booking_window': an integer representing how many days until the booking
    
    Returns:
        pl.DataFrame: A new DataFrame with columns:
            - booking_date (Date)
            - booking_month (int)
            - booking_day_of_month (int)
            - booking_day_of_week (int)
            - booking_weekend_bool (0 or 1)
    """
    # Turn srch_window from int to polars Duration in days
    srch_window = pl.col("srch_booking_window").cast(pl.Duration)
    assert "srch_date" in df.columns, "Column 'srch_date' not found. Run create_search_temp_features first."


    return df.with_columns(
        booking_date=(pl.col("srch_date") + srch_window),
    ).with_columns(
        booking_month=pl.col("booking_date").dt.month(),
        booking_day_of_month=pl.col("booking_date").dt.day(),
        booking_day_of_week=pl.col("booking_date").dt.weekday(),
        booking_weekend_bool=(pl.col("booking_date").dt.weekday() >= 5).cast(pl.Int8),
        
    )


def add_holiday_feature(df: pl.DataFrame, date_col: str) -> pl.DataFrame:
    """
    Adds a binary column indicating whether a date is a US holiday.

    Args:
      - df (pl.DataFrame): The input DataFrame.
      -  date_col (str): The name of the date column to check for holidays.

    Returns:
      -  pl.DataFrame: The input DataFrame with an additional column 'is_holiday' (0 or 1).
    """

    us_holidays = holidays.US()
    return df.with_columns(
        is_us_holiday=pl.col(date_col).is_in(us_holidays).cast(pl.Int8)
    )

