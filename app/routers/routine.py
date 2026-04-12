from typing import Optional
from requests import request
from app.utilities.flash import flash
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
                exercises.append({
                    "id": item.id,
                    "name": exercise.name,
                    "sets": item.sets,
                    "reps": item.reps
                })
        routines.append({
            "id": routine.id,
            "name": routine.name,
            "exercises": exercises
        })

    return templates.TemplateResponse(
        request=request,
        name="routines.html",
        context={
            "user": user,
            "routines": routines
        },
    )


@router.post("/create")
async def create_routine_form(
    request: Request, user: AuthDep, db: SessionDep, name: str = Form(...)):
    routine = Routine(name=name, user_id=user.id)
    db.add(routine)
    db.commit()
    flash(request, "Routine created successfully!")
    return RedirectResponse(url="/routines", status_code=303)


@router.post("/{routine_id}/edit")
async def edit_routine_form(
    request: Request,
    routine_id: int,
    user: AuthDep,
    db: SessionDep,
    name: str = Form(...)
):
    routine = db.get(Routine, routine_id)

    if not routine:
        return HTMLResponse("Routine not found", status_code=404)

    if routine.user_id != user.id:
        return HTMLResponse("Unauthorized", status_code=403)

    routine.name = name
    db.add(routine)
    db.commit()
    db.refresh(routine)

    return RedirectResponse(url="/routines", status_code=303)


@router.post("/{routine_id}/delete")
async def delete_routine_form(
    request: Request, routine_id: int, user: AuthDep, db: SessionDep):
    routine = db.get(Routine, routine_id)

    if not routine:
        return HTMLResponse("Routine not found", status_code=404)

    if routine.user_id != user.id:
        return HTMLResponse("Unauthorized", status_code=403)

    routine_exercises = db.exec(
        select(RoutineExercise).where(RoutineExercise.routine_id == routine_id)
    ).all()

    for item in routine_exercises:
        db.delete(item)

    db.delete(routine)
    db.commit()

    flash(request, "Routine deleted successfully!")
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


@router.get("/{routine_id}", response_class=HTMLResponse)
async def get_routine(request: Request, routine_id: int, user: AuthDep, db: SessionDep):
    routine = db.get(Routine, routine_id)
    if not routine:
        return HTMLResponse("Routine not found", status_code=404)

    if routine.user_id != user.id:
        return HTMLResponse("Unauthorized", status_code=403)

    routine_exercises = db.exec(
        select(RoutineExercise).where(RoutineExercise.routine_id == routine_id)
    ).all()

    exercises = []
    for item in routine_exercises:
        exercise = db.get(Exercise, item.exercise_id)
        if exercise:
            exercises.append({
                "id": item.id,
                "exercise_id": exercise.id,
                "exercise_name": exercise.name,
                "image_url": exercise.image_url,
                "body_part": exercise.body_part,
                "target_muscle": exercise.target_muscle,
                "secondary_muscle": exercise.secondary_muscle,
                "equipment": exercise.equipment,
                "difficulty": exercise.difficulty,
                "exercise_type": exercise.exercise_type,
                "instructions": exercise.instructions,
                "sets": item.sets,
                "reps": item.reps
            })

    return templates.TemplateResponse(
        request=request,
        name="routine_detail.html",
        context={"user": user, "routine": routine, "exercises": exercises},
    )


@router.post("/{exercise_id}/add-exercise")
async def add_exercise_to_routine(
    request: Request,
    exercise_id: int,
    db: SessionDep,
    user: AuthDep,
    routine_id: int = Form(...),
):
    routine = db.get(Routine, routine_id)

    if not routine:
        return HTMLResponse("Routine not found", status_code=404)

    if routine.user_id != user.id:
        return HTMLResponse("Unauthorized", status_code=403)

    routine_exercise = RoutineExercise(
        routine_id=routine_id,
        exercise_id=exercise_id,
        sets=3,
        reps=10,
    )
    db.add(routine_exercise)
    db.commit()

    flash(request, "Exercise added to routine!")
    return RedirectResponse(url="/app", status_code=303)


@router.post("/{routine_id}/remove-exercise/{routine_exercise_id}")
async def remove_exercise_from_routine(
    routine_id: int,
    routine_exercise_id: int,
    user: AuthDep,
    db: SessionDep,
    request: Request,
):
    routine = db.get(Routine, routine_id)

    if not routine:
        return HTMLResponse("Routine not found", status_code=404)

    if routine.user_id != user.id:
        return HTMLResponse("Unauthorized", status_code=403)

    routine_exercise = db.get(RoutineExercise, routine_exercise_id)

    if not routine_exercise or routine_exercise.routine_id != routine_id:
        return HTMLResponse("Routine exercise not found", status_code=404)

    db.delete(routine_exercise)
    db.commit()

    flash(request, "Exercise removed from routine!")
    return RedirectResponse(url=f"/routines/{routine_id}", status_code=303)