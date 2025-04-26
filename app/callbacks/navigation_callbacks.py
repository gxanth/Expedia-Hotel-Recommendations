from dash import Input, Output
from app.layout.overview_layout import create_overview_layout
from app.layout.univariate_layout import create_univariate_layout
from app.layout.multivariate_layout import create_multivariate_layout
from dash import dcc, html


def register_navigation_callbacks(app, summary_df):
    """
    Handle page routing based on URL.
    """

    @app.callback(Output("page-content", "children"), Input("url", "pathname"))
    def display_page(pathname):
        if pathname == "/":
            return create_overview_layout(summary_df)
        elif pathname == "/univariate":
            return create_univariate_layout()
        elif pathname == "/multivariate":
            return create_multivariate_layout()
        else:
            return html.H1("404: Page not found", className="text-danger")
