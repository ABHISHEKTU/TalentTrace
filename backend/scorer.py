import spacy
from sentence_transformers import SentenceTransformer, util
import re

# Load models (happens once when server starts)
nlp = spacy.load("en_core_web_md")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Common tech skills to look for
SKILLS_LIST = [
    "python", "java", "javascript", "typescript", "c++", "c#", "r", "sql",
    "machine learning", "deep learning", "nlp", "computer vision", "ai",
    "tensorflow", "pytorch", "keras", "scikit-learn", "opencv",
    "react", "angular", "vue", "node.js", "django", "fastapi", "flask",
    "html", "css", "tailwind",
    "mysql", "postgresql", "mongodb", "firebase", "sqlite",
    "git", "github", "docker", "kubernetes", "aws", "azure", "gcp",
    "rest api", "graphql", "microservices",
    "data analysis", "data visualization", "pandas", "numpy", "matplotlib",
    "excel", "power bi", "tableau",
    "communication", "teamwork", "leadership", "problem solving",
    "agile", "scrum", "jira",
]


def extract_skills(text: str) -> list:
    """
    Extract skills from text by matching against known skills list.
    """
    text_lower = text.lower()
    found_skills = []

    for skill in SKILLS_LIST:
        if skill in text_lower:
            found_skills.append(skill)

    return list(set(found_skills))


def calculate_match_score(resume_text: str, job_description: str) -> dict:
    """
    Compares resume to job description and returns:
    - match score (0-100)
    - matched skills
    - missing skills
    - suggestions
    """

    # 1. Extract skills from both
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)

    # 2. Find matched and missing skills
    matched_skills = [s for s in jd_skills if s in resume_skills]
    missing_skills = [s for s in jd_skills if s not in resume_skills]

    # 3. Calculate skill match percentage
    if len(jd_skills) > 0:
        skill_score = (len(matched_skills) / len(jd_skills)) * 100
    else:
        skill_score = 0

    # 4. Calculate semantic similarity using sentence-transformers
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    jd_embedding = model.encode(job_description, convert_to_tensor=True)
    semantic_score = float(util.cos_sim(resume_embedding, jd_embedding)[0][0]) * 100

    # 5. Final score — 50% skill match + 50% semantic similarity
    final_score = round((skill_score * 0.5) + (semantic_score * 0.5), 1)

    # 6. Generate suggestions based on missing skills
    suggestions = generate_suggestions(missing_skills)

    return {
        "match_score": final_score,
        "skill_score": round(skill_score, 1),
        "semantic_score": round(semantic_score, 1),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "total_jd_skills": len(jd_skills),
        "total_resume_skills": len(resume_skills),
        "suggestions": suggestions
    }


def generate_suggestions(missing_skills: list) -> list:
    """
    Generate improvement suggestions based on missing skills.
    """
    suggestions = []

    if not missing_skills:
        suggestions.append("Great match! Your resume covers all key skills.")
        return suggestions

    # Group missing skills by category
    ml_skills = ["machine learning", "deep learning", "tensorflow",
                  "pytorch", "keras", "scikit-learn", "nlp", "computer vision"]
    web_skills = ["react", "angular", "vue", "node.js",
                  "django", "fastapi", "flask", "html", "css"]
    db_skills = ["mysql", "postgresql", "mongodb", "firebase", "sql"]
    cloud_skills = ["aws", "azure", "gcp", "docker", "kubernetes"]

    missing_ml = [s for s in missing_skills if s in ml_skills]
    missing_web = [s for s in missing_skills if s in web_skills]
    missing_db = [s for s in missing_skills if s in db_skills]
    missing_cloud = [s for s in missing_skills if s in cloud_skills]

    if missing_ml:
        suggestions.append(
            f"Add ML/AI skills to your resume: {', '.join(missing_ml)}"
        )
    if missing_web:
        suggestions.append(
            f"Mention web technologies you know: {', '.join(missing_web)}"
        )
    if missing_db:
        suggestions.append(
            f"Include database experience: {', '.join(missing_db)}"
        )
    if missing_cloud:
        suggestions.append(
            f"Consider learning or adding cloud skills: {', '.join(missing_cloud)}"
        )

    # General suggestion
    if len(missing_skills) > 5:
        suggestions.append(
            "Your resume is missing several key skills. "
            "Tailor it specifically for this job description."
        )

    return suggestions


# ---- TEST IT HERE ----
if __name__ == "__main__":
    sample_resume = """
    Experienced Python developer with skills in machine learning,
    deep learning, tensorflow, and scikit-learn. Built projects using
    FastAPI, PostgreSQL, and Git. Strong communication and teamwork skills.
    """

    sample_jd = """
    Looking for a Python developer with experience in machine learning,
    NLP, React, PostgreSQL, Docker, and AWS. Must have good communication skills.
    """

    result = calculate_match_score(sample_resume, sample_jd)

    print(f"Match Score: {result['match_score']}%")
    print(f"Skill Score: {result['skill_score']}%")
    print(f"Semantic Score: {result['semantic_score']}%")
    print(f"Matched Skills: {result['matched_skills']}")
    print(f"Missing Skills: {result['missing_skills']}")
    print(f"Suggestions: {result['suggestions']}")