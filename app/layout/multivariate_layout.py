from dash import dcc, html
import dash_bootstrap_components as dbc
from app.utils.data_loader import list_available_features


def create_multivariate_layout() -> html.Div:
    feature_list = list_available_features()

    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3(
                                "🔍 Compare Multiple Features",
                                style={"margin-top": "15px"},
                            ),
                        ]
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Select Features to Compare"),
                            dcc.Dropdown(
                                id="multi-feature-dropdown",
                                options=[
                                    {"label": f, "value": f} for f in feature_list
                                ],
                                multi=True,
                                placeholder="Select one or more features",
                            ),
                            html.Br(),
                            html.Label("Group by Target?"),
                            dcc.RadioItems(
                                id="multi-target-toggle",
                                options=[
                                    {"label": "Group by Target", "value": "on"},
                                    {"label": "No Grouping", "value": "off"},
                                ],
                                value="off",
                                inline=True,
                            ),
                        ],
                        width=3,
                    ),
                    dbc.Col(
                        [
                            dcc.Graph(id="multi-feature-graph"),
                        ],
                        width=9,
                    ),
                ],
                style={"margin-top": "20px"},
            ),
        ],
        fluid=True,
    )
