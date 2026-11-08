from collections.abc import Sequence

from app.core.exceptions import ConflictError, NotFoundError
from app.models import Tag
from app.repositories.tag_repository import TagRepository
from app.schemas.tag import TagCreate, TagUpdate


class TagService:
    def __init__(self, repository: TagRepository) -> None:
        self._repository = repository

    def list_tags(self) -> Sequence[Tag]:
        return self._repository.list_all()

    def create_tag(self, payload: TagCreate) -> Tag:
        self._ensure_name_available(payload.name)
        return self._repository.add(Tag(**payload.model_dump()))

    def update_tag(self, tag_id: int, payload: TagUpdate) -> Tag:
        tag = self._get_or_raise(tag_id)
        changes = payload.model_dump(exclude_unset=True, exclude_none=True)
        if "name" in changes and changes["name"] != tag.name:
            self._ensure_name_available(changes["name"])
        for field, value in changes.items():
            setattr(tag, field, value)
        return self._repository.save(tag)

    def delete_tag(self, tag_id: int) -> None:
        self._repository.delete(self._get_or_raise(tag_id))

    def _get_or_raise(self, tag_id: int) -> Tag:
        tag = self._repository.get(tag_id)
        if tag is None:
            raise NotFoundError(f"Tag {tag_id} not found")
        return tag

    def _ensure_name_available(self, name: str) -> None:
        if self._repository.get_by_name(name) is not None:
            raise ConflictError(f"Tag '{name}' already exists")
