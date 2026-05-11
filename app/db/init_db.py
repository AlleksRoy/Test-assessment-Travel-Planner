from pathlib import Path
from urllib.parse import urlparse

from app.db.session import Base, engine
from app.models.project import Project
from app.models.project_place import ProjectPlace


def _ensure_sqlite_directory_exists() -> None:
    database_url = str(engine.url)
    if not database_url.startswith("sqlite"):
        return

    database_path = urlparse(database_url).path
    if database_path and database_path != ":memory:":
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)


def init_db() -> None:
    _ensure_sqlite_directory_exists()
    Base.metadata.create_all(bind=engine)
