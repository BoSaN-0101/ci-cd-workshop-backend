from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.tag_repository import TagRepository
from app.repositories.todo_repository import TodoRepository
from app.services.tag_service import TagService
from app.services.todo_service import TodoService

DbSession = Annotated[Session, Depends(get_db)]


def get_todo_service(session: DbSession) -> TodoService:
    return TodoService(TodoRepository(session), TagRepository(session))


def get_tag_service(session: DbSession) -> TagService:
    return TagService(TagRepository(session))


TodoServiceDep = Annotated[TodoService, Depends(get_todo_service)]
TagServiceDep = Annotated[TagService, Depends(get_tag_service)]
