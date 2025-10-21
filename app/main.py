from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from . import models, schemas, services, database, auth
from fastapi.security import OAuth2PasswordRequestForm
from app.database import init_db
from openai import OpenAI
import os,json



load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()





init_db()
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
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)): 
    user = services.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
@app.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user
@app.post("/ai")
async def analyze_transaction(data : schemas.AIinput, db: Session = Depends(get_db),current_user: models.User = Depends(auth.get_current_user)):
    prompt = f"""
You are an intelligent financial assistant.
Your task is to analyze the following sentence and determine whether it represents an income or an expense transaction.

Rules:
- Words like "buy", "pay", "eat", "spend" → expense  
- Words like "receive", "salary", "sell", "refund" → income  
- If no monetary transaction is detected → none  
- If no currency is mentioned, default to "EUR".

Return a JSON object strictly in the following format:
{{
  "type": "income" | "expense" | "none",
  "category": "food" | "salary" | "shopping" | "other",
  "amount": numeric value or 0,
  "date": datetime = None
  "description": short summary in English
  "id": int
  "owner_id": int
}}

User input: "{data.input_text}"
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts financial transaction details."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,)
    content = response.choices[0].message.content
    try: 
        result = json.loads(content)
    except json.JSONDecodeError:
        return {"error": "Invalid AI response", "raw": content}
    if result.get("type") in ["income", "expense"]:
        txn_data = schemas.TransactionCreate(
            type=result["type"],
            category=result.get("category", "other"),
            amount=result.get("amount", 0),
            description=result.get("description", data.input_text)
        )
        txn = services.create_transaction(db, txn_data, current_user.id)
        return txn

    return result