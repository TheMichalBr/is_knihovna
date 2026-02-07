from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.schemas import UserResponse, UserCreate, UserRole, AdminChangePassword
from models.models import User, RoleEnum
from repositories.repositories import UserRepository
from api.dependencies import get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/users", response_model=list[UserResponse])
def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nemáte oprávnění pro tuto akci"
        )
    return UserRepository.get_all_users(db)

@router.post("/users", response_model=UserResponse)
def create_user(
    user: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nemáte oprávnění pro tuto akci"
        )
    
    existing = UserRepository.get_user_by_username(db, user.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uživatel s tímto jménem již existuje"
        )
    
    return UserRepository.create_user(db, user)

@router.put("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role_update: UserRole,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nemáte oprávnění pro tuto akci"
        )
    
    valid_roles = [RoleEnum.READER, RoleEnum.LIBRARIAN, RoleEnum.ADMIN]
    if role_update.role not in [r.value for r in valid_roles]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Neplatná role"
        )
    
    user = UserRepository.update_user_role(db, user_id, role_update.role)
    if not user:
        raise HTTPException(status_code=404, detail="Uživatel nenalezen")
    return user

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nemáte oprávnění pro tuto akci"
        )
    
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nemůžete smazat svůj vlastní účet"
        )
    
    deleted = UserRepository.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Uživatel nenalezen")
    return {"message": "Uživatel byl smazán"}

@router.post("/users/{user_id}/change-password")
def admin_change_user_password(
    user_id: int,
    request: AdminChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nemáte oprávnění pro tuto akci"
        )
    
    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nové heslo musí mít alespoň 6 znaků"
        )
    
    user = UserRepository.update_user_password(db, request.user_id, request.new_password)
    if not user:
        raise HTTPException(status_code=404, detail="Uživatel nenalezen")
    return {"message": f"Heslo uživatele {user.username} bylo změněno"}