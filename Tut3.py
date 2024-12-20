# Tutorial # 3 : Database , User login, password hashing
from fastapi import FastAPI,Depends,HTTPException,status
from pydantic import BaseModel
from sqlalchemy import create_engine,Column,String,Integer,Float,Boolean
from sqlalchemy.orm import declarative_base,sessionmaker,Session
from typing import Optional,List
# from passlib.context import CryptContext
import bcrypt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import jwt

app=FastAPI()

DATABASE_URL = "sqlite:///./places.db"  # SQLite database file
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

# JWT configuration
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30




# Password hashing and verification functions using bcrypt
def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT helper functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# A SQLAlchemny ORM Place
class DBPlace(Base):
    __tablename__ = 'places'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    description = Column(String, nullable=True)
    coffee = Column(Boolean)
    wifi = Column(Boolean)
    food = Column(Boolean)


class DBUser(Base):
     __tablename__ = 'users'

     id = Column(Integer, primary_key=True, index=True)
     name = Column(String(50))
     email=Column(String,unique=True)
     password=Column(String)   
# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models for request/response validation
class Place(BaseModel):
    id: int  # Add this to include `id` in the response
    name: str
    description: Optional[str] = None
    coffee: bool
    wifi: bool
    food: bool
    

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    name:str
    email:str
    password:str

class UserResponse(BaseModel):
    id:int
    name:str
    email:str

    class Config:
        orm_mode = True
#--------------------------------------------
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/secure-endpoint", tags=["Secure"])
def secure_endpoint(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    return {"message": f"Hello {payload['sub']}! You have accessed a secure endpoint."}
# -------------------------------------------
# Endpoints
# Routes for interacting with the API
# Create Place
@app.post('/create-place/',response_model=Place,tags=["Places"])
def create_place(place:Place,db:Session=Depends(get_db)):
    db_place=DBPlace(name=place.name,description=place.description,coffee=place.coffee,wifi=place.wifi,food=place.food)
    # db_place = DBPlace(**place.dict())
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place

# get place by id
@app.get('/get-place/{place_id}',response_model=Place,tags=["Places"])
def get_place(place_id:int,db: Session = Depends(get_db)):
    place=db.query(DBPlace).filter(DBPlace.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="place not found")
    return place

# get all places
@app.get('/get-all-places',response_model=List[Place],tags=["Places"])
def get_all_places(db: Session = Depends(get_db)):
    places_all=db.query(DBPlace).all()
    return places_all

# PUT - Update a place
@app.put('/update-place/{place_id}', response_model=Place,tags=["Places"])
def update_place(place_id: int, updated_place: Place, db: Session = Depends(get_db)):
    place = db.query(DBPlace).filter(DBPlace.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")

    # Update the place's fields
    place.name = updated_place.name
    place.description = updated_place.description
    place.coffee = updated_place.coffee
    place.wifi = updated_place.wifi
    place.food = updated_place.food

    db.commit()
    db.refresh(place)  # Refresh to get the updated data from the database
    return place

# DELETE - Delete a place
@app.delete('/delete-place/{place_id}', status_code=status.HTTP_204_NO_CONTENT,tags=["Places"])
def delete_place(place_id: int, db: Session = Depends(get_db)):
    place = db.query(DBPlace).filter(DBPlace.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")

    db.delete(place)
    db.commit()
    return {"detail": "Place successfully deleted"}

# -----------------------------------------
# Now Handling the user , login, password hashing things
# For this we would create another Pydantic model for user
#----------------------------


# Create a User
@app.post('/create-user',response_model=UserResponse,tags=["Users"])
def create_user(user:UserCreate,db:Session=Depends(get_db)):
    # Check if the email is already registered
    existing_user = db.query(DBUser).filter(DBUser.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")
    
    # Hash the password and create the user
    hashed_password = get_password_hash(user.password)
    db_user = DBUser(name=user.name, email=user.email, password=hashed_password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Get a User
@app.get('/get-user/{user_id}',response_model=UserResponse,tags=["Users"])
def get_user(user_id:int,db:Session=Depends(get_db)):
    user=db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="place not found")
    return user





    