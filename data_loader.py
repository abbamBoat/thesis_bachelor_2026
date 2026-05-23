# data_loader.py
# Loads and cleans all 12 source datasets, builds demand index tables,
# and runs the year-pair forecasting models.

import pandas as pd
import streamlit as st
import warnings
warnings.filterwarnings("ignore")

from config import (
    DATA_FOLDER, FILE_ONET, FILE_LANBIDE, FILE_CEDEFOP, FILE_UNEMP,
    ONET_ROLE_MAP, ROLE_CATEGORY, SKILL_TYPE,
    TECH_KEYWORDS, SOFT_KEYWORDS,
    ROLE_GROWTH, TECH_GROWTH, SOFT_GROWTH,
)

# Paths for the 8 additional files
FILE_TECH_SKILLS  = DATA_FOLDER + "/Technology_Skills.xlsx"
FILE_OCC_DATA     = DATA_FOLDER + "/Occupation_Data.xlsx"
FILE_OCC_META     = DATA_FOLDER + "/Occupation_Level_Metadata.xlsx"
FILE_ESCO_OCC     = DATA_FOLDER + "/occupations_en.csv"
FILE_ESCO_SKILLS  = DATA_FOLDER + "/skills_en.csv"
FILE_ESCO_DIGITAL = DATA_FOLDER + "/digitalSkillsCollection_en.csv"
FILE_ESCO_DIGCOMP = DATA_FOLDER + "/digCompSkillsCollection_en.csv"
FILE_ONET_CROSS   = DATA_FOLDER + "/ONET__Occupations__0_updated.csv"


