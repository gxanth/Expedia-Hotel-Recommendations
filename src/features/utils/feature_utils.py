import polars as pl
from typing import List


def standardize_expr(col: str) -> pl.Expr:
    return ((pl.col(col) - pl.col(col).mean()) / pl.col(col).std()).alias(
        f"{col}_zscore"
    )


def normalize_expr(col: str) -> pl.Expr:
    return (
        (pl.col(col) - pl.col(col).min()) / (pl.col(col).max() - pl.col(col).min())
    ).alias(f"{col}_norm")


def mad_filter(
    lf: pl.LazyFrame,
    input_column: str,
    z_thresh: float = 3.5,
    output_suffix: str = "_mad_filtered",
) -> pl.LazyFrame:
    output_suffix = output_suffix or input_column

    # Compute median and MAD (once) in eager mode
    median = lf.select(pl.col(input_column).median().alias("median")).collect()[
        "median"
    ][
        0
    ]  # <- can we collect on a part of the lazy frame?

    mad = lf.select(
        (pl.col(input_column) - median).abs().median().alias("mad")
    ).collect()["mad"][0]
    threshold = z_thresh * mad

    return lf.with_columns(
        pl.when((pl.col(input_column) - median).abs() > threshold)
        .then(None)
        .otherwise(pl.col(input_column))
        .name.suffix(output_suffix)
    )


def groupwise_mean_imputation(
    lf: pl.LazyFrame,
    groupby_cols: List[str],
    feature_to_impute: str,
    output_suffix: str = "_mean_imputed",
) -> pl.LazyFrame:
    """
    Perform group-wise mean imputation for a specified column in a LazyFrame.

    Parameters:
    ----------
    lf : pl.LazyFrame
        The input LazyFrame.
    groupby_cols : List[str]
        List of columns to group by.
    feature_to_impute : str
        The column to be imputed.
    output_suffix : str
        Suffix for the new imputed column.

    Returns:
    -------
    pl.LazyFrame
        LazyFrame with the imputed column added.
    """
    return lf.with_columns(
        pl.col(feature_to_impute)
        .fill_null(pl.col(feature_to_impute).mean().over(groupby_cols))
        .name.suffix(output_suffix)
    )


# Example usage with renamed columns
# For instance, if you want to standardize or normalize "display_price":
# standardized_expr = standardize_expr("display_price")
# normalized_expr = normalize_expr("display_price")
