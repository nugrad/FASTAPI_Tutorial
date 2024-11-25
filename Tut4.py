# Tutorial # 4 : Relationships Between the Tables
from fastapi import FastAPI,Depends,HTTPException,status
from pydantic import BaseModel
from sqlalchemy import create_engine,Column,String,Integer,Float,Boolean
from sqlalchemy.orm import declarative_base,sessionmaker,Session
from typing import Optional,List
import bcrypt
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

app=FastAPI()
DATABASE_URL = "sqlite:///./Blogs.db"  # SQLite database file
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# Session for interacting with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()


# A SQLAlchemny ORM Place
class DBBlog(Base):
    __tablename__ = 'blogs'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    description = Column(String, nullable=True)
    author_id = Column(Integer, ForeignKey('authors.id'))  # ForeignKey to the authors table

    # Relationship to DBAuthor
    writer = relationship("DBAuthor", back_populates="writings")
    


class DBAuthor(Base):
     __tablename__ = 'authors'

     id = Column(Integer, primary_key=True, index=True)
     name = Column(String(50))
     email=Column(String,unique=True)
     password=Column(String)   

     # Relationship to DBBlog
     writings= relationship("DBBlog", back_populates="writer")

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models for request/response validation
class Blogs(BaseModel):
    id: int  # Add this to include `id` in the response
    name: str
    description:str
    author_id: int  # To show which user owns this blog
    
    

    class Config:
        orm_mode = True


class AuthorCreate(BaseModel):
    name:str
    email:str
    password:str

class AuthorResponse(BaseModel):
    id:int
    name:str
    email:str

    class Config:
        orm_mode = True
#-----------------------------------------
# Endpoints
# Routes for interacting with the API
# Create Blog
@app.post('/create-blog/',response_model=Blogs,tags=["Blogs"])
def create_blog(blog:Blogs,db:Session=Depends(get_db)):
    # # Check if a blog with the same ID already exists
    # existing_blog = db.query(DBBlog).filter(DBBlog.id == blog.id).first()
    # if existing_blog:
    #     raise HTTPException(status_code=400, detail="Blog with this ID already exists.")
    
    # Create a new blog entry
    author=db.query(DBAuthor).filter(DBAuthor.id == blog.author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author  not found")
    
    db_blog = DBBlog( name=blog.name, description=blog.description,author_id=blog.author_id)  
    db.add(db_blog)
    db.commit()
    db.refresh(db_blog)
    
    return db_blog
    

# get blog by id
@app.get('/get-place/{blog_id}',response_model=Blogs,tags=["Blogs"])
def get_blog(blog_id:int,db: Session = Depends(get_db)):
    blog=db.query(DBBlog).filter(DBBlog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="blog not found")
    return blog

# get all blogs
@app.get('/get-all-blogs',response_model=List[Blogs],tags=["Blogs"])
def get_all_blogs(db: Session = Depends(get_db)):
    blogs_all=db.query(DBBlog).all()
    return blogs_all

# get blog created by specific user
@app.get('/get-author-blogs/{author_id}', response_model=List[Blogs], tags=["Authors"])
def get_author_blogs(author_id: int, db: Session = Depends(get_db)):
    author = db.query(DBAuthor).filter(DBAuthor.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    return author.writings  # Automatically fetches all blogs associated with the author

# PUT - Update a Blog
@app.put('/update-blog/{blog_id}', response_model=Blogs,tags=["Blogs"])
def update_blog(blog_id: int, updated_blog: Blogs, db: Session = Depends(get_db)):
    blog = db.query(DBBlog).filter(DBBlog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="blog not found")

    # Update the blog's fields
    blog.name = updated_blog.name
    blog.description = updated_blog.description
    
    db.commit()
    db.refresh(blog)  # Refresh to get the updated data from the database
    return blog

# DELETE - Delete a blog
@app.delete('/delete-blog/{blog_id}', status_code=status.HTTP_204_NO_CONTENT,tags=["Blogs"])
def delete_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(DBBlog).filter(DBBlog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="blog not found")

    db.delete(blog)
    db.commit()
    return {"detail": "blog successfully deleted"}

# Password hashing and verification functions using bcrypt
def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Create a author
@app.post('/create-author',response_model=AuthorResponse,tags=["Authors"])
def create_author(author:AuthorCreate,db:Session=Depends(get_db)):
    # Check if the email is already registered
    existing_author = db.query(DBAuthor).filter(DBAuthor.email == author.email).first()
    if existing_author:
        raise HTTPException(status_code=400, detail="Email is already registered")
    
    # Hash the password and create the author
    hashed_password = get_password_hash(author.password)
    db_author = DBAuthor(name=author.name, email=author.email, password=hashed_password)

    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author

# Get a author
@app.get('/get-author/{author_id}',response_model=AuthorResponse,tags=["Authors"])
def get_author(author_id:int,db:Session=Depends(get_db)):
    author=db.query(DBAuthor).filter(DBAuthor.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="place not found")
    return author

# logging in the author
@app.post('/login',tags=["login"])
def login(email: str, password: str, db: Session = Depends(get_db)):
    author = db.query(DBAuthor).filter(DBAuthor.email == email).first()
    if not author or not verify_password(password, author.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"message": "Login successful!"}