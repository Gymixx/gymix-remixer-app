from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request, status, Form
from app.dependencies import SessionDep
from . import api_router, router
from app.services.user_service import UserService
from app.repositories.user import UserRepository
from app.dependencies.auth import AdminDep
from app.schemas import UserResponse
from app.schemas.user import UserUpdate
from app.utilities.flash import flash


# API endpoint for listing users
@api_router.get("/users", response_model=list[UserResponse])
async def list_users(request: Request, db: SessionDep):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    return user_service.get_all_users()


@router.post("/admin/users/{user_id}/delete")
async def delete_user(request: Request, user_id: int, admin: AdminDep, db: SessionDep):
    user_repo = UserRepository(db)
    try:
        user_repo.delete_user(user_id)
        flash(request, "User deleted successfully.", "success")
    except Exception as e:
        flash(request, f"Error deleting user: {e}", "danger")
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/admin/users/{user_id}/role")
async def toggle_role(request: Request, user_id: int, admin: AdminDep, db: SessionDep):
    user_repo = UserRepository(db)
    target = user_repo.get_by_id(user_id)
    if not target:
        flash(request, "User not found.", "danger")
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    new_role = "user" if target.role == "admin" else "admin"
    try:
        user_repo.update_user(user_id, UserUpdate(role=new_role))
        flash(request, f"{target.username} is now {new_role}.", "success")
    except Exception as e:
        flash(request, f"Error updating role: {e}", "danger")
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/admin/users/{user_id}/update")
async def update_user(
    request: Request,
    user_id: int,
    admin: AdminDep,
    db: SessionDep,
    username: str = Form(...),
    email: str = Form(...),
):
    user_repo = UserRepository(db)
    try:
        user_repo.update_user(user_id, UserUpdate(username=username, email=email))
        flash(request, "User updated successfully.", "success")
    except Exception as e:
        flash(request, f"Error updating user: {e}", "danger")
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)