from fastapi import APIRouter, status

from app.api.dependencies import TagServiceDep
from app.schemas.tag import TagCreate, TagRead, TagUpdate

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagRead])
def list_tags(service: TagServiceDep):
    return service.list_tags()


@router.post("", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(payload: TagCreate, service: TagServiceDep):
    return service.create_tag(payload)


@router.patch("/{tag_id}", response_model=TagRead)
def update_tag(tag_id: int, payload: TagUpdate, service: TagServiceDep):
    return service.update_tag(tag_id, payload)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, service: TagServiceDep) -> None:
    service.delete_tag(tag_id)
