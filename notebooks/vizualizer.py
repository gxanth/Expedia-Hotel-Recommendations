import re
import altair as alt
import polars as pl
import numpy as np
from typing import List, Optional


class Visualizer:
    def __init__(
        self,
        lazy_df: pl.LazyFrame,
        default_width: int = 800,
        default_height: int = 400,
        color_scheme: dict = None,
        theme: dict = None,
        debug: bool = False
    ):
        """
        🚀 Initialize the Visualizer with a Polars LazyFrame and optional settings.
        """
        self.lazy_df = lazy_df
        self.default_width = default_width
        self.default_height = default_height
        self.debug = debug

        self.color_scheme = color_scheme or {
            "booking": "#1f77b4",
            "not_booking": "#d62728",
            "click": "#1f77b4",
            "not_click": "#ff7f0e"
        }

        self.theme = theme or {
            "title_fontsize": 14,
            "title_anchor": "middle",
            "title_fontweight": "bold",
            "axis_label_angle": 45
        }

    def _compute_histogram(
        self,
        column: str,
        bins: Optional[int] = None,
        normalize: bool = True
    ) -> pl.DataFrame:
        """📊 Compute histogram for a numeric column in a LazyFrame."""
        min_max = self.lazy_df.select([
            pl.col(column).min().alias("min_val"),
            pl.col(column).max().alias("max_val")
        ]).collect()

        min_val, max_val = min_max.item(0,0), min_max.item(0,1)

        if bins is None:
            non_null_count = self.lazy_df.select(pl.col(column).is_not_null().sum()).collect().item()
            bins = max(1, int(1 + 3.322 * np.log10(non_null_count))) if non_null_count > 1 else 1
        
        bin_edges = np.linspace(min_val, max_val, bins + 1).tolist()
        bin_width = (max_val - min_val) / bins if bins > 0 else 1e-9

        hist_data = (
            self.lazy_df
            .select(pl.col(column))
            .filter(pl.col(column).is_not_null())
            .with_columns(
                pl.col(column).cut(bin_edges, include_breaks=True).alias("bin_range")
            )
            .group_by("bin_range")
            .agg(pl.len().alias("count"))
            .filter(pl.col("bin_range").is_not_null())
            .with_columns([
                (pl.col("bin_range").struct.field("breakpoint") - bin_width / 2).alias("bin_center"),
                pl.lit(column).alias("column"),
            ])
            .select(["column", "bin_center", "count"])
        )

        if normalize:
            hist_data = hist_data.with_columns(
                (pl.col("count") / pl.col("count").sum()).alias("rel_freq")
            )

        return hist_data.collect()

    def plot_histogram_with_checkboxes(
        self, columns: List[str], bins: int = 30, normalize: bool = True, logy: bool = False, logx: bool = False
    ) -> alt.Chart:
        """📊 Allows selection of multiple columns to compare in a histogram using checkboxes."""
        frames = [
            self._compute_histogram(col, bins=None, normalize=True)
            for col in columns
        ]
        hist_data = pl.concat(frames, how="vertical")

        column_checkboxes = {
            col: alt.param(name=f"checkbox_{col}", bind=alt.binding_checkbox(), value=True)
            for col in columns
        }

        combined_filter = " || ".join([f"checkbox_{col} && datum.column == '{col}'" for col in columns])

        y_scale = alt.Scale(type="symlog") if logy else alt.Undefined
        x_scale = alt.Scale(type="symlog") if logx else alt.Undefined
        title="Relative Frequency" if normalize else "Count"

        return (
            alt.Chart(hist_data)
            .mark_bar(opacity=0.6)
            .encode(
                x=alt.X("bin_center:Q", title="Value", scale=x_scale),
                y=alt.Y("rel_freq:Q" if normalize else "count:Q", title=title, scale=y_scale),
                color=alt.Color("column:N", title="Column"),
                tooltip=["column:N", "bin_center:Q", "rel_freq:Q" if normalize else "count:Q"]
            )
            .transform_filter(combined_filter)
            .add_params(*column_checkboxes.values())
            .properties(width=self.default_width, height=self.default_height)
            .interactive()
        )

    def plot_conditional_barchart(self, var_x: str) -> alt.Chart:
        """📊 Categorical Distribution with Click & Booking Filters."""
        df_agg = (
            self.lazy_df.group_by([var_x, "click_bool", "booking_bool"])
            .agg(pl.count().alias("count_rows"))
        ).collect()

        n_rows = df_agg["count_rows"].sum()
        df_agg = df_agg.with_columns(
            (pl.col("count_rows") / n_rows * 100).alias("proportion")
        ).sort("proportion", descending=True)

        return (
            alt.Chart(df_agg)
            .mark_bar(opacity=0.8)
            .encode(
                x=alt.X(f"{var_x}:O", title=var_x.replace("_", " ").title()),  
                xOffset=alt.XOffset("booking_bool:N"),
                y=alt.Y("proportion:Q", title="Percentage"),  
                color=alt.Color("booking_bool:N", title="Booking Status"),
                tooltip=["category", "sum(proportion):Q", "booking_bool:N"]

            )
            .properties(width=self.default_width, height=self.default_height)
        )

# Example Usage
if __name__ == "__main__":
    lazy_df = pl.DataFrame({
        "price_usd": np.random.normal(100, 20, 1000),
        "srch_booking_window": np.random.randint(1, 30, 1000),
    }).lazy()
    viz = Visualizer(lazy_df)
    hist_chart = viz.plot_histogram_with_checkboxes(["price_usd", "srch_booking_window"], bins=20, normalize=True)
    hist_chart.display()
