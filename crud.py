import traceback
from sqlalchemy.orm import Session
import models, schemas
from auth import hash_password, verify_password
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

def create_user(db: Session, user: schemas.UserCreate):
    try:
        hashed_pw = hash_password(user.password)
        db_user = models.User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password_hash=hashed_pw,            
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        leave_balance = models.LeaveBalance(user_id=db_user.id)
        db.add(leave_balance)
        db.commit()
        return db_user

    except SQLAlchemyError as e:
        db.rollback()
        print("Error creating user:", e)
        traceback.print_exc()  
        raise HTTPException(status_code=500, detail="Error creating user")

def login_user(db :Session, email : str, password : str):
    try:
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    except SQLAlchemyError:  
        raise HTTPException(status_code = 500, detail = "Error doing login")    

def apply_leave(db: Session, user_id : int, leave :  schemas.LeaveApplicationCreate):
    try:
        leave_app = models.LeaveApplication(user_id = user_id, status = "Pending",**leave.dict())
        db.add(leave_app)
        db.commit()
        db.refresh(leave_app)
        return leave_app
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code = 500, detail = "Error applying for leave")

def cancel_leave(db: Session, user_id : int, leave_id : int):
    try:
        leave = db.query(models.LeaveApplication).filter_by(
            id  = leave_id, user_id = user_id, status = "Pending"
        ).first()
        if not leave:
            return None

        leave.status = "Cancelled"
        db.commit()
        return leave
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code = 500, detail = "Error cancelling leave")

def get_leave_balance(db: Session, user_id : int):
    try:
        return db.query(models.LeaveBalance).filter_by(user_id = user_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code = 500, detail = "Error fetching leave balance")    

def get_user_info(db : Session, user_id : int):
    try:
        return db.query(models.User).filter_by(id = user_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code = 500, detail = "Error fetching user info")

def get_user_leave_applications(db : Session, user_id : int):
    try:
        return db.query(models.LeaveApplication).filter_by(user_id = user_id).all()
    except SQLAlchemyError:
        raise HTTPException(status_code = 500, detail="Error fetching leave applications")

def get_leave_by_id(db : Session, leave_id : int):
    try:
        return db.query(models.LeaveApplication).filter_by(id=leave_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code = 500, detail="Error fetching leave" )

def admin_update_leave_status(db: Session, leave_id: int, status: str):
    try:
        leave = db.query(models.LeaveApplication).filter_by(id=leave_id).first()
        if not leave:
            return None

        if leave.status != "Pending":
            raise HTTPException(status_code=400, detail="Leave already processed")

        if status not in ["Approved", "Rejected"]:
            raise HTTPException(status_code=400, detail="Invalid status. Only 'Approved' or 'Rejected' allowed.")

        if status == "Approved":
            days = (leave.to_date - leave.from_date).days + 1
            balance = db.query(models.LeaveBalance).filter_by(user_id=leave.user_id).first()
            if not balance or balance.balance_leave < days:
                raise HTTPException(status_code=400, detail="Insufficient balance to approve leave")

            balance.balance_leave -= days
            db.add(balance)  # Optional, but makes the change explicit

        leave.status = status
        db.commit()
        return leave

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error updating leave status")

        