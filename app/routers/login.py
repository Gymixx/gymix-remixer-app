from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request, status, Form
from app.dependencies import SessionDep
from . import router, templates
from app.services.auth_service import AuthService
from app.repositories.user import UserRepository
from app.utilities.flash import flash
from app.config import get_settings

# View route responsible for UI
@router.get("/login", response_class=HTMLResponse)
async def login_view(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="login.html",
    )

#Action route responsible for actually logging in the person
@router.post("/login", response_class=HTMLResponse)
async def login_action_ajax(
    db: SessionDep,
    request: Request,
    username: str = Form(),
    password: str = Form(),
):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)

    user = user_repo.get_by_username(username)  

    access_token = auth_service.authenticate_user(username, password)

    if not access_token or not user:
        flash(request, "Incorrect username or password", "danger")
        return RedirectResponse(
            url=request.url_for("login_view"),
            status_code=status.HTTP_303_SEE_OTHER
        )

    # PROFILE CHECK
    if not user.age or not user.height or not user.weight or not user.gender or not user.goal or not user.activity_level:
        response = RedirectResponse(url="/profile", status_code=303)
    else:
        response = RedirectResponse(
            url=request.url_for("index_view"),
            status_code=status.HTTP_303_SEE_OTHER
        )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="none",
        secure=True,
    )

    return response