from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select

from app.database import engine
from app.models.routine import Routine
from app.models.routine_exercise import RoutineExercise
from app.models.exercise import Exercise
from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.routers import templates

router = APIRouter(prefix="/routines", tags=["Routines"])


@router.get("", response_class=HTMLResponse)
async def routines_page(request: Request, user: AuthDep, db: SessionDep):
    routines_raw = db.exec(select(Routine).where(Routine.user_id == user.id)).all()

    routines = []
    for routine in routines_raw:
        routine_exercises = db.exec(
            select(RoutineExercise).where(RoutineExercise.routine_id == routine.id)
        ).all()
        exercises = []
        for item in routine_exercises:
            exercise = db.get(Exercise, item.exercise_id)
            if exercise:
                exercises.append({"name": exercise.name, "sets": item.sets, "reps": item.reps})
        routines.append({"id": routine.id, "name": routine.name, "exercises": exercises})

    return templates.TemplateResponse(
        request=request,
        name="routines.html",
        context={"user": user,
                "routines": routines},
    )


@router.post("/create")
async def create_routine_form(user: AuthDep, db: SessionDep, name: str = Form(...)):
    routine = Routine(name=name, user_id=user.id)
    db.add(routine)
    db.commit()
    return RedirectResponse(url="/routines", status_code=303)


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


@router.post("/{exercise_id}/add-exercise")
async def add_exercise_to_routine(
    exercise_id: int,
    db: SessionDep,
    user: AuthDep,
    routine_id: int = Form(...),
):
    routine_exercise = RoutineExercise(
        routine_id=routine_id,
        exercise_id=exercise_id,
        sets=3,
        reps=10,
    )
    db.add(routine_exercise)
    db.commit()
    return RedirectResponse(url="/app", status_code=303)


@router.delete("/{routine_id}/remove-exercise/{routine_exercise_id}")
def remove_exercise_from_routine(routine_id: int, routine_exercise_id: int):
    with Session(engine) as session:
        routine_exercise = session.get(RoutineExercise, routine_exercise_id)

        if not routine_exercise or routine_exercise.routine_id != routine_id:
            return {"message": "Routine exercise not found"}

        session.delete(routine_exercise)
        session.commit()

        return {"message": "Exercise removed from routine"}