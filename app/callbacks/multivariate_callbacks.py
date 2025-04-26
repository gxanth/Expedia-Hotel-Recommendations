from dash import Input, Output
from app.utils.data_loader import load_feature_histogram
from app.utils.figure_factory import make_multifeature_histogram


def register_multivariate_callbacks(app):
    """
    Register callbacks for the Multivariate Analysis tab.
    """

    @app.callback(
        Output("multi-feature-graph", "figure"),
        Input("multi-feature-dropdown", "value"),
        Input("multi-target-toggle", "value"),
    )
    def update_multifeature_graph(selected_features, group_mode):
        if not selected_features:
            return {}

        fig = make_multifeature_histogram(selected_features, group_mode)
        return fig
