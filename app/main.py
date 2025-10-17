from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from . import models, schemas, services, database, auth


app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = services.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return services.create_user(db, user)
@app.post("/transactions/", response_model=schemas.TransactionOut)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db),current_user: models.User = Depends(auth.get_current_user)):
    return services.create_transaction(db, transaction, current_user.id)
@app.get("/transactions/", response_model=list[schemas.TransactionOut])
def list_transactions(db: Session = Depends(get_db),current_user: models.User = Depends(auth.get_current_user)):
    return services.get_transactions_by_user(db, current_user.id)
@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = services.get_user_by_username(db, username=username)
    if not user or not auth.verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}