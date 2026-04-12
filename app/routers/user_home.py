from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from sqlmodel import select
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.models.exercise import Exercise
from app.models.routine import Routine
from app.utilities.pagination import Pagination
from . import router, templates

PAGE_SIZE = 20


@router.get("/app", response_class=HTMLResponse)
async def user_home_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    page: int = Query(default=1, ge=1),
    target_muscle: str | None = Query(default=None),
):
    all_for_filter = db.exec(select(Exercise)).all()
    target_muscles = sorted({e.target_muscle for e in all_for_filter if e.target_muscle})

    statement = select(Exercise)
    if target_muscle:
        statement = statement.where(Exercise.target_muscle.contains(target_muscle))
    all_exercises = db.exec(statement).all()
    total_count = len(all_exercises)

    pagination = Pagination(total_count=total_count, current_page=page, limit=PAGE_SIZE)

    offset = (page - 1) * PAGE_SIZE
    exercises = all_exercises[offset: offset + PAGE_SIZE]

    routines  = db.exec(select(Routine)).all()

    return templates.TemplateResponse(
        request=request,
        name="app.html",
        context={
            "user": user,
            "exercises": exercises,
            "pagination": pagination,
            "routines": routines,
            "target_muscles": target_muscles,
            "selected_target_muscle": target_muscle,
        }
    )
