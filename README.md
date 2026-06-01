# Indian Tech Job Market Intelligence Platform (2025)

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-orange?style=for-the-badge&logo=render)](https://tech-jobs-india.onrender.com)

### 🌐 Live Deployment: [tech-jobs-india.onrender.com](https://tech-jobs-india.onrender.com)

Welcome to the **Indian Tech Job Market Intelligence Platform**, a comprehensive data engineering and machine learning platform built on standard 2025 Indian technology job openings data. 

The application utilizes a cleaned dataset of **3,535 job listings** to generate interactive market visualizations, execute raw SQL analysis, predict expected salary ranges using a trained Random Forest regressor, and perform dynamic resume gap analysis.

---

## 🚀 Key Features

1. **Interactive Glassmorphic UI**: High-impact modern dark-mode interface utilizing Outfit & Inter typography, frosted surfaces, neon highlights, and smooth animations.
2. **Interactive Market Dashboard**: Built with dynamic **ApexCharts** plotting city hiring densities, popular roles, salary spreads, and salary vs. experience ratios.
3. **AI Expected Salary Estimator**: Backed by a trained `RandomForestRegressor` pipeline using TF-IDF for skills vectorization and category-based encoders for roles & cities.
4. **Resume Gap Analyzer**: A rule-based parser that scans resume text for 60+ tech skills, matches them dynamically against top database requirements for your target role, and returns a matching score and a structured gap analysis.
5. **Personalized Job Recommendations**: Recommends actual job openings in the database matching your target role, ranked dynamically by the skill overlap between your profile and the job description.
6. **SQL Query Playground**: Run raw SQL statements directly on the active database using a frosted terminal emulator interface. Features 6 pre-configured analytical reports!

---

## 🛠️ Tech Stack
- **Backend Framework**: Flask (Python)
- **Database Engine**: Dual-support SQLAlchemy interfacing with **PostgreSQL** and local **SQLite** (automatic out-of-the-box fallback!)
- **Machine Learning**: Scikit-Learn (`RandomForestRegressor` pipeline utilizing `ColumnTransformer`, `OneHotEncoder`, `StandardScaler`, and `TfidfVectorizer`)
- **Data Engineering**: Pandas, OpenPyXL, NumPy
- **Frontend Core**: Vanilla HTML5, premium vanilla CSS3 (with responsive flexbox/grid layout and custom glassmorphism)
- **Charting & Visuals**: ApexCharts JS CDN, WordCloud, FontAwesome

---

## 📁 Reorganized Directory Layout
```
indian-tech-job-market-intelligence/
├── app.py                      # Flask backend controller & API endpoints
├── notebooks/                  # Interactive Jupyter Notebooks
│   ├── File Cleaning.ipynb     # Raw excel cleaning & title casing normalization
│   ├── EDA.ipynb               # Exploratory data plotting & matplotlib charts
│   └── Model Training.ipynb    # Random Forest regression model training
├── data/
│   ├── raw/                    # Original Excel spreadsheets
│   │   ├── indian-job-market-dataset-2025.xlsx
│   │   └── computer_engineering_jobs_only.xlsx
│   └── processed/              # Cleaned CSV & SQLite database outputs
│       ├── jobs_cleaned.csv    # Deduplicated 3,535 jobs record set
│       └── jobs.db             # Dynamic local SQLite database file
├── sql/
│   ├── schema.sql              # Database schema layout for jobs table
│   └── Query of the project.sql # Pre-configured analytical SQL queries
├── models/
│   └── salary_model.pkl        # Serialized Random Forest ML model pipeline
├── utils/
│   ├── db.py                   # Seamless PostgreSQL -> SQLite database connector
│   ├── skill_extractor.py      # Resume skill matching and gap analyzer
│   └── salary_predictor.py     # Model inference & statistical fallback processor
├── templates/                  # Jinja2 HTML layout views
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── skills.html
│   ├── salary.html
│   └── resume.html
├── static/                     # Assets & Static layouts
│   ├── css/
│   │   └── style.css           # Custom dark glassmorphism stylesheet
│   └── js/
│       └── script.js           # AJAX handlers & ApexCharts controller
├── requirements.txt            # Package dependencies list
├── .gitignore                  # Git tracking exclusion list
└── README.md                   # Platform documentation
```

---

## ⚙️ Setup and Installation

### 1. Clone the project and navigate to the directory
```bash
cd indian-tech-job-market-intelligence
```

### 2. Set up a virtual environment (Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install packages
```bash
pip install -r requirements.txt
```

### 4. Database Setup (Dual-Support)
- **Zero Configuration (Default)**: The application automatically boots up with a local **SQLite** database (`data/processed/jobs.db`). It automatically creates the table structure from `sql/schema.sql` and loads the cleaned `jobs_cleaned.csv` into it. No setup required!
- **PostgreSQL Connection**: If you have a PostgreSQL server running locally, create a database named `job_market_db` and ensure your username is `postgres` and password is `rohan@4321` (matches standard URI: `postgresql://postgres:rohan%404321@localhost:5432/job_market_db`). The system will automatically detect the connection, initialize schemas, and seed data dynamically on start!

### 5. Launch the Web Platform
```bash
python app.py
```
Open your browser and navigate to: `http://127.0.0.1:5000`

---

## 📈 Machine Learning Insights
The Regressor was trained on the **388 jobs** which had disclosed salaries in the dataset.
- **Model**: `RandomForestRegressor(n_estimators=150, max_depth=12)`
- **Cross-Validation MAE**: **2.87 LPA** (meaning salary predictions fall within ±2.87 Lakhs Per Annum of actual market value).
- **R² Score**: **0.5745** (explaining ~57.5% of variance in salary distributions using geographic hubs, role definitions, and skill tf-idfs).
