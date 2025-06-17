from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import schemas, crud
from database import engine, Base, get_db
from admin_config import ADMIN_CREDENTIALS

# create the tables defined in the models 
Base.metadata.create_all(bind=engine)

app = FastAPI()

# root
@app.get("/")
def root():
    return {"message": "Hello, Leave Management App is running"}


# creating a user sign_up
@app.post("/signup", response_model= schemas.UserOut)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

# user login
@app.post("/login", response_model= schemas.UserOut)
def login(data: schemas.LoginSchema, db: Session = Depends(get_db)):
    user = crud.login_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code = 401, detail = "Invalid credentials" )
    return user
    
# applying for leave
@app.post("/apply_leave/{user_id}")
def apply_leave(user_id : int, leave : schemas.LeaveApplicationCreate, db : Session = Depends(get_db)):
    return crud.apply_leave(db, user_id, leave)

# cancle leave
@app.post("/cancel_leave/{user_id}/{leave_id}")
def cancel_leave(user_id : int, leave_id : int,db: Session = Depends(get_db)):
    leave = crud.cancel_leave(db, user_id, leave_id)
    if not leave:
        raise HTTPException(status_code= 404, detail = "Leave not found or already processed")
    return leave

# get balance leave
@app.get("/leave_balance/{user_id}", response_model= schemas.LeaveBalanceOut)
def leave_balance(user_id : int, db : Session = Depends(get_db)):
    return crud.get_leave_balance(db, user_id)

# get user info
@app.get("/user_info/{user_id}", response_model= schemas.UserOut)
def user_info(user_id : int, db : Session = Depends(get_db)):
    user = crud.get_user_info(db, user_id)
    if not user:
        raise HTTPException(status_code= 404, detail = "user not found")
    return user

# get all leave applications
@app.get("/get_leave_applications/{user_id}", response_model= list[schemas.LeaveApplicationout])
def get_leave_applications(user_id : int, db : Session = Depends(get_db)):
    return crud.get_user_leave_applications(db, user_id)

# get leave by id
@app.get("/get_leave_by_id/{leave_id}", response_model= schemas.LeaveApplicationout)
def get_leave_by_id(leave_id :int , db: Session = Depends(get_db)):
    leave = crud.get_leave_by_id(db, leave_id)
    if not leave:
        raise HTTPException(status_code= 404, detail = "Leave Not Found")
    return leave

# admin login 
@app.post("/admin/login")
def admin_login(data :schemas.AdminLoginSchema):
    if data.username == ADMIN_CREDENTIALS['username'] and data.password == ADMIN_CREDENTIALS['password']:
        return {"message": "Admin login successful"}
    raise HTTPException(status_code= 401, detail= "Invalid Admin Credentials")

# admint leave approval (status update)
@app.post("/admin/update_leave_status/{leave_id}")
def update_leave_status(leave_id : int,status : str, db : Session =Depends(get_db)):
    updated = crud.admin_update_leave_status(db, leave_id, status)
    if not updated:
        raise HTTPException(status_code= 404 , detail = "Leave Not Found")
    return updated

