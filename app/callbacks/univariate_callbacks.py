from dash import Input, Output
from app.utils.data_loader import load_feature_histogram, load_feature_boxplot
from app.utils.figure_factory import (
    make_target_histograms,
    make_standard_histogram,
    make_boxplot,
)


def register_univariate_callbacks(app):
    """
    Register callbacks for the Univariate Analysis tab.
    """

    @app.callback(
        Output("histogram-compare", "figure"),
        Output("boxplot-compare", "figure"),
        Input("primary-feature-dropdown", "value"),
        Input("target-toggle", "value"),
    )
    def update_univariate_graphs(feature: str, group_mode: str):
        if not feature:
            return {}, {}

        # Load feature data
        df_hist = load_feature_histogram(feature)
        df_box = load_feature_boxplot(feature)

        # Build histogram
        if group_mode == "on" and "target_label" in df_hist.columns:
            fig_hist = make_target_histograms(df_hist)
        else:
            fig_hist = make_standard_histogram(df_hist)

        # Build boxplot
        fig_box = make_boxplot(df_box, feature, group_mode)

        return fig_hist, fig_box
