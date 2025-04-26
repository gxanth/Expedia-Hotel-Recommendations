from dash import dcc, html, dash_table
from app.utils.config_loader import ConfigLoader

config_loader = ConfigLoader()
# ? centalize>


def create_overview_layout(summary_df):
    """
    Build the layout for the Overview tab.
    """
    return html.Div(
        [
            html.H3("📋 Feature Summary Table"),
            dcc.Loading(
                children=[
                    dash_table.DataTable(
                        id="summary-table",
                        data=summary_df.to_dict("records"),
                        columns=[
                            {"name": col, "id": col} for col in summary_df.columns
                        ],
                        page_size=10,
                        sort_action="native",
                        filter_action="native",
                        style_table={"overflowX": "auto"},
                        style_cell={"textAlign": "center"},
                        style_header={"fontWeight": "bold"},
                        style_data_conditional=config_loader.load_table_styles(),
                    )
                ],
                type="default",
            ),
        ]
    )
