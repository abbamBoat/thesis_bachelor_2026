# R with: streamlit run dashboard_design.py

import streamlit as st

# Import the data loader and all page files
from data_loader import get_all_data

from sections import (
    page_cleaning,
    page_occupations,
    page_technical_skills,
    page_soft_skills,
    page_comparison,
    page_forecast,
    page_heatmap,
    page_eu_context,
)


# ── Page setup ───────────────────────────────────────────────
st.set_page_config(
    page_title="AI Impact on IT Workforce",
    page_icon="🤖❗",
    layout="wide",
)

st.title("🤖 AI Impact on IT Workforce")
st.markdown("Bachelor Thesis — Modelling the future impact of AI automation on the IT workforce")
st.divider()


# Load all data once
data = get_all_data()


# Sidebar navigation
page = st.sidebar.radio("Go to:", [
    "📊 Data Cleaning Report",
    "💼 Occupation Demand",
    "🔧 Technical Skills",
    "🤝 Soft / Non-Technical Skills",
    "📊 Technical vs Soft Comparison",
    "🔮 Forecast 2026–2027",
    "🗺 Skill Heatmap",
    "🌍 EU & Basque Context",
])

st.sidebar.divider()
if not data["lanbide"].empty:
    st.sidebar.metric("Total Lanbide postings", f"{len(data['lanbide']):,}")
    st.sidebar.metric("IT-related postings",    f"{data['lanbide']['is_IT'].sum():,}")
if not data["onet"].empty:
    n_tech = (data["onet"]["Skill Type"] == "Technical").sum()
    n_soft = (data["onet"]["Skill Type"] == "Soft / Non-Technical").sum()
    st.sidebar.metric("O*NET Technical rows", f"{n_tech:,}")
    st.sidebar.metric("O*NET Soft rows",       f"{n_soft:,}")


# Route to the correct page
if   page == "📊 Data Cleaning Report":         page_cleaning.show(data)
elif page == "💼 Occupation Demand":             page_occupations.show(data)
elif page == "🔧 Technical Skills":              page_technical_skills.show(data)
elif page == "🤝 Soft / Non-Technical Skills":   page_soft_skills.show(data)
elif page == "📊 Technical vs Soft Comparison":  page_comparison.show(data)
elif page == "🔮 Forecast 2026–2027":            page_forecast.show(data)
elif page == "🗺 Skill Heatmap":                 page_heatmap.show(data)
elif page == "🌍 EU & Basque Context":           page_eu_context.show(data)


# Footer
st.divider()
st.caption(
    "Bachelor Thesis — AI Impact on IT Workforce | by me :)"
)
