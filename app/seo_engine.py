import requests
from bs4 import BeautifulSoup
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import json
import re
from typing import List, Dict, Any
import openai
import os
from dotenv import load_dotenv

load_dotenv()

class SEOEngine:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
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
        """Generate content outline using OpenAI"""
        try:
            # Prepare context for OpenAI
            entities_text = ", ".join([f"{ent['text']} ({ent['label']})" for ent in analysis['entities'][:10]])
            keywords_text = ", ".join([kw['keyword'] for kw in analysis['tfidf_keywords'][:15]])
            
            prompt = f"""
            Generate a comprehensive blog post outline for the keyword "{keyword}".
            
            Use these extracted entities naturally: {entities_text}
            Include these important keywords: {keywords_text}
            
            Format the outline with:
            - H2 headings for main sections
            - H3 subheadings for subsections
            - Brief description of what each section should cover
            
            Make it SEO-optimized and engaging for readers.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert SEO content strategist."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
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
        entities = [ent['text'] for ent in analysis['entities'][:5]]
        keywords = [kw['keyword'] for kw in analysis['tfidf_keywords'][:10]]
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": f"Best {keyword.title()} in 2025 - Complete Guide",
            "description": f"Comprehensive guide to {keyword} options, features, and buying advice for 2025.",
            "keywords": ", ".join(keywords[:10]),
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
            "dateModified": "2025-01-01"
        }
        
        return json.dumps(schema, indent=2)
    
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

