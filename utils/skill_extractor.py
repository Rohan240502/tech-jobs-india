import re
from collections import Counter
from utils.db import execute_query

# Predefined list of standard tech skills with their regex search patterns
TECH_SKILLS_PATTERNS = {
    "Python": r"\bpython\b",
    "SQL": r"\bsql\b|\bmysql\b|\bpostgresql\b|\bsqlite\b",
    "JavaScript": r"\bjavascript\b|\bjs\b",
    "TypeScript": r"\btypescript\b|\bts\b",
    "HTML": r"\bhtml\b|\bhtml5\b",
    "CSS": r"\bcss\b|\bcss3\b|\bsass\b",
    "React": r"\breact\b|\breact\.js\b|\breactjs\b",
    "Angular": r"\bangular\b|\bangular\.js\b|\bangularjs\b",
    "Vue": r"\bvue\b|\bvue\.js\b|\bvuejs\b",
    "Node.js": r"\bnode\b|\bnode\.js\b|\bnodejs\b",
    "Express": r"\bexpress\b|\bexpressjs\b",
    "Django": r"\bdjango\b",
    "Flask": r"\bflask\b",
    "Spring Boot": r"\bspring boot\b|\bspringboot\b|\bspring\b",
    "Java": r"\bjava\b(?! script)",
    "C++": r"\bc\+\+\b",
    "C#": r"\bc#\b|\bc-sharp\b",
    "C": r"\b\bc\b\b", # Single letter word 'c'
    "Go": r"\bgo\b|\bgolang\b",
    "Rust": r"\brust\b",
    "PHP": r"\bphp\b",
    "Ruby": r"\bruby\b|\brails\b",
    "Swift": r"\bswift\b",
    "Kotlin": r"\bkotlin\b",
    "Flutter": r"\bflutter\b",
    "React Native": r"\breact native\b|\breact-native\b",
    "Android": r"\bandroid\b",
    "iOS": r"\bios\b",
    "AWS": r"\baws\b|\bamazon web services\b",
    "Azure": r"\bazure\b",
    "GCP": r"\bgcp\b|\bgoogle cloud\b",
    "Docker": r"\bdocker\b",
    "Kubernetes": r"\bkubernetes\b|\bk8s\b",
    "Jenkins": r"\bjenkins\b",
    "Git": r"\bgit\b|\bgithub\b|\bgitlab\b",
    "CI/CD": r"\bci/cd\b|\bci-cd\b|\bcontinuous integration\b",
    "Terraform": r"\bterraform\b",
    "Linux": r"\blinux\b|\bunix\b|\bubuntu\b|\bcentos\b",
    "Bash/Shell": r"\bbash\b|\bshell\b|\bpowershell\b",
    "MongoDB": r"\bmongodb\b|\bmongo\b",
    "Redis": r"\bredis\b",
    "Elasticsearch": r"\belasticsearch\b",
    "Cassandra": r"\bcassandra\b",
    "Hadoop": r"\bhadoop\b|\bmapreduce\b",
    "Spark": r"\bspark\b|\bpyspark\b",
    "Kafka": r"\bkafka\b",
    "Snowflake": r"\bsnowflake\b",
    "Machine Learning": r"\bmachine learning\b|\bml\b",
    "Deep Learning": r"\bdeep learning\b|\bdl\b",
    "Artificial Intelligence": r"\bartificial intelligence\b|\bai\b",
    "NLP": r"\bnlp\b|\bnatural language processing\b",
    "Computer Vision": r"\bcomputer vision\b|\bcv\b",
    "TensorFlow": r"\btensorflow\b",
    "PyTorch": r"\bpytorch\b",
    "Scikit-Learn": r"\bscikit-learn\b|\bsklearn\b",
    "Pandas": r"\bpandas\b",
    "NumPy": r"\bnumpy\b",
    "Tableau": r"\btableau\b",
    "Power BI": r"\bpower bi\b|\bpowerbi\b",
    "Excel": r"\bexcel\b",
    "Solidity": r"\bsolidity\b",
    "Smart Contracts": r"\bsmart contract\b|\bsmart contracts\b",
    "Cryptography": r"\bcryptography\b|\bsecurity\b",
    "REST APIs": r"\brest\b|\brestful\b|\brest api\b|\bapis\b",
    "GraphQL": r"\bgraphql\b",
    "Microservices": r"\bmicroservices\b|\bmicroservice\b",
    "Agile": r"\bagile\b|\bscrum\b",
    "JIRA": r"\bjira\b",
    "Unit Testing": r"\bunit testing\b|\bjunit\b|\bpytest\b|\btesting\b",
    "DevOps": r"\bdevops\b"
}

