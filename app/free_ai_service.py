"""
Free AI Service using Hugging Face models
Alternative to OpenAI API for content generation
"""

import requests
import json
from typing import Dict, Any, Optional
import os

class FreeAIService:
    def __init__(self):
        self.huggingface_token = os.getenv("HUGGINGFACE_TOKEN", "")
        self.use_local_fallback = True
        
    def generate_content_outline(self, keyword: str, entities: list, keywords: list) -> str:
        """
        Generate content outline using free AI alternatives
        """
        # Try Hugging Face first
        if self.huggingface_token:
            try:
                return self._generate_with_huggingface(keyword, entities, keywords)
            except Exception as e:
                print(f"Hugging Face failed: {e}")
        
        # Fallback to local generation
        return self._generate_local_outline(keyword, entities, keywords)
    
    def _generate_with_huggingface(self, keyword: str, entities: list, keywords: list) -> str:
        """
        Use Hugging Face Inference API (free tier: 30k requests/month)
        """
        API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        
        # Prepare prompt
        entities_text = ", ".join([f"{ent['text']} ({ent['label']})" for ent in entities[:5]])
        keywords_text = ", ".join([kw['keyword'] for kw in keywords[:10]])
        
        prompt = f"""Generate a blog post outline for "{keyword}". 
        
        Use these entities naturally: {entities_text}
        Include these keywords: {keywords_text}
        
        Format with H2 and H3 headings. Make it SEO-optimized."""
        
        headers = {"Authorization": f"Bearer {self.huggingface_token}"}
        
        try:
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '')[:1000]  # Limit length
        except Exception as e:
            print(f"Error with Hugging Face API: {e}")
        
        # If Hugging Face fails, return local generation
        return self._generate_local_outline(keyword, entities, keywords)
    
    def _generate_local_outline(self, keyword: str, entities: list, keywords: list) -> str:
        """
        Generate outline locally without external APIs
        """
        # Extract key information
        entity_names = [ent['text'] for ent in entities[:5]]
        keyword_names = [kw['keyword'] for kw in keywords[:10]]
        
        # Create structured outline
        outline = f"""# {keyword.title()} - Complete Guide 2025

## Introduction
Overview of {keyword} and why it matters in 2025. This comprehensive guide covers everything you need to know about {keyword}.

## Key Features and Benefits
- {entity_names[0] if entity_names else 'Feature 1'}: Essential aspect of {keyword}
- {entity_names[1] if len(entity_names) > 1 else 'Feature 2'}: Important consideration for users
- {entity_names[2] if len(entity_names) > 2 else 'Feature 3'}: Critical factor in decision making

## Top Options and Comparisons
- {keyword_names[0] if keyword_names else 'Option 1'}: Leading choice in the market
- {keyword_names[1] if len(keyword_names) > 1 else 'Option 2'}: Popular alternative with unique benefits
- {keyword_names[2] if len(keyword_names) > 2 else 'Option 3'}: Emerging option worth considering

## Detailed Analysis
### {keyword_names[3] if len(keyword_names) > 3 else 'Analysis Point 1'}
Deep dive into this important aspect of {keyword}.

### {keyword_names[4] if len(keyword_names) > 4 else 'Analysis Point 2'}
Understanding the implications and benefits.

## Buying Guide and Recommendations
Factors to consider when choosing {keyword}:
- Quality and reliability
- Price and value for money
- User reviews and ratings
- Long-term benefits

## Expert Tips and Best Practices
- Research thoroughly before making a decision
- Compare multiple options
- Consider your specific needs
- Read user reviews and expert opinions

## Conclusion
Summary of key points and final recommendations for {keyword}. Choose the option that best fits your requirements and budget.

## Additional Resources
- Related articles and guides
- Expert recommendations
- User community discussions
- Latest updates and trends"""
        
        return outline
    
    def generate_schema_markup(self, keyword: str, entities: list, keywords: list) -> str:
        """
        Generate JSON-LD schema markup locally
        """
        entity_names = [ent['text'] for ent in entities[:5]]
        keyword_names = [kw['keyword'] for kw in keywords[:10]]
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": f"Best {keyword.title()} in 2025 - Complete Guide",
            "description": f"Comprehensive guide to {keyword} options, features, and buying advice for 2025.",
            "keywords": ", ".join(keyword_names[:10]),
            "about": {
                "@type": "Thing",
                "name": keyword
            },
            "mainEntity": {
                "@type": "Thing",
                "name": keyword,
                "description": f"Complete analysis of {keyword} options and features"
            },
            "author": {
                "@type": "Organization",
                "name": "SEO Content Generator"
            },
            "publisher": {
                "@type": "Organization",
                "name": "SEO Content Generator"
            },
            "datePublished": "2025-01-01",
            "dateModified": "2025-01-01",
            "articleSection": "Technology",
            "inLanguage": "en-US"
        }
        
        return json.dumps(schema, indent=2)
