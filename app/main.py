from fastapi import FastAPI, Request, Depends, HTTPException, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from .database import get_db, create_tables
from .models import User, Project, Analysis
from .auth import get_password_hash, verify_password, create_access_token, get_current_active_user
from .seo_engine import SEOEngine
from .utils import validate_keyword, generate_project_title, calculate_analysis_score

load_dotenv()

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

# Login page
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Register page
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Dashboard
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # Get user's projects
    projects = db.query(Project).filter(Project.user_id == current_user.id).order_by(Project.created_at.desc()).all()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": current_user,
        "projects": projects
    })

# User registration
@app.post("/register")
async def register_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    # Create new user
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return RedirectResponse(url="/login", status_code=303)

# User login
@app.post("/login")
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    
    # In a real app, you'd set this as a cookie
    # For demo purposes, we'll redirect with a token parameter
    return RedirectResponse(url=f"/dashboard?token={access_token}", status_code=303)

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

