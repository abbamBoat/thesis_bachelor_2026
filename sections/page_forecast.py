# sections/page_forecast.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import TARGET_ROLES, ROLE_COLOURS, ROLE_CATEGORY, TECH_GROWTH, SOFT_GROWTH


def _line_with_stars(hist_df, forecast_df, colour_map, title, rf_col, dt_col, yr_rf, yr_dt):
    """Helper: draws historical lines then overlays RF (star) and DT (diamond) forecast points."""
    fig = px.line(
        hist_df, x="Year", y="Demand Index", color="Name",
        markers=True, title=title,
        color_discrete_map=colour_map if colour_map else None,
        color_discrete_sequence=None if colour_map else px.colors.qualitative.Bold,
    )
    fig.add_hline(y=100, line_dash="dot", line_color="grey", annotation_text="2018 Baseline")

    colours = list(colour_map.values()) if colour_map else px.colors.qualitative.Bold

    for i, (_, row) in enumerate(forecast_df.iterrows()):
        c = colours[i % len(colours)] if not colour_map else colour_map.get(row["Name"], colours[i % len(colours)])

        # RF predictions — star symbol
        for col, yr in [(rf_col[0], yr_rf[0]), (rf_col[1], yr_rf[1])]:
            fig.add_scatter(
                x=[yr], y=[row[col]], mode="markers",
                marker=dict(symbol="star", size=14, color=c, line=dict(width=1, color="white")),
                text=[f"RF {row[col]:.1f}"], textposition="top center",
                showlegend=False,
            )
        # DT predictions — diamond symbol
        for col, yr in [(dt_col[0], yr_dt[0]), (dt_col[1], yr_dt[1])]:
            fig.add_scatter(
                x=[yr], y=[row[col]], mode="markers",
                marker=dict(symbol="diamond", size=11, color=c,
                            line=dict(width=1.5, color="white")),
                text=[f"DT {row[col]:.1f}"], textposition="bottom center",
                showlegend=False,
            )

    fig.add_vline(x=2025.5, line_dash="dash", line_color="grey",
                  annotation_text="← Actual  |  Predicted →")

    # Manual legend entries for the symbols
    fig.add_scatter(x=[None], y=[None], mode="markers",
                    marker=dict(symbol="star", size=12, color="grey"),
                    name="★ Random Forest", showlegend=True)
    fig.add_scatter(x=[None], y=[None], mode="markers",
                    marker=dict(symbol="diamond", size=10, color="grey"),
                    name="◆ Decision Tree", showlegend=True)

    fig.update_layout(height=530, legend=dict(orientation="h", y=-0.35))
    return fig


