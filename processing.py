def calculate_scores(resume_data: dict) -> dict:
    """
    Returns: {
        "gen_ai_score": 0-100,
        "ai_score": 0-100,
        "grammar_errors": list,
        "missing_sections": list
    }
    """
    # Implementation using HuggingFace transformers
    from transformers import pipeline
    analyzer = pipeline('text-classification', model='distilbert-base-uncased')
    
    # ... existing scoring logic with added input validation ...