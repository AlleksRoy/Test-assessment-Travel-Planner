from typing import Optional, List
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

class PlaceBase(SQLModel):
    external_id: int
    notes: Optional[str] = None
    is_visited: bool = Field(default=False)

class Place(PlaceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    project: Optional["Project"] = Relationship(back_populates="places")

class ProjectBase(SQLModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None

class Project(ProjectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    is_completed: bool = Field(default=False)
    places: List[Place] = Relationship(back_populates="project")


class ProjectResponse(ProjectBase):
    id: int
    is_completed: bool

class PlaceResponse(PlaceBase):
    id: int
    project_id: int