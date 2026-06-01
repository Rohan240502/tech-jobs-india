import os
import pickle
import pandas as pd
import numpy as np
from utils.db import execute_query

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(WORKSPACE_DIR, "models", "salary_model.pkl")

# Load model pipeline on import
model_pipeline = None
if os.path.exists(MODEL_PATH):
    try:
        with open(MODEL_PATH, "rb") as f:
            model_pipeline = pickle.load(f)
        print("[ML] Successfully loaded salary prediction model.")
    except Exception as e:
        print(f"[ML] Error loading pickle model: {e}")
else:
    print(f"[ML] WARNING: Model pickle file not found at {MODEL_PATH}.")

def predict_salary(title, location, minimum_experience, maximum_experience, skills):
    """
    Predicts the salary in LPA (Lakhs Per Annum) based on input features.
    If the model pipeline is not loaded, uses a database fallback.
    """
    global model_pipeline
    
    # Clean and validate input values
    title = str(title).strip().title()
    location = str(location).strip()
    skills_str = ", ".join(skills) if isinstance(skills, list) else str(skills)
    
    try:
        minimum_experience = float(minimum_experience)
    except:
        minimum_experience = 0.0
        
    try:
        maximum_experience = float(maximum_experience)
    except:
        maximum_experience = minimum_experience + 2.0

    # 1. Use ML Model if loaded
    if model_pipeline is not None:
        try:
            # Create a 1-row DataFrame matching the model's training columns
            input_df = pd.DataFrame([{
                "title": title,
                "location": location,
                "minimumExperience": minimum_experience,
                "maximumExperience": maximum_experience,
                "tagsAndSkills": skills_str
            }])
            
            prediction = model_pipeline.predict(input_df)[0]
            
            # Ensure prediction is positive and realistic
            prediction = max(2.5, float(prediction))
            
            # Create a realistic range (e.g. ±15% of prediction)
            min_salary = round(prediction * 0.85, 2)
            max_salary = round(prediction * 1.15, 2)
            avg_salary = round(prediction, 2)
            
            return {
                "avg_lpa": avg_salary,
                "min_lpa": min_salary,
                "max_lpa": max_salary,
                "method": "Random Forest ML Model"
            }
        except Exception as e:
            print(f"[ML] Model prediction failed: {e}. Falling back to DB stats...")

    # 2. Database Fallback (if model is missing or fails)
    try:
        escaped_title = title.replace("'", "''")
        
        # Query average salary for this title and experience level in database
        query = f"""
            SELECT AVG(avg_salary) as db_avg
            FROM jobs
            WHERE LOWER(title) = LOWER('{escaped_title}') AND avg_salary > 0
        """
        _, rows = execute_query(query)
        db_avg_val = None
        if rows and rows[0]["db_avg"]:
            db_avg_val = float(rows[0]["db_avg"]) / 100000.0 # convert to LPA
            
        # If specific title has no salary data, query general average salary by experience
        if not db_avg_val:
            query = f"""
                SELECT AVG(avg_salary) as db_avg
                FROM jobs
                WHERE "minimumExperience" <= {minimum_experience} AND "maximumExperience" >= {maximum_experience} AND avg_salary > 0
            """
            _, rows = execute_query(query)
            if rows and rows[0]["db_avg"]:
                db_avg_val = float(rows[0]["db_avg"]) / 100000.0
                
        # Hard fallback to a reasonable default based on experience
        if not db_avg_val:
            db_avg_val = 4.0 + (minimum_experience * 1.5)
            
        avg_lpa = round(db_avg_val, 2)
        min_lpa = round(avg_lpa * 0.8, 2)
        max_lpa = round(avg_lpa * 1.2, 2)
        
        return {
            "avg_lpa": avg_lpa,
            "min_lpa": min_lpa,
            "max_lpa": max_lpa,
            "method": "Database Statistical Averages (Fallback)"
        }
    except Exception as e:
        print(f"[ML] Database fallback failed: {e}")
        # absolute emergency default
        avg_lpa = 6.5
        return {
            "avg_lpa": avg_lpa,
            "min_lpa": 5.0,
            "max_lpa": 8.0,
            "method": "Emergency Default (Fallback)"
        }

if __name__ == "__main__":
    # Test salary predictor
    test_title = "Software Engineer"
    test_loc = "Bengaluru"
    test_min_exp = 3
    test_max_exp = 6
    test_skills = ["Python", "SQL", "Git"]
    
    result = predict_salary(test_title, test_loc, test_min_exp, test_max_exp, test_skills)
    print(f"Salary Prediction for {test_title} ({test_min_exp}-{test_max_exp} Yrs Exp) in {test_loc}:")
    for k, v in result.items():
        print(f"  {k}: {v}")
