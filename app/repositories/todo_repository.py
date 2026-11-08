from collections.abc import Sequence
from datetime import date

from sqlalchemy import ColumnElement, Select, case, delete, func, or_, select
from sqlalchemy.orm import Session

from app.models import Priority, Tag, Todo
from app.schemas.todo import SortField, SortOrder, TodoFilter

PRIORITY_RANK = case(
    {
        Priority.LOW: 0,
        Priority.MEDIUM: 1,
        Priority.HIGH: 2,
        Priority.URGENT: 3,
    },
    value=Todo.priority,
)

SORT_COLUMNS: dict[SortField, ColumnElement] = {
    SortField.DUE_DATE: Todo.due_date,
    SortField.PRIORITY: PRIORITY_RANK,
    SortField.CREATED_AT: Todo.created_at,
}


class TodoRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find(self, filters: TodoFilter, today: date) -> tuple[Sequence[Todo], int]:
        conditions = self._build_conditions(filters, today)
        total = self._session.scalar(select(func.count(Todo.id)).where(*conditions)) or 0
        query = self._apply_sorting(select(Todo).where(*conditions), filters)
        items = self._session.scalars(query.limit(filters.limit).offset(filters.offset)).all()
        return items, total

    def get(self, todo_id: int) -> Todo | None:
        return self._session.get(Todo, todo_id)

    def add(self, todo: Todo) -> Todo:
        self._session.add(todo)
        self._session.commit()
        self._session.refresh(todo)
        return todo

    def save(self, todo: Todo) -> Todo:
        self._session.commit()
        self._session.refresh(todo)
        return todo

    def delete(self, todo: Todo) -> None:
        self._session.delete(todo)
        self._session.commit()

    def delete_completed(self) -> int:
        result = self._session.execute(delete(Todo).where(Todo.is_completed.is_(True)))
        self._session.commit()
        return result.rowcount

    def count(self, *conditions: ColumnElement[bool]) -> int:
        return self._session.scalar(select(func.count(Todo.id)).where(*conditions)) or 0

    @staticmethod
    def _build_conditions(filters: TodoFilter, today: date) -> list[ColumnElement[bool]]:
        conditions: list[ColumnElement[bool]] = []
        if filters.due_date is not None:
            conditions.append(Todo.due_date == filters.due_date)
        if filters.due_from is not None:
            conditions.append(Todo.due_date >= filters.due_from)
        if filters.due_to is not None:
            conditions.append(Todo.due_date <= filters.due_to)
        if filters.overdue:
            conditions.extend(overdue_conditions(today))
        if filters.is_completed is not None:
            conditions.append(Todo.is_completed.is_(filters.is_completed))
        if filters.priority is not None:
            conditions.append(Todo.priority == filters.priority)
        if filters.tag_ids:
            conditions.append(Todo.tags.any(Tag.id.in_(filters.tag_ids)))
        if filters.search:
            pattern = f"%{filters.search}%"
            conditions.append(or_(Todo.title.ilike(pattern), Todo.description.ilike(pattern)))
        return conditions

    @staticmethod
    def _apply_sorting(query: Select, filters: TodoFilter) -> Select:
        column = SORT_COLUMNS[filters.sort_by]
        ordered = column.asc() if filters.order is SortOrder.ASC else column.desc()
        return query.order_by(ordered.nulls_last(), Todo.id.desc())


def overdue_conditions(today: date) -> list[ColumnElement[bool]]:
    return [Todo.due_date < today, Todo.is_completed.is_(False)]
