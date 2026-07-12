import requests

BASE = "http://localhost:8000/api"

# Login
token = requests.post(f"{BASE}/auth/login", json={
    "email": "hr@company.com",
    "password": "password123"
}).json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}
print("Logged in!")

# Create a Job Description
jd = requests.post(f"{BASE}/hr/upload-jd", headers=headers, json={
    "title": "Python ML Engineer",
    "company": "TechCorp",
    "description_text": "We need a Python developer skilled in machine learning, TensorFlow, pandas and data analysis. Must have experience with React and SQL databases.",
    "required_skills": ["Python", "Machine Learning", "TensorFlow", "SQL", "React"],
    "required_experience": "2-5 years"
}).json()

print(f"JD Created: {jd['title']} (ID: {jd['id']})")

# Run Analysis
analysis = requests.post(f"{BASE}/hr/analyze", headers=headers, json={
    "jd_id": jd["id"]
}).json()

print(f"Analysis: {analysis['message']}")

# Get Results
results = requests.get(
    f"{BASE}/hr/results/{jd['id']}",
    headers=headers
).json()

print("\n--- CANDIDATE RANKINGS ---")
for r in results:
    print(f"Rank {r['rank']}: {r['candidate_name']}")
    print(f"  Overall Score : {r['overall_score']}")
    print(f"  Skills Score  : {r['skills_score']}")
    print(f"  Matched Skills: {r['matched_skills']}")
    print(f"  Missing Skills: {r['missing_skills']}")
    print(f"  Strengths     : {r['strengths']}")
    print()

print("Full HR flow test complete!")