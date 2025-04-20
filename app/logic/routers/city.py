import os

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.schemas.city import (
    CitySuggestion,
    CitySelectSchema,
    CityDBSchema,
    NearestCitySchema,
)
from app.infra.settings import get_db
from app.logic.utils.city import (
    add_city_to_database,
    fuzzy_get_city,
    fetch_cities,
    get_city,
    get_all_cities_func,
    get_two_nearest_func,
)

city_router = APIRouter()
GEOCODING_API_URL = os.getenv("GEOCODING_API_URL")


@city_router.get("/", response_model=list[CitySuggestion])
async def suggest_cities(
    city_name: str,
):
    """Получаем все города, которые похожт на то, что ввел пользователь"""
    suggestions = await fetch_cities(city_name)
    return suggestions


@city_router.post("/add", response_model=CitySuggestion, status_code=201)
async def add_city(
    selection: CitySelectSchema,
    db: AsyncSession = Depends(get_db),
):
    city = await get_city(selection)
    await add_city_to_database(
        db, city_name=city.name, city_lat=city.lat, city_lon=city.lon
    )

    return city


@city_router.get("/all", response_model=list[CityDBSchema])
async def get_all_cities(db: AsyncSession = Depends(get_db)):
    cities = await get_all_cities_func(db)
    return cities


@city_router.get("/{city_name}", response_model=CityDBSchema)
async def get_city_by_name(
    city_name: str,
    db: AsyncSession = Depends(get_db),
):
    city = await fuzzy_get_city(city_name, db, cutoff=0.5)
    return city


@city_router.get("/{city_name}/nearest", response_model=list[NearestCitySchema])
async def get_two_nearest(
    city_name: str,
    db: AsyncSession = Depends(get_db),
):
    base = await fuzzy_get_city(city_name, db, cutoff=0.5)
    nearest = await get_two_nearest_func(
        db,
        base,
    )

    return nearest
