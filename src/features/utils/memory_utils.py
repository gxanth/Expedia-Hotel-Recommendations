import polars as pl
import re
from typing import List, Dict, Optional


def optimize_memory(lf: pl.LazyFrame, debug: bool = True) -> pl.LazyFrame:
    """
    Optimize memory usage in a Polars LazyFrame with improved error handling:
    - Attempt to convert string columns that look like dates to Date/Datetime
    - Ensure numeric columns are properly typed for arithmetic operations
    - Provide detailed debugging information when requested

    Parameters:
    -----------
    lf : pl.LazyFrame
        The LazyFrame to optimize
    debug : bool, default=False
        Whether to print detailed debugging information

    Returns:
    --------
    pl.LazyFrame
        An optimized LazyFrame with proper type conversions
    """
    print("🔧 Optimizing memory types (lazy)...")

    # Get schema information
    schema = lf.schema
    if debug:
        print(f"Original schema: {schema}")

    # Step 1: Handle date/time columns
    date_pattern = re.compile(r"(date|time)", re.IGNORECASE)
    date_cols = [
        col for col in schema if date_pattern.search(col) and schema[col] == pl.String
    ]

    if date_cols:
        if debug:
            print(f"Attempting to convert date columns: {date_cols}")

        date_exprs = []
        for col in date_cols:
            date_exprs.extend(
                [
                    pl.col(col).cast(pl.Date, strict=False).alias(f"{col}__try_date"),
                    pl.col(col)
                    .cast(pl.Datetime, strict=False)
                    .alias(f"{col}__try_datetime"),
                ]
            )

        lf = lf.with_columns(date_exprs)

        for col in date_cols:
            lf = lf.with_columns(
                pl.when(pl.col(f"{col}__try_date").is_not_null())
                .then(pl.col(f"{col}__try_date"))
                .when(pl.col(f"{col}__try_datetime").is_not_null())
                .then(pl.col(f"{col}__try_datetime"))
                .otherwise(pl.col(col))
                .alias(col)
            )

        # Drop temporary columns
        temp_cols = [f"{col}__try_date" for col in date_cols] + [
            f"{col}__try_datetime" for col in date_cols
        ]
        lf = lf.drop(temp_cols)

    # Step 2: Ensure numeric columns are properly typed
    # This is critical for arithmetic operations
    numeric_pattern = re.compile(
        r"(price|rating|score|diff|avg|mean|std|count|sum|min|max|rate)", re.IGNORECASE
    )
    potential_numeric_cols = [
        col
        for col in schema
        if numeric_pattern.search(col) and schema[col] == pl.String
    ]

    if potential_numeric_cols:
        if debug:
            print(
                f"Attempting to convert potential numeric columns: {potential_numeric_cols}"
            )

        numeric_exprs = []
        for col in potential_numeric_cols:
            # Try integer first, then float, keeping original if both fail
            numeric_exprs.append(
                pl.when(pl.col(col).cast(pl.Int64, strict=False).is_not_null())
                .then(pl.col(col).cast(pl.Int64, strict=False))
                .when(pl.col(col).cast(pl.Float64, strict=False).is_not_null())
                .then(pl.col(col).cast(pl.Float64, strict=False))
                .otherwise(pl.col(col))
                .alias(col)
            )

        lf = lf.with_columns(numeric_exprs)

    # Step 3: Downcast existing numeric columns
    numeric_cols = [
        col
        for col, dtype in schema.items()
        if isinstance(dtype, pl.DataType) and (dtype.is_integer() or dtype.is_float())
    ]

    if numeric_cols:
        if debug:
            print(f"Downcasting numeric columns: {numeric_cols}")
        lf = lf.with_columns([pl.col(col).shrink_dtype() for col in numeric_cols])

    # Step 4: Add a validation step to catch potential type issues
    if debug:
        # Create a small sample to check for potential issues
        try:
            print("Validating with a small sample...")
            sample_schema = lf.limit(5).collect_schema()
            print(f"Optimized schema: {sample_schema}")

            # Check for columns that might cause arithmetic issues
            arithmetic_cols = [
                col for col in sample_schema if numeric_pattern.search(col)
            ]
            for col in arithmetic_cols:
                if sample_schema[col] == pl.String:
                    print(
                        f"⚠️ Warning: Column '{col}' is still a string but might be used in arithmetic"
                    )
        except Exception as e:
            print(f"❌ Validation error: {e}")
            print(
                "Consider adding explicit casts for columns used in arithmetic operations"
            )

    print("✅ Type optimization complete.")
    return lf
