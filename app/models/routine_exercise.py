from typing import Optional
from sqlmodel import Field, SQLModel


class RoutineExercise(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    routine_id: int = Field(foreign_key="routine.id")
    exercise_id: int = Field(foreign_key="exercise.id")
    image_url: Optional[str] = None
    body_part: Optional[str] = None
    target_muscle: Optional[str] = None
    secondary_muscle: Optional[str] = None
    equipment: Optional[str] = None
    difficulty: Optional[str] = None
    exercise_type: Optional[str] = None
    sets: Optional[int] = Field(default=None)
    reps: Optional[int] = Field(default=None)