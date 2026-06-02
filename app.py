import os
from flask import Flask, render_template, request, jsonify
from collections import Counter
from utils.db import init_db, execute_query
from utils.skill_extractor import analyze_skill_gap, extract_skills
from utils.salary_predictor import predict_salary

app = Flask(__name__)

# Initialize database schema and seed data on startup
print("[Flask] Initializing system database...")
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/skills')
def skills():
    # 1. Dynamically retrieve all skills from the active database
    query = "SELECT \"tagsAndSkills\" FROM jobs WHERE \"tagsAndSkills\" IS NOT NULL"
    _, rows = execute_query(query)
    
    all_skills = []
    for r in rows:
        skills_str = r.get("tagsAndSkills")
        if skills_str:
            for s in skills_str.split(","):
                s_clean = s.strip().title()
                if s_clean and s_clean != 'Nan' and s_clean != 'None' and s_clean != '':
                    all_skills.append(s_clean)
                    
    counter = Counter(all_skills)
    
    # 2. Get top 10 skills for table
    top_skills = counter.most_common(10)
    
    # 3. Get top 35 skills for the visual tag cloud
    cloud_skills = counter.most_common(35)
    max_count = cloud_skills[0][1] if cloud_skills else 1
    
    # Get total job listings count
    count_query = "SELECT COUNT(*) as cnt FROM jobs"
    _, count_rows = execute_query(count_query)
    total_jobs = count_rows[0]["cnt"] if count_rows else 3535
    
    return render_template(
        'skills.html',
        top_skills=top_skills,
        cloud_skills=cloud_skills,
        max_count=max_count,
        total_jobs=total_jobs
    )

@app.route('/salary')
def salary_estimator():
    # 1. Fetch unique job titles from DB for dropdown selection
    title_query = "SELECT DISTINCT title FROM jobs ORDER BY title ASC"
    _, title_rows = execute_query(title_query)
    unique_titles = [r["title"] for r in title_rows if r["title"]]
    
    # 2. Fetch unique job locations from DB for dropdown selection
    # We clean it to get main cities (first part of split) or just take the top unique locations
    loc_query = "SELECT DISTINCT location FROM jobs ORDER BY location ASC"
    _, loc_rows = execute_query(loc_query)
    raw_locations = [r["location"] for r in loc_rows if r["location"]]
    
    # Extract major unique cities to make the dropdown tidy
    unique_locations = set()
    for loc in raw_locations:
        for city in loc.split(","):
            city_clean = city.strip()
            if city_clean and "hybrid" not in city_clean.lower() and "onsite" not in city_clean.lower():
                unique_locations.add(city_clean)
                
    unique_locations = sorted(list(unique_locations))
    
    # Ensure standard fallback list if database is empty
    if not unique_titles:
        unique_titles = ["Software Engineer", "Full Stack Developer", "Data Scientist", "DevOps Engineer"]
    if not unique_locations:
        unique_locations = ["Bengaluru", "Pune", "Hyderabad", "Mumbai", "Chennai", "Gurugram"]
        
    return render_template(
        'salary.html',
        unique_titles=unique_titles,
        unique_locations=unique_locations
    )

@app.route('/resume')
def resume_analyzer():
    # Fetch unique titles for role selection
    title_query = "SELECT DISTINCT title FROM jobs ORDER BY title ASC"
    _, title_rows = execute_query(title_query)
    unique_titles = [r["title"] for r in title_rows if r["title"]]
    
    if not unique_titles:
        unique_titles = ["Software Engineer", "Full Stack Developer", "Data Scientist", "DevOps Engineer"]
        
    return render_template('resume.html', unique_titles=unique_titles)


# --- DYNAMIC CHART JSON APIs ---

@app.route('/api/stats/locations')
def api_stats_locations():
    # Top 10 locations by job count
    query = """
        SELECT location, COUNT(*) as cnt
        FROM jobs
        GROUP BY location
        ORDER BY cnt DESC
        LIMIT 10
    """
    _, rows = execute_query(query)
    
    # Process multiple cities (e.g. "New Delhi, Gurugram" -> count for each)
    city_counter = Counter()
    for r in rows:
        loc = r["location"]
        cnt = r["cnt"]
        # Split cities and distribute count
        cities = [c.strip() for c in loc.split(",") if c.strip()]
        for city in cities:
            if "hybrid" not in city.lower() and "onsite" not in city.lower():
                city_counter[city] += cnt
                
    top_cities = city_counter.most_common(10)
    
    return jsonify({
        "labels": [item[0] for item in top_cities],
        "counts": [item[1] for item in top_cities]
    })

@app.route('/api/stats/roles')
def api_stats_roles():
    # Top 6 job roles
    query = """
        SELECT title, COUNT(*) as cnt
        FROM jobs
        GROUP BY title
        ORDER BY cnt DESC
        LIMIT 6
    """
    _, rows = execute_query(query)
    return jsonify({
        "labels": [r["title"] for r in rows],
        "counts": [r["cnt"] for r in rows]
    })

