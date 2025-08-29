#!/usr/bin/env python3
"""
SEO Content Generator - Main Application Entry Point

A powerful AI-powered SEO content generation tool that analyzes SERP data,
extracts entities, and generates optimized content outlines with structured schema markup.

Features:
- SERP Analysis and competitor research
- Entity extraction using NLP (spaCy)
- TF-IDF keyword analysis
- AI-generated content outlines
- Automatic JSON-LD schema generation
- Modern web interface with authentication

Author: SEO Content Generator Team
License: MIT
"""

import uvicorn
from app.main import app
from app.database import create_tables

if __name__ == "__main__":
    # Create database tables on startup
    create_tables()
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

