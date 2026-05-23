# sections/page_cleaning.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def show(data):
    log     = data["log"]
    onet    = data["onet"]
    lanbide = data["lanbide"]

    st.header("📊 Data Cleaning Report — All 12 Source Files")
    st.markdown(
        "This page documents exactly what was done to each of the 12 datasets "
        "used in this thesis — how many rows existed before cleaning, how many "
        "remain after cleaning, why rows were removed, and what structural null "
        "patterns were identified and handled."
    )

    # ── Summary table ────────────────────────────────────────
    st.subheader("Summary: All 12 Files")
    log_df = pd.DataFrame(log)
    st.dataframe(log_df, use_container_width=True, hide_index=True)

    # ── Before vs After bar chart ────────────────────────────
    st.subheader("Records Before vs After Cleaning")
    fig = go.Figure()
    fig.add_bar(x=log_df["File"], y=log_df["Rows Before"],
                name="Before Cleaning", marker_color="#4C8BF5")
    fig.add_bar(x=log_df["File"], y=log_df["Rows After"],
                name="After Cleaning", marker_color="#0F9D58")
    fig.update_layout(barmode="group", height=430,
                      xaxis_tickangle=-30,
                      legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True)

    st.metric("Total raw rows across all 12 files",
              f"{log_df['Rows Before'].sum():,}")
    st.metric("Total clean rows kept",
              f"{log_df['Rows After'].sum():,}")

    # ── Individual file cards ─────────────────────────────────
    st.subheader("Individual File Detail")

    file_info = [
        ("1",  "Skills.xlsx", "O*NET v30.2 — Skill importance scores",
         "62,580", "560",
         "The full O*NET Skills export covers every occupation in the US labour market. "
         "The vast majority are irrelevant to this thesis (e.g. nurses, welders, accountants). "
         "Filtering to the 16 titles that map to the 8 target IT roles reduced the dataset to 1,120 rows. "
         "A second filter kept only rows where Scale ID = 'IM' (Importance), discarding the 560 Level-scale rows. "
         "The 31,290 nulls in the 'Not Relevant' column are structural — that field is only populated for "
         "Level-scale rows and intentionally blank for Importance rows. "
         "Final dataset: 560 rows with a mean importance score of 2.83 out of 5.",
         "Skill Type was added to label each element as Technical or Soft/Non-Technical "
         "using the O*NET Content Model groupings."),

        ("2",  "Technology_Skills.xlsx", "O*NET v30.2 — Technology tool examples",
         "32,773", "4,148",
         "Lists specific software tools, platforms, and technologies associated with each occupation. "
         "Contains no nulls in the raw file. Filtered to the 16 IT target titles. "
         "The 'In Demand' column (originally Y/N strings) was encoded as integers (1=Yes, 0=No) "
         "for use in quantitative comparisons.",
         "Used to identify which technologies are marked as 'hot' or 'in demand' per role."),

        ("3",  "Occupation_Data.xlsx", "O*NET v30.2 — Occupation descriptions",
         "1,016", "16",
         "Short factual descriptions of each O*NET occupation. No nulls. "
         "Filtered to the 16 IT titles only. "
         "Used to provide readable role descriptions in the dashboard occupation pages.",
         "No additional transformation required beyond filtering."),

        ("4",  "Occupation_Level_Metadata.xlsx", "O*NET v30.2 — Survey metadata",
         "32,202", "400",
         "Records the number of survey respondents (N) and percentage response (Percent) "
         "for each occupation-item pair in the O*NET data collection. "
         "3,760 rows had null N values, representing items where no respondent data was collected "
         "(typically because that item was not applicable to that occupation). "
         "These were removed to retain only rows with confirmed survey backing.",
         "Used to assess the statistical confidence behind O*NET importance scores."),

        ("5",  "cedefop-datatable.xlsx", "CEDEFOP — EU Labour Market Indicators",
         "11,270", "11,136",
         "Harmonised EU labour market statistics from the European Centre for the Development "
         "of Vocational Training, covering 37 countries and 11 time points (2010–2024). "
         "The Flags column (9,607 nulls) is a quality annotation field that was not populated "
         "in this export — this is a structural null, not a data quality issue. "
         "The Value column had 134 genuinely missing entries, representing country-year "
         "combinations where member states did not report that particular indicator. "
         "Those 134 rows were removed via listwise deletion.",
         "Year cast from float64 to int64 for consistent indexing."),

        ("6",  "xls0024822_0024823_i.xlsx", "Eustat — Basque Unemployment by District",
         "30", "22",
         "Raw Excel file delivered in a presentation-style layout: a title string occupies "
         "row 0, two blank rows follow, and the actual data begins at row index 3. "
         "Columns were unnamed (Unnamed: 0 through Unnamed: 7). "
         "The data block was extracted using iloc[3:28, :6], columns were renamed to "
         "District, 2020, 2021, 2022, 2023, 2024, and blank filler rows were removed. "
         "All five year columns were coerced from mixed object type to float64.",
         "22 rows retained: 21 Basque administrative districts plus one Basque Country overall row."),

        ("7",  "Lanbide_Job_Postings.csv", "Lanbide — Basque Public Employment Portal",
         "1,509", "1,509",
         "Real job advertisements extracted from the Basque Country public employment portal "
         "on 14 April 2024. The dataset is in Spanish. "
         "No rows were lost during cleaning (0 dropped) because the core fields — "
         "title (0% null) and datePosted (0% null) — were complete. "
         "Nine columns were excluded from analysis due to null rates exceeding 80%: "
         "collective (95.8%), age (98.6%), employmentSituation (97.4%), workday (93.8%), "
         "driverLicense (88.1%), experienceRequirements (81.2%), participants (53.6%), "
         "employmentType (53.6%), and educationRequirements (52.6%). "
         "The datePosted column was parsed from DD/MM/YYYY string format to datetime64 "
         "using pd.to_datetime(dayfirst=True). "
         "A critical keyword correction was made during feature engineering: "
         "the substring 'ia ' (intended to capture 'inteligencia artificial') initially "
         "matched 757 postings incorrectly due to occurrence in common Spanish words. "
         "This was corrected to use the full phrases 'machine learning' and "
         "'inteligencia artificial', reducing the Machine Learning count to an accurate 2.",
         "A unified full_text field (title + description, lowercased) was built for NLP. "
         "14 binary skill flag columns added (7 technical + 7 soft)."),

        ("8",  "occupations_en.csv", "ESCO v1.2.1 — Occupation Taxonomy",
         "3,043", "73",
         "The ESCO occupation taxonomy contains 3,043 standardised occupation concepts. "
         "Three columns — hiddenLabels, scopeNote, and definition — contain very high null "
         "rates (99.7%, 89.8%, 99.7% respectively). These are structural nulls: "
         "ESCO only populates these optional descriptive fields for a small subset of concepts. "
         "Filtering was applied to retain only IT-relevant occupations identified by keyword "
         "matching on preferredLabel, and only concepts with 'released' status. "
         "The 73 retained concepts serve as the EU occupational classification vocabulary "
         "against which Lanbide job titles were mapped.",
         "Used as a classification bridge between Lanbide job titles and standardised EU occupations."),

        ("9",  "skills_en.csv", "ESCO v1.2.1 — Skills Taxonomy",
         "13,960", "119",
         "The full ESCO skills taxonomy covers 13,960 skill concepts across all occupational domains. "
         "The hiddenLabels column has 13,807 nulls (98.9%) — this is structural: "
         "alternative search labels are only defined for a small minority of concepts. "
         "Filtered to the 14 target skill concepts relevant to this thesis "
         "(Python, SQL, Cloud, etc. and soft skills). "
         "The 119 retained records serve as the EU skill classification vocabulary.",
         "Used to normalise free-text skill mentions from Lanbide to ESCO concept URIs."),

        ("10", "digitalSkillsCollection_en.csv", "ESCO — Digital Skills Collection",
         "1,284", "1,284",
         "A curated subset of ESCO skills specifically designated as digital competences. "
         "Contains 1,284 released digital skill concepts. "
         "Only 12 altLabels nulls (0.9%) — structural, as not every concept has alternative labels. "
         "No rows removed. Retained in full as the EU digital competence reference taxonomy.",
         "Used to contextualise digital skill demand trends within the EU framework."),

        ("11", "digCompSkillsCollection_en.csv", "ESCO — DigComp Skills Collection",
         "25", "25",
         "Contains the 25 competence areas from the EU Digital Competence Framework (DigComp 2.2). "
         "5 nulls in skillType and reuseLevel — structural, as category-level concept nodes "
         "do not carry these properties. No rows removed. "
         "All 25 EU digital competence areas retained as classification reference.",
         "Used as the top-level EU digital skills framework for contextual interpretation."),

        ("12", "ONET_Occupations_crosswalk.csv", "ESCO–O*NET Occupation Crosswalk",
         "4,269", "4,260",
         "A mapping file linking ESCO occupation concepts to their O*NET SOC code equivalents. "
         "The raw file contains 7 metadata header rows before the actual data begins. "
         "These were skipped using skiprows=7 in the read_csv call. "
         "9 rows removed: 7 were metadata/header rows, 2 were blank separator rows. "
         "The resulting 4,260-row crosswalk maps European ESCO occupations to US O*NET codes.",
         "Used to enable cross-referencing between European ESCO classifications and O*NET skill profiles."),
    ]

    for num, fname, desc, before, after, explanation, engineering in file_info:
        with st.expander(f"File {num} — {fname}  |  {before} → {after} rows"):
            st.markdown(f"**{desc}**")
            col1, col2, col3 = st.columns(3)
            col1.metric("Rows before cleaning", before)
            col2.metric("Rows after cleaning", after)
            col3.metric("Rows dropped",
                        str(int(before.replace(",","")) - int(after.replace(",",""))))
            st.markdown("**What was done:**")
            st.markdown(explanation)
            st.caption(f"Feature engineering: {engineering}")

    # ── O*NET skill type breakdown ────────────────────────────
    if not onet.empty:
        st.subheader("O*NET Skills — Technical vs Soft/Non-Technical Breakdown")
        c1, c2 = st.columns(2)
        with c1:
            n = (onet["Skill Type"] == "Technical").sum()
            st.markdown(f"**Technical skills ({n} rows)**")
            st.write(sorted(onet[onet["Skill Type"]=="Technical"]["Element Name"].unique()))
        with c2:
            n = (onet["Skill Type"] == "Soft / Non-Technical").sum()
            st.markdown(f"**Soft / Non-Technical skills ({n} rows)**")
            st.write(sorted(onet[onet["Skill Type"]=="Soft / Non-Technical"]["Element Name"].unique()))
        t_mean = onet[onet["Skill Type"]=="Technical"]["Data Value"].mean()
        s_mean = onet[onet["Skill Type"]=="Soft / Non-Technical"]["Data Value"].mean()
        st.info(f"Mean O*NET Importance — Technical: **{t_mean:.2f} / 5.00**  |  "
                f"Soft / Non-Technical: **{s_mean:.2f} / 5.00**")

    # ── Downloads ─────────────────────────────────────────────
    st.subheader("Download Cleaned Datasets")
    c1, c2, c3 = st.columns(3)
    with c1:
        if not onet.empty:
            st.download_button("⬇ O*NET Skills (CSV)",
                onet[["Title","Role","Category","Element Name","Skill Type","Data Value"]].to_csv(index=False).encode(),
                "cleaned_onet_skills.csv")
    with c2:
        if not lanbide.empty:
            keep = ["title","datePosted","Year","is_IT"] + \
                   [c for c in lanbide.columns if c.startswith("tech_") or c.startswith("soft_")]
            st.download_button("⬇ Lanbide Classified (CSV)",
                lanbide[keep].to_csv(index=False).encode(),
                "cleaned_lanbide.csv")
    with c3:
        if "cedefop" in data and not data["cedefop"].empty:
            st.download_button("⬇ CEDEFOP (CSV)",
                data["cedefop"].to_csv(index=False).encode(),
                "cleaned_cedefop.csv")
