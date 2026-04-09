from fastapi import APIRouter
from sqlmodel import Session, select

from app.database import engine
from app.models.routine import Routine
from app.models.routine_exercise import RoutineExercise
from app.models.exercise import Exercise

router = APIRouter(prefix="/routines", tags=["Routines"])


@router.post("/")
def create_routine(name: str, user_id: int):
    with Session(engine) as session:
        routine = Routine(name=name, user_id=user_id)
        session.add(routine)
        session.commit()
        session.refresh(routine)
        return routine


@router.get("/")
def get_routines():
    with Session(engine) as session:
        routines = session.exec(select(Routine)).all()
        return routines


@router.get("/{routine_id}")
def get_routine(routine_id: int):
    with Session(engine) as session:
        routine = session.get(Routine, routine_id)
        if not routine:
            return {"message": "Routine not found"}

        routine_exercises = session.exec(
            select(RoutineExercise).where(RoutineExercise.routine_id == routine_id)
        ).all()

        results = []
        for item in routine_exercises:
            exercise = session.get(Exercise, item.exercise_id)
            if exercise:
                results.append({
                    "id": item.id,
                    "exercise_id": exercise.id,
                    "exercise_name": exercise.name,
                    "sets": item.sets,
                    "reps": item.reps
                })

        return {
            "routine": routine,
            "exercises": results
        }


@router.post("/{routine_id}/add-exercise")
def add_exercise_to_routine(routine_id: int, exercise_id: int, sets: int = 3, reps: int = 10):
    with Session(engine) as session:
        routine = session.get(Routine, routine_id)
        exercise = session.get(Exercise, exercise_id)

        if not routine:
            return {"message": "Routine not found"}

        if not exercise:
            return {"message": "Exercise not found"}

        routine_exercise = RoutineExercise(
            routine_id=routine_id,
            exercise_id=exercise_id,
            sets=sets,
            reps=reps
        )

        session.add(routine_exercise)
        session.commit()
        session.refresh(routine_exercise)

        return {"message": "Exercise added to routine", "routine_exercise": routine_exercise}


@router.delete("/{routine_id}/remove-exercise/{routine_exercise_id}")
def remove_exercise_from_routine(routine_id: int, routine_exercise_id: int):
    with Session(engine) as session:
        routine_exercise = session.get(RoutineExercise, routine_exercise_id)

        if not routine_exercise or routine_exercise.routine_id != routine_id:
            return {"message": "Routine exercise not found"}

        session.delete(routine_exercise)
        session.commit()

        return {"message": "Exercise removed from routine"}