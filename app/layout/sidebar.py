# app/layout/sidebar.py
import dash_bootstrap_components as dbc
from dash import html

sidebar = dbc.Col(
    [
        html.H2("Feature Explorer", className="display-6"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Overview", href="/overview", active="exact"),
                dbc.NavLink("Univariate Analysis", href="/univariate", active="exact"),
                dbc.NavLink(
                    "Multivariate Analysis", href="/multivariate", active="exact"
                ),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    width=2,
    style={"background-color": "#2c3e50", "padding": "20px", "height": "100vh"},
)
