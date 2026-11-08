from collections.abc import Callable, Sequence
from datetime import UTC, date, datetime

from app.core.exceptions import NotFoundError
from app.models import Tag, Todo
from app.repositories.tag_repository import TagRepository
from app.repositories.todo_repository import TodoRepository, overdue_conditions
from app.schemas.todo import TodoCreate, TodoFilter, TodoPage, TodoRead, TodoStats, TodoUpdate


class TodoService:
    def __init__(
        self,
        todo_repository: TodoRepository,
        tag_repository: TagRepository,
        today_provider: Callable[[], date] = date.today,
    ) -> None:
        self._todos = todo_repository
        self._tags = tag_repository
        self._today = today_provider

    def list_todos(self, filters: TodoFilter) -> TodoPage:
        items, total = self._todos.find(filters, self._today())
        return TodoPage(items=[TodoRead.model_validate(item) for item in items], total=total)

    def get_todo(self, todo_id: int) -> Todo:
        todo = self._todos.get(todo_id)
        if todo is None:
            raise NotFoundError(f"Todo {todo_id} not found")
        return todo

    def create_todo(self, payload: TodoCreate) -> Todo:
        todo = Todo(**payload.model_dump(exclude={"tag_ids"}))
        todo.tags = list(self._resolve_tags(payload.tag_ids))
        return self._todos.add(todo)

    def update_todo(self, todo_id: int, payload: TodoUpdate) -> Todo:
        todo = self.get_todo(todo_id)
        changes = payload.model_dump(exclude_unset=True)
        tag_ids = changes.pop("tag_ids", None)
        is_completed = changes.pop("is_completed", None)

        for field, value in changes.items():
            setattr(todo, field, value)
        if tag_ids is not None:
            todo.tags = list(self._resolve_tags(tag_ids))
        if is_completed is not None:
            self._set_completion(todo, is_completed)

        return self._todos.save(todo)

    def delete_todo(self, todo_id: int) -> None:
        self._todos.delete(self.get_todo(todo_id))

    def clear_completed(self) -> int:
        return self._todos.delete_completed()

    def get_stats(self) -> TodoStats:
        today = self._today()
        total = self._todos.count()
        completed = self._todos.count(Todo.is_completed.is_(True))
        return TodoStats(
            total=total,
            completed=completed,
            active=total - completed,
            overdue=self._todos.count(*overdue_conditions(today)),
            due_today=self._todos.count(Todo.due_date == today, Todo.is_completed.is_(False)),
        )

    def _resolve_tags(self, tag_ids: Sequence[int]) -> Sequence[Tag]:
        unique_ids = set(tag_ids)
        tags = self._tags.get_many(list(unique_ids))
        missing = unique_ids - {tag.id for tag in tags}
        if missing:
            raise NotFoundError(f"Tags not found: {sorted(missing)}")
        return tags

    @staticmethod
    def _set_completion(todo: Todo, is_completed: bool) -> None:
        if todo.is_completed == is_completed:
            return
        todo.is_completed = is_completed
        todo.completed_at = datetime.now(UTC) if is_completed else None
