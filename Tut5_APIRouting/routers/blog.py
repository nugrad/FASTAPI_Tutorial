from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database

router = APIRouter(
    prefix="/blogs",
    tags=["Blogs"]
)

# Create a Blog
@router.post("/", response_model=schemas.Blogs)
def create_blog(blog: schemas.Blogs, db: Session = Depends(database.get_db)):
    author = db.query(models.DBAuthor).filter(models.DBAuthor.id == blog.author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    
    db_blog = models.DBBlog(name=blog.name, description=blog.description, author_id=blog.author_id)
    db.add(db_blog)
    db.commit()
    db.refresh(db_blog)
    return db_blog

# Get a Blog by ID
@router.get("/{blog_id}", response_model=schemas.Blogs)
def get_blog(blog_id: int, db: Session = Depends(database.get_db)):
    blog = db.query(models.DBBlog).filter(models.DBBlog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog

# Get All Blogs
@router.get("/", response_model=List[schemas.Blogs])
def get_all_blogs(db: Session = Depends(database.get_db)):
    blogs_all = db.query(models.DBBlog).all()
    return blogs_all

# Get Blogs by Specific Author
@router.get("/author/{author_id}", response_model=List[schemas.Blogs])
def get_author_blogs(author_id: int, db: Session = Depends(database.get_db)):
    author = db.query(models.DBAuthor).filter(models.DBAuthor.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    return author.writings  # Automatically fetches all blogs for the author

# Update a Blog
@router.put("/{blog_id}", response_model=schemas.Blogs)
def update_blog(blog_id: int, updated_blog: schemas.Blogs, db: Session = Depends(database.get_db)):
    blog = db.query(models.DBBlog).filter(models.DBBlog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    blog.name = updated_blog.name
    blog.description = updated_blog.description

    db.commit()
    db.refresh(blog)  # Refresh to get updated data from the database
    return blog

# Delete a Blog
@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(blog_id: int, db: Session = Depends(database.get_db)):
    blog = db.query(models.DBBlog).filter(models.DBBlog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    db.delete(blog)
    db.commit()
    return {"detail": "Blog successfully deleted"}
