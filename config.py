# config.py
# Shared settings, lists, and dictionaries used across the dashboard.

import os

# ── Where are the dataset files? ────────────────────────────
# The raw datasets are in the data/raw folder inside the project.
# Run the dashboard from inside the thesis_project folder:
#   cd thesis_project
#   streamlit run dashboard_thesis.py

DATA_FOLDER = "data/raw"

FILE_ONET    = DATA_FOLDER + "/Skills.xlsx"
FILE_LANBIDE = DATA_FOLDER + "/20240414_Job_offers_from_Lanbide_Basque_Country_Public_Employment_Portal.csv"
FILE_CEDEFOP = DATA_FOLDER + "/cedefop-datatable.xlsx"
FILE_UNEMP   = DATA_FOLDER + "/xls0024822_0024823_i.xlsx"


# ── The 8 IT roles this thesis focuses on ───────────────────
TARGET_ROLES = [
    "Software Developer",
    "AI/ML Engineer",
    "Data Scientist",
    "Cybersecurity Specialist",
    "DevOps Engineer",
    "Data Engineer",
    "QA / Software Tester",
    "Cloud Computing Specialist",
]

# Maps each O*NET job title to one of the 8 roles above
ONET_ROLE_MAP = {
    "Software Developers":                          "Software Developer",
    "Web Developers":                               "Software Developer",
    "Computer Programmers":                         "Software Developer",
    "Computer Systems Engineers/Architects":        "Software Developer",
    "Computer and Information Research Scientists": "AI/ML Engineer",
    "Computer Systems Analysts":                    "Data Scientist",
    "Business Intelligence Analysts":               "Data Scientist",
    "Information Security Analysts":                "Cybersecurity Specialist",
    "Information Security Engineers":               "Cybersecurity Specialist",
    "Computer Network Architects":                  "DevOps Engineer",
    "Database Administrators":                      "Data Engineer",
    "Database Architects":                          "Data Engineer",
    "Data Warehousing Specialists":                 "Data Engineer",
    "Software Quality Assurance Analysts and Testers": "QA / Software Tester",
    "Network and Computer Systems Administrators":  "Cloud Computing Specialist",
    "Computer Network Support Specialists":         "Cloud Computing Specialist",
}

# Whether each role is growing fast, changing, or slowing down
ROLE_CATEGORY = {
    "Software Developer":        "Transforming",
    "AI/ML Engineer":            "AI-Complementary",
    "Data Scientist":            "AI-Complementary",
    "Cybersecurity Specialist":  "AI-Complementary",
    "DevOps Engineer":           "AI-Complementary",
    "Data Engineer":             "AI-Complementary",
    "QA / Software Tester":      "Routine / Declining",
    "Cloud Computing Specialist":"AI-Complementary",
}

# Chart colours — one colour per role, used consistently everywhere
ROLE_COLOURS = {
    "Software Developer":        "#4C8BF5",
    "AI/ML Engineer":            "#E91E63",
    "Data Scientist":            "#9C27B0",
    "Cybersecurity Specialist":  "#F44336",
    "DevOps Engineer":           "#FF9800",
    "Data Engineer":             "#009688",
    "QA / Software Tester":      "#795548",
    "Cloud Computing Specialist":"#03A9F4",
}

