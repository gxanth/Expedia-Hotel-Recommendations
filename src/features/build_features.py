import polars as pl
import numpy as np


def set_target_column(train_df: pl.DataFrame) -> pl.DataFrame:
    return train_df.with_columns(
        pl.when(pl.col("booking_bool") == 1).then(5)
        .when(pl.col("click_bool") == 1).then(1)
        .otherwise(0)
        .alias("target")
    )

train_df = train_df.with_columns(
    cs.matches("_inv").replace(-1, None)
)

def extract_temporal_features(df: pl.DataFrame, datetime_col: str) -> pl.DataFrame:
    return df.with_columns(
        pl.col(datetime_col).dt.year().alias("year"),
        pl.col(datetime_col).dt.month().alias("month"),
        pl.col(datetime_col).dt.day().alias("day_of_month"),
        pl.col(datetime_col).dt.hour().alias("hour"),
        pl.col(datetime_col).dt.weekday().alias("day_of_week"),
        pl.col(datetime_col).dt.week().alias("week"),
        pl.col(datetime_col).dt.quarter().alias("quarter"),
        (pl.col(datetime_col).dt.weekday() >= 5).cast(pl.Int8).alias("is_weekend")
    )


def set_and_downcast_dtypes(df: pl.DataFrame) -> pl.DataFrame:
    """
    Sets the correct data types and automatically downcasts numerical columns 
    to the smallest possible data type without loss of information.
    """
    print("\nStarting dtype correction & downcast process...")
    initial_memory = df.estimated_size('mb')
    print(f"Initial memory usage: {initial_memory:.2f} MB")

    # Define correct dtypes from schema
    dtype_map = {
        "srch_id": pl.Int64,
        "date_time": pl.Datetime(time_unit="us"),
        "site_id": pl.Int64,
        "visitor_location_country_id": pl.Int64,
        "visitor_hist_starrating": pl.Float64,
        "visitor_hist_adr_usd": pl.Float64,
        "prop_country_id": pl.Int64,
        "prop_id": pl.Int64,
        "prop_starrating": pl.Int64,
        "prop_review_score": pl.Float64,
        "prop_brand_bool": pl.Int64,
        "prop_location_score1": pl.Float64,
        "prop_location_score2": pl.Float64,
        "prop_log_historical_price": pl.Float64,
        "position": pl.Int64,
        "price_usd": pl.Float64,
        "promotion_flag": pl.Int64,
        "srch_destination_id": pl.Int64,
        "srch_length_of_stay": pl.Int64,
        "srch_booking_window": pl.Int64,
        "srch_adults_count": pl.Int64,
        "srch_children_count": pl.Int64,
        "srch_room_count": pl.Int64,
        "srch_saturday_night_bool": pl.Int64,
        "srch_query_affinity_score": pl.Float64,
        "orig_destination_distance": pl.Float64,
        "random_bool": pl.Int64,
        "click_bool": pl.Int64,
        "gross_bookings_usd": pl.Float64,
        "booking_bool": pl.Int64
    }

    # Ensure correct types first
    df = df.with_columns([pl.col(col).cast(dtype_map[col]) for col in dtype_map if col in df.columns])

    # Now apply downcasting
    for col in df.columns:
        dtype = df[col].dtype

        # Downcast Integer Types
        if dtype == pl.Int64:
            min_val, max_val = df[col].min(), df[col].max()
            if min_val is not None and max_val is not None:
                if min_val >= np.iinfo(np.int8).min and max_val <= np.iinfo(np.int8).max:
                    df = df.with_columns(pl.col(col).cast(pl.Int8))
                    print(f"Downcasted {col}: Int64 -> Int8")
                elif min_val >= np.iinfo(np.int16).min and max_val <= np.iinfo(np.int16).max:
                    df = df.with_columns(pl.col(col).cast(pl.Int16))
                    print(f"Downcasted {col}: Int64 -> Int16")
                elif min_val >= np.iinfo(np.int32).min and max_val <= np.iinfo(np.int32).max:
                    df = df.with_columns(pl.col(col).cast(pl.Int32))
                    print(f"Downcasted {col}: Int64 -> Int32")

        # Downcast Floating Point Types
        elif dtype == pl.Float64:
            try:
                min_val, max_val = df[col].min(), df[col].max()

                # Handle NaNs and large values
                if min_val is None or max_val is None or np.isnan(min_val) or np.isnan(max_val):
                    print(f"Skipping downcast for {col} due to NaN values.")
                    continue

                if np.finfo(np.float32).min <= min_val <= np.finfo(np.float32).max and \
                   np.finfo(np.float32).min <= max_val <= np.finfo(np.float32).max:
                    df = df.with_columns(pl.col(col).cast(pl.Float32))
                    print(f"Downcasted {col}: Float64 -> Float32")

            except FloatingPointError:
                print(f"Skipping downcast for {col} due to overflow risk.")

    final_memory = df.estimated_size('mb')
    print(f"\nFinal memory usage: {final_memory:.2f} MB")
    print(f"Memory saved: {initial_memory - final_memory:.2f} MB ({((initial_memory - final_memory)/initial_memory)*100:.2f}%)")

    return df
