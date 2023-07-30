from sqlalchemy import Integer, String, Column, update, Float, Text, ForeignKey
from sqlalchemy.orm import Session, relationship
from .database import Base

from pydantic import BaseModel
from attrs import define

class Shanyrak(Base):
    __tablename__ = "shanyraks"

    id = Column(Integer, primary_key=True)
    type = Column(String)
    price = Column(Integer)
    address = Column(String)
    area = Column(Float)
    room_count = Column(Integer)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_comments = Column(Integer, default=0)

    user = relationship("User", back_populates="shanyrak")
    comments = relationship("Comment", back_populates="shanyraks")

class ShanyrakRequest(BaseModel):
    type: str
    price: int
    address: str
    area: float
    room_count: int
    description: str

class ShanyrakResponse(BaseModel):
    type: str
    price: int
    address: str
    area: float
    room_count: int
    description: str
    user_id: int
    total_comments: int=0

@define
class ShanyrakSave():
    type: str
    price: int
    address: str
    area: float
    room_count: int
    description: str

class ShanyrakRepository():
    def save(self, db: Session, shanyrak: ShanyrakSave, user_id: int) -> int:
        db_shanurak = Shanyrak(**shanyrak.model_dump(), user_id=user_id)
        db.add(db_shanurak)
        db.commit()
        db.refresh(db_shanurak)
        return db_shanurak.id 
    
    def get_shanyrak(self, db: Session, shanyrak_id) -> Shanyrak:
        return db.query(Shanyrak).filter(Shanyrak.id == shanyrak_id).first()
    
    def update(self, db: Session, shanyrak_id: int, new_shanyrak: ShanyrakSave) -> Shanyrak:
        shanyrak = update(Shanyrak).where(Shanyrak.id == shanyrak_id).values(**new_shanyrak.model_dump())
        db.execute(shanyrak)
        db.commit()
        return shanyrak
    
    def delete(self, db: Session, shanyrak: Shanyrak) -> bool:
        db.delete(shanyrak)
        db.commit()
        return True
    
    def plus_total_comment(self, db: Session, shanyrak_id: int) -> Shanyrak:
        shanyrak = db.query(Shanyrak).filter(Shanyrak.id == shanyrak_id).first()
        total_comments = shanyrak.total_comments + 1
        shanyrak = update(Shanyrak).where(Shanyrak.id == shanyrak_id).values(total_comments=total_comments)
        db.execute(shanyrak)
        db.commit()
        return shanyrak
    
    def minus_total_comment(self, db: Session, shanyrak_id: int) -> Shanyrak:
        shanyrak = db.query(Shanyrak).filter(Shanyrak.id == shanyrak_id).first()
        if shanyrak.total_comments > 0:
            total_comments = shanyrak.total_comments - 1
            pro = update(Shanyrak).where(Shanyrak.id == shanyrak_id).values(total_comments=total_comments)
            db.execute(pro)
            db.commit()
        return shanyrak