# Labels each O*NET skill as Technical or Soft / Non-Technical
SKILL_TYPE = {
    "Reading Comprehension":              "Soft / Non-Technical",
    "Active Listening":                   "Soft / Non-Technical",
    "Writing":                            "Soft / Non-Technical",
    "Speaking":                           "Soft / Non-Technical",
    "Critical Thinking":                  "Soft / Non-Technical",
    "Active Learning":                    "Soft / Non-Technical",
    "Learning Strategies":                "Soft / Non-Technical",
    "Monitoring":                         "Soft / Non-Technical",
    "Social Perceptiveness":              "Soft / Non-Technical",
    "Coordination":                       "Soft / Non-Technical",
    "Persuasion":                         "Soft / Non-Technical",
    "Negotiation":                        "Soft / Non-Technical",
    "Instructing":                        "Soft / Non-Technical",
    "Service Orientation":                "Soft / Non-Technical",
    "Complex Problem Solving":            "Soft / Non-Technical",
    "Management of Financial Resources":  "Soft / Non-Technical",
    "Management of Material Resources":   "Soft / Non-Technical",
    "Management of Personnel Resources":  "Soft / Non-Technical",
    "Time Management":                    "Soft / Non-Technical",
    "Judgment and Decision Making":       "Soft / Non-Technical",
    "Mathematics":                        "Technical",
    "Science":                            "Technical",
    "Operations Analysis":                "Technical",
    "Technology Design":                  "Technical",
    "Equipment Selection":                "Technical",
    "Installation":                       "Technical",
    "Programming":                        "Technical",
    "Operation and Control":              "Technical",
    "Operations Monitoring":              "Technical",
    "Troubleshooting":                    "Technical",
    "Repairing":                          "Technical",
    "Quality Control Analysis":           "Technical",
    "Equipment Maintenance":              "Technical",
    "Systems Analysis":                   "Technical",
    "Systems Evaluation":                 "Technical",
}

# Keywords to detect technical skills in Lanbide job descriptions
# Spanish and English because Lanbide postings are in Spanish
TECH_KEYWORDS = {
    "Python":                ["python"],
    "SQL / Databases":       ["sql", "mysql", "postgresql", "bbdd", "oracle"],
    "Machine Learning / AI": ["machine learning", "inteligencia artificial", "big data"],
    "Cloud (AWS/Azure/GCP)": ["cloud", "aws", "azure", "gcp"],
    "Cybersecurity":         ["ciberseguridad", "csirt", "seguridad informatica"],
    "DevOps / Docker":       ["devops", "docker", "kubernetes", "jenkins"],
    "Data Engineering":      ["etl", "spark", "airflow", "data engineer"],
}

# Keywords to detect soft skills in Lanbide job descriptions
SOFT_KEYWORDS = {
    "Teamwork":            ["trabajo en equipo", "teamwork", "equipo", "colabora"],
    "Communication":       ["comunicaci", "communication", "presentacion", "redaccion"],
    "Critical Thinking":   ["pensamiento critico", "critical thinking", "análisis"],
    "Adaptability":        ["adaptab", "flexible", "flexibilidad", "proactiv"],
    "Leadership":          ["liderazgo", "leadership", "coordinacion de equipo"],
    "Client-Facing":       ["atencion al cliente", "customer", "cliente", "stakeholder"],
    "Complex Problem Solving": ["resolución de problemas", "problem solving", "pensamiento analitico"],
}

# ── Demand index growth rates ────────────────────────────────
# Format: (rate before 2023 %, rate from 2023 onwards %)
# Sourced from WEF 2025, PwC 2025, Frank et al. 2019

ROLE_GROWTH = {
    "Software Developer":        (3.0,   1.5),
    "AI/ML Engineer":            (12.0, 22.0),
    "Data Scientist":            (10.0, 14.0),
    "Cybersecurity Specialist":  (8.0,  11.0),
    "DevOps Engineer":           (7.0,   9.0),
    "Data Engineer":             (9.0,  13.0),
    "QA / Software Tester":      (2.0,  -1.5),
    "Cloud Computing Specialist":(9.0,  12.0),
}

# Sourced from WEF 2025, Coursera 2024, CEDEFOP
TECH_GROWTH = {
    "Python":                (6.0,  10.0),
    "SQL / Databases":       (2.0,   1.5),
    "Machine Learning / AI": (14.0, 24.0),
    "Cloud (AWS/Azure/GCP)": (10.0, 14.0),
    "Cybersecurity":         (8.0,  12.0),
    "DevOps / Docker":       (7.0,   9.5),
    "Data Engineering":      (9.0,  15.0),
}

# Sourced from WEF 2025, LinkedIn Workplace Learning 2024, Cramarenco et al. 2023
SOFT_GROWTH = {
    "Critical Thinking":        (3.5, 6.0),
    "Complex Problem Solving":  (3.5, 6.5),
    "Teamwork":                 (3.0, 4.5),
    "Communication":            (2.5, 4.0),
    "Adaptability":             (4.0, 7.5),
    "Leadership":               (2.5, 3.5),
    "Client-Facing":            (2.0, 3.0),
}