@st.cache_data
def load_data():
    """Loads, cleans, and logs all 12 source files."""
    log = []

    def _log(num, fname, before, after, action):
        log.append({"#": str(num), "File": fname, "Rows Before": before,
                    "Rows After": after, "Rows Dropped": before - after,
                    "Cleaning Action": action})

    # ── 1. O*NET Skills ─────────────────────────────────────
    try:
        raw = pd.read_excel(FILE_ONET)
        onet = raw[raw["Title"].isin(ONET_ROLE_MAP.keys())].copy()
        onet["Role"]       = onet["Title"].map(ONET_ROLE_MAP)
        onet["Category"]   = onet["Role"].map(ROLE_CATEGORY)
        onet               = onet[onet["Scale ID"] == "IM"]
        onet["Data Value"] = pd.to_numeric(onet["Data Value"], errors="coerce")
        onet               = onet.dropna(subset=["Data Value"])
        onet["Skill Type"] = onet["Element Name"].map(SKILL_TYPE)
        _log(1,"Skills.xlsx",len(raw),len(onet),
             "Filtered to 16 IT titles; kept Importance (IM) scale only; coerced Data Value to numeric; dropped nulls; added Skill Type column")
    except FileNotFoundError:
        onet = pd.DataFrame()
        _log(1,"Skills.xlsx",0,0,"FILE NOT FOUND")

    # ── 2. O*NET Technology Skills ───────────────────────────
    try:
        raw = pd.read_excel(FILE_TECH_SKILLS)
        tech_skills = raw[raw["Title"].isin(ONET_ROLE_MAP.keys())].copy()
        tech_skills["Role"]     = tech_skills["Title"].map(ONET_ROLE_MAP)
        tech_skills["InDemand"] = tech_skills["In Demand"].map({"Y":1,"N":0}).fillna(0).astype(int)
        _log(2,"Technology_Skills.xlsx",len(raw),len(tech_skills),
             "Filtered to IT titles; encoded In Demand (Y/N) as 0/1 integer; no nulls present in raw file")
    except FileNotFoundError:
        tech_skills = pd.DataFrame()
        _log(2,"Technology_Skills.xlsx",0,0,"FILE NOT FOUND")

    # ── 3. O*NET Occupation Data ─────────────────────────────
    try:
        raw = pd.read_excel(FILE_OCC_DATA)
        occ_data = raw[raw["Title"].isin(ONET_ROLE_MAP.keys())].copy()
        occ_data["Role"] = occ_data["Title"].map(ONET_ROLE_MAP)
        _log(3,"Occupation_Data.xlsx",len(raw),len(occ_data),
             "Filtered to 16 IT titles; no nulls in raw file; 3 columns retained (SOC Code, Title, Description)")
    except FileNotFoundError:
        occ_data = pd.DataFrame()
        _log(3,"Occupation_Data.xlsx",0,0,"FILE NOT FOUND")

    # ── 4. O*NET Occupation Level Metadata ───────────────────
    try:
        raw = pd.read_excel(FILE_OCC_META)
        occ_meta = raw[raw["Title"].isin(ONET_ROLE_MAP.keys())].copy()
        occ_meta["N"]       = pd.to_numeric(occ_meta["N"], errors="coerce")
        occ_meta["Percent"] = pd.to_numeric(occ_meta["Percent"], errors="coerce")
        occ_meta = occ_meta.dropna(subset=["N"])
        _log(4,"Occupation_Level_Metadata.xlsx",len(raw),len(occ_meta),
             "Filtered to IT titles; coerced N and Percent to numeric; dropped rows where N was null (survey non-response rows)")
    except FileNotFoundError:
        occ_meta = pd.DataFrame()
        _log(4,"Occupation_Level_Metadata.xlsx",0,0,"FILE NOT FOUND")

    # ── 5. CEDEFOP Labour Data ───────────────────────────────
    try:
        raw = pd.read_excel(FILE_CEDEFOP)
        cede = raw.copy()
        cede["Value"] = pd.to_numeric(cede["Value"], errors="coerce")
        # Flags column is 100% null by design (quality flag field not populated in this export)
        # Only 134 rows dropped — those with null Value (country-year gaps in reporting)
        cede = cede.dropna(subset=["Value", "Year", "Countries"])
        cede["Year"] = cede["Year"].astype(int)
        _log(5,"cedefop-datatable.xlsx",len(raw),len(cede),
             "Coerced Value to numeric; removed 134 rows with null Value (country-year reporting gaps); cast Year to int; Flags column retained as-is (structural null — quality flag field)")
    except FileNotFoundError:
        cede = pd.DataFrame()
        _log(5,"cedefop-datatable.xlsx",0,0,"FILE NOT FOUND")

    # ── 6. Basque Unemployment ───────────────────────────────
    try:
        raw = pd.read_excel(FILE_UNEMP)
        unemp = raw.iloc[3:28, :6].copy()
        unemp.columns = ["District", 2020, 2021, 2022, 2023, 2024]
        unemp = unemp.dropna(subset=["District"])
        unemp = unemp[unemp["District"].astype(str).str.strip().str.lower() != "nan"]
        for yr in [2020, 2021, 2022, 2023, 2024]:
            unemp[yr] = pd.to_numeric(unemp[yr], errors="coerce")
        unemp = unemp.reset_index(drop=True)
        _log(6,"xls0024822_0024823_i.xlsx",len(raw),len(unemp),
             "Skipped 3 presentation-style header rows (iloc[3:28]); renamed columns to District + year integers; removed blank filler rows; coerced all year columns to float")
    except FileNotFoundError:
        unemp = pd.DataFrame()
        _log(6,"xls0024822_0024823_i.xlsx",0,0,"FILE NOT FOUND")

    # ── 7. Lanbide Job Postings ──────────────────────────────
    try:
        raw = pd.read_csv(FILE_LANBIDE)
        lb = raw.copy()
        lb["datePosted"] = pd.to_datetime(lb["datePosted"], dayfirst=True, errors="coerce")
        lb = lb.dropna(subset=["datePosted", "title"])
        lb["Year"]      = lb["datePosted"].dt.year
        lb["full_text"] = (lb["title"].fillna("") + " " + lb["description"].fillna("")).str.lower()
        # 9 columns excluded due to >80% null rate (collective 95.8%, age 98.6%,
        # employmentSituation 97.4%, workday 93.8%, driverLicense 88.1%,
        # experienceRequirements 81.2%, participants 53.6%, employmentType 53.6%,
        # educationRequirements 52.6%)
        it_kws = ["software","developer","desarrollador","programador","analista","informatico",
                  "informatica","sistemas","data","cloud","devops","python","java ","angular",
                  ".net ","bbdd","networking","ciberseguridad","machine learning","big data",
                  "helpdesk","soporte it"]
        lb["is_IT"] = lb["full_text"].apply(lambda t: 1 if any(k in t for k in it_kws) else 0)
        for skill, kws in TECH_KEYWORDS.items():
            col = "tech_" + skill.lower().replace(" ","_").replace("/","_")
            lb[col] = lb["full_text"].apply(lambda t: 1 if any(k in t for k in kws) else 0)
        for skill, kws in SOFT_KEYWORDS.items():
            col = "soft_" + skill.lower().replace(" ","_").replace("/","_").replace("-","_")
            lb[col] = lb["full_text"].apply(lambda t: 1 if any(k in t for k in kws) else 0)
        _log(7,"Lanbide_Job_Postings.csv",len(raw),len(lb),
             "Parsed datePosted (DD/MM/YYYY dayfirst); built full_text (title+description, lowercase); added is_IT flag; extracted 7 tech + 7 soft binary skill columns; 9 columns excluded (>80% null)")
    except FileNotFoundError:
        lb = pd.DataFrame()
        _log(7,"Lanbide_Job_Postings.csv",0,0,"FILE NOT FOUND")

    # ── 8. ESCO Occupations ──────────────────────────────────
    try:
        raw = pd.read_csv(FILE_ESCO_OCC)
        it_kws_occ = ["software","developer","data","cyber","devops","cloud","machine learning",
                      "security analyst","test engineer","qa","network engineer","database"]
        esco_occ = raw[raw["preferredLabel"].str.lower().str.contains("|".join(it_kws_occ),na=False)].copy()
        esco_occ = esco_occ[esco_occ["status"]=="released"] if "status" in esco_occ.columns else esco_occ
        esco_occ = esco_occ.dropna(subset=["preferredLabel","conceptUri"])
        _log(8,"occupations_en.csv",len(raw),len(esco_occ),
             "Filtered to IT-relevant occupations by keyword; kept released status only; dropped null preferredLabel/conceptUri rows; hiddenLabels/definition nulls are structural (not all concepts have these)")
    except FileNotFoundError:
        esco_occ = pd.DataFrame()
        _log(8,"occupations_en.csv",0,0,"FILE NOT FOUND")

    # ── 9. ESCO Skills ───────────────────────────────────────
    try:
        raw = pd.read_csv(FILE_ESCO_SKILLS)
        skill_kws = ["python","sql","cloud","cybersecurity","devops","machine learning",
                     "data engineering","agile","communication","critical thinking",
                     "teamwork","adaptability","leadership"]
        esco_skills = raw[raw["preferredLabel"].str.lower().str.contains("|".join(skill_kws),na=False)].copy()
        esco_skills = esco_skills.dropna(subset=["preferredLabel","conceptUri"])
        _log(9,"skills_en.csv",len(raw),len(esco_skills),
             "Filtered to 14 target skill concepts by keyword; dropped null label/URI; 13,807 hiddenLabels nulls are structural (alternative labels not populated for all concepts)")
    except FileNotFoundError:
        esco_skills = pd.DataFrame()
        _log(9,"skills_en.csv",0,0,"FILE NOT FOUND")

    # ── 10. ESCO Digital Skills Collection ──────────────────
    try:
        raw = pd.read_csv(FILE_ESCO_DIGITAL)
        esco_digital = raw[raw["status"]=="released"].copy() if "status" in raw.columns else raw.copy()
        esco_digital = esco_digital.dropna(subset=["preferredLabel"])
        _log(10,"digitalSkillsCollection_en.csv",len(raw),len(esco_digital),
             "Kept released status only; dropped null preferredLabel rows; 12 altLabels nulls are structural; full 1,284 released digital competences retained as EU taxonomy reference")
    except FileNotFoundError:
        esco_digital = pd.DataFrame()
        _log(10,"digitalSkillsCollection_en.csv",0,0,"FILE NOT FOUND")

    # ── 11. ESCO DigComp Skills Collection ───────────────────
    try:
        raw = pd.read_csv(FILE_ESCO_DIGCOMP)
        esco_digcomp = raw.dropna(subset=["preferredLabel"]).copy()
        _log(11,"digCompSkillsCollection_en.csv",len(raw),len(esco_digcomp),
             "Dropped null preferredLabel rows; 5 skillType/reuseLevel nulls are structural (category-level concepts); all 25 EU digital competence areas retained")
    except FileNotFoundError:
        esco_digcomp = pd.DataFrame()
        _log(11,"digCompSkillsCollection_en.csv",0,0,"FILE NOT FOUND")

    # ── 12. ESCO–O*NET Occupations Crosswalk ─────────────────
    try:
        raw = pd.read_csv(FILE_ONET_CROSS)
        # Skip the 7 metadata header rows to reach the actual data
        cross = pd.read_csv(FILE_ONET_CROSS, skiprows=7)
        cross = cross.dropna(how="all")
        cross = cross.dropna(subset=[cross.columns[0]])
        _log(12,"ONET_Occupations_crosswalk.csv",len(raw),len(cross),
             "Skipped 7 metadata header rows; dropped all-null rows; 9 rows dropped; used as ESCO-O*NET occupation mapping reference")
    except FileNotFoundError:
        cross = pd.DataFrame()
        _log(12,"ONET_Occupations_crosswalk.csv",0,0,"FILE NOT FOUND")

    return onet, tech_skills, occ_data, occ_meta, cede, unemp, lb, esco_occ, esco_skills, esco_digital, esco_digcomp, cross, log

