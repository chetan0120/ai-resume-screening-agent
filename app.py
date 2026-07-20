import os
import json
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename

# Import local utilities
from utils.parser import extract_text_from_pdf
from utils.skills import analyze_skills_overlap
from utils.similarity import calculate_semantic_similarity
from utils.ats import analyze_ats_compliance
from utils.llm import query_resume_screening_llm
from utils.report import generate_text_report
from utils.helpers import (
    allowed_file, 
    generate_unique_id, 
    sanitize_filename, 
    save_to_history, 
    get_screening_history
)
from utils.shortlist import compile_shortlist

app = Flask(__name__)

# Application Configuration
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
REPORT_FOLDER = os.path.join(os.getcwd(), 'reports')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORT_FOLDER'] = REPORT_FOLDER
# Set maximum upload size limit to 8MB
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
app.config['SECRET_KEY'] = 'dev-resume-screening-agent-key-192837'

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """
    Renders the main dashboard index page.
    """
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Pipeline route that uploads a PDF resume, parses it, extracts details,
    calculates metrics, calls LLM, saves report files, and updates history.
    """
    # 1. Validation checks
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file uploaded. Please attach a PDF resume."}), 400
        
    file = request.files['resume']
    jd_text = request.form.get('job_description', '').strip()
    
    if file.filename == '':
        return jsonify({"error": "No file selected. Please choose a valid PDF resume."}), 400
        
    if not jd_text:
        return jsonify({"error": "Job description cannot be empty. Please paste a JD to match against."}), 400
        
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file format. Only PDF files (.pdf) are supported."}), 400
        
    try:
        # 2. Setup IDs and save temporary upload file
        report_id = generate_unique_id()
        original_filename = secure_filename(file.filename)
        temp_filename = f"{report_id}_{original_filename}"
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        file.save(temp_path)
        
        # 3. Extract text
        print(f"Extracting text from {temp_path}...")
        resume_text = extract_text_from_pdf(temp_path)
        
        if not resume_text or len(resume_text.strip()) == 0:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return jsonify({"error": "We could not extract any readable text from this PDF. Please verify that the PDF contains copyable text (not just scanned images)."}), 400
            
        # 4. Perform skill matching & classification
        print("Extracting and aligning skills...")
        found_skills_categorized, missing_skills_categorized, found_skills_flat, missing_skills_flat = analyze_skills_overlap(resume_text, jd_text)
        
        # 5. Compute semantic similarity
        print("Running semantic similarity...")
        semantic_score = calculate_semantic_similarity(resume_text, jd_text)
        
        # 6. Assess ATS checklist alignment
        print("Evaluating ATS scoring metric...")
        ats_data = analyze_ats_compliance(resume_text, jd_text, found_skills_flat, missing_skills_flat)
        ats_score = ats_data.get("ats_score", 0.0)
        
        # 7. Feed data into LLM for deeper recruiters evaluations
        print("Invoking Groq LLM agent screening analysis...")
        llm_report = query_resume_screening_llm(
            resume_text=resume_text,
            jd_text=jd_text,
            extracted_skills=found_skills_categorized,
            missing_skills=missing_skills_categorized
        )
        
        # Extract individual scores from the LLM assessment
        experience_score = float(llm_report.get("experience_score", 50))
        education_score = float(llm_report.get("education_score", 50))
        
        # 8. Calculate unified overall match score
        # Formula: ATS (30%), Semantic (30%), Experience (30%), Education (10%)
        overall_match_score = (ats_score * 0.3) + (semantic_score * 0.3) + (experience_score * 0.3) + (education_score * 0.1)
        overall_match_score = round(overall_match_score, 2)
        
        # 9. Formulate full combined dataset
        candidate_name = llm_report.get("candidate_name", "Candidate")
        if candidate_name == "Unknown Candidate":
            # Extract name fallback from clean filename (e.g. "John_Doe_CV" -> "John Doe")
            clean_fn = original_filename.rsplit('.', 1)[0]
            clean_fn = re.sub(r'[-_]', ' ', clean_fn)
            clean_fn = re.sub(r'(?i)\b(resume|cv|file|screening|job|desc)\b', '', clean_fn)
            candidate_name = clean_fn.strip().title() or "Unknown Candidate"
            
        full_report_data = {
            "id": report_id,
            "candidate_name": candidate_name,
            "overall_match_score": overall_match_score,
            "semantic_similarity_score": semantic_score,
            "ats_score": ats_score,
            "experience_score": experience_score,
            "education_score": education_score,
            
            "found_skills": found_skills_categorized,
            "missing_skills": missing_skills_categorized,
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
        
        # 10. Persist Report files to disk
        # Save structured JSON
        json_report_path = os.path.join(app.config['REPORT_FOLDER'], f"{report_id}.json")
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(full_report_data, f, indent=2, ensure_ascii=False)
            
        # Save formatted plaintext report
        text_report_filename = f"{report_id}_{sanitize_filename(candidate_name)}_report.txt"
        text_report_path = os.path.join(app.config['REPORT_FOLDER'], text_report_filename)
        generate_text_report(full_report_data, text_report_path)
        
        # Attach the text filename to the return payload for downloading
        full_report_data["download_filename"] = text_report_filename
        
        # 11. Append to recent screenings log
        save_to_history(full_report_data)
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return jsonify(full_report_data)
        
    except Exception as e:
        print(f"Server critical exception: {e}")
        # Make sure to cleanup file if present
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({"error": f"An unexpected error occurred during analysis: {str(e)}"}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """
    Retrieves the lightweight list of recent screenings.
    """
    history = get_screening_history()
    return jsonify(history)

@app.route('/clear-history', methods=['POST'])
def clear_history():
    """
    Clears all saved screenings from history list.
    """
    history_file_path = os.path.join(app.config['REPORT_FOLDER'], "history.json")
    if os.path.exists(history_file_path):
        try:
            with open(history_file_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
            return jsonify({"status": "success", "message": "Screening history cleared successfully."})
        except Exception as e:
            return jsonify({"error": f"Failed to clear history: {str(e)}"}), 500
    return jsonify({"status": "success", "message": "History already empty."})

@app.route('/load-report/<report_id>', methods=['GET'])
def load_report(report_id):
    """
    Retrieves the complete data of a specific screening report.
    """
    json_path = os.path.join(app.config['REPORT_FOLDER'], f"{report_id}.json")
    if not os.path.exists(json_path):
        return jsonify({"error": f"Report with ID {report_id} not found."}), 404
        
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Dynamically verify if text report is present to supply the download filename
        candidate_name = data.get("candidate_name", "Candidate")
        text_report_filename = f"{report_id}_{sanitize_filename(candidate_name)}_report.txt"
        data["download_filename"] = text_report_filename
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"Failed to load report: {str(e)}"}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """
    Exposes report text file for download.
    """
    # Standard security checks on filename to prevent path traversal
    filename = secure_filename(filename)
    report_path = os.path.join(app.config['REPORT_FOLDER'], filename)
    if not os.path.exists(report_path):
        return "Report file not found", 404
        
    return send_from_directory(
        directory=app.config['REPORT_FOLDER'],
        path=filename,
        as_attachment=True
    )

@app.route('/analyze_batch', methods=['POST'])
def analyze_batch():
    """
    Evaluates multiple resumes in a single run against a job description,
    ranks them, and generates shortlist summaries (CSV and JSON).
    """
    # Grab the files from the request (supports multiple inputs under 'resumes' or 'resumes[]')
    files = request.files.getlist('resumes') or request.files.getlist('resumes[]')
    jd_text = request.form.get('job_description', '').strip()
    
    if not files or len(files) == 0 or (len(files) == 1 and files[0].filename == ''):
        return jsonify({"error": "No resume files uploaded. Please attach one or more PDF resumes."}), 400
        
    if not jd_text:
        return jsonify({"error": "Job description cannot be empty. Please paste a JD to match against."}), 400
        
    screened_candidates = []
    skipped_files = []
    
    import re
    
    for file in files:
        if not file or file.filename == '':
            continue
            
        if not allowed_file(file.filename):
            skipped_files.append(f"{file.filename} (Invalid format, only PDF allowed)")
            continue
            
        temp_path = None
        try:
            report_id = generate_unique_id()
            original_filename = secure_filename(file.filename)
            temp_filename = f"{report_id}_{original_filename}"
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
            file.save(temp_path)
            
            # Extract text
            resume_text = extract_text_from_pdf(temp_path)
            if not resume_text or len(resume_text.strip()) == 0:
                skipped_files.append(f"{file.filename} (Unreadable or empty PDF)")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                continue
                
            # Run algorithms
            found_skills_categorized, missing_skills_categorized, found_skills_flat, missing_skills_flat = analyze_skills_overlap(resume_text, jd_text)
            semantic_score = calculate_semantic_similarity(resume_text, jd_text)
            ats_data = analyze_ats_compliance(resume_text, jd_text, found_skills_flat, missing_skills_flat)
            ats_score = ats_data.get("ats_score", 0.0)
            
            # Query LLM
            llm_report = query_resume_screening_llm(
                resume_text=resume_text,
                jd_text=jd_text,
                extracted_skills=found_skills_categorized,
                missing_skills=missing_skills_categorized
            )
            
            experience_score = float(llm_report.get("experience_score", 50))
            education_score = float(llm_report.get("education_score", 50))
            
            # Weighted Overall Score
            overall_match_score = (ats_score * 0.3) + (semantic_score * 0.3) + (experience_score * 0.3) + (education_score * 0.1)
            overall_match_score = round(overall_match_score, 2)
            
            candidate_name = llm_report.get("candidate_name", "Candidate")
            if candidate_name == "Unknown Candidate":
                clean_fn = original_filename.rsplit('.', 1)[0]
                clean_fn = re.sub(r'[-_]', ' ', clean_fn)
                clean_fn = re.sub(r'(?i)\b(resume|cv|file|screening|job|desc)\b', '', clean_fn)
                candidate_name = clean_fn.strip().title() or "Unknown Candidate"
                
            full_report_data = {
                "id": report_id,
                "candidate_name": candidate_name,
                "overall_match_score": overall_match_score,
                "semantic_similarity_score": semantic_score,
                "ats_score": ats_score,
                "experience_score": experience_score,
                "education_score": education_score,
                
                "found_skills": found_skills_categorized,
                "missing_skills": missing_skills_categorized,
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
            
            # Save single report formats
            json_report_path = os.path.join(app.config['REPORT_FOLDER'], f"{report_id}.json")
            with open(json_report_path, 'w', encoding='utf-8') as f:
                json.dump(full_report_data, f, indent=2, ensure_ascii=False)
                
            text_report_filename = f"{report_id}_{sanitize_filename(candidate_name)}_report.txt"
            text_report_path = os.path.join(app.config['REPORT_FOLDER'], text_report_filename)
            generate_text_report(full_report_data, text_report_path)
            
            full_report_data["download_filename"] = text_report_filename
            
            # Append to history drawer list
            save_to_history(full_report_data)
            
            screened_candidates.append(full_report_data)
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        except Exception as e:
            print(f"Failed to screen candidate file: {file.filename}. Error: {e}")
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            skipped_files.append(f"{file.filename} (Analysis failed: {str(e)})")
            
    if not screened_candidates:
        return jsonify({"error": "Failed to successfully screen any of the uploaded resumes.", "skipped": skipped_files}), 400
        
    # Compile ranked shortlist CSV/JSON
    shortlist_paths = compile_shortlist(screened_candidates, app.config['REPORT_FOLDER'])
    
    # Sort the results descending to display on the leaderboard
    ranked_leaderboard = sorted(screened_candidates, key=lambda x: x.get("overall_match_score", 0.0), reverse=True)
    
    return jsonify({
        "status": "success",
        "shortlist_created": True,
        "leaderboard": ranked_leaderboard,
        "skipped": skipped_files,
        "csv_shortlist_filename": "shortlist.csv",
        "json_shortlist_filename": "shortlist.json"
    })

@app.route('/download_shortlist/<format_type>', methods=['GET'])
def download_shortlist(format_type):
    """
    Downloads the compiled batch shortlist file (CSV or JSON).
    """
    filename = f"shortlist.{format_type.lower()}"
    filepath = os.path.join(app.config['REPORT_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "Shortlist file has not been compiled yet. Please run a batch screening."}), 404
        
    return send_from_directory(
        directory=app.config['REPORT_FOLDER'],
        path=filename,
        as_attachment=True
    )

if __name__ == '__main__':
    # Listen on all addresses by default (ideal for local/container dev)
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development" or os.getenv("FLASK_DEBUG") == "1"
    app.run(host='0.0.0.0', port=port, debug=debug)
