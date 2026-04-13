from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import select

from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.models.workout_log import WorkoutLog
from app.utilities.flash import flash
from . import templates

router = APIRouter(prefix="/tracker", tags=["Tracker"])


@router.get("", response_class=HTMLResponse)
async def tracker_page(request: Request, user: AuthDep):
    return templates.TemplateResponse(
        request=request,
        name="tracker.html",
        context={"current_user": user}
    )


@router.post("")
async def handle_tracker(
    request: Request,
    age: Annotated[int, Form()],
    gender: Annotated[str, Form()],
    height: Annotated[float, Form()],
    weight: Annotated[float, Form()],
    goal: Annotated[str, Form()],
    activity_level: Annotated[str, Form()],
    user: AuthDep,
    db: SessionDep
):
    bmi = weight / ((height / 100) ** 2)

    print("Tracker Data:")
    print(age, gender, height, weight, goal, activity_level)
    print("BMI:", round(bmi, 2))

    flash(request, f"Saved! Your BMI is {round(bmi, 2)}")

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
        return RedirectResponse(url="/app", status_code=303)

    log = WorkoutLog(user_id=user.id, date=today)
    db.add(log)
    db.commit()

    flash(request, "Workout logged for today!", "success")
    return RedirectResponse(url="/app", status_code=303)


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