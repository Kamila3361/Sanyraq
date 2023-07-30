from sqlalchemy import Integer, String, Column, update, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import Session, relationship
from .database import Base

from pydantic import BaseModel
from attrs import define

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    content = Column(Text)
    created_time = Column(DateTime(timezone=True), server_default=func.now())
    author_id = Column(Integer, ForeignKey("users.id"))
    shanyrak_id = Column(Integer, ForeignKey("shanyraks.id"))

    author = relationship("User", back_populates="comments")
    shanyraks = relationship("Shanyrak", back_populates="comments")

class CommentRequest(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: int
    content: str
    created_time: str
    author_id: int   

@define
class CommentSave():
    content: str    

class CommentsRepository():
    def save(self, db: Session, comment: CommentSave, author_id: int, shanyrak_id: int) -> int:
        db_comment = Comment(**comment.model_dump(), author_id=author_id, shanyrak_id=shanyrak_id)
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment.id 
    
    def get_comments_by_shanyrak_id(self, db: Session, shanyrak_id: int) -> list[Comment]:
        return db.query(Comment).filter(Comment.shanyrak_id == shanyrak_id).all()
    
    def get_comments_by_id(self, db: Session, comment_id: int) -> Comment:
        return db.query(Comment).filter(Comment.id == comment_id).first()
    
    def update(self, db: Session, comment_id: int, new_comment: CommentSave):
        comment = update(Comment).where(Comment.id == comment_id).values(**new_comment.model_dump())
        db.execute(comment)
        db.commit()
        return comment
    
    def delete(self, db: Session, comment: Comment) -> bool:
        db.delete(comment)
        db.commit()
        return True
    

