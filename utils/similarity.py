import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Lazy loader for model to prevent loading on import
_model = None

def get_transformer_model():
    """
    Get or load the sentence transformer model lazily.
    """
    global _model
    if _model is None:
        try:
            print("Initializing SentenceTransformer model (all-MiniLM-L6-v2)...")
            _model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Failed to load sentence transformer model: {e}")
            raise RuntimeError(f"Could not load SentenceTransformer: {str(e)}")
    return _model

def calculate_semantic_similarity(resume_text: str, jd_text: str) -> float:
    """
    Calculates the cosine semantic similarity between the resume and the job description.
    
    Args:
        resume_text (str): Cleaned resume text.
        jd_text (str): Cleaned job description text.
        
    Returns:
        float: Similarity percentage (0 to 100).
    """
    if not resume_text.strip() or not jd_text.strip():
        return 0.0
        
    try:
        model = get_transformer_model()
        
        # Generate embeddings
        embeddings = model.encode([resume_text, jd_text])
        
        # Calculate cosine similarity
        sim_matrix = cosine_similarity([embeddings[0]], [embeddings[1]])
        similarity = float(sim_matrix[0][0])
        
        # Convert to percentage and clip to [0, 100]
        similarity_percentage = max(0.0, min(100.0, similarity * 100.0))
        return round(similarity_percentage, 2)
        
    except Exception as e:
        print(f"Error calculating semantic similarity: {e}")
        # Return fallback score or raise depending on preference
        return 0.0
