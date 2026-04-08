from sqlmodel import Field, SQLModel, Optional 
from typing import Optional
from pydantic import EmailStr

class Exercise(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    exerciseId: str = Field(index=True, unique=True)
    name: str
    imageUrl: str
    videoUrl: str
    gender: str
    excersiseType: str
    bodyPart: str
    equipment: str
    targetMuscle: str
    secondaryMuscle: Optional[str] = None
    overview: Optional[str] = None
    instructions: Optional[str] = None
    exerciseTips: str
    variations: str
    relatedExercisesId: str
    
    


