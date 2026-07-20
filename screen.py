import os
import sys
import argparse
import re
import json
from dotenv import load_dotenv

# Load configurations
load_dotenv()

# Add current path to sys.path to resolve local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.parser import extract_text_from_pdf
from utils.skills import analyze_skills_overlap
from utils.similarity import calculate_semantic_similarity
from utils.ats import analyze_ats_compliance
from utils.llm import query_resume_screening_llm
from utils.report import generate_text_report
from utils.shortlist import compile_shortlist
from utils.helpers import generate_unique_id, sanitize_filename

# ANSI Terminal Colors
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_RED = "\033[91m"
C_CYAN = "\033[96m"
C_MAGENTA = "\033[95m"
C_BOLD = "\033[1m"
C_RESET = "\033[0m"

def log_header(title: str):
    print("\n" + C_BOLD + C_MAGENTA + "=" * 80 + C_RESET)
    print(C_BOLD + C_MAGENTA + f" {title.upper()} ".center(80, "=") + C_RESET)
    print(C_BOLD + C_MAGENTA + "=" * 80 + C_RESET + "\n")

def parse_args():
    parser = argparse.ArgumentParser(
        description="AI Resume Screening Agent CLI - Match resumes against job descriptions."
    )
    parser.add_argument(
        "--jd", 
        required=True, 
        help="The job description text or path to a text file containing the job description."
    )
    parser.add_argument(
        "--folder", 
        default="sample_resumes", 
        help="Path to the directory containing candidate PDF resumes (default: sample_resumes)."
    )
    parser.add_argument(
        "--output", 
        default="reports", 
        help="Directory to save the analysis reports and shortlist (default: reports)."
    )
    return parser.parse_args()