@app.route('/api/stats/salary-by-role')
def api_stats_salary_role():
    # Top 8 highest paying roles on average
    query = """
        SELECT title, ROUND(AVG(avg_salary) / 100000.0, 2) as avg_lpa
        FROM jobs
        WHERE avg_salary > 0
        GROUP BY title
        ORDER BY avg_lpa DESC
        LIMIT 8
    """
    _, rows = execute_query(query)
    return jsonify({
        "labels": [r["title"] for r in rows],
        "salaries": [r["avg_lpa"] for r in rows]
    })

@app.route('/api/stats/salary-vs-experience')
def api_stats_salary_exp():
    # Retrieve scatter points representing experience vs salary
    query = """
        SELECT "minimumExperience" as exp, ROUND(avg_salary / 100000.0, 2) as lpa
        FROM jobs
        WHERE avg_salary > 0 AND "minimumExperience" IS NOT NULL
        LIMIT 100
    """
    _, rows = execute_query(query)
    points = [{"experience": r["exp"], "salary": r["lpa"]} for r in rows]
    return jsonify({"points": points})

@app.route('/api/stats/skills-top-25')
def api_stats_skills_top_25():
    # Dynamic top 25 skills for visual horizontal bar chart
    query = "SELECT \"tagsAndSkills\" FROM jobs WHERE \"tagsAndSkills\" IS NOT NULL"
    _, rows = execute_query(query)
    
    all_skills = []
    for r in rows:
        skills_str = r.get("tagsAndSkills")
        if skills_str:
            for s in skills_str.split(","):
                s_clean = s.strip().lower()
                if s_clean and s_clean != 'nan' and s_clean != 'none' and s_clean != '':
                    all_skills.append(s_clean)
                    
    counter = Counter(all_skills)
    top_25 = counter.most_common(25)
    
    return jsonify({
        "labels": [item[0].title() for item in top_25],
        "counts": [item[1] for item in top_25]
    })


# --- INTERACTIVE TOOL SUBMISSION APIs ---

@app.route('/api/predict-salary', methods=['POST'])
def api_predict_salary():
    data = request.json or {}
    title = data.get("title", "Software Engineer")
    location = data.get("location", "Bengaluru")
    experience = data.get("experience", 4)
    
    prediction = predict_salary(title, location, experience)
    return jsonify(prediction)

@app.route('/api/analyze-resume', methods=['POST'])
def api_analyze_resume():
    data = request.json or {}
    resume_text = data.get("resume_text", "")
    target_role = data.get("target_role", "Software Engineer")
    
    analysis = analyze_skill_gap(resume_text, target_role)
    
    # Dynamically find 3 job recommendations in the database matching target role and user skills
    user_skills_set = {s.lower() for s in analysis["user_skills"]}
    
    escaped_role = target_role.replace("'", "''")
    jobs_query = f"""
        SELECT title, "companyName", location, "tagsAndSkills"
        FROM jobs
        WHERE LOWER(title) = LOWER('{escaped_role}')
        LIMIT 50
    """
    _, jobs_rows = execute_query(jobs_query)
    
    # Rank recommendations by skill intersection count
    ranked_recommendations = []
    for job in jobs_rows:
        skills_str = job.get("tagsAndSkills") or ""
        job_skills = [s.strip().lower() for s in skills_str.split(",") if s.strip()]
        overlap = len(user_skills_set.intersection(set(job_skills)))
        
        ranked_recommendations.append({
            "title": job["title"],
            "companyName": job["companyName"],
            "location": job["location"],
            "tagsAndSkills": skills_str,
            "overlap": overlap
        })
        
    # Sort descending by overlap score
    ranked_recommendations = sorted(ranked_recommendations, key=lambda x: x["overlap"], reverse=True)
    
    # Return top 3 recommendations
    analysis["recommended_jobs"] = ranked_recommendations[:3]
    return jsonify(analysis)

@app.route('/api/run-query', methods=['POST'])
def api_run_query():
    data = request.json or {}
    query = data.get("query", "").strip()
    
    if not query:
        return jsonify({"error": "Empty SQL query."})
        
    # Security filter: restrict executing write/modify/schema deletion statements
    restricted_keywords = ["drop", "delete", "insert", "update", "alter", "truncate", "create table", "drop table", "grant"]
    query_lower = query.lower()
    for kw in restricted_keywords:
        if kw in query_lower:
            return jsonify({"error": f"Restricted action: keyword '{kw}' is not allowed in this read-only query playground."})
            
    columns, rows = execute_query(query)
    
    # Handle possible errors (e.g. wrong syntax)
    if not columns and not rows:
        # Check if we can determine error
        # In general, if both are empty it means either error or empty result
        return jsonify({"columns": [], "rows": [], "error": "Query executed with no results or invalid SQL syntax."})
        
    return jsonify({
        "columns": columns,
        "rows": rows
    })

if __name__ == '__main__':
    # Start web server locally
    app.run(debug=True, port=5000)
