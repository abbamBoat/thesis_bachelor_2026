# sections/page_comparison.py

import streamlit as st
import pandas as pd
import plotly.express as px

from config import TARGET_ROLES, TECH_KEYWORDS, SOFT_KEYWORDS


def show(data):
    onet             = data["onet"]
    lanbide          = data["lanbide"]
    tech_skill_index = data["tech_skill_index"]
    soft_skill_index = data["soft_skill_index"]

    st.header("📊 Technical vs Soft Skills — Side-by-Side")

    # Key metrics at the top
    col1, col2 = st.columns(2)
    col1.metric("Mean O*NET Importance — Technical",             "2.50 / 5.00")
    col2.metric("Mean O*NET Importance — Soft / Non-Technical",  "3.07 / 5.00")

    # 2025 demand index for all skills in one chart
    st.subheader("2025 Demand Index — All Skills")
    tech_2025 = tech_skill_index[tech_skill_index["Year"] == 2025][["Name", "Demand Index"]].copy()
    tech_2025["Type"] = "Technical"
    soft_2025 = soft_skill_index[soft_skill_index["Year"] == 2025][["Name", "Demand Index"]].copy()
    soft_2025["Type"] = "Soft / Non-Technical"
    combined = pd.concat([tech_2025, soft_2025]).sort_values("Demand Index", ascending=True)

    fig = px.bar(
        combined, x="Demand Index", y="Name", color="Type", orientation="h",
        color_discrete_map={"Technical": "#2E4057", "Soft / Non-Technical": "#03A9F4"},
        title="Demand Index in 2025 — Technical vs Soft (2018 = 100)",
        barmode="group",
    )
    fig.add_vline(x=100, line_dash="dot", line_color="grey", annotation_text="Baseline (2018)")
    fig.update_layout(height=580, legend=dict(orientation="h", y=1.05))
    st.plotly_chart(fig, use_container_width=True)

    # Combined Lanbide mentions
    if not lanbide.empty:
        st.subheader("All Skill Mentions — Lanbide (n=1,509 postings)")
        all_counts = []
        for skill in TECH_KEYWORDS:
            col = "tech_" + skill.lower().replace(" ", "_").replace("/", "_")
            if col in lanbide.columns:
                all_counts.append({"Skill": skill, "Mentions": int(lanbide[col].sum()), "Type": "Technical"})
        for skill in SOFT_KEYWORDS:
            col = "soft_" + skill.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
            if col in lanbide.columns:
                all_counts.append({"Skill": skill, "Mentions": int(lanbide[col].sum()), "Type": "Soft / Non-Technical"})
        df_all = pd.DataFrame(all_counts).sort_values("Mentions", ascending=True)

        fig2 = px.bar(
            df_all, x="Mentions", y="Skill", color="Type", orientation="h",
            color_discrete_map={"Technical": "#2E4057", "Soft / Non-Technical": "#03A9F4"},
            title="All Skill Mentions in Lanbide Job Postings",
            text="Mentions",
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(height=560, legend=dict(orientation="h", y=1.05))
        st.plotly_chart(fig2, use_container_width=True)

    # Top skills per role — grouped bar instead of radar
    if not onet.empty:
        st.subheader("Top Skills per Role — Technical vs Soft")
        st.markdown("Select a role to see its top 6 technical and top 6 soft skills "
                    "side by side as a bar chart.")
        role_choice = st.selectbox("Select a role:", TARGET_ROLES)

        role_df  = onet[onet["Role"] == role_choice]
        top_tech = (role_df[role_df["Skill Type"] == "Technical"]
                    .groupby("Element Name")["Data Value"].mean()
                    .sort_values(ascending=False).head(6).reset_index())
        top_tech["Skill Type"] = "Technical"

        top_soft = (role_df[role_df["Skill Type"] == "Soft / Non-Technical"]
                    .groupby("Element Name")["Data Value"].mean()
                    .sort_values(ascending=False).head(6).reset_index())
        top_soft["Skill Type"] = "Soft / Non-Technical"

        combined = pd.concat([top_tech, top_soft]).sort_values("Data Value", ascending=True)
        combined["Data Value"] = combined["Data Value"].round(1)

        fig3 = px.bar(
            combined, x="Data Value", y="Element Name", color="Skill Type",
            orientation="h",
            color_discrete_map={"Technical": "#2E4057", "Soft / Non-Technical": "#03A9F4"},
            title=f"Top 6 Technical + Top 6 Soft Skills — {role_choice} (O*NET Importance 0–5)",
            text="Data Value",
            labels={"Data Value": "Importance (0–5)"},
        )
        fig3.update_traces(textposition="outside")
        fig3.update_layout(height=500, legend=dict(orientation="h", y=1.05))
        st.plotly_chart(fig3, use_container_width=True)
