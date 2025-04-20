import os

import httpx

from app.infra.schemas.city import CitySuggestion

GEOCODING_API_URL = os.getenv("GEOCODING_API_URL")


async def fetch_city_suggestions(city_name: str) -> list[CitySuggestion]:
    params = {"q": city_name, "format": "json"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{GEOCODING_API_URL}/search", params=params)
        resp.raise_for_status()
        data = resp.json()
    return data


async def get_city_by_osm(params) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{GEOCODING_API_URL}/lookup", params=params)
        resp.raise_for_status()
        data = resp.json()
        return data
