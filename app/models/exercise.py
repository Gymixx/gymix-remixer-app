from typing import Optional
from sqlmodel import Field, SQLModel


class Exercise(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    exercise_id: str = Field(index=True, unique=True)
    name: str

    image_url: Optional[str] = None

    body_part: Optional[str] = None
    target_muscle: Optional[str] = None
    secondary_muscle: Optional[str] = None
    equipment: Optional[str] = None

    difficulty: Optional[str] = None
    exercise_type: Optional[str] = None
    instructions: Optional[str] = None
    