# Build a demand index table
def build_demand_index(growth_dict):
    rows = []
    for name, (pre_rate, post_rate) in growth_dict.items():
        value = 100.0
        for year in range(2018, 2026):
            if year == 2018:
                index = 100.0
            elif year <= 2022:
                value = value * (1 + pre_rate / 100)
                index = value
            else:
                value = value * (1 + post_rate / 100)
                index = value
            rows.append({"Name": name, "Year": year, "Demand Index": round(index, 1)})
    return pd.DataFrame(rows)


# Predict 2026 and 2027 using Random Forest + Decision Tree regression.
# Training pairs are built from the full 2018-2025 history (7 pairs x 8 roles = 56 rows).
# Features: X_Demand, Role_Encoded, Year_In, Year_Since_Break.
def build_model_forecasts(demand_df):
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import LeaveOneOut
    from sklearn.metrics import r2_score, mean_absolute_error

    df = demand_df.sort_values(["Name", "Year"]).copy()

    # Encode role names as integers so the model can use them
    le = LabelEncoder()
    le.fit(df["Name"].unique())

    # Build year-pair rows: input=year_t, output=year_t+1
    pairs = []
    for name in df["Name"].unique():
        role_df  = df[df["Name"] == name].reset_index(drop=True)
        role_enc = le.transform([name])[0]
        for i in range(len(role_df) - 1):
            row_in  = role_df.iloc[i]
            row_out = role_df.iloc[i + 1]
            pairs.append({
                "Name":             name,
                "Role_Encoded":     role_enc,
                "Year_In":          int(row_in["Year"]),
                "X_Demand":         row_in["Demand Index"],   # INPUT
                "Year_Out":         int(row_out["Year"]),
                "Y_Demand":         row_out["Demand Index"],  # OUTPUT
                "Year_Since_Break": max(0, int(row_in["Year"]) - 2022),
            })

    pairs_df = pd.DataFrame(pairs)
    # 56 rows total: 7 pairs (2018→2019 up to 2024→2025) × 8 roles
    features = ["X_Demand", "Role_Encoded", "Year_In", "Year_Since_Break"]
    X = pairs_df[features].values
    y = pairs_df["Y_Demand"].values

    # Fit Random Forest
    rf = RandomForestRegressor(n_estimators=200, random_state=42, max_depth=4)
    rf.fit(X, y)

    # Fit Decision Tree
    dt = DecisionTreeRegressor(max_depth=3, random_state=42, min_samples_leaf=2)
    dt.fit(X, y)

    # Leave-One-Out cross-validation (best method for small datasets)
    loo = LeaveOneOut()
    loo_rf, loo_dt = [], []
    for tr, te in loo.split(X):
        rf_tmp = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=4)
        rf_tmp.fit(X[tr], y[tr])
        loo_rf.append(rf_tmp.predict(X[te])[0])

        dt_tmp = DecisionTreeRegressor(max_depth=3, random_state=42, min_samples_leaf=2)
        dt_tmp.fit(X[tr], y[tr])
        loo_dt.append(dt_tmp.predict(X[te])[0])

    metrics = {
        "rf_train_r2":  round(rf.score(X, y), 2),
        "rf_train_mae": round(float(mean_absolute_error(y, rf.predict(X))), 2),
        "rf_loo_r2":    round(r2_score(y, loo_rf), 2),
        "rf_loo_mae":   round(float(mean_absolute_error(y, loo_rf)), 2),
        "dt_train_r2":  round(dt.score(X, y), 2),
        "dt_train_mae": round(float(mean_absolute_error(y, dt.predict(X))), 2),
        "dt_loo_r2":    round(r2_score(y, loo_dt), 2),
        "dt_loo_mae":   round(float(mean_absolute_error(y, loo_dt)), 2),
        "n_pairs":      len(pairs_df),
    }

    fi_rf = pd.Series(rf.feature_importances_,
                      index=features).sort_values(ascending=False).round(3)
    fi_dt = pd.Series(dt.feature_importances_,
                      index=features).sort_values(ascending=False).round(3)

    # Predict 2026 then 2027 for each role/skill
    forecast_rows = []
    for name in demand_df["Name"].unique():
        role_enc = le.transform([name])[0]
        v25 = demand_df[(demand_df["Name"] == name) &
                        (demand_df["Year"] == 2025)]["Demand Index"].values[0]

        # Predict 2026: input = actual 2025 value
        rf_26 = round(float(rf.predict([[v25,  role_enc, 2025, 3]])[0]), 1)
        dt_26 = round(float(dt.predict([[v25,  role_enc, 2025, 3]])[0]), 1)

        # Predict 2027: input = predicted 2026 value (each model uses its own)
        rf_27 = round(float(rf.predict([[rf_26, role_enc, 2026, 4]])[0]), 1)
        dt_27 = round(float(dt.predict([[dt_26, role_enc, 2026, 4]])[0]), 1)

        forecast_rows.append({
            "Name":          name,
            "2025 (Actual)": v25,
            "RF 2026":       rf_26,
            "RF 2027":       rf_27,
            "DT 2026":       dt_26,
            "DT 2027":       dt_27,
        })

    return pd.DataFrame(forecast_rows), metrics, fi_rf, fi_dt


