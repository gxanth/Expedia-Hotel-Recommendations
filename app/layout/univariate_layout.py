# 📁 app/layout/univariate_layout.py

from dash import dcc, html
import dash_bootstrap_components as dbc
from app.utils.data_loader import list_available_features


def create_univariate_layout() -> html.Div:
    """
    Build the layout for the Univariate Analysis tab.
    """
    feature_list = list_available_features()

    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3(
                                "📈 Explore One Feature", style={"margin-top": "15px"}
                            ),
                        ]
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Select Feature"),
                            dcc.Dropdown(
                                id="primary-feature-dropdown",
                                options=[
                                    {"label": f, "value": f} for f in feature_list
                                ],
                                value=feature_list[0] if feature_list else None,
                                placeholder="Select a feature",
                            ),
                            html.Br(),
                            html.Label("Target Grouping"),
                            dcc.RadioItems(
                                id="target-toggle",
                                options=[
                                    {"label": "Group by Target", "value": "on"},
                                    {"label": "Off", "value": "off"},
                                ],
                                value="off",
                                inline=True,
                            ),
                        ],
                        width=3,
                    ),  # Sidebar (3/12)
                    dbc.Col(
                        [
                            dcc.Graph(id="histogram-compare"),
                            dcc.Graph(id="boxplot-compare"),
                        ],
                        width=9,
                    ),  # Main Graphs (9/12)
                ],
                style={"margin-top": "20px"},
            ),
        ],
        fluid=True,
    )
