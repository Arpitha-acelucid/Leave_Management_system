from pydantic import BaseModel
from datetime import datetime, timezone


class UserCreate(BaseModel):
    first_name : str
    last_name : str    
    email : str
    password : str

class UserOut(BaseModel):
    id : int
    first_name : str
    last_name : str
    email : str

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email : str
    password : str

class AdminLoginSchema(BaseModel):
    username : str
    password : str

class LeaveApplicationCreate(BaseModel):
    from_date : datetime
    to_date : datetime
    applying_to : str
    cc_to : str
    reason : str

class LeaveApplicationout(BaseModel):
    id : int
    from_date : datetime
    to_date : datetime
    applying_to : str
    cc_to : str
    reason : str
    status : str
    class Config:
        from_attributes = True

class LeaveBalanceOut(BaseModel):
    balance_leave : int
    class Config:
        from_attributes = True
