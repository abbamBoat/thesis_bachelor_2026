# sections/page_eu_context.py

import streamlit as st
import plotly.express as px


def show(data):
    cedefop = data["cedefop"]
    unemp   = data["unemp"]

    st.header("🌍 EU Labour Market & Basque Country Context")

    # CEDEFOP — EU indicators
    if not cedefop.empty:
        st.subheader("CEDEFOP: EU Labour Market Indicators")

        all_countries = sorted(cedefop["Countries"].unique())
        default_c = [c for c in ["European Union", "Spain", "Germany", "Netherlands", "France"]
                     if c in all_countries]
        selected_countries  = st.multiselect("Countries:", all_countries, default=default_c)
        selected_indicator  = st.selectbox("Indicator:", sorted(cedefop["Indicator"].unique()))

        filtered = cedefop[
            (cedefop["Indicator"] == selected_indicator) &
            (cedefop["Countries"].isin(selected_countries))
        ]
        if not filtered.empty:
            fig = px.line(filtered, x="Year", y="Value", color="Countries",
                          markers=True, title=selected_indicator)
            fig.update_layout(
                height=460,
                margin=dict(b=120),
                legend=dict(orientation="h", y=-0.25, x=0, yanchor="top"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data for this combination. Try different filters.")

    # Basque unemployment by district
    if not unemp.empty:
        st.subheader("Basque Country Unemployment Rate by District (2020–2024)")
        unemp_long = unemp.melt(
            id_vars="District",
            value_vars=[2020, 2021, 2022, 2023, 2024],
            var_name="Year",
            value_name="Unemployment %",
        )
        fig2 = px.line(
            unemp_long, x="Year", y="Unemployment %", color="District",
            title="Unemployment Rate (%) — Basque Districts 2020–2024",
            markers=True,
        )
        fig2.update_layout(
            height=480,
            margin=dict(b=140),
            legend=dict(orientation="h", y=-0.28, x=0, yanchor="top", font=dict(size=9)),
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.dataframe(unemp, use_container_width=True)
