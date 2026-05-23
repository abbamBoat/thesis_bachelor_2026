# sections/page_heatmap.py

import streamlit as st
import pandas as pd
import plotly.express as px

from config import TARGET_ROLES


def show(data):
    onet = data["onet"]

    st.header("🗺 Skill Importance by Role (O*NET)")
    st.markdown(
        "Importance scale: **0 to 5**. Darker = more important. "
        "Numbers are shown to **1 decimal place**. "
        "Use the filter below to switch between technical and soft skills."
    )

    skill_filter = st.radio(
        "Show:",
        ["All skills", "Technical only", "Soft / Non-Technical only"],
        horizontal=True,
    )

    if not onet.empty:

        # Filter the data based on the radio button
        if skill_filter == "Technical only":
            hm_data = onet[onet["Skill Type"] == "Technical"]
            colour  = "Blues"
        elif skill_filter == "Soft / Non-Technical only":
            hm_data = onet[onet["Skill Type"] == "Soft / Non-Technical"]
            colour  = "Purples"
        else:
            hm_data = onet.copy()
            colour  = "Blues"

        # Build the pivot table — rows = role, columns = skill
        pivot = (
            hm_data.groupby(["Role", "Element Name"])["Data Value"]
            .mean().reset_index()
            .pivot(index="Role", columns="Element Name", values="Data Value")
            .fillna(0)
            .round(1)   # 1 decimal place
        )

        fig = px.imshow(
            pivot,
            text_auto=".1f",            # show 1 decimal place in every cell
            color_continuous_scale=colour,
            aspect="auto",
            title=f"Skill Importance — {skill_filter} (O*NET, scale 0–5)",
            labels={"x": "Skill", "y": "Role", "color": "Importance"},
        )
        fig.update_xaxes(tickangle=-35)
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        # Drill down — top skills for a specific role
        st.subheader("Top 10 Skills for a Specific Role")
        role_choice = st.selectbox("Select role:", TARGET_ROLES)
        type_choice = st.radio(
            "Skill type:",
            ["Both", "Technical", "Soft / Non-Technical"],
            horizontal=True,
            key="hm_type",
        )

        role_df = onet[onet["Role"] == role_choice].copy()
        if type_choice == "Technical":
            role_df = role_df[role_df["Skill Type"] == "Technical"]
        elif type_choice == "Soft / Non-Technical":
            role_df = role_df[role_df["Skill Type"] == "Soft / Non-Technical"]

        top10 = (
            role_df.groupby(["Element Name", "Skill Type"])["Data Value"]
            .mean().reset_index()
            .sort_values("Data Value", ascending=False)
            .head(10)
        )
        top10["Data Value"] = top10["Data Value"].round(1)

        fig2 = px.bar(
            top10, x="Data Value", y="Element Name", orientation="h",
            color="Skill Type",
            color_discrete_map={"Technical": "#2E4057", "Soft / Non-Technical": "#03A9F4"},
            title=f"Top 10 Skills — {role_choice}",
            text="Data Value",
            labels={"Data Value": "Importance (0–5)"},
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(height=420)
        st.plotly_chart(fig2, use_container_width=True)
