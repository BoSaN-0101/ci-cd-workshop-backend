from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.dependencies import TodoServiceDep
from app.schemas.todo import TodoCreate, TodoFilter, TodoPage, TodoRead, TodoStats, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("", response_model=TodoPage)
def list_todos(filters: Annotated[TodoFilter, Query()], service: TodoServiceDep) -> TodoPage:
    return service.list_todos(filters)


@router.get("/stats", response_model=TodoStats)
def get_stats(service: TodoServiceDep) -> TodoStats:
    return service.get_stats()


@router.delete("/completed", status_code=status.HTTP_200_OK)
def clear_completed(service: TodoServiceDep) -> dict[str, int]:
    return {"deleted": service.clear_completed()}


@router.get("/{todo_id}", response_model=TodoRead)
def get_todo(todo_id: int, service: TodoServiceDep):
    return service.get_todo(todo_id)


@router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate, service: TodoServiceDep):
    return service.create_todo(payload)


@router.patch("/{todo_id}", response_model=TodoRead)
def update_todo(todo_id: int, payload: TodoUpdate, service: TodoServiceDep):
    return service.update_todo(todo_id, payload)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, service: TodoServiceDep) -> None:
    service.delete_todo(todo_id)
