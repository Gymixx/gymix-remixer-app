from typing import Optional
from sqlmodel import Field, SQLModel


class Exercise(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    exercise_id: str = Field(index=True, unique=True)
    name: str

    image_url: Optional[str] = None
    video_url: Optional[str] = None

    gender: Optional[str] = None
    exercise_type: Optional[str] = None
    body_part: Optional[str] = None
    equipment: Optional[str] = None
    target_muscle: Optional[str] = None
    secondary_muscle: Optional[str] = None

    overview: Optional[str] = None
    instructions: Optional[str] = None
    exercise_tips: Optional[str] = None
    variations: Optional[str] = None
    related_exercise_ids: Optional[str] = None