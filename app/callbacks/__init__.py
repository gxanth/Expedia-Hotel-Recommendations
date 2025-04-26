from .univariate_callbacks import register_univariate_callbacks
from .multivariate_callbacks import register_multivariate_callbacks
from .overview_callbacks import register_overview_callbacks
from .navigation_callbacks import register_navigation_callbacks


def register_callbacks(app, summary_df):
    """
    Register all app callbacks.
    """
    register_overview_callbacks(app)
    register_univariate_callbacks(app)
    register_multivariate_callbacks(app)
    register_navigation_callbacks(app, summary_df)