def main():
    args = parse_args()
    
    log_header("AI Resume Screening Pipeline Initializing")
    
    # 1. Resolve Job Description
    jd_content = ""
    if os.path.exists(args.jd):
        print(f"Reading job description from file: {args.jd}")
        try:
            with open(args.jd, 'r', encoding='utf-8') as f:
                jd_content = f.read().strip()
        except Exception as e:
            print(f"{C_RED}Error reading JD file: {e}{C_RESET}")
            sys.exit(1)
    else:
        jd_content = args.jd.strip()
        
    if not jd_content:
        print(f"{C_RED}Error: Job description content cannot be empty.{C_RESET}")
        sys.exit(1)
        
    # 2. Check Resumes Directory
    resume_dir = args.folder
    if not os.path.exists(resume_dir) or not os.path.isdir(resume_dir):
        print(f"{C_RED}Error: Resume folder directory '{resume_dir}' does not exist.{C_RESET}")
        print("Please check the path or run 'python utils/generate_samples.py' first.")
        sys.exit(1)
        
    pdf_files = [f for f in os.listdir(resume_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"{C_RED}Error: No PDF files found in '{resume_dir}'. Please upload candidate resumes.{C_RESET}")
        sys.exit(1)
        
    print(f"Found {len(pdf_files)} candidate resumes to evaluate...")
    
    # Verify API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print(f"{C_YELLOW}WARNING: GROQ_API_KEY not found in environment. Running in Offline Mock mode.{C_RESET}")
        print("Set GROQ_API_KEY in a .env file for live LLM assessments.")
    else:
        print("Groq API key loaded successfully.")
        
    # 3. Process each candidate
    screened_candidates = []
    
    for idx, filename in enumerate(pdf_files, 1):
        filepath = os.path.join(resume_dir, filename)
        print(f"\n[{idx}/{len(pdf_files)}] {C_BOLD}Screening Candidate File: {filename}{C_RESET}...")
        
        try:
            # Parse Text
            print(" -> Extracting PDF structures...")
            resume_text = extract_text_from_pdf(filepath)
            
            if not resume_text or len(resume_text.strip()) == 0:
                print(f" -> {C_RED}Skip: No readable text extracted.{C_RESET}")
                continue
                
            # Parse Skills
            print(" -> Analyzing technical and soft skills...")
            found_skills_cat, missing_skills_cat, found_skills_flat, missing_skills_flat = analyze_skills_overlap(
                resume_text, jd_content
            )
            
            # Semantic Similarity
            print(" -> Calculating semantic cosine similarity...")
            semantic_score = calculate_semantic_similarity(resume_text, jd_content)
            
            # ATS scorecard
            print(" -> Auditing ATS structure headings & contact data...")
            ats_data = analyze_ats_compliance(resume_text, jd_content, found_skills_flat, missing_skills_flat)
            ats_score = ats_data.get("ats_score", 0.0)
            
            # Query LLM
            print(" -> Consulting Groq LLM agent Matchmaker analysis...")
            llm_report = query_resume_screening_llm(
                resume_text=resume_text,
                jd_text=jd_content,
                extracted_skills=found_skills_cat,
                missing_skills=missing_skills_cat
            )
            
            # Weighted Scoring
            experience_score = float(llm_report.get("experience_score", 50))
            education_score = float(llm_report.get("education_score", 50))
            overall_match_score = (ats_score * 0.3) + (semantic_score * 0.3) + (experience_score * 0.3) + (education_score * 0.1)
            overall_match_score = round(overall_match_score, 2)
            
            # Name fallback
            candidate_name = llm_report.get("candidate_name", "Candidate")
            if candidate_name == "Unknown Candidate":
                clean_name = filename.rsplit('.', 1)[0]
                clean_name = re.sub(r'[-_]', ' ', clean_name)
                clean_name = re.sub(r'(?i)\b(resume|cv|file|screening|job|desc)\b', '', clean_name)
                candidate_name = clean_name.strip().title() or "Unknown Candidate"
                
            # Compile individual report path
            report_id = generate_unique_id()
            candidate_data = {
                "id": report_id,
                "candidate_name": candidate_name,
                "overall_match_score": overall_match_score,
                "semantic_similarity_score": semantic_score,
                "ats_score": ats_score,
                "experience_score": experience_score,
                "education_score": education_score,
                
                "found_skills": found_skills_cat,
                "missing_skills": missing_skills_cat,
                "found_skills_flat": found_skills_flat,
                "missing_skills_flat": missing_skills_flat,
                
                "ats_checklist": ats_data.get("sections_found", {}),
                "ats_contacts": ats_data.get("contact_info", {}),
                "formatting_issues": ats_data.get("formatting_issues", []),
                
                "candidate_summary": llm_report.get("candidate_summary", ""),
                "strengths": llm_report.get("strengths", []),
                "weaknesses": llm_report.get("weaknesses", []),
                "suggested_improvements": llm_report.get("suggested_improvements", []),
                "missing_keywords": llm_report.get("missing_keywords", []),
                "hiring_recommendation": llm_report.get("hiring_recommendation", "Borderline"),
                "recruiter_verdict": llm_report.get("recruiter_verdict", ""),
                "interview_readiness": llm_report.get("interview_readiness", "Medium"),
                "suggested_interview_questions": llm_report.get("suggested_interview_questions", [])
            }
            
            # Save single report
            sanitized_name = sanitize_filename(candidate_name)
            report_filename = f"{report_id}_{sanitized_name}_report.txt"
            report_path = os.path.join(args.output, report_filename)
            generate_text_report(candidate_data, report_path)
            
            # Console reporting
            color = C_GREEN if overall_match_score >= 70 else (C_YELLOW if overall_match_score >= 50 else C_RED)
            print(f" -> {C_BOLD}Evaluated:{C_RESET} {candidate_name}")
            print(f" -> {C_BOLD}Score:{C_RESET} {color}{overall_match_score}%{C_RESET} | {C_BOLD}Verdict:{C_RESET} {candidate_data['hiring_recommendation']}")
            
            screened_candidates.append(candidate_data)
            
        except Exception as e:
            print(f" -> {C_RED}Error screening candidate '{filename}': {e}{C_RESET}")
            continue

    # 4. Shortlist compile
    if not screened_candidates:
        print(f"{C_RED}No resumes were successfully screened. Check logs above.{C_RESET}")
        sys.exit(1)
        
    log_header("Compiling Shortlist Rankings")
    shortlist_paths = compile_shortlist(screened_candidates, args.output)
    
    # Save the raw full results as historical screening record
    history_path = os.path.join(args.output, "history.json")
    # Store summaries for UI history loading
    lightweight_history = []
    for res in screened_candidates:
        entry = {
            "id": res["id"],
            "candidate_name": res["candidate_name"],
            "overall_match_score": res["overall_match_score"],
            "semantic_similarity_score": res["semantic_similarity_score"],
            "ats_score": res["ats_score"],
            "hiring_recommendation": res["hiring_recommendation"],
            "interview_readiness": res["interview_readiness"],
            "timestamp": "CLI Matcher Run",
            "skills_count": len(res.get("found_skills_flat", []))
        }
        lightweight_history.append(entry)
        
        # Save individual JSON files to allow dashboard loading
        json_report_path = os.path.join(args.output, f"{res['id']}.json")
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(res, f, indent=2, ensure_ascii=False)
            
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(lightweight_history, f, indent=2, ensure_ascii=False)
        
    print(f"Saved ranked Shortlist table:   {C_GREEN}{shortlist_paths['csv']}{C_RESET}")
    print(f"Saved JSON shortlist data:      {C_GREEN}{shortlist_paths['json']}{C_RESET}")
    print(f"Saved individual reports folder: {C_GREEN}{args.output}/{C_RESET}")
    
    # Display Leaderboard
    print("\n" + C_BOLD + " RANKED LEADERBOARD SUMMARY ".center(80, "#") + C_RESET + "\n")
    sorted_ranks = sorted(screened_candidates, key=lambda x: x.get("overall_match_score", 0.0), reverse=True)
    
    print(f"{'Rank':<5} | {'Candidate Name':<20} | {'Match Score':<12} | {'ATS Score':<10} | {'Verdict':<15}")
    print("-" * 80)
    for idx, c in enumerate(sorted_ranks, 1):
        color = C_GREEN if c['overall_match_score'] >= 70 else (C_YELLOW if c['overall_match_score'] >= 50 else C_RED)
        print(f"{idx:<5} | {c['candidate_name']:<20} | {color}{c['overall_match_score']:>10}%{C_RESET} | {c['ats_score']:>8}% | {c['hiring_recommendation']:<15}")
        
    print("\n" + C_BOLD + C_GREEN + "SCREENING PIPELINE COMPLETED SUCCESSFULLY!" + C_RESET + "\n")

if __name__ == "__main__":
    main()
