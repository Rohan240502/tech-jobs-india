import os
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

def train_and_save_model():
    # Paths
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(utils_dir)
    csv_path = os.path.join(workspace_dir, "data", "processed", "jobs_cleaned.csv")
    model_path = os.path.join(workspace_dir, "models", "salary_model.pkl")

    print(f"[ML Training] Loading cleaned dataset from {csv_path}...")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Cleaned CSV not found at {csv_path}")

    df = pd.read_csv(csv_path)
    df_ml = df[df['avg_salary'] > 0].copy()
    df_ml['target_lpa'] = df_ml['avg_salary'] / 100000.0
    print(f"[ML Training] Total records with disclosed salaries for ML: {len(df_ml)}")

    # Preprocessing
    df_ml['title'] = df_ml['title'].fillna('Software Engineer')
    df_ml['location'] = df_ml['location'].fillna('Bengaluru')
    df_ml['minimumExperience'] = df_ml['minimumExperience'].fillna(0.0)
    df_ml['maximumExperience'] = df_ml['maximumExperience'].fillna(df_ml['minimumExperience'] + 2.0)
    
    # Compute Average Experience feature
    df_ml['averageExperience'] = (df_ml['minimumExperience'] + df_ml['maximumExperience']) / 2.0
    
    print("[ML Training] Features prepared. Typical Average Experience examples:")
    print(df_ml[['minimumExperience', 'maximumExperience', 'averageExperience']].head(5))

    # Feature matrix X and target y
    X = df_ml[['title', 'location', 'averageExperience']]
    y = df_ml['target_lpa']

    # Column transformer (num = StandardScaler, cat = OneHotEncoder)
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), ['averageExperience']),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['title', 'location'])
        ]
    )

    # Regressor Pipeline
    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=150, max_depth=12, random_state=42))
    ])

    # Train Test Split
    print("[ML Training] Splitting data into 80/20 train/test sets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Fit Model
    print("[ML Training] Training Random Forest model...")
    model_pipeline.fit(X_train, y_train)
    print("[ML Training] Training complete.")

    # Evaluate Model
    y_pred = model_pipeline.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"[ML Training] Evaluation Metrics:")
    print(f"  Mean Absolute Error: {mae:.2f} LPA")
    print(f"  R2 Score: {r2:.4f}")

    # Save Pickle File
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, 'wb') as f:
        pickle.dump(model_pipeline, f)
    print(f"[ML Training] Model pipeline successfully saved to: {model_path}")

if __name__ == "__main__":
    train_and_save_model()
