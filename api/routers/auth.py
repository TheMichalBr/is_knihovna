from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.schemas import Token, UserCreate, UserResponse, UserChangePassword
from models.models import User
from core.security import verify_password, create_access_token
from repositories.repositories import UserRepository
from datetime import timedelta
from core.config import settings
from fastapi import Request
from api.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = UserRepository.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uživatel již existuje"
        )
    return UserRepository.create_user(db, user)

@router.post("/login", response_model=Token)
async def login(request: Request, db: Session = Depends(get_db)):
    data = {}
    content_type = request.headers.get('content-type', '')
    if content_type.startswith('application/json'):
        try:
            data = await request.json()
        except Exception:
            data = {}
    elif content_type.startswith('application/x-www-form-urlencoded') or content_type.startswith('multipart/form-data'):
        form = await request.form()
        data = dict(form)
    else:
        data = {k: v for k, v in request.query_params.items()}

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='username and password required')

    user = UserRepository.get_user_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nesprávné přihlašovací údaje"
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/change-password")
def change_password(
    change_pwd: UserChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(change_pwd.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Staré heslo je nesprávné"
        )
    
    UserRepository.update_user_password(db, current_user.id, change_pwd.new_password)
    return {"message": "Heslo bylo úspěšně změněno"}