# dtypes.py
import polars as pl
import numpy as np

def downcast_dtypes(df: pl.DataFrame) -> pl.DataFrame:
    """
    Attempts to downcast integer and float columns where possible to reduce memory usage.
    """
    print("Downcasting data types...")
    initial_memory = df.estimated_size("mb")

    for col in df.columns:
        dtype = df[col].dtype

        if dtype == pl.Int64:
            min_val = df[col].min()
            max_val = df[col].max()
            if min_val is not None and max_val is not None:
                if np.iinfo(np.int8).min <= min_val <= max_val <= np.iinfo(np.int8).max:
                    df = df.with_columns(pl.col(col).cast(pl.Int8))
                    print(f"Column '{col}' casted to Int8")
                elif np.iinfo(np.int16).min <= min_val <= max_val <= np.iinfo(np.int16).max:
                    df = df.with_columns(pl.col(col).cast(pl.Int16))
                    print(f"Column '{col}' casted to Int16")
                elif np.iinfo(np.int32).min <= min_val <= max_val <= np.iinfo(np.int32).max:
                    df = df.with_columns(pl.col(col).cast(pl.Int32))
                    print(f"Column '{col}' casted to Int32")

        elif dtype == pl.Float64:
            min_val = df[col].min()
            max_val = df[col].max()
            if min_val is not None and max_val is not None:
                if np.finfo(np.float32).min <= min_val <= max_val <= np.finfo(np.float32).max:
                    df = df.with_columns(pl.col(col).cast(pl.Float32))
                    print(f"Column '{col}' casted to Float32")

    final_memory = df.estimated_size("mb")
    saved = initial_memory - final_memory
    print(f"Downcasted data types.")
    print(f"Memory before: {initial_memory:.2f} MB; after: {final_memory:.2f} MB; saved: {saved:.2f} MB")
    return df


__all__ = ["downcast_dtypes"]