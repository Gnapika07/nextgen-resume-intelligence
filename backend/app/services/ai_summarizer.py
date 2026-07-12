from typing import List


def generate_ai_summary(
    candidate_name: str,
    skills: List[str],
    experience_years: float,
    overall_score: float,
    matched_skills: List[str],
    missing_skills: List[str],
    job_title: str
) -> str:
    """
    Generate a human-readable AI summary for a candidate.
    This is the Explainable AI feature — explains the score in plain English.
    """
    name = candidate_name or "The candidate"
    score_label = get_score_label(overall_score)
    top_skills = ", ".join(skills[:5]) if skills else "general skills"
    matched_str = ", ".join(matched_skills[:3]) if matched_skills else "some"
    missing_str = ", ".join(missing_skills[:2]) if missing_skills else "none"

    if overall_score >= 80:
        summary = (
            f"{name} is an {score_label} for the {job_title} role with a score of "
            f"{overall_score:.1f}/100. They demonstrate strong proficiency in "
            f"{matched_str} — all key requirements for this position. "
            f"With {experience_years} years of experience and a comprehensive "
            f"skill set including {top_skills}, this candidate stands out as a "
            f"top contender. "
        )
        if missing_skills:
            summary += f"Minor gaps in {missing_str} could be addressed through onboarding."
        else:
            summary += "No significant skill gaps were identified."

    elif overall_score >= 60:
        summary = (
            f"{name} is a {score_label} for the {job_title} role with a score of "
            f"{overall_score:.1f}/100. They show solid alignment in {matched_str}. "
            f"With {experience_years} years of experience, they bring valuable "
            f"background to the role. "
        )
        if missing_skills:
            summary += (
                f"Key areas for development include {missing_str}, "
                f"which may require additional training or ramp-up time."
            )

    else:
        summary = (
            f"{name} shows a {score_label} for the {job_title} role with a score of "
            f"{overall_score:.1f}/100. While they have experience in {matched_str}, "
            f"there are notable gaps in {missing_str} that are critical for this position. "
            f"With {experience_years} years of experience, they may benefit from "
            f"targeted upskilling before fully meeting the role requirements."
        )

    return summary


def generate_resume_improvement_suggestions(
    skills: List[str],
    missing_skills: List[str],
    experience_years: float,
    overall_score: float
) -> List[str]:
    """
    Generate specific, actionable resume improvement tips.
    """
    suggestions = []

    # Skill-based suggestions
    if missing_skills:
        for skill in missing_skills[:2]:
            suggestions.append(
                f"Learn {skill}: Add it to projects or take a "
                f"certification course to strengthen your profile"
            )

    # Score-based suggestions
    if overall_score < 60:
        suggestions.append(
            "Tailor your resume specifically for each job — "
            "use keywords directly from the job description"
        )
        suggestions.append(
            "Add a strong 3-line professional summary at the top "
            "highlighting your most relevant skills"
        )

    if overall_score < 80:
        suggestions.append(
            "Quantify your achievements — instead of 'improved performance', "
            "write 'improved performance by 35% using Python optimization'"
        )
        suggestions.append(
            "Add GitHub links to projects that demonstrate your technical skills"
        )

    # Experience suggestions
    if experience_years < 2:
        suggestions.append(
            "Build 2-3 portfolio projects showcasing relevant skills "
            "and add them to your resume with clear descriptions"
        )

    # General best practices
    suggestions.append(
        "Keep resume to 1-2 pages — recruiters spend average 6 seconds on first scan"
    )
    suggestions.append(
        "Use action verbs: Built, Developed, Designed, Implemented, Optimized"
    )

    return suggestions


def get_score_label(score: float) -> str:
    if score >= 85:
        return "Excellent Match"
    elif score >= 70:
        return "Strong Match"
    elif score >= 55:
        return "Good Match"
    elif score >= 40:
        return "Partial Match"
    else:
        return "Low Match"