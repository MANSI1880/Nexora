from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta
import datetime

from app.database.connection import get_db
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token
from app.auth.security import hash_password, verify_password
from app.auth.jwt import create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

async def create_audit_log(db: AsyncSession, action: str, user_id: int | None = None, details: str | None = None):
    log = AuditLog(user_id=user_id, action=action, details=details, timestamp=datetime.datetime.utcnow())
    db.add(log)
    await db.commit()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check duplicate username
    result = await db.execute(select(User).where(User.username == user_in.username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username already registered")
        
    # Check duplicate email
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_pwd = hash_password(user_in.password)
    
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_pwd,
        role="user",
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    await create_audit_log(db, "registration", user_id=new_user.id, details=f"User {new_user.username} registered.")
    
    return new_user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalars().first()
    
    if not user:
        await create_audit_log(db, "failed_login", details=f"Failed login attempt for username {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not verify_password(form_data.password, user.hashed_password):
        await create_audit_log(db, "failed_login", user_id=user.id, details=f"Failed login attempt for username {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
        
    access_token = create_access_token(data={"sub": user.username})
    
    await create_audit_log(db, "successful_login", user_id=user.id, details=f"User {user.username} logged in.")
    
    return {"access_token": access_token, "token_type": "bearer"}
