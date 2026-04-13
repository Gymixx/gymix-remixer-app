from fastapi import APIRouter, Query, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.database import engine
from app.models.exercise import Exercise

router = APIRouter(prefix="/exercises", tags=["Exercises"])


@router.get("/")
def get_exercises(
    body_part: str | None = Query(default=None),
    target_muscle: str | None = Query(default=None),
    difficulty: str | None = Query(default=None),
):
    with Session(engine) as session:
        statement = select(Exercise)

        if body_part:
            statement = statement.where(Exercise.body_part.contains(body_part))

        if target_muscle:
            statement = statement.where(Exercise.target_muscle.contains(target_muscle))

        if difficulty:
            statement = statement.where(Exercise.difficulty == difficulty)

        exercises = session.exec(statement).all()
        return exercises
    
    
@router.post("/delete/{exercise_id}")
def delete_exercise(exercise_id: int):
    with Session(engine) as session:
        exercise = session.get(Exercise, exercise_id)
        if exercise:
            session.delete(exercise)
            session.commit()
    return RedirectResponse(url="/app", status_code=status.HTTP_303_SEE_OTHER)