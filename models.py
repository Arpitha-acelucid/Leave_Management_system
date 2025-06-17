from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone

class User(Base):
    __tablename__ = "user_table"
    id = Column(Integer, primary_key = True, index = True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique = True)
    password_hash = Column(String)

    leave_balance = relationship("LeaveBalance", back_populates= "user", uselist=False)
    leave_applications = relationship("LeaveApplication", back_populates="user")

class LeaveBalance(Base):
    __tablename__ = "leave_balance_table"
    id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("user_table.id"))
    balance_leave = Column(Integer, default = 30)

    user = relationship("User", back_populates="leave_balance")

class LeaveApplication(Base):
    __tablename__ = "leave_application_table"
    id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("user_table.id"))
    from_date = Column(DateTime(timezone=True))
    to_date = Column(DateTime(timezone=True))       
    reason = Column(String)
    applying_to = Column(String)
    cc_to = Column(String)
    status = Column(String, default = "Pending")

    user = relationship("User", back_populates=("leave_applications"))
