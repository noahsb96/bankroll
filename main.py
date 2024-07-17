from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/singles/", response_model=schemas.Single)
def create_single(single: schemas.SingleCreate, db: Session = Depends(get_db)):
    return crud.create_single(db=db, single=single)