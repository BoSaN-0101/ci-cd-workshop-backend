from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Tag


class TagRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> Sequence[Tag]:
        return self._session.scalars(select(Tag).order_by(Tag.name)).all()

    def get(self, tag_id: int) -> Tag | None:
        return self._session.get(Tag, tag_id)

    def get_by_name(self, name: str) -> Tag | None:
        return self._session.scalar(select(Tag).where(Tag.name == name))

    def get_many(self, tag_ids: Sequence[int]) -> Sequence[Tag]:
        if not tag_ids:
            return []
        return self._session.scalars(select(Tag).where(Tag.id.in_(tag_ids))).all()

    def add(self, tag: Tag) -> Tag:
        self._session.add(tag)
        self._session.commit()
        self._session.refresh(tag)
        return tag

    def save(self, tag: Tag) -> Tag:
        self._session.commit()
        self._session.refresh(tag)
        return tag

    def delete(self, tag: Tag) -> None:
        self._session.delete(tag)
        self._session.commit()
