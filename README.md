# NextGen Resume Intelligence

An AI-powered Resume Analysis and Candidate Ranking System designed to streamline the recruitment process by intelligently evaluating resumes against job descriptions.

Developed as a Mini Project at Stanley College of Engineering and Technology for Women.

---

## Project Overview

NextGen Resume Intelligence helps recruiters efficiently screen candidates by automating resume analysis, ATS score calculation, skill matching, and candidate ranking.

The system also provides separate interfaces for Students and HR, allowing students to upload and analyze their resumes while enabling HR to evaluate multiple candidates against a specific job description.

---

## Features

### Student Module
- Secure Login
- Upload Resume (PDF)
- Resume Analysis
- ATS Score Calculation
- Skill Extraction
- Resume Feedback

### HR Module
- Secure Login
- Upload Multiple Resumes
- Upload Job Description
- Resume Parsing
- Candidate Ranking
- Resume Comparison
- Match Score Calculation

### Analytics
- PostgreSQL Database
- Power BI Dashboard for Recruitment Insights

---

## Tech Stack

### Frontend
- React
- Vite
- HTML
- CSS
- JavaScript

### Backend
- Python
- FastAPI

### Database
- PostgreSQL

### Analytics
- Power BI

### Other Technologies
- NLP
- TF-IDF Based Skill Matching
- REST APIs

---

## Project Structure

```
NextGen Resume Intelligence
│
├── backend/
│   ├── app/
│   ├── uploads/
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│
├── docs/
│
├── screenshots/
│
├── .gitignore
└── README.md
```

---

## Workflow

1. User logs into the system.
2. Student uploads a resume.
3. HR uploads one or more resumes along with a Job Description.
4. The backend parses resumes and extracts relevant information.
5. Skills are matched against the Job Description.
6. ATS scores are calculated.
7. Candidates are ranked based on their matching score.
8. Recruitment analytics are visualized using Power BI.

---

## Installation

### Clone Repository

```bash
git clone <repository-url>
```

### Backend

```bash
cd backend
pip install -r requirements.txt
python run.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Future Improvements

Version 2.0 will include:

- Semantic Resume Matching using Sentence Transformers
- AI-based Resume Recommendations
- Recruiter Dashboard Enhancements
- Authentication Improvements
- Cloud Deployment
- Docker Support
- Advanced Analytics
- Better UI/UX
- API Documentation

---

## Contributors

- Gnapika Devarakonda
- A. Anjana
- A. Bindu

Mini Project submitted to:

**Stanley College of Engineering and Technology for Women**

---

## License

This project is intended for educational and portfolio purposes.