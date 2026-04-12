from fastapi import Request
import typing

def flash(request: Request, message: str, type: str = "success") -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append({"message": message, "type": type})


def get_flashed_messages(request: Request, with_categories: bool = False):
    messages = request.session.pop("_messages") if "_messages" in request.session else [] 

    if with_categories:
        return [(msg["type"], msg["message"]) for msg in messages]
    
    return messages
