import time
from dataclasses import dataclass

import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings


@dataclass
class CachedPlace:
    value: dict
    expires_at: float


class ArticClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.cache: dict[str, CachedPlace] = {}

    async def get_artwork(self, external_id: str) -> dict:
        now = time.time()
        cached = self.cache.get(external_id)
        if cached and cached.expires_at > now:
            return cached.value

        url = f"{self.settings.artic_base_url}/artworks/{external_id}"
        params = {"fields": "id,title,artist_display,image_id"}

        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                response = await client.get(url, params=params)
        except httpx.TimeoutException as exc:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Art Institute API timeout",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Art Institute API is unavailable",
            ) from exc

        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Place with external_id={external_id} was not found in Art Institute API",
            )
        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Art Institute API returned an error",
            )

        payload = response.json()
        data = payload.get("data")
        if not data or not data.get("id") or not data.get("title"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Place with external_id={external_id} was not found in Art Institute API",
            )

        place = {
            "external_id": str(data["id"]),
            "title": data["title"],
            "artist_display": data.get("artist_display"),
            "image_id": data.get("image_id"),
        }
        self.cache[external_id] = CachedPlace(
            value=place,
            expires_at=now + self.settings.place_cache_ttl_seconds,
        )
        return place


artic_client = ArticClient()
