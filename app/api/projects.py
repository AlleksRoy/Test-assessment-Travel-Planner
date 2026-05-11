from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import Message
from app.schemas.pagination import Page
from app.schemas.place import PlaceCreate, PlaceRead, PlaceUpdate
from app.schemas.project import ProjectCreate, ProjectDetail, ProjectRead, ProjectUpdate
from app.services import projects as project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectDetail, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    return await project_service.create_project(db, payload)


@router.get("", response_model=Page[ProjectRead])
def list_projects(
    search: str | None = None,
    is_completed: bool | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return project_service.list_projects(db, search, is_completed, limit, offset)


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(project_id: int, db: Session = Depends(get_db)):
    return project_service.get_project(db, project_id)


@router.patch("/{project_id}", response_model=ProjectDetail)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    return project_service.update_project(db, project_id, payload)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT, responses={409: {"model": Message}})
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project_service.delete_project(db, project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{project_id}/places", response_model=PlaceRead, status_code=status.HTTP_201_CREATED)
async def add_place(project_id: int, payload: PlaceCreate, db: Session = Depends(get_db)):
    return await project_service.add_place(db, project_id, payload)


@router.get("/{project_id}/places", response_model=Page[PlaceRead])
def list_places(
    project_id: int,
    visited: bool | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return project_service.list_places(db, project_id, visited, limit, offset)


@router.get("/{project_id}/places/{place_id}", response_model=PlaceRead)
def get_place(project_id: int, place_id: int, db: Session = Depends(get_db)):
    return project_service.get_place(db, project_id, place_id)


@router.patch("/{project_id}/places/{place_id}", response_model=PlaceRead)
def update_place(project_id: int, place_id: int, payload: PlaceUpdate, db: Session = Depends(get_db)):
    return project_service.update_place(db, project_id, place_id, payload)
