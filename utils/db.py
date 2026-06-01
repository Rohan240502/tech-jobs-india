import os
import pandas as pd
from sqlalchemy import create_engine, text

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(WORKSPACE_DIR, "data", "processed", "jobs_cleaned.csv")
SQL_SCHEMA_PATH = os.path.join(WORKSPACE_DIR, "sql", "schema.sql")
SQLITE_PATH = os.path.join(WORKSPACE_DIR, "data", "processed", "jobs.db")

# PostgreSQL connection configuration
db_url = os.environ.get("DATABASE_URL")
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    POSTGRES_URI = db_url
else:
    POSTGRES_URI = "postgresql://postgres:rohan%404321@localhost:5432/job_market_db"

def get_db_engine():
    """
    Attempts to connect to PostgreSQL. If that fails, falls back gracefully to local SQLite.
    """
    # 1. Try PostgreSQL
    try:
        engine = create_engine(POSTGRES_URI, connect_args={"connect_timeout": 3})
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[DB] Successfully connected to PostgreSQL database: job_market_db")
        return engine, "postgresql"
    except Exception as e:
        print(f"[DB] PostgreSQL connection failed: {e}. Falling back to SQLite...")
        
    # 2. Fallback to SQLite
    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
    engine = create_engine(f"sqlite:///{SQLITE_PATH}")
    print(f"[DB] Connected to SQLite database at: {SQLITE_PATH}")
    return engine, "sqlite"

def init_db():
    """
    Initializes the database schema and loads clean CSV data if the table is empty.
    """
    engine, db_type = get_db_engine()
    
    # Check if table exists and has data
    table_exists = False
    table_has_data = False
    
    try:
        with engine.connect() as conn:
            if db_type == "postgresql":
                res = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'jobs')"))
                table_exists = res.scalar()
            else:  # sqlite
                res = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'"))
                table_exists = res.fetchone() is not None
                
            if table_exists:
                count_res = conn.execute(text("SELECT COUNT(*) FROM jobs"))
                table_has_data = count_res.scalar() > 0
    except Exception as e:
        print(f"[DB] Error checking table existence: {e}")
        table_exists = False

    if table_exists and table_has_data:
        print(f"[DB] Database already initialized with jobs table.")
        return
        
    print("[DB] Initializing database schema...")
    
    # 1. Read schema SQL
    if os.path.exists(SQL_SCHEMA_PATH):
        with open(SQL_SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()
    else:
        # Fallback schema string
        schema_sql = """
        DROP TABLE IF EXISTS jobs;
        CREATE TABLE jobs (
            "title" VARCHAR(255),
            "jobId" BIGINT PRIMARY KEY,
            "currency" VARCHAR(50),
            "jobUploaded" VARCHAR(255),
            "companyName" VARCHAR(255),
            "tagsAndSkills" TEXT,
            "experience" VARCHAR(255),
            "salary" VARCHAR(255),
            "location" VARCHAR(555),
            "companyId" BIGINT,
            "jobDescription" TEXT,
            "minimumSalary" DOUBLE PRECISION,
            "maximumSalary" DOUBLE PRECISION,
            "minimumExperience" DOUBLE PRECISION,
            "maximumExperience" DOUBLE PRECISION,
            "avg_salary" DOUBLE PRECISION,
            "jobUploaded_cleaned" DOUBLE PRECISION
        );
        """
        
    # Split queries by semicolon to execute one by one in SQLAlchemy
    queries = [q.strip() for q in schema_sql.split(";") if q.strip()]
    
    with engine.begin() as conn:
        for q in queries:
            conn.execute(text(q))
            
    print(f"[DB] Schema initialized successfully.")
    
    # 2. Seed database
    if os.path.exists(CSV_PATH):
        print(f"[DB] Seeding database from cleaned CSV: {CSV_PATH}...")
        try:
            df = pd.read_csv(CSV_PATH)
            # Seed to DB using pandas
            df.to_sql("jobs", engine, if_exists="append", index=False)
            print(f"[DB] Successfully loaded {len(df)} records into the 'jobs' table.")
        except Exception as e:
            print(f"[DB] Seeding failed: {e}")
    else:
        print(f"[DB] ERROR: Cleaned CSV not found at {CSV_PATH}. Seeding skipped.")

def execute_query(query_str):
    """
    Executes a query and returns the column headers and result rows as a tuple.
    """
    engine, _ = get_db_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query_str))
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            return columns, rows
    except Exception as e:
        print(f"[DB] Query execution error: {e}")
        return [], []

if __name__ == "__main__":
    init_db()
