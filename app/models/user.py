from sqlmodel import Field, SQLModel  
from typing import Optional
from pydantic import EmailStr


class UserBase(SQLModel,):
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password: str
    role:str = Field(default="user")

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    weight: Optional[float] = None
    height: Optional[float] = None
    gender: Optional[str] = None
    activity_level: Optional[str] = None
    goal: Optional[str] = None
    body_fat_percentage: Optional[float] = None
    age: Optional[int] = None