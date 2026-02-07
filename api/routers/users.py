from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.schemas import UserDetailResponse, UserChangePassword
from models.models import User
from repositories.repositories import UserRepository
from core.security import verify_password
from api.routers.auth import get_current_user
from api.dependencies import get_current_user

router = APIRouter(prefix="/api/profile", tags=["profile"])

@router.get("/", response_model=UserDetailResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = UserRepository.get_user_by_id(db, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="Uživatel nenalezen")
    return user

@router.post("/change-password")
def change_password(
    change_pwd: UserChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = UserRepository.get_user_by_id(db, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="Uživatel nenalezen")
    
    if not verify_password(change_pwd.old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Staré heslo je nesprávné"
        )
    
    UserRepository.update_user_password(db, current_user.id, change_pwd.new_password)
    return {"message": "Heslo bylo úspěšně změněno"}