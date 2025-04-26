# -*- coding: utf-8 -*-
from dash import dcc, html
import dash_bootstrap_components as dbc

from app.layout.overview_layout import create_overview_layout
from app.layout.univariate_layout import create_univariate_layout
from app.layout.multivariate_layout import create_multivariate_layout


def create_sidebar():
    """
    Creates the sidebar navigation with a title.
    """
    return html.Div(
        [
            html.H2(
                "📈 Expedia Explorer",
                className="display-6",
                style={"textAlign": "center", "margin-bottom": "20px"},
            ),
            dbc.Nav(
                [
                    dbc.NavLink("📊 Overview", href="/", active="exact"),
                    dbc.NavLink(
                        "📈 Univariate Analysis", href="/univariate", active="exact"
                    ),
                    dbc.NavLink(
                        "🔍 Multivariate Analysis", href="/multivariate", active="exact"
                    ),
                ],
                vertical=True,
                pills=True,
            ),
        ],
        style={"padding": "20px", "backgroundColor": "#f8f9fa", "height": "100vh"},
    )


def create_layout(summary_df):
    """
    Create the overall app layout with sidebar navigation.
    """
    sidebar = create_sidebar()

    content = html.Div(id="page-content", style={"padding": "20px"})

    return dbc.Container(
        [
            dcc.Location(id="url"),
            dbc.Row(
                [
                    dbc.Col(sidebar, width=2),  # Sidebar: 2/12 of screen
                    dbc.Col(content, width=10),  # Main content: 10/12
                ]
            ),
        ],
        fluid=True,
    )
