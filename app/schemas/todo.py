from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.models.todo import Priority
from app.schemas.tag import TagRead


class SortField(StrEnum):
    DUE_DATE = "due_date"
    PRIORITY = "priority"
    CREATED_AT = "created_at"


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class TodoBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    due_date: date | None = None
    priority: Priority = Priority.MEDIUM


class TodoCreate(TodoBase):
    tag_ids: list[int] = Field(default_factory=list)


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    due_date: date | None = None
    priority: Priority | None = None
    is_completed: bool | None = None
    tag_ids: list[int] | None = None


class TodoRead(TodoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_completed: bool
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    tags: list[TagRead]


class TodoFilter(BaseModel):
    due_date: date | None = None
    due_from: date | None = None
    due_to: date | None = None
    overdue: bool | None = None
    is_completed: bool | None = None
    priority: Priority | None = None
    tag_ids: list[int] = Field(default_factory=list)
    search: str | None = None
    sort_by: SortField = SortField.CREATED_AT
    order: SortOrder = SortOrder.DESC
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class TodoPage(BaseModel):
    items: list[TodoRead]
    total: int


class TodoStats(BaseModel):
    total: int
    completed: int
    active: int
    overdue: int
    due_today: int
