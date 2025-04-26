from app import app  # <--- init app here
from app.layout import create_layout
from app.callbacks import register_callbacks
from app.utils.data_loader import load_summary_df
from app.utils.config_loader import ConfigLoader

# Initialize ConfigLoader
config_loader = ConfigLoader()

# Load configs (optional: preload now, use later if needed)
app_config = config_loader.load_app_config()
style_config = config_loader.load_styles()

# Load data
summary_df = load_summary_df()
print("Summary DataFrame loaded successfully.")
print(summary_df.head())

# Attach layout and callbacks
app.layout = create_layout(summary_df)
register_callbacks(app, summary_df)

if __name__ == "__main__":
    app.run(debug=True)
