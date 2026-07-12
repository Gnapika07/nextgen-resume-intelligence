import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict


def preprocess_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def calculate_tfidf_similarity(text1: str, text2: str) -> float:
    if not text1 or not text2:
        return 0.0
    text1 = preprocess_text(text1)
    text2 = preprocess_text(text2)
    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000
        )
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return float(similarity[0][0])
    except Exception as e:
        print(f"TF-IDF error: {e}")
        return 0.0


def calculate_skills_score(
    resume_skills: List[str],
    required_skills: List[str]
) -> Dict:
    if not required_skills:
        return {
            "score": 50.0,
            "matched": [],
            "missing": [],
            "extra": resume_skills
        }

    resume_lower = [s.lower().strip() for s in resume_skills]
    required_lower = [s.lower().strip() for s in required_skills]

    matched = []
    missing = []

    for skill in required_lower:
        found = False
        for resume_skill in resume_lower:
            if skill in resume_skill or resume_skill in skill:
                found = True
                matched.append(skill.title())
                break
        if not found:
            missing.append(skill.title())

    extra = [s for s in resume_skills
             if s.lower() not in required_lower]

    score = (len(matched) / len(required_lower)) * 100 if required_lower else 0

    return {
        "score": round(score, 2),
        "matched": matched,
        "missing": missing,
        "extra": extra
    }


def calculate_experience_score(
    resume_years: float,
    required_experience: str
) -> float:
    if not required_experience:
        return 70.0

    numbers = re.findall(r'\d+', str(required_experience))

    if not numbers:
        return 70.0

    if len(numbers) >= 2:
        min_exp = float(numbers[0])
        max_exp = float(numbers[1])
    else:
        min_exp = float(numbers[0])
        max_exp = min_exp + 2

    if resume_years >= min_exp and resume_years <= max_exp:
        return 100.0
    elif resume_years >= min_exp:
        return max(70.0, 100.0 - (resume_years - max_exp) * 5)
    else:
        gap = min_exp - resume_years
        return max(0.0, 100.0 - gap * 20)


def extract_keywords_from_jd(jd_text: str) -> List[str]:
    if not jd_text:
        return []
    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=30
        )
        vectorizer.fit_transform([jd_text])
        keywords = vectorizer.get_feature_names_out().tolist()
        return [kw.title() for kw in keywords]
    except:
        return []


def calculate_keyword_score(
    resume_text: str,
    jd_keywords: List[str]
) -> float:
    if not jd_keywords or not resume_text:
        return 0.0

    resume_lower = resume_text.lower()
    matched = 0

    for keyword in jd_keywords:
        if keyword.lower() in resume_lower:
            matched += 1

    return round((matched / len(jd_keywords)) * 100, 2)


def generate_score_breakdown(
    skills_score: float,
    experience_score: float,
    keyword_score: float,
    text_similarity: float
) -> Dict:
    return {
        "skills_match": {
            "score": skills_score,
            "weight": "40%",
            "contribution": round(skills_score * 0.40, 2),
            "explanation": "How many required skills the candidate has"
        },
        "experience_match": {
            "score": experience_score,
            "weight": "25%",
            "contribution": round(experience_score * 0.25, 2),
            "explanation": "How well experience years match the requirement"
        },
        "keyword_match": {
            "score": keyword_score,
            "weight": "20%",
            "contribution": round(keyword_score * 0.20, 2),
            "explanation": "How many JD keywords appear in the resume"
        },
        "text_similarity": {
            "score": round(text_similarity * 100, 2),
            "weight": "15%",
            "contribution": round(text_similarity * 100 * 0.15, 2),
            "explanation": "Overall text similarity using TF-IDF cosine similarity"
        }
    }


def generate_strengths(
    matched_skills: List[str],
    experience_years: float,
    overall_score: float
) -> List[str]:
    strengths = []
    if len(matched_skills) > 5:
        strengths.append(
            f"Strong skill alignment with {len(matched_skills)} matching skills"
        )
    if matched_skills:
        top_skills = ", ".join(matched_skills[:3])
        strengths.append(f"Proficient in key required skills: {top_skills}")
    if experience_years >= 3:
        strengths.append(
            f"{experience_years} years of experience demonstrates solid background"
        )
    if overall_score >= 70:
        strengths.append("Overall strong candidate profile for this role")
    return strengths if strengths else ["Candidate shows potential for the role"]


