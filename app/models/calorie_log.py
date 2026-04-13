from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field

class CalorieLog(SQLModel, table=True):
    __tablename__ = "calorielog"  # explicit table name to avoid conflicts
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    log_date: date = Field(index=True)  # renamed from 'date' to avoid clash
    calories: int = Field(default=0)