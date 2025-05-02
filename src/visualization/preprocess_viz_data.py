import polars as pl
import numpy as np
from pathlib import Path
import logging

def setup_logger():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    return logging.getLogger(__name__)

def load_data(data_path: Path) -> pl.LazyFrame:
    logger.info("Loading dataset...")
    df = pl.scan_parquet(str(data_path))
    df = df.with_columns(
    pl.when(pl.col("target") == 0).then(pl.lit("Not Clicked"))
            .when(pl.col("target") == 1).then(pl.lit("Clicked"))
            .when(pl.col("target") == 5).then(pl.lit("Booked"))
            .otherwise(pl.lit("Unknown"))
            .alias("target_label")
)
    logger.info("Dataset loaded successfully.")
    return df

def compute_histogram(df: pl.LazyFrame, column: str, bins: int = 50) -> pl.DataFrame:
    min_max = df.select([
        pl.col(column).min().alias("min_val"),
        pl.col(column).max().alias("max_val")
    ]).collect()
    min_val, max_val = min_max.item(0, 0), min_max.item(0, 1)
    bin_edges = np.linspace(min_val, max_val, bins + 1).tolist()
    hist_data = (
        df.select([pl.col(column), pl.col("target_label")])
        .filter(pl.col(column).is_not_null())
        .with_columns(pl.col(column).cut(bin_edges, include_breaks=True).alias("bin_range"))
        .group_by(["bin_range", "target_label"])
        .agg(pl.len().alias("count"))
        .filter(pl.col("bin_range").is_not_null())
        .with_columns([
            pl.col("bin_range").struct.field("breakpoint").alias("bin_center"),
            pl.lit(column).alias("column"),
        ])
        .select(["column", "bin_center", "target_label", "count"])
        .with_columns((pl.col("count") / pl.sum("count")).alias("rel_freq"))
    )
    return hist_data.collect()

def main():
    global logger
    DATA_PATH = Path("data/processed/dummy_expedia.parquet")
    OUTPUT_DIR = Path("data/viz")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    BIN_SIZE = 50
    DISCRETE_THRESHOLD = 10

    df_lazy = load_data(DATA_PATH)

    schema = df_lazy.collect_schema()
    numeric_features = [col for col, dtype in schema.items() if dtype in [pl.Float64, pl.Int64]]
    logger.info(f"Identified numeric features: {numeric_features}")

    for feature in numeric_features:
        unique_vals = df_lazy.select(pl.col(feature).n_unique()).collect().item()
        dtype = schema.get(feature)

        feature_dir = OUTPUT_DIR / feature
        feature_dir.mkdir(parents=True, exist_ok=True)

        if dtype == pl.Int64 and unique_vals <= DISCRETE_THRESHOLD:
            logger.info(f"Saving barplot for discrete int feature: {feature}")
            bar_df = (
                df_lazy.group_by([feature, "target_label"])
                .agg(pl.len().alias("count_rows"))
                .collect()
            )
            bar_df.write_parquet(feature_dir / "barplot.parquet")
        else:
            logger.info(f"Saving binned histogram for feature: {feature}")
            hist_df = compute_histogram(df_lazy, feature, bins=BIN_SIZE)
            hist_df.write_parquet(feature_dir / "histogram.parquet")
        # ➕ NEW: Boxplot Sample Data
        logger.info(f"Saving boxplot sample for feature: {feature}")
        boxplot_sample_df = (
        df_lazy
        .select([pl.col(feature), pl.col("target_label")])
        .filter(pl.col(feature).is_not_null())
        .collect()  # Collect first to get a DataFrame
        .sample(n=100, with_replacement=False, seed=42)  # Then sample
    )
        boxplot_sample_df.write_parquet(feature_dir / "boxplot_sample.parquet")




    logger.info("Saving feature summary...")
    summary_stats = []

    for col in numeric_features:
        metrics = df_lazy.select([
            pl.lit(col).alias("feature")
,
            pl.col(col).mean().alias("mean"),
            pl.col(col).std().alias("std"),
            pl.col(col).min().alias("min"),
            pl.col(col).max().alias("max"),
            (pl.col(col).is_null().sum() / pl.len()).alias("null_pct"),
            ((pl.col(col) == 0).sum() / pl.len()).alias("zero_pct"),
            ((0.6745 * (pl.col(col) - pl.col(col).median()) / (pl.col(col).abs().median() + 1e-6)).abs() > 3.0).sum().alias("outlier_count"),
            pl.col(col).n_unique().alias("n_unique"),
            (((pl.col(col) - pl.col(col).mean()) ** 3).mean() / (pl.col(col).std() ** 3)).alias("skew"),
            (((pl.col(col) - pl.col(col).mean()) ** 4).mean() / (pl.col(col).std() ** 4)).alias("kurt")
        ]).collect().to_dicts()[0]

    summary_stats.append(metrics)

    summary_df = pl.DataFrame(summary_stats)

    

    summary_df.write_parquet(OUTPUT_DIR / "feature_summary.parquet")

    logger.info("Saving small random sample for exploration...")
    sample_df = df_lazy.collect().sample(n=1000, with_replacement=False)    
    sample_df.write_parquet(OUTPUT_DIR / "small_sample.parquet")

    logger.info("✅ Preprocessing complete! Files saved to /data/viz/")

if __name__ == "__main__":
    logger = setup_logger()
    main()