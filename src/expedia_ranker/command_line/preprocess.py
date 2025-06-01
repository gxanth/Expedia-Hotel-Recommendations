from pathlib import Path

import polars as pl
import typer

from expedia_ranker.data_pipeline.preprocessing.data_standardization import (
    standardize_single_file,
)
from expedia_ranker.io.path_helpers import (
    get_feature_rename_map_path,
    get_feature_schema_path,
)
from expedia_ranker.io.paths import DATA_INTERIM_DIR, DATA_RAW_DIR
from expedia_ranker.io.yaml_io import load_yaml
from expedia_ranker.utilities.logging import logger

app = typer.Typer()


@app.command("preprocess")
def preprocess_command(
    input_dir: Path = typer.Option(
        DATA_RAW_DIR,
        prompt=True,
        help="Input directory for raw .csv files",
    ),
    output_dir: Path = typer.Option(
        DATA_INTERIM_DIR,
        prompt=True,
        help="Output directory for processed .parquet files",
    ),
):
    """
    Standardize and convert raw Expedia .csv files (Step 1 of the pipeline).:
    - Renames columns
    - Casts data types
    - Adds missing columns
    - Saves as .parquet
    """
    logger.info(f"Starting preprocessing: {input_dir.name} to {output_dir.name}")

    rename_map = load_yaml(get_feature_rename_map_path())
    schema_yaml = load_yaml(get_feature_schema_path())
    schema = {k: getattr(pl, v) for k, v in schema_yaml.items()}

    output_dir.mkdir(parents=True, exist_ok=True)

    for file in input_dir.glob("*.csv"):
        output_dir = output_dir / f"{file}.parquet"
        standardize_single_file(file, output_dir, rename_map, schema)

    logger.success("All files processed.")
