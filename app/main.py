import uvicorn
from fastapi import FastAPI, Request, status
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from app.routers import profile, templates, static_files, router, api_router
from app.routers import exercise, routine, tracker
from app.api.chat import router as chat_api_router      
from app.views.chat import router as chat_view_router  
from app.config import get_settings
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.models.user import User
    from app.models.exercise import Exercise
    from app.models.routine import Routine
    from app.models.routine_exercise import RoutineExercise
    from app.models.workout_log import WorkoutLog
    from app.models.completed_exercise import CompletedExercise
    from app.models.calorie_log import CalorieLog
    from app.database import create_db_and_tables
    create_db_and_tables()
    yield


app = FastAPI(middleware=[
    Middleware(SessionMiddleware, secret_key=get_settings().secret_key)
],
    lifespan=lifespan
)   

app.include_router(router)
app.include_router(api_router)
app.include_router(exercise.router)
app.include_router(routine.router)
app.include_router(tracker.router)
app.include_router(profile.router)
app.include_router(chat_api_router)      
app.include_router(chat_view_router)     
app.mount("/static", static_files, name="static")

@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def unauthorized_redirect_handler(request: Request, exc: Exception):
    return templates.TemplateResponse(
        request=request, 
        name="401.html",
    )

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=get_settings().app_host, port=get_settings().app_port, reload=get_settings().env.lower()!="production")