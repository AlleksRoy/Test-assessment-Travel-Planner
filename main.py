from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select
from database import create_db_and_tables, get_session
from models import Project, ProjectBase, ProjectResponse

app = FastAPI(title="Travel Planner API")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/projects/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectBase, session: Session = Depends(get_session)):
    db_project = Project.model_validate(project)
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project

# Пример эндпоинта: Получение всех проектов
@app.get("/projects/", response_model=list[ProjectResponse])
def read_projects(session: Session = Depends(get_session)):
    projects = session.exec(select(Project)).all()
    return projects

# TODO: Добавить эндпоинты DELETE, UPDATE для проектов
# TODO: Добавить эндпоинты CRUD для Places
# TODO: Реализовать запрос к https://api.artic.edu/api/v1/artworks/{external_id} через httpx