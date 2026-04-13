from datetime import date
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint


class WorkoutLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    date: date

    __table_args__ = (UniqueConstraint("user_id", "date"),)