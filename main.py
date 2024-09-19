from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine

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
    try:
        return crud.create_single(db=db, single=single)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/singles/", response_model=list[schemas.Single])
def read_singles(limit: int = 100, db: Session = Depends(get_db)):
    singles = crud.get_singles(db, limit=limit)
    return singles

@app.post("/months/", response_model=schemas.Month)
def create_month(month: schemas.MonthCreate, db: Session = Depends(get_db)):
    try:
        db_month = crud.get_or_create_month(db=db, month_create=month)
        return db_month
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))