from dash import Input, Output, State, callback, ctx
import json

@callback(
    Output("df-store", "data"),
    [
        Input("primary-feature-dropdown", "value"),
        Input("exploration-mode-toggle", "value"),
    ],
    [State("df-store", "data")]
)
def update_df_store(primary_feature, exploration_mode, current_data):
    """
    Combined callback to update `df-store.data` based on multiple triggers.
    """
    triggered_id = ctx.triggered_id  # Get the ID of the triggered input

    if triggered_id == "primary-feature-dropdown":
        # Update based on primary feature selection
        updated_data = {"primary_feature": primary_feature}
    elif triggered_id == "exploration-mode-toggle":
        # Update based on exploration mode toggle
        updated_data = {"exploration_mode": exploration_mode}
    else:
        updated_data = {}

    # Merge with existing data
    if current_data:
        current_data = json.loads(current_data)
        current_data.update(updated_data)
    else:
        current_data = updated_data

    return json.dumps(current_data)