def generate_weaknesses(
    missing_skills: List[str],
    experience_years: float,
    required_experience: str
) -> List[str]:
    weaknesses = []
    if missing_skills:
        missing_str = ", ".join(missing_skills[:3])
        weaknesses.append(f"Missing required skills: {missing_str}")
    if len(missing_skills) > 3:
        weaknesses.append(
            f"{len(missing_skills) - 3} additional required skills not found"
        )
    numbers = re.findall(r'\d+', str(required_experience or ""))
    if numbers and experience_years < float(numbers[0]):
        gap = float(numbers[0]) - experience_years
        weaknesses.append(
            f"Experience gap of {gap:.1f} years below minimum requirement"
        )
    return weaknesses if weaknesses else ["No major weaknesses identified"]


def generate_suggestions(
    missing_skills: List[str],
    weaknesses: List[str]
) -> List[str]:
    suggestions = []
    if missing_skills:
        for skill in missing_skills[:3]:
            suggestions.append(
                f"Add '{skill}' to your skillset — consider online courses or projects"
            )
    suggestions.append(
        "Quantify achievements with numbers (e.g. 'Improved performance by 40%')"
    )
    suggestions.append(
        "Use keywords from the job description naturally throughout your resume"
    )
    suggestions.append(
        "Add a strong professional summary at the top of your resume"
    )
    return suggestions


def analyze_resume_against_jd(resume: dict, jd: dict) -> dict:
    """
    MAIN FUNCTION — Full analysis of one resume against one job description.
    """
    print(f"Analyzing: {resume.get('candidate_name')} vs JD: {jd.get('title')}")

    skills_result = calculate_skills_score(
        resume_skills=resume.get("skills", []),
        required_skills=jd.get("required_skills", [])
    )
    skills_score = skills_result["score"]

    experience_score = calculate_experience_score(
        resume_years=resume.get("experience_years", 0),
        required_experience=jd.get("required_experience", "")
    )

    jd_keywords = jd.get("keywords", [])
    if not jd_keywords:
        jd_keywords = extract_keywords_from_jd(jd.get("description_text", ""))

    keyword_score = calculate_keyword_score(
        resume_text=resume.get("raw_text", ""),
        jd_keywords=jd_keywords
    )

    text_similarity = calculate_tfidf_similarity(
        resume.get("raw_text", ""),
        jd.get("description_text", "")
    )

    overall_score = (
        skills_score * 0.40 +
        experience_score * 0.25 +
        keyword_score * 0.20 +
        text_similarity * 100 * 0.15
    )
    overall_score = round(min(overall_score, 100.0), 2)

    strengths = generate_strengths(
        skills_result["matched"],
        resume.get("experience_years", 0),
        overall_score
    )

    weaknesses = generate_weaknesses(
        skills_result["missing"],
        resume.get("experience_years", 0),
        jd.get("required_experience", "")
    )

    suggestions = generate_suggestions(
        skills_result["missing"],
        weaknesses
    )

    score_breakdown = generate_score_breakdown(
        skills_score, experience_score,
        keyword_score, text_similarity
    )

    print(f"Overall score: {overall_score}")

    return {
        "overall_score": overall_score,
        "skills_score": skills_score,
        "experience_score": experience_score,
        "keyword_score": keyword_score,
        "matched_skills": skills_result["matched"],
        "missing_skills": skills_result["missing"],
        "extra_skills": skills_result["extra"],
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "score_breakdown": score_breakdown,
        "recommended_roles": []
    }


def rank_candidates(analyses: List[dict]) -> List[dict]:
    sorted_analyses = sorted(
        analyses,
        key=lambda x: x["overall_score"],
        reverse=True
    )
    for i, analysis in enumerate(sorted_analyses):
        analysis["rank"] = i + 1
    return sorted_analyses