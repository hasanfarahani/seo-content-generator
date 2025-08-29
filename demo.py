#!/usr/bin/env python3
"""
Demo script for SEO Content Generator

This script demonstrates the core functionality of the SEO engine
without running the full web application.
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from seo_engine import SEOEngine

def main():
    """Run a demo of the SEO engine"""
    print("🚀 SEO Content Generator Demo (Free AI Version)")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check if Hugging Face token is set
    if not os.getenv("HUGGINGFACE_TOKEN"):
        print("ℹ️  No HUGGINGFACE_TOKEN found - using local content generation")
        print("   To use Hugging Face AI, get a free token from: https://huggingface.co/settings/tokens")
        print()
    
    # Initialize SEO engine
    print("🔄 Initializing SEO engine...")
    try:
        seo_engine = SEOEngine()
        print("✅ SEO engine initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize SEO engine: {e}")
        return
    
    # Demo keywords
    demo_keywords = [
        "best gravel bikes 2025",
        "digital marketing strategies",
        "python web development",
        "healthy breakfast recipes"
    ]
    
    print(f"\n📝 Running demo analysis for: {demo_keywords[0]}")
    print("-" * 50)
    
    try:
        # Run full analysis
        results = seo_engine.run_full_analysis(demo_keywords[0])
        
        if results["status"] == "completed":
            print("✅ Analysis completed successfully!")
            print()
            
            # Display results
            print("🔍 SERP Analysis Results:")
            print(f"   Found {len(results['serp_results'])} SERP results")
            for i, result in enumerate(results['serp_results'][:3], 1):
                print(f"   {i}. {result['title']}")
            print()
            
            print("🏷️  Extracted Entities:")
            entities = results['analysis']['entities']
            for entity in entities[:5]:
                print(f"   • {entity['text']} ({entity['label']})")
            print()
            
            print("🔑 Top Keywords (TF-IDF):")
            keywords = results['analysis']['tfidf_keywords']
            for keyword in keywords[:10]:
                print(f"   • {keyword['keyword']} (Score: {keyword['score']:.3f})")
            print()
            
            print("📋 Content Outline Preview:")
            outline_lines = results['content_outline'].split('\n')[:10]
            for line in outline_lines:
                if line.strip():
                    print(f"   {line}")
            if len(results['content_outline'].split('\n')) > 10:
                print("   ... (truncated)")
            print()
            
            print("🏗️  Schema Markup Preview:")
            schema_lines = results['schema_markup'].split('\n')[:5]
            for line in schema_lines:
                print(f"   {line}")
            print("   ... (truncated)")
            
        else:
            print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