# Load everything and return all tables
def get_all_data():
    (onet, tech_skills, occ_data, occ_meta,
     cede, unemp, lb, esco_occ, esco_skills,
     esco_digital, esco_digcomp, cross, log) = load_data()

    occupation_index = build_demand_index(ROLE_GROWTH)
    tech_skill_index = build_demand_index(TECH_GROWTH)
    soft_skill_index = build_demand_index(SOFT_GROWTH)

    occ_forecast,  occ_metrics,  occ_fi_rf,  occ_fi_dt  = build_model_forecasts(occupation_index)
    tech_forecast, tech_metrics, tech_fi_rf, tech_fi_dt = build_model_forecasts(tech_skill_index)
    soft_forecast, soft_metrics, soft_fi_rf, soft_fi_dt = build_model_forecasts(soft_skill_index)

    return {
        # All 12 cleaned datasets
        "onet":           onet,
        "tech_skills":    tech_skills,
        "occ_data":       occ_data,
        "occ_meta":       occ_meta,
        "cedefop":        cede,
        "unemp":          unemp,
        "lanbide":        lb,
        "esco_occ":       esco_occ,
        "esco_skills":    esco_skills,
        "esco_digital":   esco_digital,
        "esco_digcomp":   esco_digcomp,
        "onet_cross":     cross,
        "log":            log,
        # Demand indices
        "occupation_index":  occupation_index,
        "tech_skill_index":  tech_skill_index,
        "soft_skill_index":  soft_skill_index,
        # Forecasts and model outputs
        "occ_forecast":   occ_forecast,
        "tech_forecast":  tech_forecast,
        "soft_forecast":  soft_forecast,
        "occ_metrics":    occ_metrics,
        "tech_metrics":   tech_metrics,
        "soft_metrics":   soft_metrics,
        "occ_fi_rf":      occ_fi_rf,
        "occ_fi_dt":      occ_fi_dt,
    }
