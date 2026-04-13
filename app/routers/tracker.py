from fastapi import APIRouter, HTTPException, Depends, Request, Response, Form, status
from sqlmodel import select
from app.dependencies import SessionDep
from app.models import *
from app.utilities import flash
from app.dependencies import AuthDep
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from . import tracker, templates
from fastapi.responses import HTMLResponse, RedirectResponse


@tracker.get("/tracker", response_class=HTMLResponse)
async def tracker_page(request: Request, user: AuthDep):
    return templates.TemplateResponse(
        request=request,
        name="tracker.html",
        context={"current_user": user}
    )


@tracker.post("/tracker")
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