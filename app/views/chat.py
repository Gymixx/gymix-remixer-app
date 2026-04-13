from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from app.dependencies.auth import AuthDep
from ..routers import templates   

router = APIRouter(include_in_schema=False)

@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request, user: AuthDep):
    return templates.TemplateResponse(request, "chat.html", {"user": user})