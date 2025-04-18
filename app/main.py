from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.auth.router import router as auth_router
from app.routers.diagnostics import router as diagnostics_router
from app.models.user import User
from app.auth.jwt import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="WomSoft Server")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(auth_router)
app.include_router(diagnostics_router)

# Root route
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/entry")
async def entry_form(request: Request):
    return templates.TemplateResponse("entry_form.html", {"request": request})

# Create initial admin user if none exists
@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    user_count = db.query(User).count()
    if user_count == 0:
        admin_user = User(
            username="admin",
            email="admin@mimark.es",
            hashed_password=get_password_hash("admin")
        )
        db.add(admin_user)
        db.commit()