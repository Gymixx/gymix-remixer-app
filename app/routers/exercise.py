from fastapi import APIRouter
from sqlmodel import Session, select

from app.database import engine
from app.models.exercise import Exercise

router = APIRouter(prefix="/exercises", tags=["Exercises"])


@router.get("/")
def get_exercises():
    with Session(engine) as session:
        exercises = session.exec(select(Exercise)).all()
        return exercises