from collections.abc import Iterator
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_todo_service
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.repositories.tag_repository import TagRepository
from app.repositories.todo_repository import TodoRepository
from app.services.todo_service import TodoService

FIXED_TODAY = date(2026, 1, 15)


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    event.listen(engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with testing_session() as db_session:
        yield db_session
    engine.dispose()


@pytest.fixture
def client(session: Session) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_todo_service] = lambda: TodoService(
        TodoRepository(session), TagRepository(session), lambda: FIXED_TODAY
    )
    with TestClient(app) as test_client:
        yield test_client
