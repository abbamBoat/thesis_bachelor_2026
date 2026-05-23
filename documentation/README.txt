README — Thesis Project Folder

FOLDER STRUCTURE


thesis_bachelor_2026(myrepo)/
│
├── dashboard_app.py              ← The main dashboard file. Run this.
│
├── data/
│   ├── raw/                      ← Original datasets, untouched
│   │   ├── Skills.xlsx
│   │   ├── Technology_Skills.xlsx
│   │   ├── Occupation_Data.xlsx
│   │   ├── cedefop-datatable.xlsx
│   │   ├── xls0024822_0024823_i.xlsx
│   │   ├── 20240414_Job_offers_from_Lanbide...csv
│   │   ├── skills_en.csv
│   │   ├── occupations_en.csv
│   │   └── digitalSkillsCollection_en.csv
│   │
│   └── cleaned/                  ← Cleaned and processed files
│       ├── dataset_record_counts.csv       ← Before/after row counts
│       ├── cleaned_onet_skills.csv         ← O*NET after cleaning
│       ├── cleaned_lanbide.csv             ← Lanbide with skill flags
│       ├── cleaned_cedefop.csv             ← CEDEFOP after cleaning
│       ├── cleaned_basque_unemployment.csv ← Basque districts
│       ├── occupation_demand_index.csv     ← Demand index 2018-2025
│       ├── technical_skill_index.csv       ← Tech skills index
│       ├── soft_skill_index.csv            ← Soft skills index
│       ├── occupation_forecast.csv         ← Forecast 2026-2029
│       ├── technical_skill_forecast.csv    ← Tech skill forecast
│       └── soft_skill_forecast.csv         ← Soft skill forecast
│
└── documentation/
    ├── README.txt                          ← This file
    ├── data_cleaning_process.txt           ← What was done to clean each dataset
    └── models_and_methods.txt             ← What models were used and why


HOW TO RUN THE DASHBOARD, yay


Step 1 — Install Python libraries (do this once only)
  Open terminal and run:

    pip install streamlit plotly pandas openpyxl statsmodels

  
Step 2 — Run the dashboard (DONT FORGET please aba)

    streamlit run dashboard_app.py

  This opens a browser window automatically at http://localhost:8501


WHAT EACH CLEANED FILE CONTAINS
        ---

dataset_record_counts.csv
  Summary of how many rows each dataset had before and after cleaning.

cleaned_onet_skills.csv
  560 rows. Columns: Title, Role, Category, Element Name, Skill Type, Data Value.
  Only IT roles kept. Only Importance scores kept. Skill Type = Technical or Soft.

cleaned_lanbide.csv
  1,509 rows. Columns include: title, datePosted, Year, is_IT,
  plus 10 technical skill columns (tech_python, tech_sql_databases, etc.)
  and 10 soft skill columns (soft_teamwork, soft_communication, etc.).
  Each skill column is 0 (not mentioned) or 1 (mentioned in that posting).

cleaned_cedefop.csv
  11,136 rows. Columns: Dataset, Indicator, Countries, Year, Flags, Value.
  EU labour market indicators, 37 countries, 2010-2024.

cleaned_basque_unemployment.csv
  22 rows. Columns: District, 2020, 2021, 2022, 2023, 2024.
  Unemployment % per Basque district per year.

occupation_demand_index.csv
  Demand index for each of the 8 IT roles, 2018-2025 (2018 = 100).
  Includes a "Growth 2018 to 2025 (%)" column.

technical_skill_index.csv
  Demand index for 10 technical skills, 2018-2025.

soft_skill_index.csv
  Demand index for 10 soft / non-technical skills, 2018-2025.

occupation_forecast.csv
  Random Forest & Decision Tree forecast for each role, 2026-2027.

technical_skill_forecast.csv
  RF & DT forecast for each technical skill, 2026-2027.

soft_skill_forecast.csv
  RF & DT forecast for each soft skill, 2026-2027.