click
# Multi-Selection Dropdown for Clicked vs Not Clicked
click_selection = alt.param(
    name="click_bool_selection",
    bind=alt.binding_select(
        options=["All", 0, 1],
        labels=["Both", "Not Clicked", "Clicked"],
        name="Click Status"
    ),
    value="All"
)

# Multi-Selection Dropdown for Booked vs Not Booked
book_selection = alt.param(
    name="book_bool_selection",
    bind=alt.binding_select(
        options=["All", 0, 1],
        labels=["Both", "Not Booked", "Booked"],
        name="Booking Status"
    ),
    value="All"
)

# Combined Filtering Logic
filter_condition = (
    ((click_selection == "All") | 
     ((click_selection == 0) & (alt.datum.click_bool == 0)) |
     ((click_selection == 1) & (alt.datum.click_bool == 1))) &
    ((book_selection == "All") | 
     ((book_selection == 0) & (alt.datum.booking_bool == 0)) |
     ((book_selection == 1) & (alt.datum.booking_bool == 1)))
)

# Define Y-Axis
y_axis = alt.Y(
    "proportion:Q",
    title="Overall Proportion",
    scale=alt.Scale(domain=[0, 1]),
    axis=alt.Axis(tickCount=10)
)

# Enable Zooming
zoom = alt.selection_interval(bind="scales")

# Dynamic Title Using `alt.expr`
title_expr = alt.expr(
    "click_bool_selection === 1 ? 'Property Star Rating for Clicked Users' : "
    "click_bool_selection === 0 ? 'Property Star Rating for Not Clicked Users' : "
    "'Property Star Rating by Booking and Click Status'"
)

chart = alt.Chart(agg_df).transform_calculate(
    click_label="datum.click_bool == 1 ? 'Clicked' : 'Not Clicked'",
    book_label="datum.booking_bool == 1 ? 'Booked' : 'Not Booked'"
).mark_bar(opacity=0.8).encode(
    x=alt.X("prop_starrating:O", title="Property Star Rating"),
    xOffset=alt.XOffset("book_label:N"),
    y=y_axis,
    color=alt.Color(
        "book_label:N",
        title="Booking Status",
        scale=alt.Scale(domain=["Not Booked", "Booked"], range=["#ff7f0e", "#1f77b4"]),
    ),
    tooltip=["prop_starrating", "proportion", "click_label:N", "book_label:N"]
).transform_filter(
    filter_condition
).add_params(
    click_selection,
    book_selection,
    zoom
).properties(
    width=700,
    height=400,
    title=alt.TitleParams(
        text=title_expr,  # Dynamically updates based on Clicked/Not Clicked
        fontSize=14,
        anchor="middle",
        fontWeight="bold"
    )
)

chart



train_df = train_df.with_columns(
    booking_date=(pl.col("date") + pl.duration(days=pl.col("srch_booking_window"))).cast(pl.Date),
    is_booking_weekend=(pl.col("booking_date").dt.weekday() >= 5).cast(pl.Int8),
    is_saturday_night=(pl.col("date").dt.weekday() == 5).cast(pl.Int8),
    booking_day_of_week=pl.col("booking_date").dt.weekday(),
    booking_day_of_month=pl.col("booking_date").dt.day(),
    booking_month=pl.col("booking_date").dt.month(),
)
