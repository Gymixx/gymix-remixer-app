from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status
from app.dependencies.session import SessionDep
from app.dependencies.auth import AdminDep, IsUserLoggedIn, get_current_user, is_admin
from app.repositories.user import UserRepository
from . import router, templates


@router.get("/admin", response_class=HTMLResponse)
async def admin_home_view(
    request: Request,
    user: AdminDep,
    db:SessionDep,
    q: str = Query(default=""),
    page: int = Query(default=1, ge=1),
):
    user_repo = UserRepository(db)
    users, pagination = user_repo.search_users(query=q, page=page, limit=10)
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "user": user,
            "users": users,
            "pagination": pagination,
            "q": q,
        }
    )
