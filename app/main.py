from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.auth.router import router as auth_router
from app.routers.diagnostics import router as diagnostics_router
from app.routers.admin import router as admin_router  # Add this import
from app.routers.orders import router as orders_router
from app.middleware.audit_middleware import AuditMiddleware  # Add this import
from app.models.user import User
from app.auth.jwt import get_password_hash
from app.database import TEST_MODE

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="WomSoft Server")

# Add audit middleware
app.add_middleware(AuditMiddleware)  # Add this line

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(auth_router)
app.include_router(diagnostics_router)
app.include_router(admin_router)  # Add this line
app.include_router(orders_router)

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

@app.get("/admin/audit")
async def admin_audit(request: Request):
    return templates.TemplateResponse("admin_audit.html", {"request": request})

# Create initial admin user if none exists
@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    user_count = db.query(User).count()
    if user_count == 0 and not TEST_MODE:
        admin_user = User(
            username="admin",
            email="admin@mimark.es",
            hashed_password=get_password_hash("admin")
        )
        db.add(admin_user)
        db.commit()