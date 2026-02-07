from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserChangePassword(BaseModel):
    old_password: str
    new_password: str

class UserRole(BaseModel):
    role: str

class AdminChangePassword(BaseModel):
    user_id: int
    new_password: str

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserBasicResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserDetailResponse(UserResponse):
    reservations: List['ReservationResponse'] = []

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    description: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    pages: Optional[int] = None
    category: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    pages: Optional[int] = None
    category: Optional[str] = None

class BookResponse(BookBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class BookCopyBase(BaseModel):
    inventory_number: str
    condition: str = "dobrá"

class BookCopyCreate(BookCopyBase):
    book_id: int | None = None

class BookCopyUpdate(BaseModel):
    condition: Optional[str] = None
    is_available: Optional[bool] = None

class BookCopyResponse(BookCopyBase):
    id: int
    book_id: int
    is_available: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReservationBase(BaseModel):
    due_date: Optional[datetime] = None

class ReservationCreate(ReservationBase):
    book_copy_id: int

class BookCopyWithBook(BookCopyBase):
    id: int
    is_available: bool
    book: 'BookResponse'
    
    class Config:
        from_attributes = True

class ReservationResponse(BaseModel):
    id: int
    user_id: int
    book_copy_id: int
    reservation_date: datetime
    due_date: Optional[datetime]
    return_date: Optional[datetime]
    status: str
    book_copy: Optional['BookCopyWithBook'] = None
    user: Optional['UserBasicResponse'] = None
    
    class Config:
        from_attributes = True

class ReservationReturnRequest(BaseModel):
    reservation_id: int

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    username: Optional[str] = None

# Rebuild models to resolve forward references
ReservationResponse.model_rebuild()
UserDetailResponse.model_rebuild()