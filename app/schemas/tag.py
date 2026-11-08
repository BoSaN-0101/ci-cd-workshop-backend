from pydantic import BaseModel, ConfigDict, Field

HEX_COLOR_PATTERN = r"^#[0-9a-fA-F]{6}$"


class TagBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    color: str = Field(default="#6b7280", pattern=HEX_COLOR_PATTERN)


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    color: str | None = Field(default=None, pattern=HEX_COLOR_PATTERN)


class TagRead(TagBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