def extract_skills(text_content):
    """
    Extracts tech skills present in a text content string using regex.
    """
    if not text_content:
        return []
        
    extracted = []
    text_lower = text_content.lower()
    
    for skill_name, pattern in TECH_SKILLS_PATTERNS.items():
        if re.search(pattern, text_lower):
            extracted.append(skill_name)
            
    return extracted

def get_role_demanded_skills(role_title, top_n=10):
    """
    Queries the database to find the most demanded skills for a specific job title.
    """
    # Fetch tagsAndSkills for all jobs matching the role title
    query = f"SELECT \"tagsAndSkills\" FROM jobs WHERE title = :role"
    
    # We will run execute_query. Wait! execute_query in utils/db takes a plain string.
    # To prevent SQL injection and handle parameters properly in plain string:
    # Let's execute using a standard SQL where title matches.
    # Because role_title comes from a dropdown, it is safe, but we can clean it.
    escaped_role = role_title.replace("'", "''")
    query = f"SELECT \"tagsAndSkills\" FROM jobs WHERE LOWER(title) = LOWER('{escaped_role}')"
    
    columns, rows = execute_query(query)
    
    all_skills = []
    for row in rows:
        skills_str = row.get("tagsAndSkills")
        if skills_str:
            for s in skills_str.split(","):
                s_clean = s.strip().title()
                if s_clean and s_clean != 'Nan':
                    all_skills.append(s_clean)
                    
    counter = Counter(all_skills)
    
    # Filter to match our standard names if possible, or just keep as is
    demanded = [skill for skill, count in counter.most_common(top_n)]
    return demanded

def analyze_skill_gap(resume_text, target_role):
    """
    Compares resume skills with target job role skills.
    Returns:
    - user_skills: List of skills found in the resume
    - required_skills: List of top skills required for the role in the database
    - matching_skills: Intersection of both
    - missing_skills: Required skills that the user does not have
    - match_percentage: Percentage of required skills the user possesses
    """
    user_skills = extract_skills(resume_text)
    required_skills = get_role_demanded_skills(target_role, top_n=10)
    
    if not required_skills:
        # Fallback standard skills if none found in database for some reason
        required_skills = ["Python", "SQL", "Git", "REST APIs", "JavaScript", "Docker", "AWS", "Agile", "Linux", "DevOps"]
        
    # Standardize casing for comparison
    user_skills_set = {s.lower() for s in user_skills}
    required_skills_set = {s.lower() for s in required_skills}
    
    matching_skills = []
    missing_skills = []
    
    # Map back to original casing
    skill_mapping = {s.lower(): s for s in required_skills}
    for us in user_skills:
        skill_mapping[us.lower()] = us
        
    for req in required_skills_set:
        if req in user_skills_set:
            matching_skills.append(skill_mapping[req])
        else:
            missing_skills.append(skill_mapping[req])
            
    # Calculate percentage based on matches against target role's top skills
    total_required = len(required_skills)
    matched_count = len(matching_skills)
    match_percentage = round((matched_count / total_required) * 100) if total_required > 0 else 0
    
    return {
        "user_skills": user_skills,
        "required_skills": required_skills,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "match_percentage": match_percentage
    }

if __name__ == "__main__":
    # Test skill extraction
    sample_resume = "Highly skilled Software Engineer with 4 years experience. Strong in Python, SQL, React and Docker. Familiar with Git, AWS and Linux."
    results = analyze_skill_gap(sample_resume, "Software Engineer")
    print("Skill Gap Analysis for Software Engineer:")
    for k, v in results.items():
        print(f"  {k}: {v}")
