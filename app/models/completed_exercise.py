from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field


class CompletedExercise(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    exercise_id: int = Field(foreign_key="exercise.id")
    routine_id: int = Field(default=None, foreign_key="routine.id")
    completed_on: date