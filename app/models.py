from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=1)
    
    projects = relationship("Project", back_populates="user")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    keyword = Column(String, index=True)
    title = Column(String)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="projects")
    analysis = relationship("Analysis", back_populates="project", uselist=False)

class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    # SERP Data
    serp_results = Column(JSON)  # Top 10 results with titles, URLs, snippets
    
    # Extracted Data
    entities = Column(JSON)  # Named entities from spaCy
    tfidf_keywords = Column(JSON)  # TF-IDF keywords with scores
    competitor_urls = Column(JSON)  # Competitor URLs analyzed
    
    # Generated Content
    content_outline = Column(Text)  # AI-generated outline
    schema_markup = Column(Text)  # JSON-LD schema
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="analysis")

