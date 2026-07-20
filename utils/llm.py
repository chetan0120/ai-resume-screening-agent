import os
import json
import re
from typing import Dict, Any, List
from groq import Groq
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Pre-defined list of models to try in case of rate limits or service unavailability
GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3-3-70b-versatile",
    "llama3-70b-8192",
    "mixtral-8x7b-32768"
]

def get_groq_client() -> Groq:
    """
    Retrieves the Groq API client if the API key is present.
    Raises ValueError if API key is missing.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured in the environment (.env file).")
    return Groq(api_key=api_key)

def query_resume_screening_llm(resume_text: str, jd_text: str, extracted_skills: Dict[str, List[str]], missing_skills: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Sends the resume, job description, and pre-extracted skill metrics to Groq to generate a structured report.
    
    Args:
        resume_text (str): Extracted resume text.
        jd_text (str): Job description text.
        extracted_skills (Dict[str, List[str]]): Pre-extracted categorized skills.
        missing_skills (Dict[str, List[str]]): Pre-extracted missing skills.
        
    Returns:
        Dict[str, Any]: Analyzed structured metrics and summaries.
    """
    try:
        client = get_groq_client()
    except ValueError as e:
        return get_error_fallback_response(str(e))
        
    system_prompt = (
        "You are an Elite Technical Recruiter and Senior Talent Acquisition Architect. "
        "Your task is to critically analyze the candidate's Resume against the provided Job Description. "
        "You must return your evaluation in a strictly valid JSON format. Do not write any conversational text, "
        "preamble, or post-explanation outside of the JSON structure. Ensure the JSON is clean and parsable.\n\n"
        "Here is the required JSON structure and type specifications:\n"
        "{\n"
        '  "candidate_name": "<string: candidate\'s full name, extracted from the top of the resume. If not found, use \'Unknown Candidate\'>",\n'
        '  "experience_score": <int: 0-100 score indicating candidate\'s experience relevance>,\n'
        '  "education_score": <int: 0-100 score representing candidate\'s educational alignment>,\n'
        '  "candidate_summary": "<string: concise 3-4 sentence professional summary of candidate\'s suitability>",\n'
        '  "strengths": [<string: list of key technical or leadership strengths>],\n'
        '  "weaknesses": [<string: list of key candidate gaps, areas of concern, or lack of critical experience>],\n'
        '  "suggested_improvements": [<string: list of specific, actionable advice to improve their resume/fit>],\n'
        '  "missing_keywords": [<string: key industry-standard terminology or buzzwords missing from the resume>],\n'
        '  "hiring_recommendation": "<string: Strong Hire | Hire | Borderline | Reject>",\n'
        '  "recruiter_verdict": "<string: a 2-paragraph justification for the hiring recommendation from a technical recruiter perspective>",\n'
        '  "interview_readiness": "<string: High | Medium | Low>",\n'
        '  "suggested_interview_questions": [\n'
        "    {\n"
        '      "question": "<string: highly targeted, technical, or soft skill question tailored to this candidate\'s background vs the JD>",\n'
        '      "expected_answer": "<string: guidelines for what a strong answer should cover, including technical keywords>",\n'
        '      "difficulty": "<string: Easy | Medium | Hard>"\n'
        "    }\n"
        "  ]\n"
        "}"
    )

    user_content = (
        f"--- JOB DESCRIPTION ---\n{jd_text}\n\n"
        f"--- CANDIDATE RESUME ---\n{resume_text}\n\n"
        f"--- PRE-EXTRACTED CANDIDATE SKILLS ---\n{json.dumps(extracted_skills)}\n\n"
        f"--- EXTRACTED MISSING SKILLS REQUIRED BY JD ---\n{json.dumps(missing_skills)}\n\n"
        "Perform a thorough match evaluation. Provide objective scores based on qualifications. Be critical and professional."
    )

    # Attempt to query Groq using one of the models
    last_error = None
    for model_name in GROQ_MODELS:
        try:
            print(f"Querying Groq model: {model_name}...")
            # We enforce json_object to guarantee structural returns
            chat_completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=2500
            )
            
            response_text = chat_completion.choices[0].message.content
            parsed_json = json.loads(response_text)
            
            # Validation checks on response
            required_keys = ["candidate_name", "experience_score", "education_score", "candidate_summary", 
                             "strengths", "weaknesses", "suggested_improvements", "missing_keywords", 
                             "hiring_recommendation", "recruiter_verdict", "interview_readiness", 
                             "suggested_interview_questions"]
                             
            # Inject defaults if keys are missing
            for key in required_keys:
                if key not in parsed_json:
                    parsed_json[key] = get_default_fallback_value(key)
                    
            return parsed_json
            
        except Exception as e:
            print(f"Error querying {model_name}: {e}")
            last_error = e
            continue
            
    # If all models fail, trigger error fallback response
    error_msg = f"Groq API call failed. Details: {str(last_error)}" if last_error else "All Groq model attempts failed."
    return get_error_fallback_response(error_msg)

def get_default_fallback_value(key: str) -> Any:
    """Returns a safe default value for specific keys in the JSON response."""
    defaults = {
        "candidate_name": "Unknown Candidate",
        "experience_score": 50,
        "education_score": 50,
        "candidate_summary": "Unable to generate summary due to analysis failure.",
        "strengths": ["Not analyzed"],
        "weaknesses": ["Not analyzed"],
        "suggested_improvements": ["Ensure resume formatting is standardized"],
        "missing_keywords": ["N/A"],
        "hiring_recommendation": "Borderline",
        "recruiter_verdict": "Automatic analysis system fallback.",
        "interview_readiness": "Medium",
        "suggested_interview_questions": [
            {
                "question": "Can you walk me through your technical experience and projects?",
                "expected_answer": "Candidate should summarize past engineering projects.",
                "difficulty": "Medium"
            }
        ]
    }
    return defaults.get(key, None)

def get_error_fallback_response(error_message: str) -> Dict[str, Any]:
    """Generates a graceful fallback JSON response when the API is down or unavailable."""
    return {
        "candidate_name": "Unknown Candidate",
        "experience_score": 0,
        "education_score": 0,
        "candidate_summary": f"Could not generate report automatically. {error_message}",
        "strengths": ["Check manual analysis reports"],
        "weaknesses": ["Check manual analysis reports"],
        "suggested_improvements": ["Check your API key setup in .env"],
        "missing_keywords": ["Error API key missing or invalid"],
        "hiring_recommendation": "Borderline",
        "recruiter_verdict": f"The LLM server could not be reached. Details: {error_message}",
        "interview_readiness": "Medium",
        "suggested_interview_questions": [
            {
                "question": "Could you describe a challenging technical problem you solved recently?",
                "expected_answer": "Look for structure: Problem, Action, Result (STAR method).",
                "difficulty": "Medium"
            }
        ],
        "api_error": True,
        "error_details": error_message
    }
