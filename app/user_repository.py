from sqlalchemy import Integer, String, Column, update
from sqlalchemy.orm import Session, relationship
from .database import Base

from pydantic import BaseModel
from attrs import define

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    phone = Column(String)
    password = Column(String)
    name = Column(String)
    city = Column(String)

    shanyrak = relationship("Shanyrak", back_populates="user")
    comments = relationship("Comment", back_populates="author")
    favorites = relationship("Favorite", back_populates="author")

class UserRequest(BaseModel):
    username: str
    phone: str
    password: str
    name: str
    city: str

class UserResponse(BaseModel):
    id: int
    username: str
    phone: str
    name: str
    city: str

class UserUpdateRequest(BaseModel):
    phone: str
    name: str
    city: str

@define
class UserSave():
    username: str
    phone: str
    password: str
    name: str
    city: str 

@define
class UserUpdate():
    phone: str
    name: str
    city: str

class UserRepository():
    def save(self, db: Session, user: UserSave) -> User:
        db_user = User(**user.model_dump())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def get_user_username(self, db: Session, username: str) -> User:
        return db.query(User).filter(User.username == username).first()
    
    def get_user(self, db: Session, user_id: int) -> User:
        return db.query(User).filter(User.id == user_id).first()
    
    def update(self, db: Session, user_id: int, new_user: UserUpdate) -> User:
        user = update(User).where(User.id == user_id).values(**new_user.model_dump())
        db.execute(user)
        db.commit()
        return user
        