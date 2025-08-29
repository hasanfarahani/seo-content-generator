from fastapi import FastAPI, Request, Depends, HTTPException, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from jose import JWTError, jwt

from .database import get_db, create_tables
from .models import User, Project, Analysis
from .auth import get_password_hash, verify_password, create_access_token, get_current_active_user
from .seo_engine import SEOEngine
from .utils import validate_keyword, generate_project_title, calculate_analysis_score

load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

app = FastAPI(title="SEO Content Generator", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# SEO Engine instance
seo_engine = SEOEngine()

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Landing page
@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

# Email capture and direct access
@app.post("/capture-email")
async def capture_email(
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == email).first()
    
    if existing_user:
        # User exists, create access token
        access_token = create_access_token(data={"sub": existing_user.username})
        return RedirectResponse(url=f"/generator?token={access_token}", status_code=303)
    
    # Create new user with email only
    user = User(
        username=email.split('@')[0],  # Use email prefix as username
        email=email,
        hashed_password="",  # No password needed
        is_active=1
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    return RedirectResponse(url=f"/generator?token={access_token}", status_code=303)

# Direct access generator (no login required)
@app.get("/generator", response_class=HTMLResponse)
async def generator_page(request: Request, token: str = None):
    if not token:
        return RedirectResponse(url="/", status_code=303)
    
    try:
        # Verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return RedirectResponse(url="/", status_code=303)
    except JWTError:
        return RedirectResponse(url="/", status_code=303)
    
    return templates.TemplateResponse("generator.html", {"request": request, "token": token})

# Create new project (no auth required)
@app.post("/create-project")
async def create_project(
    keyword: str = Form(...),
    token: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create project
        project = Project(
            user_id=user.id,
            keyword=keyword,
            title=generate_project_title(keyword),
            status="pending"
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        
        # Run analysis
        analysis_result = seo_engine.run_full_analysis(keyword)
        
        # Check if analysis was successful
        if analysis_result.get('status') != 'completed':
            raise HTTPException(status_code=500, detail=f"Analysis failed: {analysis_result.get('error', 'Unknown error')}")
        
        # Get analysis data with fallbacks
        serp_results = analysis_result.get('serp_results', [])
        entities = analysis_result.get('analysis', {}).get('entities', [])
        tfidf_keywords = analysis_result.get('analysis', {}).get('tfidf_keywords', [])
        content_outline = analysis_result.get('content_outline', '')
        schema_markup = analysis_result.get('schema_markup', '')
        
        # Provide fallback data if analysis is empty
        if not entities:
            entities = [{"text": keyword, "label": "TOPIC"}]
        if not tfidf_keywords:
            tfidf_keywords = [{"keyword": keyword, "score": 1.0}]
        if not content_outline:
            content_outline = f"# {keyword.title()}\n\n## Introduction\n\n## Main Content\n\n## Conclusion"
        if not schema_markup:
            schema_markup = '{"@context": "https://schema.org", "@type": "Article", "headline": "' + keyword + '"}'
        
        # Save analysis
        analysis = Analysis(
            project_id=project.id,
            serp_results=serp_results,
            entities=entities,
            tfidf_keywords=tfidf_keywords,
            competitor_urls=serp_results,  # Use SERP results as competitor URLs
            content_outline=content_outline,
            schema_markup=schema_markup
        )
        
        db.add(analysis)
        db.commit()
        
        return RedirectResponse(url=f"/results/{project.id}?token={token}", status_code=303)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# View results
@app.get("/results/{project_id}", response_class=HTMLResponse)
async def view_results(request: Request, project_id: int, token: str = None):
    if not token:
        return RedirectResponse(url="/", status_code=303)
    
    try:
        # Verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return RedirectResponse(url="/", status_code=303)
    except JWTError:
        return RedirectResponse(url="/", status_code=303)
    
    # Get project and analysis
    project = db.query(Project).filter(Project.id == project_id).first()
    analysis = db.query(Analysis).filter(Analysis.project_id == project_id).first()
    
    if not project or not analysis:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return templates.TemplateResponse("results.html", {
        "request": request,
        "project": project,
        "analysis": analysis,
        "token": token
    })

# Create new project
@app.post("/project")
async def create_project(
    keyword: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not validate_keyword(keyword):
        raise HTTPException(status_code=400, detail="Invalid keyword")
    
    # Create project
    project = Project(
        user_id=current_user.id,
        keyword=keyword,
        title=generate_project_title(keyword),
        status="pending"
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return RedirectResponse(url="/dashboard", status_code=303)

# Run SEO analysis
@app.post("/analyze/{project_id}")
async def run_analysis(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get project
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update status
    project.status = "processing"
    db.commit()
    
    try:
        # Run SEO analysis
        analysis_result = seo_engine.run_full_analysis(project.keyword)
        
        if analysis_result["status"] == "completed":
            # Create analysis record
            analysis = Analysis(
                project_id=project.id,
                serp_results=analysis_result["serp_results"],
                entities=analysis_result["analysis"]["entities"],
                tfidf_keywords=analysis_result["analysis"]["tfidf_keywords"],
                competitor_urls=analysis_result["analysis"].get("h2_analysis", []),
                content_outline=analysis_result["content_outline"],
                schema_markup=analysis_result["schema_markup"]
            )
            
            db.add(analysis)
            project.status = "completed"
            db.commit()
            
        else:
            project.status = "failed"
            db.commit()
            
    except Exception as e:
        project.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    return RedirectResponse(url="/dashboard", status_code=303)

# View project analysis
@app.get("/project/{project_id}", response_class=HTMLResponse)
async def view_project(
    project_id: int,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get project and analysis
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    analysis = db.query(Analysis).filter(Analysis.project_id == project.id).first()
    
    if analysis:
        # Calculate analysis score
        score = calculate_analysis_score(analysis.analysis if hasattr(analysis, 'analysis') else {
            "entities": analysis.entities,
            "tfidf_keywords": analysis.tfidf_keywords,
            "total_results": len(analysis.serp_results) if analysis.serp_results else 0,
            "content_outline": analysis.content_outline
        })
    else:
        score = 0
    
    return templates.TemplateResponse("project.html", {
        "request": request,
        "project": project,
        "analysis": analysis,
        "score": score
    })

# API endpoint for getting project data
@app.get("/api/project/{project_id}")
async def get_project_data(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    analysis = db.query(Analysis).filter(Analysis.project_id == project.id).first()
    
    return {
        "project": {
            "id": project.id,
            "keyword": project.keyword,
            "title": project.title,
            "status": project.status,
            "created_at": project.created_at.isoformat()
        },
        "analysis": analysis.to_dict() if analysis else None
    }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "SEO Content Generator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

