from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.place import PlaceImport, PlaceRead


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=5000)
    start_date: date | None = None


class ProjectCreate(ProjectBase):
    places: list[PlaceImport] = Field(min_length=1, max_length=10)

    @model_validator(mode="after")
    def validate_unique_places(self):
        external_ids = [place.external_id for place in self.places]
        if len(external_ids) != len(set(external_ids)):
            raise ValueError("places must contain unique external_id values")
        return self


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=5000)
    start_date: date | None = None


class ProjectRead(ProjectBase):
    id: int
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    places_count: int = 0
    visited_places_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class ProjectDetail(ProjectRead):
    places: list[PlaceRead]
