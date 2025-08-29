import requests
from bs4 import BeautifulSoup
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import json
import re
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from .free_ai_service import FreeAIService

load_dotenv()

class SEOEngine:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.ai_service = FreeAIService()
        
    def scrape_serp_results(self, keyword: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Simulate SERP scraping (in production, use a SERP API)
        For demo purposes, we'll create mock data
        """
        # Mock SERP results - in production, integrate with SerpAPI, Zenserp, etc.
        mock_results = [
            {
                "title": f"Best {keyword} in 2025 - Complete Guide",
                "url": f"https://example1.com/{keyword.replace(' ', '-')}",
                "snippet": f"Discover the top {keyword} options for 2025. Expert reviews and comparisons.",
                "h1": f"Best {keyword} 2025",
                "h2s": [f"Top {keyword} Brands", f"{keyword} Features", f"{keyword} Buying Guide"]
            },
            {
                "title": f"2025 {keyword} Comparison - Which One to Choose?",
                "url": f"https://example2.com/{keyword.replace(' ', '-')}-2025",
                "snippet": f"Compare the latest {keyword} models and find your perfect match.",
                "h1": f"{keyword} Comparison 2025",
                "h2s": [f"{keyword} Models", f"Price Comparison", f"User Reviews"]
            }
        ]
        
        # Add more mock results to reach num_results
        for i in range(3, num_results + 1):
            mock_results.append({
                "title": f"{keyword} Guide {i} - Expert Analysis",
                "url": f"https://example{i}.com/{keyword.replace(' ', '-')}",
                "snippet": f"Professional analysis of {keyword} options and recommendations.",
                "h1": f"{keyword} Analysis",
                "h2s": [f"{keyword} Overview", f"Key Features", f"Recommendations"]
            })
        
        return mock_results
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities using spaCy"""
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        
        return entities
    
    def extract_tfidf_keywords(self, texts: List[str], max_features: int = 50) -> List[Dict[str, Any]]:
        """Extract TF-IDF keywords from text corpus"""
        if not texts:
            return []
        
        # Clean and preprocess texts
        cleaned_texts = [re.sub(r'[^\w\s]', '', text.lower()) for text in texts]
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(cleaned_texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get TF-IDF scores for each feature
            tfidf_scores = tfidf_matrix.toarray().sum(axis=0)
            
            # Create keyword-score pairs
            keywords = []
            for i, score in enumerate(tfidf_scores):
                if score > 0:
                    keywords.append({
                        "keyword": feature_names[i],
                        "score": float(score),
                        "frequency": int(score * 100)  # Normalize for display
                    })
            
            # Sort by score
            keywords.sort(key=lambda x: x["score"], reverse=True)
            return keywords[:max_features]
            
        except Exception as e:
            print(f"Error in TF-IDF extraction: {e}")
            return []
    
    def analyze_serp_content(self, serp_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze SERP content for entities and keywords"""
        all_texts = []
        all_h2s = []
        
        for result in serp_results:
            # Combine title, snippet, and H1
            combined_text = f"{result['title']} {result['snippet']} {result['h1']}"
            all_texts.append(combined_text)
            
            # Add H2 tags
            all_h2s.extend(result.get('h2s', []))
        
        # Extract entities from all text
        combined_text = " ".join(all_texts)
        entities = self.extract_entities(combined_text)
        
        # Extract TF-IDF keywords
        keywords = self.extract_tfidf_keywords(all_texts)
        
        return {
            "entities": entities,
            "tfidf_keywords": keywords,
            "h2_analysis": all_h2s,
            "total_results": len(serp_results)
        }
    
    def generate_content_outline(self, keyword: str, analysis: Dict[str, Any]) -> str:
        """Generate content outline using free AI service"""
        try:
            return self.ai_service.generate_content_outline(
                keyword, 
                analysis['entities'], 
                analysis['tfidf_keywords']
            )
        except Exception as e:
            print(f"Error generating outline: {e}")
            return self._generate_fallback_outline(keyword, analysis)
    
    def _generate_fallback_outline(self, keyword: str, analysis: Dict[str, Any]) -> str:
        """Fallback outline generation if OpenAI fails"""
        entities = [ent['text'] for ent in analysis['entities'][:5]]
        keywords = [kw['keyword'] for kw in analysis['tfidf_keywords'][:10]]
        
        outline = f"""
        # {keyword.title()} - Complete Guide 2025
        
        ## Introduction
        Overview of {keyword} and why it matters in 2025
        
        ## Key Features and Benefits
        - {entities[0] if entities else 'Feature 1'}
        - {entities[1] if len(entities) > 1 else 'Feature 2'}
        - {entities[2] if len(entities) > 2 else 'Feature 3'}
        
        ## Top Options and Comparisons
        - {keywords[0] if keywords else 'Option 1'}
        - {keywords[1] if len(keywords) > 1 else 'Option 2'}
        - {keywords[2] if len(keywords) > 2 else 'Option 3'}
        
        ## Buying Guide
        Factors to consider when choosing {keyword}
        
        ## Conclusion
        Summary and final recommendations
        """
        
        return outline
    
    def generate_schema_markup(self, keyword: str, analysis: Dict[str, Any]) -> str:
        """Generate JSON-LD schema markup"""
        return self.ai_service.generate_schema_markup(
            keyword, 
            analysis['entities'], 
            analysis['tfidf_keywords']
        )
    
    def run_full_analysis(self, keyword: str) -> Dict[str, Any]:
        """Run complete SEO analysis pipeline"""
        try:
            # Step 1: Gather SERP data
            serp_results = self.scrape_serp_results(keyword)
            
            # Step 2: Analyze content
            analysis = self.analyze_serp_content(serp_results)
            
            # Step 3: Generate outline
            content_outline = self.generate_content_outline(keyword, analysis)
            
            # Step 4: Generate schema
            schema_markup = self.generate_schema_markup(keyword, analysis)
            
            return {
                "keyword": keyword,
                "serp_results": serp_results,
                "analysis": analysis,
                "content_outline": content_outline,
                "schema_markup": schema_markup,
                "status": "completed"
            }
            
        except Exception as e:
            print(f"Error in full analysis: {e}")
            return {
                "keyword": keyword,
                "status": "failed",
                "error": str(e)
            }

