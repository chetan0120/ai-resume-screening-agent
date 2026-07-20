import os
import csv
import json
from typing import List, Dict, Any

def compile_shortlist(results: List[Dict[str, Any]], output_dir: str = "reports") -> Dict[str, str]:
    """
    Sorts the screen results by Overall Match Score in descending order
    and writes shortlist.csv and shortlist.json.
    
    Args:
        results (List[Dict[str, Any]]): List of full reports of screened candidates.
        output_dir (str): Directory where outputs should be saved.
        
    Returns:
        Dict[str, str]: Absolute paths of the compiled CSV and JSON shortlist files.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Sort results by Overall Match Score descending
    sorted_results = sorted(results, key=lambda x: x.get("overall_match_score", 0.0), reverse=True)
    
    csv_filename = "shortlist.csv"
    json_filename = "shortlist.json"
    
    csv_path = os.path.join(output_dir, csv_filename)
    json_path = os.path.join(output_dir, json_filename)
    
    # 1. Write CSV shortlist
    headers = [
        "Rank", "Candidate Name", "Overall Match Score (%)", 
        "Semantic Similarity (%)", "ATS Score (%)", 
        "Experience Relevance (%)", "Education Alignment (%)", 
        "Hiring Recommendation", "Interview Readiness", "Strengths", "Weaknesses"
    ]
    
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for idx, res in enumerate(sorted_results, 1):
                writer.writerow([
                    idx,
                    res.get("candidate_name", "Unknown"),
                    f"{res.get('overall_match_score', 0):.2f}",
                    f"{res.get('semantic_similarity_score', 0):.2f}",
                    f"{res.get('ats_score', 0):.2f}",
                    f"{res.get('experience_score', 0):.2f}",
                    f"{res.get('education_score', 0):.2f}",
                    res.get("hiring_recommendation", "Borderline"),
                    res.get("interview_readiness", "Medium"),
                    "; ".join(res.get("strengths", [])[:3]),
                    "; ".join(res.get("weaknesses", [])[:3])
                ])
    except Exception as e:
        print(f"Failed to generate CSV shortlist: {e}")
        
    # 2. Write JSON shortlist (just high-level ranked summary)
    json_summary = []
    for idx, res in enumerate(sorted_results, 1):
        json_summary.append({
            "rank": idx,
            "id": res.get("id"),
            "candidate_name": res.get("candidate_name"),
            "overall_match_score": res.get("overall_match_score"),
            "semantic_similarity_score": res.get("semantic_similarity_score"),
            "ats_score": res.get("ats_score"),
            "experience_score": res.get("experience_score"),
            "education_score": res.get("education_score"),
            "hiring_recommendation": res.get("hiring_recommendation"),
            "interview_readiness": res.get("interview_readiness"),
            "summary_verdict": res.get("candidate_summary")
        })
        
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_summary, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to generate JSON shortlist: {e}")
        
    return {
        "csv": csv_path,
        "json": json_path
    }
