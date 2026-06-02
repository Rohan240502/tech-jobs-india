import os
from flask import Flask, render_template, request, jsonify
from collections import Counter
from utils.db import init_db, execute_query, log_user_analytics
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
    email = data.get("email") # optional email capture
    
    prediction = predict_salary(title, location, experience)
    
    # Log search intelligence to user_analytics
    log_user_analytics(
        query_type="salary_prediction",
        job_role=title,
        experience=experience,
        location=location,
        predicted_lpa=prediction.get("avg_lpa", 0.0),
        user_email=email
    )
    return jsonify(prediction)

@app.route('/api/analyze-resume', methods=['POST'])
def api_analyze_resume():
    data = request.json or {}
    resume_text = data.get("resume_text", "")
    target_role = data.get("target_role", "Software Engineer")
    email = data.get("email") # optional email capture
    
    analysis = analyze_skill_gap(resume_text, target_role)
    
    # Log resume scanning intelligence to user_analytics
    log_user_analytics(
        query_type="resume_matching",
        job_role=target_role,
        experience=None,
        location="",
        predicted_lpa=0.0,
        user_email=email
    )
    
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

@app.route('/trends')
def trends():
    return render_template('trends.html')

@app.route('/api/stats/crowdsourced')
def api_stats_crowdsourced():
    # 1. Total predictions logged where query_type = 'salary_prediction'
    _, pred_rows = execute_query("SELECT COUNT(*) as cnt FROM user_analytics WHERE query_type = 'salary_prediction'")
    total_predictions = pred_rows[0]["cnt"] if pred_rows else 0

    # 2. Email Leads Captured where user_email IS NOT NULL AND user_email != ''
    _, email_rows = execute_query("SELECT COUNT(*) as cnt FROM user_analytics WHERE user_email IS NOT NULL AND user_email != ''")
    total_emails = email_rows[0]["cnt"] if email_rows else 0

    # 3. Average expected LPA where query_type = 'salary_prediction' AND predicted_lpa > 0
    _, lpa_rows = execute_query("SELECT AVG(predicted_lpa) as avg_lpa FROM user_analytics WHERE query_type = 'salary_prediction' AND predicted_lpa > 0")
    avg_lpa = round(lpa_rows[0]["avg_lpa"], 2) if lpa_rows and lpa_rows[0]["avg_lpa"] is not None else 0.0

    # 4. Top 8 job roles
    _, roles_rows = execute_query("""
        SELECT job_role, COUNT(*) as cnt 
        FROM user_analytics 
        WHERE job_role IS NOT NULL AND job_role != '' 
        GROUP BY job_role 
        ORDER BY cnt DESC 
        LIMIT 8
    """)
    roles_labels = [r["job_role"].title() for r in roles_rows]
    roles_counts = [r["cnt"] for r in roles_rows]

    # 5. Top 8 locations
    _, locs_rows = execute_query("""
        SELECT location, COUNT(*) as cnt 
        FROM user_analytics 
        WHERE location IS NOT NULL AND location != '' 
        GROUP BY location 
        ORDER BY cnt DESC 
        LIMIT 8
    """)
    locs_labels = [r["location"].title() for r in locs_rows]
    locs_counts = [r["cnt"] for r in locs_rows]

    # 6. Last 8 queries
    _, last_queries = execute_query("""
        SELECT id, query_type, job_role, experience, location, predicted_lpa, user_email, timestamp 
        FROM user_analytics 
        ORDER BY timestamp DESC 
        LIMIT 8
    """)
    
    # Process timestamps safely to avoid serialization issues
    for q in last_queries:
        if "timestamp" in q and q["timestamp"] is not None:
            if not isinstance(q["timestamp"], str):
                q["timestamp"] = q["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        # clean display text
        if q.get("user_email"):
            # mask email slightly for privacy: ro***@domain.com
            email = q["user_email"]
            if "@" in email:
                parts = email.split("@")
                masked = parts[0][:2] + "***@" + parts[1]
                q["user_email"] = masked
        else:
            q["user_email"] = "-"
        
        if not q.get("location"):
            q["location"] = "-"
            
        if q.get("experience") is not None and q["experience"] > 0:
            q["experience"] = f"{int(q['experience'])} Yrs" if q["experience"].is_integer() else f"{q['experience']} Yrs"
        else:
            q["experience"] = "-"
            
        if q.get("predicted_lpa") and q["predicted_lpa"] > 0:
            q["predicted_lpa"] = f"₹ {q['predicted_lpa']} LPA"
        else:
            q["predicted_lpa"] = "-"

    return jsonify({
        "metrics": {
            "total_predictions": total_predictions,
            "total_emails": total_emails,
            "avg_lpa": avg_lpa
        },
        "roles": {
            "labels": roles_labels,
            "counts": roles_counts
        },
        "locations": {
            "labels": locs_labels,
            "counts": locs_counts
        },
        "recent_queries": last_queries
    })

@app.route('/api/career-chat', methods=['POST'])
def api_career_chat():
    data = request.json or {}
    message = data.get("message", "").strip()
    
    if not message:
        return jsonify({"response": "I didn't receive any message. How can I assist you with your tech career in India?"})
        
    api_key = os.environ.get("GEMINI_API_KEY")
    
    # 1. If Gemini API Key is configured, attempt to use generative AI
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=(
                    "You are 'Antigravity AI Career Coach', a premium, helpful career mentor specializing in the Indian Tech Job Market. "
                    "You provide expert guidance on salary negotiation, interview preparation, upskilling, resume building, and dynamic market trends in tech hubs like Bengaluru, Pune, Hyderabad, Mumbai, Chennai, and Gurugram. "
                    "Keep your responses concise, highly structured, professional, and readable. Use standard markdown for bold text and bullet points."
                )
            )
            
            response = model.generate_content(message)
            return jsonify({"response": response.text, "mode": "gemini"})
        except Exception as e:
            print(f"[Chatbot] Gemini API execution failed: {e}. Falling back to NLP Coach...")
            
    # 2. Rule-based local NLP Fallback Coach if key is missing or failed
    response_text = get_local_coach_response(message)
    return jsonify({"response": response_text, "mode": "fallback"})

