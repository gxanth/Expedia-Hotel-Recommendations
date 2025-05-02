from dash import Dash, dcc, html, dash_table, Input, Output
import plotly.express as px
import polars as pl
import pandas as pd
import numpy as np
from collections import defaultdict

# -----------------------------
# 1. Generate dummy data
# -----------------------------
np.random.seed(42)
dummy_df = pl.DataFrame({
    "price_usd": np.random.normal(120, 25, 1000),
    "log_price_usd": np.log1p(np.random.normal(120, 25, 1000)),
    "price_usd_norm": np.random.beta(2, 5, 1000),
    "visitor_hist_adr_usd": np.random.normal(100, 20, 1000),
    "log_visitor_hist_adr_usd": np.log1p(np.random.normal(100, 20, 1000)),
    "prop_review_score": np.clip(np.random.normal(4.2, 0.6, 1000), 1.0, 5.0)
}).lazy()

features = [name for name, dtype in dummy_df.collect_schema().items() if dtype in [pl.Float64, pl.Int64]]
summary_df = pl.concat([
    dummy_df.select([
        pl.lit(col).alias("feature"),
        pl.col(col).mean().alias("mean"),
        pl.col(col).std().alias("std"),
        pl.col(col).min().alias("min"),
        pl.col(col).max().alias("max"),
        (pl.col(col).is_null().sum() / pl.len()).alias("null_pct"),
        ((pl.col(col) == 0).sum() / pl.len()).alias("zero_pct"),
        ((0.6745 * (pl.col(col) - pl.col(col).median()) / (pl.col(col).abs().median() + 1e-6)).abs() > 3.0).sum().alias("outlier_count"),
        pl.col(col).n_unique().alias("n_unique"),
        (((pl.col(col) - pl.col(col).mean()) ** 3).mean() / (pl.col(col).std() ** 3)).alias("skew"),
        (((pl.col(col) - pl.col(col).mean()) ** 4).mean() / (pl.col(col).std() ** 4)).alias("kurt")
    ]) for col in features
]).collect()
summary_data = summary_df.to_dicts()

df = dummy_df.collect().to_pandas()
df["target"] = np.random.choice([0, 1, 5], size=len(df), p=[0.7, 0.2, 0.1])

# -----------------------------
# 2. Feature variant mapping
# -----------------------------
def find_feature_variants(columns):
    variant_map = defaultdict(list)
    for col in columns:
        base = col
        if col.startswith("log_"):
            base = col.replace("log_", "")
        elif col.endswith("_mad_filtered"):
            base = col.replace("_mad_filtered", "")
        elif col.endswith("_norm"):
            base = col.replace("_norm", "")
        variant_map[base].append(col)
    return dict(variant_map)

feature_variant_map = find_feature_variants(df.columns)

# -----------------------------
# 3. App Layout
# -----------------------------
app = Dash(__name__)

app.layout = html.Div([
    html.H1("🔍 Expedia Feature Explorer"),

    dcc.Tabs([
        dcc.Tab(label="📊 Overview", children=[
            html.H3("Feature Summary Table"),
            dash_table.DataTable(
                columns=[{"name": col, "id": col} for col in summary_df.columns],
                data=[
                    {key: round(value, 3) if isinstance(value, (int, float)) else value for key, value in row.items()}
                    for row in summary_data
                ],
                page_size=10,
                style_table={"overflowX": "auto"}
            )
        ]),

        dcc.Tab(label="📈 Feature Explorer", children=[
            html.Label("Analysis Mode"),
            dcc.RadioItems(
                id="exploration-mode-toggle",
                options=[
                    {"label": "Explore single variant", "value": "explore"},
                    {"label": "Compare two variants", "value": "compare"}
                ],
                value="explore",
                inline=True
            ),

            html.Label("Base Feature"),
            dcc.Dropdown(
                id="base-feature-dropdown",
                options=[{"label": base, "value": base} for base in sorted(feature_variant_map.keys())],
                value="price_usd"
            ),

            html.Div(id="variant-inputs"),

            html.Label("Target Analysis"),
            dcc.RadioItems(
                id="target-analysis-toggle",
                options=[
                    {"label": "Off (Full Distribution)", "value": "off"},
                    {"label": "On (Group by Target)", "value": "on"}
                ],
                value="off",
                inline=True
            ),

            dcc.Graph(id="histogram-compare"),
            dcc.Graph(id="boxplot-compare")
        ])
    ])
])

# -----------------------------
# 4. Callbacks
# -----------------------------
@app.callback(
    Output("variant-inputs", "children"),
    Output("exploration-mode-toggle", "value"),
    Input("exploration-mode-toggle", "value"),
    Input("base-feature-dropdown", "value")
)
def update_variant_inputs(mode, base):
    variants = feature_variant_map.get(base, [])
    options = [{"label": v, "value": v} for v in variants]

    if len(variants) <= 1:
        return html.Div([
            html.Label("Feature"),
            dcc.Dropdown(id="variant-a-dropdown", options=options, value=variants[0] if variants else None),
            html.Div("ℹ️ Only one variant available for this feature", style={"color": "gray", "marginTop": "5px"})
        ]), "explore"

    if mode == "explore":
        return html.Div([
            html.Label("Feature"),
            dcc.Dropdown(id="variant-a-dropdown", options=options, value=variants[0])
        ]), mode
    else:
        return html.Div([
            html.Div([
                html.Label("Feature A"),
                dcc.Dropdown(id="variant-a-dropdown", options=options, value=variants[0])
            ], style={"width": "48%", "display": "inline-block"}),

            html.Div([
                html.Label("Feature B"),
                dcc.Dropdown(id="variant-b-dropdown", options=options, value=variants[1] if len(variants) > 1 else variants[0])
            ], style={"width": "48%", "float": "right", "display": "inline-block"})
        ]), mode

@app.callback(
    Output("histogram-compare", "figure"),
    Output("boxplot-compare", "figure"),
    Input("exploration-mode-toggle", "value"),
    Input("variant-a-dropdown", "value"),
    Input("variant-b-dropdown", "value"),
    Input("target-analysis-toggle", "value")
)
def update_visuals(mode, var_a, var_b, target_mode):
    dff = df.copy()
    dff["target_label"] = dff["target"].map({0: "Not Clicked", 1: "Clicked", 5: "Booked"}).fillna("Unknown")

    if mode == "explore":
        if not var_a:
            return {}, {}
        if target_mode == "on":
            hist = px.histogram(dff, x=var_a, color="target_label", histnorm="percent", barmode="overlay")
            box = px.box(dff, x="target_label", y=var_a, color="target_label")
        else:
            hist = px.histogram(dff, x=var_a, histnorm="percent")
            box = px.box(dff, y=var_a)
        return hist, box

    if not var_a or not var_b:
        return {}, {}

    melted = pd.melt(dff, id_vars=["target_label"], value_vars=[var_a, var_b], var_name="variant", value_name="value")

    if target_mode == "on":
        hist = px.histogram(melted, x="value", color="target_label", facet_col="variant", histnorm="percent")
    else:
        hist = px.histogram(melted, x="value", color="variant", histnorm="percent", barmode="overlay", opacity=0.5)

    box = px.box(melted, x="variant", y="value", color="variant")
    return hist, box

# -----------------------------
# 5. Run App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)

