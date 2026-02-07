from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.schemas import ReservationResponse, ReservationReturnRequest
from models.models import User, RoleEnum
from repositories.repositories import ReservationRepository
from api.dependencies import get_current_user

router = APIRouter(prefix="/api/reservations", tags=["reservations"])

@router.get("/my", response_model=list[ReservationResponse])
def get_my_reservations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return ReservationRepository.get_user_reservations(db, current_user.id)

@router.get("/", response_model=list[ReservationResponse])
def get_all_reservations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [RoleEnum.LIBRARIAN, RoleEnum.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nemáte oprávnění pro tuto akci"
        )
    return ReservationRepository.get_all_active_reservations(db)

@router.post("/borrow/{book_copy_id}", response_model=ReservationResponse)
def borrow_book(
    book_copy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reservation = ReservationRepository.create_reservation(
        db, current_user.id, book_copy_id
    )
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exemplář není dostupný"
        )
    return reservation

@router.post("/return")
def return_book(
    request: ReservationReturnRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reservation = ReservationRepository.get_reservation_by_id(db, request.reservation_id)
    
    if current_user.role not in [RoleEnum.LIBRARIAN, RoleEnum.ADMIN]:
        if reservation and reservation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Nemáte oprávnění pro tuto akci"
            )
    
    if not reservation:
        raise HTTPException(status_code=404, detail="Rezervace nenalezena")
    
    returned = ReservationRepository.return_book(db, request.reservation_id)
    if not returned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nelze vrátit tuto rezervaci"
        )
    return {"message": "Kniha byla vrácena"}