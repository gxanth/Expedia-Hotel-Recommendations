# 📁 app/utils/figure_factory.py
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from app.utils.data_loader import load_feature_histogram

# Load Lux figure template
from dash_bootstrap_templates import load_figure_template

load_figure_template("lux")

# --- Figure functions ---


def make_target_histograms(df_hist):
    """
    Create histograms for each target label.
    """
    # Create subplots for each target label
    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=["Not Clicked", "Clicked", "Booked"],
        shared_yaxes=True,
    )

    target_groups = ["Not Clicked", "Clicked", "Booked"]
    for i, label in enumerate(target_groups, start=1):
        group_df = df_hist[df_hist["target_label"] == label]
        fig.add_trace(
            go.Bar(
                x=group_df["bin_center"],
                y=group_df["rel_freq"],
                opacity=0.7,
                name=label,
            ),
            row=1,
            col=i,
        )

    fig.update_layout(template="lux", bargap=0.1, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def make_standard_histogram(df_hist):
    """
    Create a standard histogram for a single feature.
    """
    fig = px.bar(df_hist, x="bin_center", y="rel_freq", opacity=0.7)
    fig.update_layout(template="lux", margin=dict(l=20, r=20, t=40, b=20))
    return fig


def make_boxplot(df_box, feature, group_mode):
    if group_mode == "on":
        fig = px.box(df_box, x="target_label", y=feature, points="all")
    else:
        fig = px.box(df_box, y=feature, points="all")

    fig.update_layout(template="lux", margin=dict(l=20, r=20, t=40, b=20))
    return fig


def make_multifeature_histogram(selected_features, group_mode):
    """
    Create a histogram for multiple features.
    """
    if not selected_features:
        return go.Figure()
    n_features = len(selected_features)
    fig = make_subplots(
        rows=1,
        cols=n_features,
        subplot_titles=selected_features,
        shared_yaxes=True,
    )

    for i, feature in enumerate(selected_features, start=1):
        df_hist = load_feature_histogram(feature)

        if group_mode == "on" and "target_label" in df_hist.columns:
            targets = df_hist["target_label"].unique()
            for target in targets:
                target_df = df_hist[df_hist["target_label"] == target]
                fig.add_trace(
                    go.Bar(
                        x=target_df["bin_center"],
                        y=target_df["rel_freq"],
                        name=f"{feature} - {target}",
                        opacity=0.7,
                    ),
                    row=1,
                    col=i,
                )
        else:
            fig.add_trace(
                go.Bar(
                    x=df_hist["bin_center"],
                    y=df_hist["rel_freq"],
                    name=feature,
                    opacity=0.7,
                ),
                row=1,
                col=i,
            )

    fig.update_layout(template="lux", bargap=0.1, margin=dict(l=20, r=20, t=40, b=20))
    return fig
