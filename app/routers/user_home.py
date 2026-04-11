from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status
from sqlmodel import select
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep, IsUserLoggedIn, get_current_user, is_admin
from app.models.exercise import Exercise
from . import router, templates


@router.get("/app", response_class=HTMLResponse)
async def user_home_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    body_part: str | None = Query(default=None),
    target_muscle: str | None = Query(default=None),
    difficulty: str | None = Query(default=None),
):
    statement = select(Exercise)

    if body_part:
        statement = statement.where(Exercise.body_part.contains(body_part))
    if target_muscle:
        statement = statement.where(Exercise.target_muscle.contains(target_muscle))
    if difficulty:
        statement = statement.where(Exercise.difficulty == difficulty)

    exercises = db.exec(statement).all()

    return templates.TemplateResponse(
        request=request,
        name="app.html",
        context={
            "user": user,
            "exercises": exercises,
        }
    )