import requests

login_response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={
        "email": "hr@company.com",
        "password": "password123"
    }
)

token = login_response.json()["access_token"]
print(f"Token received: {token[:30]}...")

# Your actual resume file
pdf_path = r"C:\Users\gnapi\OneDrive\Desktop\gnapika resume.pdf"

with open(pdf_path, "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/hr/upload-resumes",
        headers={"Authorization": f"Bearer {token}"},
        files={"files": ("gnapika_resume.pdf", f, "application/pdf")}
    )

print("Status:", response.status_code)
print("Response:", response.json())