from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PlaceImport(BaseModel):
    external_id: str = Field(min_length=1, max_length=64)
    notes: str | None = Field(default=None, max_length=5000)


class PlaceCreate(PlaceImport):
    pass


class PlaceUpdate(BaseModel):
    notes: str | None = Field(default=None, max_length=5000)
    visited: bool | None = None


class PlaceRead(BaseModel):
    id: int
    project_id: int
    external_id: str
    title: str
    artist_display: str | None
    image_id: str | None
    notes: str | None
    visited: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
