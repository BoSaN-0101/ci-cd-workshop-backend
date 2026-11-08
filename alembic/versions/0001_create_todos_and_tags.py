"""create todos and tags

Revision ID: 0001
Revises:
Create Date: 2026-11-08

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=50), nullable=False, unique=True),
        sa.Column("color", sa.String(length=7), nullable=False),
    )
    op.create_table(
        "todos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column(
            "priority",
            sa.Enum(
                "low", "medium", "high", "urgent", name="priority", native_enum=False, length=10
            ),
            nullable=False,
        ),
        sa.Column("is_completed", sa.Boolean(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_todos_due_date", "todos", ["due_date"])
    op.create_index("ix_todos_is_completed", "todos", ["is_completed"])
    op.create_table(
        "todo_tags",
        sa.Column(
            "todo_id", sa.Integer(), sa.ForeignKey("todos.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column(
            "tag_id", sa.Integer(), sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
        ),
    )


def downgrade() -> None:
    op.drop_table("todo_tags")
    op.drop_index("ix_todos_is_completed", table_name="todos")
    op.drop_index("ix_todos_due_date", table_name="todos")
    op.drop_table("todos")
    op.drop_table("tags")
