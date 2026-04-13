from datetime import date
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from app.database import engine
from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.models.completed_exercise import CompletedExercise
from app.models.exercise import Exercise
from app.models.routine import Routine
from app.models.routine_exercise import RoutineExercise
from app.routers import templates
from app.utilities.flash import flash

router = APIRouter(prefix="/routines", tags=["Routines"])


@router.get("", response_class=HTMLResponse)
async def routines_page(request: Request, user: AuthDep, db: SessionDep):
    routines_raw = db.exec(
        select(Routine).where(Routine.user_id == user.id)
    ).all()

    today = date.today()

    completed_today = db.exec(
        select(CompletedExercise).where(
            CompletedExercise.user_id == user.id,
            CompletedExercise.completed_on == today
        )
    ).all()

    completed_exercise_ids = {item.exercise_id for item in completed_today}

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
                    "id": exercise.id,
                    "name": exercise.name,
                    "sets": item.sets,
                    "reps": item.reps,
                    "completed": exercise.id in completed_exercise_ids
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
    request: Request,
    user: AuthDep,
    db: SessionDep,
    name: str = Form(...)
):
    routine = Routine(name=name, user_id=user.id)
    db.add(routine)
    db.commit()

    flash(request, "Routine created successfully!", "success")
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

    flash(request, "Routine updated successfully!", "success")
    return RedirectResponse(url="/routines", status_code=303)


@router.post("/{routine_id}/delete")
async def delete_routine_form(
    request: Request,
    routine_id: int,
    user: AuthDep,
    db: SessionDep
):
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

    flash(request, "Routine deleted successfully!", "success")
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
        context={
            "user": user,
            "routine": routine,
            "exercises": exercises
        },
    )


@router.post("/{exercise_id}/add-exercise")
async def add_exercise_to_routine(
    request: Request,
    exercise_id: int,
    db: SessionDep,
    user: AuthDep,
    routine_id: int = Form(...),
):
    referer = request.headers.get("referer", "/app")

    routine = db.get(Routine, routine_id)

    if not routine:
        flash(request, "Please create a routine first!")
        return RedirectResponse(url=referer, status_code=303)

    if routine.user_id != user.id:
        return HTMLResponse("Unauthorized", status_code=403)

    existing = db.exec(
        select(RoutineExercise).where(
            RoutineExercise.routine_id == routine_id,
            RoutineExercise.exercise_id == exercise_id
        )
    ).first()

    if existing:
        flash(request, "Exercise already in routine!")
        return RedirectResponse(url=referer, status_code=303)

    routine_exercise = RoutineExercise(
        routine_id=routine_id,
        exercise_id=exercise_id,
        sets=3,
        reps=10,
    )
    db.add(routine_exercise)
    db.commit()

    flash(request, "Exercise added to routine!")
    return RedirectResponse(url=referer, status_code=303)


@router.post("/{routine_id}/remove-exercise/{routine_exercise_id}")
async def remove_exercise_from_routine(
    request: Request,
    routine_id: int,
    routine_exercise_id: int,
    user: AuthDep,
    db: SessionDep,
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


@router.post("/{routine_id}/toggle-exercise/{exercise_id}")
async def toggle_exercise_completion(
    request: Request,
    routine_id: int,
    exercise_id: int,
    user: AuthDep,
    db: SessionDep,
):
    today = date.today()

    routine = db.get(Routine, routine_id)

    if not routine:
        return HTMLResponse("Routine not found", status_code=404)

    if routine.user_id != user.id:
        return HTMLResponse("Unauthorized", status_code=403)

    existing = db.exec(
        select(CompletedExercise).where(
            CompletedExercise.user_id == user.id,
            CompletedExercise.exercise_id == exercise_id,
            CompletedExercise.routine_id == routine_id,
            CompletedExercise.completed_on == today
        )
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        flash(request, "Exercise marked as incomplete!", "warning")
        return RedirectResponse(url="/routines", status_code=303)

    completed = CompletedExercise(
        user_id=user.id,
        exercise_id=exercise_id,
        routine_id=routine_id,
        completed_on=today
    )
    db.add(completed)
    db.commit()

    flash(request, "Exercise completed!", "success")
    return RedirectResponse(url="/routines", status_code=303)

@router.post("/no-routine")
async def no_routine(request: Request):
    flash(request, "Please create a routine first, before adding exercises!")
    return RedirectResponse(url="/app", status_code=303)