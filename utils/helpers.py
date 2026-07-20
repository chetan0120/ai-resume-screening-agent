import os
import re
import uuid
import json
from datetime import datetime
from typing import Dict, List, Any

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename: str) -> bool:
    """
    Checks if a filename has an allowed extension.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_id() -> str:
    """
    Generates a unique screening ID.
    """
    return str(uuid.uuid4().hex[:12])

def sanitize_filename(name: str) -> str:
    """
    Sanitizes candidate names or job titles to make them safe for file system paths.
    """
    # Remove any non-alphanumeric, spaces, underscores, or hyphens
    s = re.sub(r'[^\w\s-]', '', name)
    # Replace spaces and consecutive hyphens/underscores with a single hyphen
    s = re.sub(r'[-\s]+', '-', s)
    return s.strip('-')

def save_to_history(data: Dict[str, Any], history_file_path: str = "reports/history.json") -> None:
    """
    Appends high-level metadata of a screening run to a JSON history file.
    Keeps only the 15 most recent screenings.
    
    Args:
        data (Dict[str, Any]): Screen report full dictionary.
        history_file_path (str): Path to the history list file.
    """
    os.makedirs(os.path.dirname(history_file_path), exist_ok=True)
    
    # Extract only metadata for lightweight retrieval
    entry = {
        "id": data.get("id"),
        "candidate_name": data.get("candidate_name", "Unknown Candidate"),
        "overall_match_score": data.get("overall_match_score", 0),
        "semantic_similarity_score": data.get("semantic_similarity_score", 0),
        "ats_score": data.get("ats_score", 0),
        "hiring_recommendation": data.get("hiring_recommendation", "Borderline"),
        "interview_readiness": data.get("interview_readiness", "Medium"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "skills_count": len(data.get("found_skills_flat", []))
    }
    
    history = []
    if os.path.exists(history_file_path):
        try:
            with open(history_file_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
                if not isinstance(history, list):
                    history = []
        except Exception:
            history = []
            
    # Insert at the beginning of the list
    history.insert(0, entry)
    
    # Cap size at 15
    history = history[:15]
    
    try:
        with open(history_file_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to save screening history: {e}")

def get_screening_history(history_file_path: str = "reports/history.json") -> List[Dict[str, Any]]:
    """
    Reads the history log. Returns an empty list if file doesn't exist.
    """
    if not os.path.exists(history_file_path):
        return []
    try:
        with open(history_file_path, 'r', encoding='utf-8') as f:
            history = json.load(f)
            if isinstance(history, list):
                return history
    except Exception as e:
        print(f"Error reading screening history: {e}")
    return []
