# Travel Planner API

FastAPI CRUD application for managing travel projects, imported places from the Art Institute of Chicago API, notes, and visited status.

## Features

- Create a project with 1 to 10 imported places in one request
- Validate every place through the Art Institute of Chicago API before saving
- Add a place to an existing project
- Prevent duplicate external places inside the same project
- Update project name, description, and start date
- Update project-place notes and visited status
- Automatically mark a project as completed when all its places are visited
- Prevent deleting a project if at least one place is already visited
- Pagination and filtering for list endpoints
- In-memory cache for third-party API responses
- SQLite database
- Docker support
- Postman collection included

## Tech stack

- Python 3.12
- FastAPI
- SQLAlchemy 2
- SQLite
- httpx
- Docker

## Project structure

```text
travel_planner/
  app/
    api/
    core/
    db/
    models/
    schemas/
    services/
    main.py
  postman/
  Dockerfile
  docker-compose.yml
  requirements.txt
  README.md
```

## Environment variables

Copy `.env.example` to `.env` if you want to override defaults.

| Variable | Default |
|---|---|
| `DATABASE_URL` | `sqlite:///./travel_planner.db` |
| `ARTIC_BASE_URL` | `https://api.artic.edu/api/v1` |
| `PLACE_CACHE_TTL_SECONDS` | `3600` |
| `REQUEST_TIMEOUT_SECONDS` | `10` |

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Application URL:

```text
http://localhost:8000
```

Swagger/OpenAPI documentation:

```text
http://localhost:8000/docs
```

## Run with Docker

```bash
docker compose up --build
```

## Art Institute API usage

The application validates places by calling the Art Institute of Chicago artwork detail endpoint:

```text
GET https://api.artic.edu/api/v1/artworks/{id}?fields=id,title,artist_display,image_id
```

Example valid external IDs:

```text
129884
27992
28560
```

## Main endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/projects` | Create project with places |
| `GET` | `/projects` | List projects with pagination and filters |
| `GET` | `/projects/{project_id}` | Get one project |
| `PATCH` | `/projects/{project_id}` | Update project |
| `DELETE` | `/projects/{project_id}` | Delete project if no place is visited |
| `POST` | `/projects/{project_id}/places` | Add place to project |
| `GET` | `/projects/{project_id}/places` | List places in project |
| `GET` | `/projects/{project_id}/places/{place_id}` | Get one project place |
| `PATCH` | `/projects/{project_id}/places/{place_id}` | Update notes or visited status |
| `GET` | `/health` | Health check |

## Example requests

### Create project with places

```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Chicago Museum Trip",
    "description": "Places I want to see during the visit",
    "start_date": "2026-06-01",
    "places": [
      {"external_id": "129884", "notes": "Start here"},
      {"external_id": "27992", "notes": "Must see"}
    ]
  }'
```

### Add place to existing project

```bash
curl -X POST http://localhost:8000/projects/1/places \
  -H "Content-Type: application/json" \
  -d '{"external_id": "28560", "notes": "Add to route"}'
```

### Mark place as visited

```bash
curl -X PATCH http://localhost:8000/projects/1/places/1 \
  -H "Content-Type: application/json" \
  -d '{"visited": true}'
```

### List projects

```bash
curl "http://localhost:8000/projects?limit=10&offset=0&is_completed=false"
```

## Postman collection

A Postman collection is included in:

```text
postman/Travel_Planner_API.postman_collection.json
```

Set the collection variable `base_url` to:

```text
http://localhost:8000
```

## Notes for reviewers

The Art Institute of Chicago API is used as the third-party source of truth. The assessment asks for places, while the provided example endpoint belongs to the `artworks` collection, so this solution treats artwork records as visitable places.
