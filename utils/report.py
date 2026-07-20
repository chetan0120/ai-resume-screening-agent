import os
from typing import Dict, Any

def generate_text_report(data: Dict[str, Any], filepath: str) -> None:
    """
    Generates a beautifully structured plaintext recruiter report from the analysis data.
    
    Args:
        data (Dict[str, Any]): Combined analysis output containing all scores, skills, summaries, etc.
        filepath (str): Target file path where the report should be saved.
    """
    # Safeguard directory presence
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    report_content = []
    
    # Header block
    report_content.append("=" * 80)
    report_content.append(" " * 20 + "AI RESUME SCREENING REPORT")
    report_content.append(" " * 12 + "Intelligent Match Candidates with Job Descriptions")
    report_content.append("=" * 80)
    report_content.append("")
    
    # Metadata
    report_content.append(f"Candidate Name:       {data.get('candidate_name', 'Unknown Candidate')}")
    report_content.append(f"Analysis ID:          {data.get('id', 'N/A')}")
    report_content.append(f"Hiring Verdict:       {data.get('hiring_recommendation', 'N/A').upper()}")
    report_content.append(f"Interview Readiness:  {data.get('interview_readiness', 'N/A')}")
    report_content.append("")
    
    # Score Section
    report_content.append("-" * 80)
    report_content.append("MATCH METRICS SCORECARD")
    report_content.append("-" * 80)
    report_content.append(f"Overall Match Score:        {data.get('overall_match_score', 0)}%")
    report_content.append(f"Semantic Similarity Score:  {data.get('semantic_similarity_score', 0)}%")
    report_content.append(f"ATS Compliance Score:       {data.get('ats_score', 0)}%")
    report_content.append(f"Experience Relevance Score: {data.get('experience_score', 0)}%")
    report_content.append(f"Education Alignment Score:  {data.get('education_score', 0)}%")
    report_content.append("")
    
    # Candidate Summary
    report_content.append("-" * 80)
    report_content.append("CANDIDATE SUITABILITY SUMMARY")
    report_content.append("-" * 80)
    report_content.append(data.get('candidate_summary', 'No summary available.'))
    report_content.append("")
    
    # Recruiter Verdict
    report_content.append("-" * 80)
    report_content.append("DETAILED RECRUITER VERDICT")
    report_content.append("-" * 80)
    report_content.append(data.get('recruiter_verdict', 'No verdict generated.'))
    report_content.append("")
    
    # Skill Analysis
    report_content.append("-" * 80)
    report_content.append("SKILL MATCHING MATRIX")
    report_content.append("-" * 80)
    
    # Found Skills (grouped if categorized dict, otherwise list)
    found_skills = data.get('found_skills', [])
    if isinstance(found_skills, dict):
        report_content.append("Skills Found on Resume:")
        has_found = False
        for cat, skills in found_skills.items():
            if skills:
                report_content.append(f"  * {cat.replace('_', ' ').capitalize()}: {', '.join(skills)}")
                has_found = True
        if not has_found:
            report_content.append("  * None detected in standard taxonomy categories.")
    else:
        report_content.append(f"Skills Found: {', '.join(found_skills) if found_skills else 'None'}")
        
    report_content.append("")
    
    # Missing Skills
    missing_skills = data.get('missing_skills', [])
    if isinstance(missing_skills, dict):
        report_content.append("Skills Required by Job Description but MISSING:")
        has_missing = False
        for cat, skills in missing_skills.items():
            if skills:
                report_content.append(f"  * {cat.replace('_', ' ').capitalize()}: {', '.join(skills)}")
                has_missing = True
        if not has_missing:
            report_content.append("  * All standard skills required by the JD match perfectly!")
    else:
        report_content.append(f"Skills Missing: {', '.join(missing_skills) if missing_skills else 'None required missing'}")
        
    report_content.append("")
    
    # Key Strengths & Weaknesses
    report_content.append("-" * 80)
    report_content.append("STRENGTHS & WEAKNESSES AUDIT")
    report_content.append("-" * 80)
    report_content.append("Candidate Strengths:")
    for strength in data.get('strengths', []):
        report_content.append(f"  [+] {strength}")
    report_content.append("")
    
    report_content.append("Candidate Weaknesses/Gaps:")
    for weakness in data.get('weaknesses', []):
        report_content.append(f"  [-] {weakness}")
    report_content.append("")
    
    # ATS / Resume improvements
    report_content.append("-" * 80)
    report_content.append("ATS COMPLIANCE & RESUME IMPROVEMENTS")
    report_content.append("-" * 80)
    report_content.append("Suggested Resume Improvements:")
    for imp in data.get('suggested_improvements', []):
        report_content.append(f"  [!] {imp}")
    report_content.append("")
    
    report_content.append("Missing Keywords / Terminology:")
    missing_kw = data.get('missing_keywords', [])
    report_content.append(f"  {', '.join(missing_kw) if missing_kw else 'No key industry terms missing.'}")
    report_content.append("")
    
    # Interview Readiness & Questions
    report_content.append("-" * 80)
    report_content.append("SUGGESTED INTERVIEW QUESTIONS")
    report_content.append("-" * 80)
    questions = data.get('suggested_interview_questions', [])
    if questions:
        for idx, q_item in enumerate(questions, 1):
            q_text = q_item.get('question', 'N/A')
            ans_text = q_item.get('expected_answer', 'N/A')
            diff = q_item.get('difficulty', 'Medium')
            report_content.append(f"Q{idx}. [{diff}] {q_text}")
            report_content.append(f"    Expected Answer Concept:")
            report_content.append(f"    {ans_text}")
            report_content.append("")
    else:
        report_content.append("No targeted interview questions generated.")
        
    report_content.append("=" * 80)
    report_content.append("End of AI Screening Report - Generated by AI Resume Screening Agent")
    report_content.append("=" * 80)
    
    # Write to target path
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_content))
