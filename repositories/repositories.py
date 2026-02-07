from sqlalchemy.orm import Session
from models.models import User, Book, BookCopy, Reservation
from models.schemas import UserCreate, BookCreate, BookUpdate, BookCopyCreate, BookCopyUpdate
from core.security import get_password_hash
from datetime import datetime, timedelta

class UserRepository:
    @staticmethod
    def get_user_by_username(db: Session, username: str):
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_user(db: Session, user: UserCreate):
        db_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            password_hash=get_password_hash(user.password),
            role="čtenář"
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update_user_password(db: Session, user_id: int, new_password: str):
        user = UserRepository.get_user_by_id(db, user_id)
        if user:
            user.password_hash = get_password_hash(new_password)
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
        return user
    
    @staticmethod
    def update_user_role(db: Session, user_id: int, role: str):
        user = UserRepository.get_user_by_id(db, user_id)
        if user:
            user.role = role
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = UserRepository.get_user_by_id(db, user_id)
        if user:
            db.delete(user)
            db.commit()
        return user

class BookRepository:
    @staticmethod
    def get_book_by_id(db: Session, book_id: int):
        return db.query(Book).filter(Book.id == book_id).first()
    
    @staticmethod
    def get_book_by_isbn(db: Session, isbn: str):
        return db.query(Book).filter(Book.isbn == isbn).first()
    
    @staticmethod
    def get_all_books(db: Session, skip: int = 0, limit: int = 100, search: str = None):
        query = db.query(Book)
        if search:
            q = f"%{search}%"
            query = query.filter(
                (Book.title.ilike(q)) | 
                (Book.author.ilike(q)) | 
                (Book.isbn.ilike(q)) |
                (Book.category.ilike(q))
            )
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def find_books_with_filters(db: Session, skip: int = 0, limit: int = 100, *, title: str | None = None, author: str | None = None, category: str | None = None, year_from: int | None = None, year_to: int | None = None, available: bool | None = None):
        query = db.query(Book)
        if title:
            query = query.filter(Book.title.ilike(f"%{title}%"))
        if author:
            query = query.filter(Book.author.ilike(f"%{author}%"))
        if category:
            query = query.filter(Book.category.ilike(f"%{category}%"))
        if year_from:
            query = query.filter(Book.publication_year >= year_from)
        if year_to:
            query = query.filter(Book.publication_year <= year_to)

        if available is not None:
            # join with copies to filter by availability
            from sqlalchemy.orm import aliased
            Copy = aliased(BookCopy)
            if available:
                query = query.join(Book.copies).filter(BookCopy.is_available == True)
            else:
                # books that have no available copies
                sub = db.query(BookCopy.book_id).filter(BookCopy.is_available == True).subquery()
                query = query.filter(~Book.id.in_(sub))

        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_book(db: Session, book: BookCreate):
        db_book = Book(**book.dict())
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book
    
    @staticmethod
    def update_book(db: Session, book_id: int, book_update: BookUpdate):
        db_book = BookRepository.get_book_by_id(db, book_id)
        if db_book:
            update_data = book_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_book, key, value)
            db_book.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_book)
        return db_book
    
    @staticmethod
    def delete_book(db: Session, book_id: int):
        db_book = BookRepository.get_book_by_id(db, book_id)
        if db_book:
            db.delete(db_book)
            db.commit()
        return db_book

class BookCopyRepository:
    @staticmethod
    def get_copy_by_id(db: Session, copy_id: int):
        return db.query(BookCopy).filter(BookCopy.id == copy_id).first()
    
    @staticmethod
    def get_copies_by_book(db: Session, book_id: int):
        return db.query(BookCopy).filter(BookCopy.book_id == book_id).all()
    
    @staticmethod
    def get_available_copies(db: Session, book_id: int):
        return db.query(BookCopy).filter(
            (BookCopy.book_id == book_id) & (BookCopy.is_available == True)
        ).all()
    
    @staticmethod
    def create_copy(db: Session, book_copy: BookCopyCreate):
        db_copy = BookCopy(**book_copy.dict())
        db.add(db_copy)
        db.commit()
        db.refresh(db_copy)
        return db_copy
    
    @staticmethod
    def update_copy(db: Session, copy_id: int, copy_update: BookCopyUpdate):
        db_copy = BookCopyRepository.get_copy_by_id(db, copy_id)
        if db_copy:
            update_data = copy_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_copy, key, value)
            db_copy.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_copy)
        return db_copy
    
    @staticmethod
    def delete_copy(db: Session, copy_id: int):
        db_copy = BookCopyRepository.get_copy_by_id(db, copy_id)
        if db_copy:
            db.delete(db_copy)
            db.commit()
        return db_copy

class ReservationRepository:
    @staticmethod
    def get_reservation_by_id(db: Session, reservation_id: int):
        return db.query(Reservation).filter(Reservation.id == reservation_id).first()
    
    @staticmethod
    def get_user_reservations(db: Session, user_id: int):
        from sqlalchemy.orm import joinedload
        return db.query(Reservation).filter(Reservation.user_id == user_id).options(
            joinedload(Reservation.book_copy).joinedload(BookCopy.book)
        ).all()
    
    @staticmethod
    def get_active_reservations(db: Session, user_id: int):
        return db.query(Reservation).filter(
            (Reservation.user_id == user_id) & (Reservation.status == "aktivní")
        ).all()
    
    @staticmethod
    def create_reservation(db: Session, user_id: int, book_copy_id: int):
        copy = BookCopyRepository.get_copy_by_id(db, book_copy_id)
        if not copy or not copy.is_available:
            return None
        
        due_date = datetime.utcnow() + timedelta(days=30)
        
        db_reservation = Reservation(
            user_id=user_id,
            book_copy_id=book_copy_id,
            due_date=due_date,
            status="aktivní"
        )
        copy.is_available = False
        db.add(db_reservation)
        db.commit()
        db.refresh(db_reservation)
        return db_reservation
    
    @staticmethod
    def return_book(db: Session, reservation_id: int):
        reservation = ReservationRepository.get_reservation_by_id(db, reservation_id)
        if reservation and reservation.status == "aktivní":
            reservation.return_date = datetime.utcnow()
            reservation.status = "vráceno"
            copy = BookCopyRepository.get_copy_by_id(db, reservation.book_copy_id)
            if copy:
                copy.is_available = True
            db.commit()
            db.refresh(reservation)
        return reservation
    
    @staticmethod
    def get_all_active_reservations(db: Session):
        from sqlalchemy.orm import joinedload
        return db.query(Reservation).filter(Reservation.status == "aktivní").options(
            joinedload(Reservation.book_copy).joinedload(BookCopy.book),
            joinedload(Reservation.user)
        ).all()