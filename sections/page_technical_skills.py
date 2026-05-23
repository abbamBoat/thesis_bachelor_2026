# sections/page_technical_skills.py

import streamlit as st
import pandas as pd
import plotly.express as px

from config import TECH_KEYWORDS, TECH_GROWTH


def show(data):
    onet            = data["onet"]
    lanbide         = data["lanbide"]
    tech_skill_index= data["tech_skill_index"]

    st.header("🔧 Technical Skill Demand (2018–2025)")
    st.markdown(
        "Technical skills are programming languages, cloud platforms, and data tools. "
        "Growth rates from WEF 2025, Coursera 2024, and CEDEFOP digital skills data."
    )

    selected = st.multiselect("Select skills:", list(TECH_GROWTH.keys()), default=list(TECH_GROWTH.keys()))
    df = tech_skill_index[tech_skill_index["Name"].isin(selected)]

    # Line chart
    fig = px.line(
        df, x="Year", y="Demand Index", color="Name", markers=True,
        title="Technical Skill Demand Index (2018 = 100)",
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig.add_hline(y=100, line_dash="dot", line_color="grey")
    fig.add_annotation(
        text="2018 Baseline", xref="paper", yref="y",
        x=1.01, y=100, showarrow=False,
        font=dict(color="grey", size=11), xanchor="left",
    )
    fig.update_layout(
        height=560,
        margin=dict(b=160, r=80),
        legend=dict(orientation="h", y=-0.28, x=0, yanchor="top"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Year-by-year table
    st.subheader("Year-by-Year Table")
    table = tech_skill_index.pivot(index="Name", columns="Year", values="Demand Index")
    year_cols_t = [c for c in table.columns if isinstance(c, int)]
    table.columns = [str(c) if isinstance(c, int) else c for c in table.columns]
    fmt_t = {str(y): "{:.1f}" for y in year_cols_t}
    fmt_t["Growth 2018→2025 (%)"] = "{:.1f}"
    table["Growth 2018→2025 (%)"] = ((table["2025"] - table["2018"]) / table["2018"] * 100).round(1)
    st.dataframe(
        table.sort_values("Growth 2018→2025 (%)", ascending=False)
             .style.format(fmt_t).background_gradient(subset=["Growth 2018→2025 (%)"], cmap="Blues"),
        use_container_width=True,
    )

    # Actual keyword counts from Lanbide
    if not lanbide.empty:
        st.subheader("Technical Skill Mentions — Lanbide (actual data, April 2024)")
        st.markdown("Real counts from 1,509 Basque job postings. "
                    "Low numbers reflect the regional/industrial nature of this labour market.")
        counts = []
        for skill in TECH_KEYWORDS:
            col = "tech_" + skill.lower().replace(" ", "_").replace("/", "_")
            if col in lanbide.columns:
                counts.append({"Skill": skill, "Mentions": int(lanbide[col].sum())})
        df_c = pd.DataFrame(counts).sort_values("Mentions", ascending=True)

        fig2 = px.bar(
            df_c, x="Mentions", y="Skill", orientation="h",
            title="Technical Skill Mentions in Lanbide (n=1,509 postings)",
            color="Mentions", color_continuous_scale="Blues", text="Mentions",
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(height=400, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    # O*NET heatmap — technical only, 14 IT-relevant skills (Equipment Selection excluded)
    if not onet.empty:
        st.subheader("O*NET Technical Skill Importance by Role")
        TECH_ONET_SKILLS = [
            "Programming",
            "Systems Analysis",
            "Systems Evaluation",
            "Technology Design",
            "Mathematics",
            "Science",
            "Operations Analysis",
            "Operation and Control",
            "Operations Monitoring",
            "Troubleshooting",
            "Quality Control Analysis",
            "Equipment Maintenance",
            "Installation",
            "Repairing",
        ]
        tech_onet = onet[
            (onet["Skill Type"] == "Technical") &
            (onet["Element Name"].isin(TECH_ONET_SKILLS))
        ]
        hm = (
            tech_onet.groupby(["Role", "Element Name"])["Data Value"]
            .mean().reset_index()
            .pivot(index="Role", columns="Element Name", values="Data Value")
            .fillna(0).round(1)
        )
        fig3 = px.imshow(
            hm, text_auto=".1f", color_continuous_scale="Blues",
            aspect="auto", title="Technical Skill Importance (O*NET, scale 0–5)",
            labels={"x": "Skill", "y": "Role", "color": "Importance"},
        )
        fig3.update_xaxes(tickangle=-35)
        fig3.update_layout(height=420)
        st.plotly_chart(fig3, use_container_width=True)
