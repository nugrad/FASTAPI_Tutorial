from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, database, hashing

router = APIRouter(
    prefix="/authors",
    tags=["Authors"]
)

# Create an Author
@router.post("/", response_model=schemas.AuthorResponse)
def create_author(author: schemas.AuthorCreate, db: Session = Depends(database.get_db)):
    existing_author = db.query(models.DBAuthor).filter(models.DBAuthor.email == author.email).first()
    if existing_author:
        raise HTTPException(status_code=400, detail="Email is already registered")

    hashed_password = hashing.get_password_hash(author.password)
    db_author = models.DBAuthor(name=author.name, email=author.email, password=hashed_password)

    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author

# Get an Author by ID
@router.get("/{author_id}", response_model=schemas.AuthorResponse)
def get_author(author_id: int, db: Session = Depends(database.get_db)):
    author = db.query(models.DBAuthor).filter(models.DBAuthor.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author

# Log in Author
@router.post("/login")
def login(email: str, password: str, db: Session = Depends(database.get_db)):
    author = db.query(models.DBAuthor).filter(models.DBAuthor.email == email).first()
    if not author or not hashing.verify_password(password, author.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"message": "Login successful!"}
