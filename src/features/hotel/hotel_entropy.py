import polars as pl
from typing import List, Tuple


def bin_price_tier_expr(
    price_col: str = "display_price",
    thresholds: Tuple[int, int] = (100, 300),
    labels: Tuple[str, str, str] = ("budget", "mid", "luxury"),
) -> pl.Expr:
    """
    Create a Polars expression to bin prices into price tiers (e.g., budget, mid, luxury).
    """
    low, high = thresholds
    low_label, mid_label, high_label = labels

    return (
        pl.when(pl.col(price_col) < low)
        .then(pl.lit(low_label))
        .when(pl.col(price_col) < high)
        .then(pl.lit(mid_label))
        .otherwise(pl.lit(high_label))
        .alias("price_tier")
    )


def hotel_click_entropy_price_tier(
    lf: pl.LazyFrame,
    thresholds: Tuple[int, int] = (100, 300),
    labels: Tuple[str, str, str] = ("budget", "mid", "luxury"),
    price_col: str = "display_price",
    click_col: str = "was_clicked",
    hotel_id_col: str = "hotel_id",
) -> pl.LazyFrame:
    """
    Add click entropy across price tiers to a LazyFrame.
    - Bins prices into tiers
    - Filters to clicked rows
    - Computes entropy per hotel
    """
    # 1. Add price tier column
    lf = lf.with_columns([bin_price_tier_expr(price_col, thresholds, labels)])

    # 2. Filter only clicked rows
    clicked = lf.filter(pl.col(click_col) == 1)

    # 3. Count clicks per hotel and price tier
    counts = clicked.group_by([hotel_id_col, "price_tier"]).agg(
        pl.count().alias("tier_click_count")
    )

    # 4. Compute total clicks per hotel
    totals = counts.group_by(hotel_id_col).agg(
        pl.sum("tier_click_count").alias("total_clicks")
    )

    # 5. Join and compute entropy components
    entropy_components = (
        counts.join(totals, on=hotel_id_col)
        .with_columns(
            [
                (pl.col("tier_click_count") / pl.col("total_clicks")).alias("p"),
                (pl.col("tier_click_count") / pl.col("total_clicks"))
                .log(base=2)
                .alias("log_p"),
            ]
        )
        .with_columns([(-pl.col("p") * pl.col("log_p")).alias("entropy_component")])
        .group_by(hotel_id_col)
        .agg(pl.sum("entropy_component").alias("click_entropy_price_tier"))
    )

    # 6. Join entropy values back to original LazyFrame
    return lf.join(entropy_components, on=hotel_id_col, how="left")
