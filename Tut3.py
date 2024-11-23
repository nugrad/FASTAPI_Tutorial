# Tutorial # 3 : Database and CRUD Operations
from fastapi import FastAPI,Depends,HTTPException,status
from pydantic import BaseModel
from sqlalchemy import create_engine,Column,String,Integer,Float,Boolean
from sqlalchemy.orm import declarative_base,sessionmaker,Session
from typing import Optional,List

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


# A SQLAlchemny ORM Place
class DBPlace(Base):
    __tablename__ = 'places'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    description = Column(String, nullable=True)
    coffee = Column(Boolean)
    wifi = Column(Boolean)
    food = Column(Boolean)
    
# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic model for request/response validation
class Place(BaseModel):
    id: int  # Add this to include `id` in the response
    name: str
    description: Optional[str] = None
    coffee: bool
    wifi: bool
    food: bool
    

    class Config:
        orm_mode = True

# -------------------------------------------
# Endpoints
# Routes for interacting with the API
# Create Place
@app.post('/create-place/',response_model=Place)
def create_place(place:Place,db:Session=Depends(get_db)):
    db_place=DBPlace(name=place.name,description=place.description,coffee=place.coffee,wifi=place.wifi,food=place.food)
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place

# get place by id
@app.get('/get-place/{place_id}',response_model=Place)
def get_item(item_id:int,db: Session = Depends(get_db)):
    place=db.query(DBPlace).filter(DBPlace.id == item_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="place not found")
    return place

# get all places
@app.get('/get-all-places',response_model=List[Place])
def get_all_places(db: Session = Depends(get_db)):
    places_all=db.query(DBPlace).all()
    return places_all

# PUT - Update a place
@app.put('/update-place/{place_id}', response_model=Place)
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
@app.delete('/delete-place/{place_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_place(place_id: int, db: Session = Depends(get_db)):
    place = db.query(DBPlace).filter(DBPlace.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")

    db.delete(place)
    db.commit()
    return {"detail": "Place successfully deleted"}