from fastapi import Cookie, FastAPI, Form, Response, HTTPException, Depends
from jose import jwt
from fastapi.security import OAuth2PasswordBearer

from .user_repository import UserRequest, UserRepository, UserUpdateRequest, UserResponse
from .shanyrak_repository import ShanyrakRepository, ShanyrakRequest, ShanyrakResponse
from .comments_repository import CommentRequest, CommentsRepository, CommentResponse

from sqlalchemy.orm import Session
from .database import SessionLocal, Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/login")

users = UserRepository()
shanyraks = ShanyrakRepository()
comments_repo = CommentsRepository()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def encode_jwt(id: int):
    data = {"user_id": id}
    token = jwt.encode(data, "Kamila", algorithm="HS256")
    return token    

def decode_jwt(token):
    data = jwt.decode(token, "Kamila", algorithms="HS256")
    return data["user_id"]

@app.post("/auth/users/")
def registration(user: UserRequest, db: Session=Depends(get_db)):
    user_check = users.get_user_username(db, user.username)
    if user_check:
        raise HTTPException(status_code=400, detail="This user already exists")
    users.save(db, user)
    return Response()

@app.post("/auth/users/login")
def login(username: str=Form(), password: str=Form(), db: Session=Depends(get_db)):
    user = users.get_user_username(db, username)
    if not user or not password == user.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    token = encode_jwt(user.id)
    return {"access_token": token, "type": "bearer"}

@app.patch("/auth/users/me")
def patch_user_info(new_user: UserUpdateRequest, db: Session=Depends(get_db), 
                    token: str=Depends(oauth2_scheme)):
    user_id = decode_jwt(token)
    users.update(db, user_id, new_user)
    return Response()

@app.get("/auth/users/me", response_model=UserResponse)
def get_profile(token: str=Depends(oauth2_scheme), db: Session=Depends(get_db)):
    user_id = decode_jwt(token)
    user = users.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not Found")
    return user

@app.post("/shanyraks/")
def post_shanyraks(shanyrak: ShanyrakRequest, token: str=Depends(oauth2_scheme), 
                   db: Session=Depends(get_db)):
    user_id = decode_jwt(token)
    shanyrak_id = shanyraks.save(db, shanyrak, user_id)
    return {"id":shanyrak_id}

@app.get("/shanyraks/{id}", response_model=ShanyrakResponse)
def get_shanyrak(id: int, token: str=Depends(oauth2_scheme), 
                 db: Session=Depends(get_db)):
    shanyrak = shanyraks.get_shanyrak(db, id)
    if not shanyrak:
        raise HTTPException(status_code=404, detail="Not Found")
    return shanyrak

@app.patch("/shanyraks/{id}")
def patch_shanyrak(id: int, new_shanyrak: ShanyrakRequest,
                   token: str=Depends(oauth2_scheme), db: Session=Depends(get_db)):
    shanyrak = shanyraks.get_shanyrak(db, id)
    user_id = decode_jwt(token)
    if not shanyrak:
        raise HTTPException(status_code=404, detail="Not Found")
    if shanyrak.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    shanyraks.update(db, id, new_shanyrak)
    return Response()

@app.delete("/shanyraks/{id}")
def delete_shanyrak(id: int, token: str=Depends(oauth2_scheme), db: Session=Depends(get_db)):
    shanyrak = shanyraks.get_shanyrak(db, id)
    user_id = decode_jwt(token)
    if not shanyrak:
        raise HTTPException(status_code=404, detail="Not Found")
    if shanyrak.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    shanyraks.delete(db, shanyrak)
    return Response()

@app.post("/shanyraks/{id}/comments")
def post_comments(id: int, comment: CommentRequest, token: str=Depends(oauth2_scheme), 
                  db: Session=Depends(get_db)):
    user_id = decode_jwt(token)
    comments_repo.save(db, comment, user_id, id)
    shanyraks.plus_total_comment(db, id)
    return Response()

@app.get("/shanyraks/{id}/comments")
def get_comments(id: int, token: str=Depends(oauth2_scheme), 
                  db: Session=Depends(get_db)):
    comments = comments_repo.get_comments_by_shanyrak_id(db, id)
    return {"comments": comments}

@app.patch("/shanyraks/{id}/comments/{comment_id}")
def patch_comment(comment_id: int, new_comment: CommentRequest,
                  token: str=Depends(oauth2_scheme), db: Session=Depends(get_db)):
    comment = comments_repo.get_comments_by_id(db, comment_id)
    user_id = decode_jwt(token)
    if not comment:
        raise HTTPException(status_code=404, detail="Not Found")
    if comment.author_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    comments_repo.update(db, comment_id, new_comment)
    return Response()

@app.delete("/shanyraks/{id}/comments/{comment_id}")
def delete_shanyrak(comment_id: int, id: int,
                    token: str=Depends(oauth2_scheme), db: Session=Depends(get_db)):
    comment = comments_repo.get_comments_by_id(db, comment_id)
    user_id = decode_jwt(token)
    if not comment:
        raise HTTPException(status_code=404, detail="Not Found")
    if comment.author_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    comments_repo.delete(db, comment)
    shanyraks.minus_total_comment(db, id)
    return Response()

    
