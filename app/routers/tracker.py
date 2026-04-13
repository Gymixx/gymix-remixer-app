from datetime import date, timedelta
from typing import Annotated
from fastapi import APIRouter, Request, Form, Query, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import select
from app.models.user import User
from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.models.completed_exercise import CompletedExercise
from app.models.exercise import Exercise
from app.models.workout_log import WorkoutLog
from app.utilities.flash import flash
from . import templates

router = APIRouter(prefix="/tracker", tags=["Tracker"])


@router.get("", response_class=HTMLResponse)
async def tracker_page(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    selected_date: date | None = Query(default=None),
):
    if selected_date is None:
        selected_date = date.today()

    completed_logs = db.exec(
        select(CompletedExercise).where(
            CompletedExercise.user_id == user.id,
            CompletedExercise.completed_on == selected_date
        )
    ).all()

    completed_exercises = []
    for log in completed_logs:
        exercise = db.get(Exercise, log.exercise_id)
        if exercise:
            completed_exercises.append({
                "id": exercise.id,
                "name": exercise.name,
                "body_part": exercise.body_part,
                "target_muscle": exercise.target_muscle,
                "equipment": exercise.equipment,
                "difficulty": exercise.difficulty,
                "image_url": exercise.image_url,
            })

    workout_logged = db.exec(
        select(WorkoutLog).where(
            WorkoutLog.user_id == user.id,
            WorkoutLog.date == selected_date
        )
    ).first()

    logs = db.exec(
        select(WorkoutLog).where(WorkoutLog.user_id == user.id)
    ).all()

    dates = sorted([log.date for log in logs], reverse=True)

    if not dates:
        streak = 0
    else:
        streak = 0
        today = date.today()
        expected_date = today

        if dates[0] != today:
            if dates[0] == today - timedelta(days=1):
                expected_date = today - timedelta(days=1)
            else:
                expected_date = None

        if expected_date is not None:
            for logged_date in dates:
                if logged_date == expected_date:
                    streak += 1
                    expected_date -= timedelta(days=1)
                elif logged_date < expected_date:
                    break

    return templates.TemplateResponse(
        request=request,
        name="tracker.html",
        context={
            "user": user,
            "selected_date": selected_date,
            "completed_exercises": completed_exercises,
            "workout_logged": workout_logged is not None,
            "streak": streak,
        }
    )

@router.post("/add-info/{user_id}")
async def add_tracker_info(
    request: Request,
    user_id: int,
    age: Annotated[int, Form()],
    gender: Annotated[str, Form()],
    height: Annotated[float, Form()],
    weight: Annotated[float, Form()],
    goal: Annotated[str, Form()],
    activity_level: Annotated[str, Form()],
    user: AuthDep,
    db: SessionDep,
):
    db_user = db.get(User, user_id)

    db_user.age = age
    db_user.gender = gender
    db_user.height = height
    db_user.weight = weight
    db_user.goal = goal
    db_user.activity_level = activity_level
    
    bmi = weight / ((height / 100) ** 2)
    db_user.body_fat_percentage = round(bmi, 2)
    
    flash(request, f"Info saved! Your BMI is {round(bmi, 2)}", "success")
    db.add(db_user)
    db.commit()

    return RedirectResponse(url="/tracker", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/log-today")
async def log_today(request: Request, user: AuthDep, db: SessionDep):
    today = date.today()

    existing = db.exec(
        select(WorkoutLog).where(
            (WorkoutLog.user_id == user.id) &
            (WorkoutLog.date == today)
        )
    ).first()

    if existing:
        flash(request, "Workout already logged for today!", "warning")
        return RedirectResponse(url="/routines", status_code=303)

    log = WorkoutLog(user_id=user.id, date=today)
    db.add(log)
    db.commit()

    flash(request, "Workout logged for today!", "success")
    return RedirectResponse(url="/routines", status_code=303)


@router.get("/history")
async def get_history(user: AuthDep, db: SessionDep):
    logs = db.exec(
        select(WorkoutLog).where(WorkoutLog.user_id == user.id)
    ).all()

    return logs


@router.get("/streak")
async def get_streak(user: AuthDep, db: SessionDep):
    logs = db.exec(
        select(WorkoutLog).where(WorkoutLog.user_id == user.id)
    ).all()

    dates = sorted([log.date for log in logs], reverse=True)

    if not dates:
        return {"current_streak": 0}

    streak = 0
    today = date.today()
    expected_date = today

    if dates[0] != today:
        if dates[0] == today - timedelta(days=1):
            expected_date = today - timedelta(days=1)
        else:
            return {"current_streak": 0}

    for logged_date in dates:
        if logged_date == expected_date:
            streak += 1
            expected_date -= timedelta(days=1)
        elif logged_date < expected_date:
            break

    return {"current_streak": streak}