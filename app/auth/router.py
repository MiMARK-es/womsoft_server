from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.auth.jwt import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
from app.schemas.user import Token, UserCreate, User as UserSchema
from app.models.user import User
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db),
    audit_service: AuditService = Depends()
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # Log failed login attempt
        await audit_service.log_event(
            action="login_failed",
            entity_type="user",
            entity_id=form_data.username,
            details={"reason": "invalid_credentials"},
            request=request
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Log successful login
    await audit_service.log_event(
        action="login_success",
        entity_type="user",
        entity_id=str(user.id),
        user_id=user.id,
        request=request
    )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserSchema)
async def register_user(
    request: Request,
    user_data: UserCreate, 
    db: Session = Depends(get_db),
    audit_service: AuditService = Depends()
):
    # Check if username already exists
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if db_user:
        await audit_service.log_event(
            action="register_failed",
            entity_type="user",
            entity_id=user_data.username,
            details={"reason": "username_exists", "email": user_data.email},
            request=request
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        await audit_service.log_event(
            action="register_failed",
            entity_type="user",
            entity_id=user_data.email,
            details={"reason": "email_exists", "username": user_data.username},
            request=request
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Log successful registration
    await audit_service.log_event(
        action="user_registered",
        entity_type="user",
        entity_id=str(new_user.id),
        user_id=new_user.id,
        details={"username": new_user.username, "email": new_user.email},
        request=request
    )
    
    return new_user

# Add this test endpoint for debugging
@router.post("/login-test")
async def login_test(form_data: dict):
    """Test endpoint for debugging login issues"""
    return {"received": form_data}