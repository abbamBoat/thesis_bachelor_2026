# sections/page_occupations.py
# IT Occupation Demand page

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import TARGET_ROLES, ROLE_CATEGORY, ROLE_COLOURS


def show(data):
    lanbide          = data["lanbide"]
    occupation_index = data["occupation_index"]

    st.header("💼 IT Occupation Demand (2018–2025)")
    st.markdown(
        "**2018 = 100** (baseline). A value of 150 means 50% more demand than 2018. "
        "Growth rates are sourced from WEF 2025, PwC 2025, and Frank et al. (2019). "
        "The structural break at 2023 reflects the post-ChatGPT acceleration in AI-complementary roles."
    )

    selected = st.multiselect("Select roles to display:", TARGET_ROLES, default=TARGET_ROLES)
    df = occupation_index[occupation_index["Name"].isin(selected)].copy()
    df["Category"] = df["Name"].map(ROLE_CATEGORY)

    # Line chart
    fig = px.line(
        df, x="Year", y="Demand Index", color="Name",
        line_dash="Category", markers=True,
        title="IT Occupation Demand Index (2018 = 100)",
        color_discrete_map=ROLE_COLOURS,
    )
    fig.add_hline(y=100, line_dash="dot", line_color="grey", annotation_text="2018 Baseline")
    fig.update_layout(height=500, legend=dict(orientation="h", y=-0.3))
    st.plotly_chart(fig, use_container_width=True)

    # Growth bar chart
    pivot = occupation_index[occupation_index["Year"].isin([2018, 2025])].pivot(
        index="Name", columns="Year", values="Demand Index"
    ).reset_index()
    pivot["Growth (%)"] = ((pivot[2025] - pivot[2018]) / pivot[2018] * 100).round(1)
    pivot["Category"]   = pivot["Name"].map(ROLE_CATEGORY)
    pivot = pivot.sort_values("Growth (%)", ascending=True)

    fig2 = px.bar(
        pivot, x="Growth (%)", y="Name", orientation="h", color="Category",
        color_discrete_map={
            "AI-Complementary":    "#0F9D58",
            "Transforming":        "#F4B400",
            "Routine / Declining": "#DB4437",
        },
        title="Total Demand Growth per Role, 2018 → 2025 (%)",
        text="Growth (%)",
    )
    fig2.update_traces(textposition="outside")
    fig2.update_layout(height=420)
    st.plotly_chart(fig2, use_container_width=True)

    # Year-by-year table — formatted to 1 decimal place, no zeros
    st.subheader("Year-by-Year Comparison Table")
    table = occupation_index.pivot(index="Name", columns="Year", values="Demand Index")
    table["Growth 2018→2025 (%)"] = ((table[2025] - table[2018]) / table[2018] * 100).round(1)
    # Rename integer year columns to strings so format works cleanly
    year_cols = [c for c in table.columns if isinstance(c, int)]
    table.columns = [str(c) if isinstance(c, int) else c for c in table.columns]
    fmt = {str(yr): "{:.1f}" for yr in year_cols}
    fmt["Growth 2018→2025 (%)"] = "{:.1f}"
    st.dataframe(
        table.style
             .format(fmt)
             .background_gradient(subset=["Growth 2018→2025 (%)"], cmap="RdYlGn"),
        use_container_width=True,
    )

    # Lanbide IT postings — show as skill breakdown since only 2024 data exists
    if not lanbide.empty:
        st.subheader("IT Job Postings — Lanbide (Basque Country, April 2024)")
        st.caption(
            "Note: 1,506 of 1,509 postings carry a 2024 date — the portal extract is "
            "a single-date snapshot. A year-by-year bar chart would show one bar only. "
            "The chart below shows the breakdown of IT postings by role category instead."
        )

        it = lanbide[lanbide["is_IT"] == 1].copy()

        # Classify into broad IT categories for a meaningful chart
        def classify(title):
            t = str(title).lower()
            if any(k in t for k in ["software","developer","programador","desarrollador","java","j2ee",".net"]):
                return "Software Development"
            if any(k in t for k in ["sistemas","system","infraestructura","soporte","helpdesk","informatico"]):
                return "IT Systems & Support"
            if any(k in t for k in ["ciberseguridad","security","csirt","seguridad"]):
                return "Cybersecurity"
            if any(k in t for k in ["redes","network","telecomunicacion"]):
                return "Networking"
            if any(k in t for k in ["data","datos","inteligencia","ia y","big data"]):
                return "Data & AI"
            if any(k in t for k in ["cloud","devops","kubernetes","docker"]):
                return "Cloud & DevOps"
            return "Other IT"

        it["IT Category"] = it["title"].apply(classify)
        cat_counts = it["IT Category"].value_counts().reset_index()
        cat_counts.columns = ["IT Category", "Postings"]

        fig3 = px.bar(
            cat_counts.sort_values("Postings", ascending=True),
            x="Postings", y="IT Category", orientation="h",
            title="IT Job Postings by Category — Lanbide (n=85 IT postings from 1,509 total)",
            color="Postings", color_continuous_scale="Blues",
            text="Postings",
        )
        fig3.update_traces(textposition="outside")
        fig3.update_layout(height=380, coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total postings", "1,509")
        col2.metric("IT-related postings", "85")
        col3.metric("IT share", "5.6%")
