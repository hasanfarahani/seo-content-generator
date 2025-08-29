import re
from typing import List, Dict, Any
from datetime import datetime

def clean_text(text: str) -> str:
    """Clean and normalize text for analysis"""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep alphanumeric and spaces
    text = re.sub(r'[^\w\s]', '', text)
    
    return text.strip()

def validate_keyword(keyword: str) -> bool:
    """Validate keyword input"""
    if not keyword or len(keyword.strip()) < 2:
        return False
    
    # Check for minimum length and maximum length
    if len(keyword.strip()) > 100:
        return False
    
    # Check for valid characters
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', keyword):
        return False
    
    return True

def format_entities_for_display(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format entities for better display in UI"""
    formatted = []
    
    for entity in entities:
        formatted.append({
            "text": entity.get("text", ""),
            "type": entity.get("label", ""),
            "type_display": get_entity_type_display(entity.get("label", "")),
            "confidence": entity.get("confidence", 0.0)
        })
    
    return formatted

def get_entity_type_display(entity_type: str) -> str:
    """Convert entity type to human-readable format"""
    type_mapping = {
        "PERSON": "Person",
        "ORG": "Organization",
        "GPE": "Geographic Location",
        "LOC": "Location",
        "PRODUCT": "Product",
        "EVENT": "Event",
        "WORK_OF_ART": "Work of Art",
        "LAW": "Law",
        "LANGUAGE": "Language",
        "DATE": "Date",
        "TIME": "Time",
        "PERCENT": "Percentage",
        "MONEY": "Money",
        "QUANTITY": "Quantity",
        "ORDINAL": "Ordinal Number",
        "CARDINAL": "Cardinal Number"
    }
    
    return type_mapping.get(entity_type, entity_type.title())

def format_keywords_for_display(keywords: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format keywords for better display in UI"""
    formatted = []
    
    for keyword in keywords:
        formatted.append({
            "keyword": keyword.get("keyword", ""),
            "score": round(keyword.get("score", 0), 3),
            "frequency": keyword.get("frequency", 0),
            "importance": get_keyword_importance(keyword.get("score", 0))
        })
    
    return formatted

def get_keyword_importance(score: float) -> str:
    """Determine keyword importance based on TF-IDF score"""
    if score >= 0.8:
        return "High"
    elif score >= 0.5:
        return "Medium"
    elif score >= 0.2:
        return "Low"
    else:
        return "Very Low"

def generate_project_title(keyword: str) -> str:
    """Generate a project title based on keyword"""
    return f"{keyword.title()} - SEO Analysis"

def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp for display"""
    return timestamp.strftime("%B %d, %Y at %I:%M %p")

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length].rsplit(' ', 1)[0] + "..."

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Limit length
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename

def calculate_analysis_score(analysis: Dict[str, Any]) -> int:
    """Calculate a score for the analysis quality"""
    score = 0
    
    # Score based on number of entities found
    entities_count = len(analysis.get("entities", []))
    if entities_count >= 10:
        score += 30
    elif entities_count >= 5:
        score += 20
    elif entities_count >= 2:
        score += 10
    
    # Score based on number of keywords found
    keywords_count = len(analysis.get("tfidf_keywords", []))
    if keywords_count >= 20:
        score += 30
    elif keywords_count >= 10:
        score += 20
    elif keywords_count >= 5:
        score += 10
    
    # Score based on SERP results
    serp_count = analysis.get("total_results", 0)
    if serp_count >= 8:
        score += 20
    elif serp_count >= 5:
        score += 15
    elif serp_count >= 2:
        score += 10
    
    # Score based on content outline quality
    outline = analysis.get("content_outline", "")
    if len(outline) > 500:
        score += 20
    elif len(outline) > 200:
        score += 15
    elif len(outline) > 50:
        score += 10
    
    return min(score, 100)  # Cap at 100

