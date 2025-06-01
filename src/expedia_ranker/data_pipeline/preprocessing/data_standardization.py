import time
from pathlib import Path

import polars as pl

from expedia_ranker.utilities.logging import logger


def _add_missing_columns(
    lf: pl.LazyFrame, schema: dict[str, pl.DataType], renamed_cols: list[str]
) -> pl.LazyFrame:
    """
    Add missing columns to the LazyFrame with typed placeholders based on the schema.
    """
    missing_cols = set(schema.keys()) - set(renamed_cols)
    if missing_cols:
        logger.info(f" Adding missing columns: {sorted(missing_cols)}")
        typed_nulls = []
        for col in sorted(missing_cols):
            dtype = schema[col]
            if dtype == pl.Categorical:
                default_val = ""
            elif dtype.__class__ in (
                pl.Int8,
                pl.Int16,
                pl.Int32,
                pl.UInt8,
                pl.UInt16,
                pl.UInt32,
            ):
                default_val = 0
            elif dtype.__class__ in (pl.Float32, pl.Float64):
                default_val = 0.0
            elif dtype == pl.Boolean:
                default_val = False
            elif dtype == pl.Utf8:
                default_val = ""
            else:
                default_val = None

            if dtype == pl.Categorical:
                typed_nulls.append(
                    pl.lit(default_val, dtype=pl.Utf8).cast(pl.Categorical).alias(col)
                )
            else:
                typed_nulls.append(pl.lit(default_val, dtype=dtype).alias(col))

        lf = lf.with_columns(typed_nulls)
    return lf


def standardize_single_file(
    input_path: Path,
    output_path: Path,
    rename_map: dict[str, str],
    schema: dict[str, pl.DataType],
) -> None:
    """
    Standardize a single raw data file:
    - Rename columns
    - Cast types
    - Add typed placeholders for missing columns
    - Save to Parquet
    - Log rows, columns, memory, and time
    """
    logger.info(f" Processing file: {input_path.resolve().name}")
    start_time = time.time()

    try:
        lf = pl.scan_csv(input_path, null_values=["NULL"], try_parse_dates=True)

        # --- Renaming ---
        lf = lf.rename(rename_map, strict=False)

        # --- Casting ---
        renamed_cols = lf.collect_schema().keys()
        for col, dtype in schema.items():
            if col in renamed_cols:
                if dtype == pl.Categorical:
                    lf = lf.with_columns(pl.col(col).cast(pl.Utf8).cast(pl.Categorical))
                else:
                    lf = lf.with_columns(pl.col(col).cast(dtype))

        # --- Missing Columns ---S
        lf = _add_missing_columns(lf, schema, renamed_cols)

        # --- Collect and Save ---
        df = lf.collect(engine="gpu")
        df.write_parquet(output_path)
        # Print schema for debugging

        # --- Summary Output ---
        elapsed = time.time() - start_time
        row_count, col_count = df.shape
        mem_usage_mb = df.estimated_size("mb")

        logger.success(
            f" Saved {row_count:,} rows, {col_count} columns "
            f"({mem_usage_mb:.2f} MB) to {output_path.name} "
            f"in {elapsed:.2f} sec"
        )

    except Exception as e:
        logger.error(f" Failed on {input_path.name}: {e}")
