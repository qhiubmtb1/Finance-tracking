from sqlalchemy.orm import Session
from . import models, schemas,auth  

def create_user(db:Session,user : schemas.UserCreate):
    hashed_pw = auth.hash_password(user.password)
    db_user = models.User(username=user.username,email=user.email,hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
def get_user_by_username(db:Session,username:str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_transaction(db:Session,transaction:schemas.TransactionCreate,user_id:int):
    db_transaction = models.Transaction(**transaction.dict(),owner_id=user_id)

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    update_total_money(db,user_id,transaction.type,transaction.amount)
    return db_transaction

def get_transactions_by_user(db:Session,user_id:int):
    return db.query(models.Transaction).filter(models.Transaction.owner_id == user_id).all()
def update_total_money(db:Session,user_id:int,type:str,amount: float):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user : 
        return None
    if type == 'income':
        user.total_money +=amount
    elif type == 'expense':
        user.total_money -=amount
    db.commit()
    db.refresh(user)
    return user.total_money