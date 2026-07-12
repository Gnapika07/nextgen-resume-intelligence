import requests

BASE = "http://localhost:8000/api"

# Login as student
token = requests.post(f"{BASE}/auth/login", json={
    "email": "student@gmail.com",
    "password": "password123"
}).json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}
print("Student logged in!")

# Upload resume
with open(r"C:\Users\gnapi\OneDrive\Desktop\gnapika resume.pdf", "rb") as f:
    resume = requests.post(
        f"{BASE}/student/upload-resume",
        headers=headers,
        files={"file": ("resume.pdf", f, "application/pdf")}
    ).json()

print(f"Resume uploaded: {resume['candidate_name']}")
print(f"Skills found: {resume['skills']}")

# Analyze against a JD
result = requests.post(f"{BASE}/student/analyze", headers=headers, json={
    "title": "Data Scientist",
    "company": "Google",
    "description_text": "Looking for a data scientist with Python, machine learning, TensorFlow experience. Must know SQL and data visualization.",
    "required_skills": ["Python", "Machine Learning", "TensorFlow", "SQL", "Power BI"],
    "required_experience": "1-3 years"
}).json()

print(f"\n--- STUDENT ANALYSIS RESULTS ---")
print(f"Job Title      : {result['job_title']}")
print(f"Overall Score  : {result['overall_score']}")
print(f"Score Label    : {result['score_label']}")
print(f"Matched Skills : {result['matched_skills']}")
print(f"Missing Skills : {result['missing_skills']}")
print(f"Strengths      : {result['strengths']}")
print(f"Suggestions    : {result['suggestions']}")
print(f"Recommended    : {result['recommended_roles']}")
print(f"ATS Tip        : {result['ats_tip']}")