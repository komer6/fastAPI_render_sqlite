from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create the Dog model
class Dog(Base):
    __tablename__ = 'dogs'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    breed = Column(String)
    color = Column(String)

# Create the database tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()

# Pydantic model for request/response
class DogCreate(BaseModel):
    name: str
    breed: str
    color: str

class DogOut(DogCreate):
    id: int

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# GET endpoint to retrieve all dogs
@app.get("/dogs", response_model=list[DogOut])
def get_dogs(db: Session = Depends(get_db)):
    return db.query(Dog).all()

# POST endpoint to add a new dog
@app.post("/dogs", response_model=DogOut)
def create_dog(dog: DogCreate, db: Session = Depends(get_db)):
    db_dog = Dog(name=dog.name, breed=dog.breed, color=dog.color)
    try:
        db.add(db_dog)
        db.commit()
        db.refresh(db_dog)
        return db_dog
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Dog already exists")
