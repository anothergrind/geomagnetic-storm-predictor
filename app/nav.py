"""Page registry.

Pages are rebuilt each script run (Streamlit's expectation) and kept in a
module-level map so components can link between them with ``st.page_link``
without importing each other.
"""
from __future__ import annotations

import streamlit as st

from app.pages import data_explorer, forecast, overview, performance, storms

_PAGES: dict = {}


def build() -> dict[str, list]:
    """Create this run's pages and return them grouped for ``st.navigation``."""
    _PAGES["overview"] = st.Page(
        overview.render, title="Overview", icon=":material/space_dashboard:",
        url_path="overview", default=True,
    )
    _PAGES["forecast"] = st.Page(
        forecast.render, title="Forecast explorer", icon=":material/timeline:",
        url_path="forecast",
    )
    _PAGES["performance"] = st.Page(
        performance.render, title="Model performance", icon=":material/bar_chart:",
        url_path="performance",
    )
    _PAGES["storms"] = st.Page(
        storms.render, title="Storm explorer", icon=":material/storm:",
        url_path="storms",
    )
    _PAGES["data_explorer"] = st.Page(
        data_explorer.render, title="Data Explorer", icon=":material/analytics:",
        url_path="data-explorer",
    )
    return {
        "Forecast": [_PAGES["overview"], _PAGES["forecast"]],
        "Analysis": [_PAGES["performance"], _PAGES["storms"], _PAGES["data_explorer"]],
    }


def page(name: str):
    """A page object built by :func:`build` this run."""
    return _PAGES[name]
