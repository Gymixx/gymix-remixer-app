from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.routers import templates
from app.utilities.flash import flash

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_class=HTMLResponse)
async def profile_page(request: Request, user: AuthDep):
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={"user": user},
    )


@router.post("")
async def update_profile(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    age: int = Form(...),
    gender: str = Form(...),
    height: float = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    activity_level: str = Form(...),
):
    if age < 1 or height <= 0 or weight <= 0:
        flash(request, "Please enter valid positive numbers for age, height, and weight.")
        return RedirectResponse(url="/profile", status_code=303)

    user.age = age
    user.gender = gender
    user.height = height
    user.weight = weight
    user.goal = goal
    user.activity_level = activity_level

    db.add(user)
    db.commit()
    db.refresh(user)

    flash(request, "Profile updated successfully!")
    return RedirectResponse(url="/app", status_code=303)