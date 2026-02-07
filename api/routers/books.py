from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.schemas import BookResponse, BookCreate, BookUpdate, BookCopyResponse, BookCopyCreate, BookCopyUpdate
from models.models import User, RoleEnum
from repositories.repositories import BookRepository, BookCopyRepository
from api.dependencies import get_current_user

router = APIRouter(prefix="/api/books", tags=["books"])

@router.get("/", response_model=list[BookResponse])
def get_books(
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    title: str | None = None,
    author: str | None = None,
    category: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    available: bool | None = None,
    db: Session = Depends(get_db)
):
    # prefer explicit filter endpoint when any filter provided
    if any([title, author, category, year_from, year_to, available]):
        return BookRepository.find_books_with_filters(db, skip, limit, title=title, author=author, category=category, year_from=year_from, year_to=year_to, available=available)
    if search:
        return BookRepository.get_all_books(db, skip, limit, search)
    return BookRepository.get_all_books(db, skip, limit)

@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = BookRepository.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Kniha nenalezena")
    return book

@router.post("/", response_model=BookResponse)
def create_book(
    book: BookCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [RoleEnum.LIBRARIAN, RoleEnum.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nemáte oprávnění pro tuto akci"
        )
    
    existing = BookRepository.get_book_by_isbn(db, book.isbn)
    if existing:
        raise HTTPException(status_code=400, detail="Kniha s tímto ISBN již existuje")
    
    return BookRepository.create_book(db, book)

@router.put("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book: BookUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [RoleEnum.LIBRARIAN, RoleEnum.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nemáte oprávnění pro tuto akci"
        )
    
    updated_book = BookRepository.update_book(db, book_id, book)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Kniha nenalezena")
    return updated_book

@router.delete("/{book_id}")
def delete_book(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nemáte oprávnění pro tuto akci"
        )
    
    deleted = BookRepository.delete_book(db, book_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Kniha nenalezena")
    return {"message": "Kniha byla smazána"}

@router.get("/{book_id}/copies", response_model=list[BookCopyResponse])
def get_book_copies(book_id: int, db: Session = Depends(get_db)):
    copies = BookCopyRepository.get_copies_by_book(db, book_id)
    # return empty list if no copies — frontend expects [] rather than 404
    return copies or []


@router.post("/copies/{copy_id}/condition", response_model=BookCopyResponse)
def set_copy_condition(copy_id: int, payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # payload expected to contain {'condition': 'poškozená'}
    if current_user.role not in [RoleEnum.LIBRARIAN, RoleEnum.ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Nemáte oprávnění")

    condition = payload.get('condition')
    if not condition:
        raise HTTPException(status_code=400, detail='Chybný payload: očekává se pole "condition"')

    copy_update = BookCopyUpdate(condition=condition)
    updated = BookCopyRepository.update_copy(db, copy_id, copy_update)
    if not updated:
        raise HTTPException(status_code=404, detail='Exemplář nenalezen')
    return updated

@router.post("/{book_id}/copies", response_model=BookCopyResponse)
def create_book_copy(
    book_id: int,
    copy: BookCopyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [RoleEnum.LIBRARIAN, RoleEnum.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nemáte oprávnění pro tuto akci"
        )
    
    book = BookRepository.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Kniha nenalezena")
    
    copy.book_id = book_id
    return BookCopyRepository.create_copy(db, copy)

@router.put("/copies/{copy_id}", response_model=BookCopyResponse)
def update_book_copy(
    copy_id: int,
    copy: BookCopyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [RoleEnum.LIBRARIAN, RoleEnum.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nemáte oprávnění pro tuto akci"
        )
    
    updated_copy = BookCopyRepository.update_copy(db, copy_id, copy)
    if not updated_copy:
        raise HTTPException(status_code=404, detail="Exemplář nenalezen")
    return updated_copy

@router.delete("/copies/{copy_id}")
def delete_book_copy(
    copy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nemáte oprávnění pro tuto akci"
        )
    
    deleted = BookCopyRepository.delete_copy(db, copy_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Exemplář nenalezen")
    return {"message": "Exemplář byl smazán"}