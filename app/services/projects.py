from fastapi import HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.project import Project
from app.models.project_place import ProjectPlace
from app.schemas.place import PlaceCreate, PlaceUpdate
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.artic import artic_client

MAX_PLACES_PER_PROJECT = 10


def _project_or_404(db: Session, project_id: int) -> Project:
    project = db.scalar(
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.places))
    )
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


def _place_or_404(db: Session, project_id: int, place_id: int) -> ProjectPlace:
    place = db.scalar(
        select(ProjectPlace).where(
            ProjectPlace.id == place_id,
            ProjectPlace.project_id == project_id,
        )
    )
    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project place not found")
    return place


def _ensure_project_place_capacity(project: Project, amount: int = 1) -> None:
    if len(project.places) + amount > MAX_PLACES_PER_PROJECT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A project can contain maximum {MAX_PLACES_PER_PROJECT} places",
        )


def _ensure_place_not_duplicate(project: Project, external_id: str) -> None:
    if any(place.external_id == external_id for place in project.places):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This external place is already added to the project",
        )


def _refresh_completed(project: Project) -> None:
    project.is_completed = bool(project.places) and all(place.visited for place in project.places)


def _project_read(project: Project) -> dict:
    places_count = len(project.places)
    visited_count = sum(1 for place in project.places if place.visited)
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "start_date": project.start_date,
        "is_completed": project.is_completed,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "places_count": places_count,
        "visited_places_count": visited_count,
    }


def _project_detail(project: Project) -> dict:
    data = _project_read(project)
    data["places"] = project.places
    return data


async def create_project(db: Session, payload: ProjectCreate) -> dict:
    project = Project(
        name=payload.name,
        description=payload.description,
        start_date=payload.start_date,
        is_completed=False,
    )

    resolved_places = []
    for place_payload in payload.places:
        place_data = await artic_client.get_artwork(place_payload.external_id)
        resolved_places.append((place_payload, place_data))

    for place_payload, place_data in resolved_places:
        project.places.append(
            ProjectPlace(
                external_id=place_data["external_id"],
                title=place_data["title"],
                artist_display=place_data.get("artist_display"),
                image_id=place_data.get("image_id"),
                notes=place_payload.notes,
                visited=False,
            )
        )

    _refresh_completed(project)
    db.add(project)
    db.commit()
    db.refresh(project)
    return _project_detail(_project_or_404(db, project.id))


def list_projects(db: Session, search: str | None, is_completed: bool | None, limit: int, offset: int) -> dict:
    statement: Select = select(Project).options(selectinload(Project.places))
    count_statement: Select = select(func.count(Project.id))

    if search:
        statement = statement.where(Project.name.ilike(f"%{search}%"))
        count_statement = count_statement.where(Project.name.ilike(f"%{search}%"))
    if is_completed is not None:
        statement = statement.where(Project.is_completed == is_completed)
        count_statement = count_statement.where(Project.is_completed == is_completed)

    total = db.scalar(count_statement) or 0
    projects = db.scalars(statement.order_by(Project.id.desc()).limit(limit).offset(offset)).all()
    return {"total": total, "limit": limit, "offset": offset, "items": [_project_read(project) for project in projects]}


def get_project(db: Session, project_id: int) -> dict:
    return _project_detail(_project_or_404(db, project_id))


def update_project(db: Session, project_id: int, payload: ProjectUpdate) -> dict:
    project = _project_or_404(db, project_id)
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return _project_detail(_project_or_404(db, project.id))


def delete_project(db: Session, project_id: int) -> None:
    project = _project_or_404(db, project_id)
    if any(place.visited for place in project.places):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project cannot be deleted because it contains visited places",
        )
    db.delete(project)
    db.commit()


async def add_place(db: Session, project_id: int, payload: PlaceCreate) -> ProjectPlace:
    project = _project_or_404(db, project_id)
    _ensure_project_place_capacity(project)
    _ensure_place_not_duplicate(project, payload.external_id)
    place_data = await artic_client.get_artwork(payload.external_id)
    _ensure_place_not_duplicate(project, place_data["external_id"])

    place = ProjectPlace(
        project_id=project.id,
        external_id=place_data["external_id"],
        title=place_data["title"],
        artist_display=place_data.get("artist_display"),
        image_id=place_data.get("image_id"),
        notes=payload.notes,
        visited=False,
    )
    db.add(place)
    db.flush()
    project.places.append(place)
    _refresh_completed(project)
    db.commit()
    db.refresh(place)
    return place


def list_places(db: Session, project_id: int, visited: bool | None, limit: int, offset: int) -> dict:
    _project_or_404(db, project_id)
    statement: Select = select(ProjectPlace).where(ProjectPlace.project_id == project_id)
    count_statement: Select = select(func.count(ProjectPlace.id)).where(ProjectPlace.project_id == project_id)

    if visited is not None:
        statement = statement.where(ProjectPlace.visited == visited)
        count_statement = count_statement.where(ProjectPlace.visited == visited)

    total = db.scalar(count_statement) or 0
    places = db.scalars(statement.order_by(ProjectPlace.id.asc()).limit(limit).offset(offset)).all()
    return {"total": total, "limit": limit, "offset": offset, "items": places}


def get_place(db: Session, project_id: int, place_id: int) -> ProjectPlace:
    _project_or_404(db, project_id)
    return _place_or_404(db, project_id, place_id)


def update_place(db: Session, project_id: int, place_id: int, payload: PlaceUpdate) -> ProjectPlace:
    project = _project_or_404(db, project_id)
    place = _place_or_404(db, project_id, place_id)
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(place, key, value)
    _refresh_completed(project)
    db.commit()
    db.refresh(place)
    return place
