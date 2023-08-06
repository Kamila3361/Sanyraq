from .database import Base
from sqlalchemy import String, Integer, Column, ForeignKey
from sqlalchemy.orm import relationship, Session


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    shanyrak_id = Column(Integer, ForeignKey("shanyraks.id"))

    author = relationship("User", back_populates="favorites")
    shanyraks = relationship("Shanyrak", back_populates="favorites")


class FavoritesRepository():
    def save(self, db: Session, user_id: int, shanyrak_id: int):
        favorite_db = Favorite(author_id=user_id, shanyrak_id=shanyrak_id)
        db.add(favorite_db)
        db.commit()
        db.refresh(favorite_db)
        return favorite_db
    
    def check(self, db: Session, user_id: int, shanyrak_id: int) -> Favorite:
        return db.query(Favorite).filter(Favorite.author_id == user_id).filter(Favorite.shanyrak_id == shanyrak_id).first()
    
    def get_favorites(self, db: Session, user_id: int) -> list[Favorite]:
        return db.query(Favorite).filter(Favorite.author_id == user_id).all()
    
    def delete(self, db: Session, user_id: int, shanyrak_id: int):
        favorite = db.query(Favorite).filter(Favorite.author_id == user_id).filter(Favorite.shanyrak_id == shanyrak_id).first()
        if not favorite:
            return False
        db.delete(favorite)
        db.commit()
        return True
    