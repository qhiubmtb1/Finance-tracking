from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    total_money: float = 0.0 
    class Config:
        orm_mode = True
class TransactionCreate(BaseModel):
    type: str  
    category: str
    amount: float
    date: datetime = None
    description: str = None
class TransactionOut(TransactionCreate):
    id: int
    owner_id: int

    class Config:
        orm_mode = True