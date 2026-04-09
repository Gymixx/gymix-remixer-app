from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


class Routine(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    user_id: int = Field(foreign_key="user.id")