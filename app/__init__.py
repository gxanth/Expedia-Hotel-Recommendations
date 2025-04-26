from dash import Dash
import dash_bootstrap_components as dbc

# Initialize app here
app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.LUX],
)
