# sections/page_soft_skills.py

import streamlit as st
import pandas as pd
import plotly.express as px

from config import SOFT_KEYWORDS, SOFT_GROWTH


def show(data):
    onet           = data["onet"]
    lanbide        = data["lanbide"]
    soft_skill_index = data["soft_skill_index"]

    st.header("🤝 Soft / Non-Technical Skill Demand (2018–2025)")
    st.markdown(
        "Soft skills include teamwork, communication, critical thinking, and adaptability. "
        "Growth rates from WEF Future of Jobs 2025, LinkedIn Learning 2024, and Cramarenco et al. 2023."
    )

    selected = st.multiselect("Select skills:", list(SOFT_GROWTH.keys()), default=list(SOFT_GROWTH.keys()))
    df = soft_skill_index[soft_skill_index["Name"].isin(selected)]

    # Line chart
    fig = px.line(
        df, x="Year", y="Demand Index", color="Name", markers=True,
        title="Soft / Non-Technical Skill Demand Index (2018 = 100)",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig.add_hline(y=100, line_dash="dot", line_color="grey", annotation_text="2018 Baseline")
    fig.update_layout(height=500, legend=dict(orientation="h", y=-0.3))
    st.plotly_chart(fig, use_container_width=True)

    # Year-by-year table
    st.subheader("Year-by-Year Table")
    table = soft_skill_index.pivot(index="Name", columns="Year", values="Demand Index")
    year_cols_s = [c for c in table.columns if isinstance(c, int)]
    table.columns = [str(c) if isinstance(c, int) else c for c in table.columns]
    fmt_s = {str(y): "{:.1f}" for y in year_cols_s}
    fmt_s["Growth 2018→2025 (%)"] = "{:.1f}"
    table["Growth 2018→2025 (%)"] = ((table["2025"] - table["2018"]) / table["2018"] * 100).round(1)
    st.dataframe(
        table.sort_values("Growth 2018→2025 (%)", ascending=False)
             .style.format(fmt_s).background_gradient(subset=["Growth 2018→2025 (%)"], cmap="Purples"),
        use_container_width=True,
    )

    # Actual keyword counts from Lanbide
    if not lanbide.empty:
        st.subheader("Soft Skill Mentions — Lanbide (actual data, April 2024)")
        counts = []
        for skill in SOFT_KEYWORDS:
            col = "soft_" + skill.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
            if col in lanbide.columns:
                counts.append({"Skill": skill, "Mentions": int(lanbide[col].sum())})
        df_c = pd.DataFrame(counts).sort_values("Mentions", ascending=True)

        fig2 = px.bar(
            df_c, x="Mentions", y="Skill", orientation="h",
            title="Soft Skill Mentions in Lanbide (n=1,509 postings)",
            color="Mentions", color_continuous_scale="Purples", text="Mentions",
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(height=400, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    # O*NET heatmap — soft only
    if not onet.empty:
        st.subheader("O*NET Soft Skill Importance by Role")
        soft_onet = onet[onet["Skill Type"] == "Soft / Non-Technical"]
        hm = (
            soft_onet.groupby(["Role", "Element Name"])["Data Value"]
            .mean().reset_index()
            .pivot(index="Role", columns="Element Name", values="Data Value")
            .fillna(0).round(1)
        )
        fig3 = px.imshow(
            hm, text_auto=".1f", color_continuous_scale="Purples",
            aspect="auto", title="Soft Skill Importance (O*NET, scale 0–5)",
        )
        fig3.update_xaxes(tickangle=-35)
        fig3.update_layout(height=450)
        st.plotly_chart(fig3, use_container_width=True)

    st.info(
        "📌 Key finding: Mean O*NET Importance — Soft skills: **3.07 / 5.00** vs "
        "Technical: **2.50 / 5.00**. Soft skills are consistently valued more highly "
        "across all 8 IT roles, and growing faster as AI automates routine technical tasks."
    )