def show(data):
    occupation_index = data["occupation_index"]
    tech_skill_index = data["tech_skill_index"]
    soft_skill_index = data["soft_skill_index"]
    occ_forecast     = data["occ_forecast"]
    tech_forecast    = data["tech_forecast"]
    soft_forecast    = data["soft_forecast"]
    occ_metrics      = data["occ_metrics"]
    tech_metrics     = data["tech_metrics"]
    soft_metrics     = data["soft_metrics"]
    occ_fi_rf        = data["occ_fi_rf"]
    occ_fi_dt        = data["occ_fi_dt"]

    st.header("⌛ Demand Forecast — 2026 & 2027")
    st.markdown(
        "This section predicts demand for **2026 and 2027** using two regression models trained "
        "on the full **2018–2025 window**. "
        "The years 2018 and 2019 are used as **input features** through lag variables "
        "(they are not training targets). The training rows are **2020–2025** — "
        "giving 48 rows across all 8 roles."
    )

    with st.expander("How the year-pair training works — click to read"):
        st.markdown("""
The model is trained on **consecutive year pairs** built from the full **2018–2025** history.
Each pair says: *"given the demand at year t, what will demand be at year t+1?"*

| Input year (t) | Output year (t+1) | Role in training |
|---|---|---|
| 2018 | 2019 | Pair 1 |
| 2019 | 2020 | Pair 2 |
| 2020 | 2021 | Pair 3 |
| 2021 | 2022 | Pair 4 |
| 2022 | 2023 | Pair 5 |
| 2023 | 2024 | Pair 6 |
| 2024 | 2025 | Pair 7 — most recent |
| **2025 → predict 2026** | Input = actual 2025 | Prediction step 1 |
| **2026 → predict 2027** | Input = predicted 2026 | Prediction step 2 |

This gives **56 training pairs** (7 pairs × 8 roles). No data is wasted.

**Features used for each pair:**
- **X_Demand** — demand index at the input year (strongest predictor by far)
- **Role_Encoded** — integer ID for the role
- **Year_In** — the input year (2018–2025)
- **Year_Since_Break** — years since the 2022 AI structural break (0–3)

**★ Random Forest** builds 200 decision trees and averages their predictions (more stable).  
**◆ Decision Tree** builds one simple interpretable tree (depth 3) — easier to explain.
        """)

    st.warning(
        "The demand indices used as model input are built from published growth rate estimates "
        "(WEF 2025, PwC 2025, Frank et al. 2019) — not directly measured job posting counts. "
        "Both models produce data-informed directional projections. "
        "See the thesis Limitations section for a full discussion."
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "💼 Occupations", "🔧 Technical Skills", "🤝 Soft Skills", "📐 Model Details"
    ])

    rf_cols = ("RF 2026", "RF 2027")
    dt_cols = ("DT 2026", "DT 2027")
    yrs     = (2026, 2027)

    # ── Tab 1: Occupations ────────────────────────────────────
    with tab1:
        st.subheader("IT Occupation Demand — RF & DT Predictions for 2026 & 2027")

        selected = st.multiselect("Select roles:", TARGET_ROLES, default=TARGET_ROLES, key="fc_occ")
        hist = occupation_index[occupation_index["Name"].isin(selected)].copy()
        hist["Category"] = hist["Name"].map(ROLE_CATEGORY)
        fc   = occ_forecast[occ_forecast["Name"].isin(selected)]

        st.plotly_chart(
            _line_with_stars(hist, fc, ROLE_COLOURS,
                             "Occupation Demand — Historical + RF ★ and DT ◆ Predictions",
                             rf_cols, dt_cols, yrs, yrs),
            use_container_width=True,
        )

        # Table with both models
        st.subheader("Forecast Table — Both Models")
        fc_show = occ_forecast[occ_forecast["Name"].isin(selected)].copy()
        fc_show = fc_show.sort_values("RF 2027", ascending=False)
        fmt_fc = {"2025 (Actual)": "{:.1f}", "RF 2026": "{:.1f}",
                  "RF 2027": "{:.1f}", "DT 2026": "{:.1f}", "DT 2027": "{:.1f}"}
        st.dataframe(
            fc_show.style.format(fmt_fc).background_gradient(
                subset=["RF 2026", "RF 2027", "DT 2026", "DT 2027"], cmap="RdYlGn"),
            use_container_width=True, hide_index=True,
        )

        # Grouped bar — RF vs DT 2027 comparison
        st.subheader("2027 Prediction — RF vs DT Comparison")
        fc_bar = occ_forecast.copy()
        bar_data = pd.concat([
            fc_bar[["Name", "RF 2027"]].rename(columns={"RF 2027": "Prediction"}).assign(Model="Random Forest ★"),
            fc_bar[["Name", "DT 2027"]].rename(columns={"DT 2027": "Prediction"}).assign(Model="Decision Tree ◆"),
        ]).sort_values("Prediction", ascending=True)

        fig2 = px.bar(
            bar_data, x="Prediction", y="Name", color="Model", orientation="h",
            barmode="group",
            color_discrete_map={"Random Forest ★": "#2E4057", "Decision Tree ◆": "#03A9F4"},
            title="Predicted Demand Index in 2027 — RF vs DT",
            text=bar_data["Prediction"].round(1),
        )
        fig2.add_vline(x=100, line_dash="dot", line_color="grey", annotation_text="Baseline")
        fig2.update_traces(textposition="outside")
        fig2.update_layout(height=450, legend=dict(orientation="h", y=1.05))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Tab 2: Technical Skills ───────────────────────────────
    with tab2:
        st.subheader("Technical Skill Demand — RF & DT Predictions for 2026 & 2027")

        st.plotly_chart(
            _line_with_stars(tech_skill_index, tech_forecast, None,
                             "Technical Skills — Historical + RF ★ and DT ◆ Predictions",
                             rf_cols, dt_cols, yrs, yrs),
            use_container_width=True,
        )

        fc_t = tech_forecast.copy().sort_values("RF 2027", ascending=False)
        st.dataframe(
            fc_t.style.background_gradient(
                subset=["RF 2026", "RF 2027", "DT 2026", "DT 2027"], cmap="Blues"),
            use_container_width=True, hide_index=True,
        )

    # ── Tab 3: Soft Skills ────────────────────────────────────
    with tab3:
        st.subheader("Soft / Non-Technical Skill Demand — RF & DT Predictions for 2026 & 2027")

        st.plotly_chart(
            _line_with_stars(soft_skill_index, soft_forecast, None,
                             "Soft Skills — Historical + RF ★ and DT ◆ Predictions",
                             rf_cols, dt_cols, yrs, yrs),
            use_container_width=True,
        )

        fc_s = soft_forecast.copy().sort_values("RF 2027", ascending=False)
        st.dataframe(
            fc_s.style.background_gradient(
                subset=["RF 2026", "RF 2027", "DT 2026", "DT 2027"], cmap="Purples"),
            use_container_width=True, hide_index=True,
        )

    # ── Tab 4: Model Details ──────────────────────────────────
    with tab4:
        st.subheader("Model Performance — Random Forest vs Decision Tree")

        # Metrics table
        metrics_df = pd.DataFrame({
            "Metric": ["Train R²", "Train MAE", "LOO-CV R²", "LOO-CV MAE",
                       "Train R²", "Train MAE", "LOO-CV R²", "LOO-CV MAE"],
            "Model":  ["RF"]*4 + ["DT"]*4,
            "Occupation": [
                occ_metrics["rf_train_r2"], occ_metrics["rf_train_mae"],
                occ_metrics["rf_loo_r2"],   occ_metrics["rf_loo_mae"],
                occ_metrics["dt_train_r2"], occ_metrics["dt_train_mae"],
                occ_metrics["dt_loo_r2"],   occ_metrics["dt_loo_mae"],
            ],
            "Technical Skill": [
                tech_metrics["rf_train_r2"], tech_metrics["rf_train_mae"],
                tech_metrics["rf_loo_r2"],   tech_metrics["rf_loo_mae"],
                tech_metrics["dt_train_r2"], tech_metrics["dt_train_mae"],
                tech_metrics["dt_loo_r2"],   tech_metrics["dt_loo_mae"],
            ],
            "Soft Skill": [
                soft_metrics["rf_train_r2"], soft_metrics["rf_train_mae"],
                soft_metrics["rf_loo_r2"],   soft_metrics["rf_loo_mae"],
                soft_metrics["dt_train_r2"], soft_metrics["dt_train_mae"],
                soft_metrics["dt_loo_r2"],   soft_metrics["dt_loo_mae"],
            ],
        })
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)

        st.caption(
            f"Training pairs: {occ_metrics['n_pairs']} "
            f"(7 year-pairs × 8 roles, built from the full 2018–2025 history). "
            "**R²** = how well the model fits the data (1.0 = perfect). "
            "**MAE** = mean absolute error in index points. "
            "**LOO-CV** = Leave-One-Out cross-validation (most honest estimate for small datasets)."
        )

        # Feature importance — side by side
        st.subheader("Feature Importance — What Each Model Relied On")

        col1, col2 = st.columns(2)
        with col1:
            fi_rf_df = occ_fi_rf.reset_index()
            fi_rf_df.columns = ["Feature", "Importance"]
            fig_rf = px.bar(
                fi_rf_df, x="Importance", y="Feature", orientation="h",
                title="Random Forest ★ Feature Importance",
                color="Importance", color_continuous_scale="Blues",
                text=fi_rf_df["Importance"].round(2),
            )
            fig_rf.update_traces(textposition="outside")
            fig_rf.update_layout(height=340, coloraxis_showscale=False,
                                  margin=dict(l=10, r=10))
            st.plotly_chart(fig_rf, use_container_width=True)

        with col2:
            fi_dt_df = occ_fi_dt.reset_index()
            fi_dt_df.columns = ["Feature", "Importance"]
            fig_dt = px.bar(
                fi_dt_df, x="Importance", y="Feature", orientation="h",
                title="Decision Tree ◆ Feature Importance",
                color="Importance", color_continuous_scale="Purples",
                text=fi_dt_df["Importance"].round(2),
            )
            fig_dt.update_traces(textposition="outside")
            fig_dt.update_layout(height=340, coloraxis_showscale=False,
                                  margin=dict(l=10, r=10))
            st.plotly_chart(fig_dt, use_container_width=True)

        st.info(
            "**Random Forest** spreads importance more evenly across features — "
            "Rolling_Mean_3, Lag_1, and Lag_2 all contribute, which makes the predictions "
            "more stable. **Decision Tree** concentrates almost entirely on Lag_2 and "
            "Rolling_Mean_3, which explains why its predictions are less nuanced "
            "but easier to interpret as a single set of if-then rules."
        )