def get_local_coach_response(message):
    msg = message.lower()
    
    # Salary / LPA / Negotiation keywords
    if any(k in msg for k in ["salary", "lpa", "negotiate", "money", "package", "compensation", "hike", "raise"]):
        return (
            "### 💰 Salary Negotiation & Compensation Guidance\n\n"
            "Navigating tech salary negotiations in India requires strategic positioning. Here is a quick guide:\n\n"
            "1. **Know Your Worth:** Use our **Salary Estimator** to search for your role, location, and experience based on Naukri 2025 benchmarks.\n"
            "2. **The 30-40% Rule:** Standard hikes for standard transitions range from 30% to 50%. For hot skills like AI/ML or cloud architecture, premiums can be much higher (up to 80-100%).\n"
            "3. **Base vs. CTC:** Always clarify the fixed base salary versus the total CTC (which includes variable pay, stock options/RSUs, and joining bonuses).\n"
            "4. **Multiple Offers:** The strongest leverage in India is having a competing offer. Be professional, show enthusiasm for the role, and let recruiters know you have active pipelines.\n\n"
            "Do you have a specific role or offer you want to discuss?"
        )
        
    # Resume / CV / ATS keywords
    if any(k in msg for k in ["resume", "cv", "ats", "portfolio", "profile", "linkedin"]):
        return (
            "### 📄 Tailoring Your Resume for the ATS\n\n"
            "Most top Indian tech employers (like TCS, Infosys, Wipro, and global capability centers) use Applicant Tracking Systems (ATS). To maximize your callbacks:\n\n"
            "1. **Use the Resume Matcher:** Go to our **Resume Matcher** tool, select your target role, paste your resume text, and run an ATS scan to instantly uncover matching skills and gaps.\n"
            "2. **Incorporate Job Keywords:** Tailor your resume summary and bullet points to explicitly match the phrasing in target job descriptions.\n"
            "3. **Quantify Achievements:** Instead of listing responsibilities, write: *'Optimized SQL query performance by 40%, reducing database load times by 2 seconds.'*\n"
            "4. **Simple Layout:** Avoid multi-column graphics, charts, or images in your resume. Use a clean, single-column PDF format that parser engines can read easily."
        )
        
    # Job hub hubs / Location keywords
    if any(k in msg for k in ["bengaluru", "bangalore", "pune", "hyderabad", "mumbai", "chennai", "gurugram", "delhi", "noida", "location"]):
        return (
            "### 📍 Indian Tech Job Geographic Hotspots\n\n"
            "The Indian tech landscape is heavily clustered in specific geographic centers:\n\n"
            "* **Bengaluru (The Silicon Valley):** Leader in product startups, global R&D centers, and SaaS. Demands high technical proficiency and commands the highest salary benchmarks.\n"
            "* **Hyderabad & Pune:** Major hubs for large IT MNCs and enterprise SaaS companies. Strong demand for Cloud, DevOps, and Full Stack developers.\n"
            "* **Gurugram/Noida (NCR):** Fast-growing fintech and consulting startup hub. High demand for Data Analysts, AI Engineers, and Product Managers.\n"
            "* **Mumbai & Chennai:** Mumbai dominates Fintech, Banking tech, and e-commerce. Chennai remains the primary hub for SaaS giants and automotive tech systems."
        )
        
    # Study plan / prep / learn keywords
    if any(k in msg for k in ["study", "learn", "course", "skill", "prepare", "upskill", "path", "roadmap"]):
        return (
            "### 📚 4-Week Structured Upskilling Prep Plan\n\n"
            "Here is a proven study path to scale your technical capacity and landing interviews:\n\n"
            "* **Week 1: Core Fundamentals & DS & Algo**\n"
            "  * Re-learn data structures (Arrays, Trees, HashMaps) and algorithms.\n"
            "  * Practice standard problems on LeetCode/HackerRank (specifically focus on arrays, string manipulations, and hashing).\n"
            "* **Week 2: System Design & Databases**\n"
            "  * Understand RESTful API structures, SQL queries, indexing, and normalization.\n"
            "  * Study key concepts: horizontal vs. vertical scaling, caching (Redis), and load balancers.\n"
            "* **Week 3: Core Specialized Frameworks**\n"
            "  * Focus on the technology stack of choice (e.g., Python/Flask/Django, Node.js, React, or Java/Spring Boot).\n"
            "  * Complete a minor portfolio project demonstrating full-stack CRUD capabilities.\n"
            "* **Week 4: ATS Resume Optimization & Mock Interviews**\n"
            "  * Run your CV through our **Resume Matcher** to remove gaps.\n"
            "  * Engage in behavioral interview prep (using the STAR method for past projects)."
        )

    # Specific role keywords
    if any(k in msg for k in ["developer", "engineer", "data scientist", "analyst", "product manager", "devops", "cloud", "frontend", "backend", "fullstack"]):
        return (
            "### 🛠️ Role-Specific Market Insights\n\n"
            "The Indian hiring ecosystem has transitioned towards high-skill specialization. Here is what is trending:\n\n"
            "* **Full-Stack / Backend Developers:** Deep knowledge of databases (Postgres, MongoDB), microservices, and asynchronous event loops is highly prized. Major stacks: MERN, Java/Spring, Python/FastAPI.\n"
            "* **Data Scientists & AI Engineers:** While standard python/pandas is common, expertise in fine-tuning LLMs, retrieval-augmented generation (RAG), and vector databases (Pinecone, Chroma) sets candidates apart.\n"
            "* **DevOps & Cloud Engineers:** AWS, Kubernetes, Terraform, and CI/CD pipelines (GitHub Actions, Jenkins) are absolute must-haves. Command high salary multipliers."
        )
        
    # Default greeting/fallback
    return (
        "### 👋 Welcome to Antigravity AI Career Coach!\n\n"
        "I am your dedicated mentor for navigating the **Indian Tech Job Market**. I can provide specialized guidance on:\n\n"
        "* **Salary Negotiation Strategies:** Learn how to maximize your hike, interpret CTC breakdowns, and handle multiple competing offers.\n"
        "* **ATS Resume Optimizations:** Perfect your skills list and structure to bypass hiring parsing tools.\n"
        "* **Geographic Trends:** Understand where roles are shifting and which cities (Bengaluru, Pune, Hyderabad, NCR) command the best premiums.\n"
        "* **Upskilling Roadmap:** Design a custom learning path to transition into high-paying engineering domains.\n\n"
        "Feel free to ask a specific question, or test your background profile with our [Salary Estimator](/salary) and [Resume Matcher](/resume)!"
    )

if __name__ == '__main__':
    # Start web server locally
    app.run(debug=True, port=5000)
