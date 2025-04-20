from difflib import get_close_matches

from fastapi import HTTPException, status
from sqlalchemy import select

from app.infra.models.city import City
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.requests_outside.openstreetmap import (
    fetch_city_suggestions,
    get_city_by_osm,
)
from app.infra.schemas.city import CitySuggestion, NearestCitySchema
from app.logic.support_funcs.city import haversine


async def fetch_cities(city_name) -> list[CitySuggestion]:
    """Забираем все города по названию"""
    data = await fetch_city_suggestions(city_name)

    suggestions: list[CitySuggestion] = []
    for item in data:
        suggestions.append(
            CitySuggestion(
                osm_type=item["osm_type"],
                osm_id=int(item["osm_id"]),
                name=item.get("name", ""),
                display_name=item.get("display_name", ""),
                lat=float(item["lat"]),
                lon=float(item["lon"]),
            )
        )
    if not suggestions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'По названию "{city_name}" ничего не найдено',
        )
    return suggestions


async def get_city(selection) -> CitySuggestion:
    prefix = {
        "node": "N",
        "way": "W",
        "relation": "R",
    }.get(selection.osm_type)
    if prefix is None:
        raise HTTPException(400, detail="Неверный osm_type")

    osm_ids = f"{prefix}{selection.osm_id}"
    params = {"osm_ids": osm_ids, "format": "json"}

    data = await get_city_by_osm(params)

    if not data:
        raise HTTPException(404, detail=f"Объект {osm_ids} не найден в геокодере")

    item = data[0]
    city = CitySuggestion(
        osm_type=item["osm_type"],
        osm_id=int(item["osm_id"]),
        name=item.get("name", ""),
        display_name=item.get("display_name", ""),
        lat=float(item["lat"]),
        lon=float(item["lon"]),
    )
    return city


async def add_city_to_database(db, city_name, city_lat, city_lon) -> City:
    query = select(City).filter_by(
        name=city_name, latitude=city_lat, longitude=city_lon
    )
    result = await db.execute(query)
    city = result.scalars().first()

    if city:
        raise HTTPException(status_code=400, detail="Город уже добавлен")

    new_city = City(name=city_name, latitude=city_lat, longitude=city_lon)
    db.add(new_city)
    await db.commit()

    return new_city


async def get_all_cities_func(db) -> list[City]:
    query = select(City)
    result = await db.execute(query)
    cities = result.scalars().all()
    return cities


async def fuzzy_get_city(city_name: str, db: AsyncSession, cutoff: float) -> City:
    query = select(City.name)
    result = await db.execute(query)
    cities = result.all()
    names = [row[0] for row in cities]

    matches = get_close_matches(city_name, names, n=1, cutoff=cutoff)
    if not matches:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Город "{city_name}" не найден (то, что вы написали не похоже ни на один город)',
        )

    best_name = matches[0]
    query2 = select(City).filter_by(name=best_name)
    result = await db.execute(query2)
    city = result.scalars().first()
    return city


async def get_two_nearest_func(
    db,
    base,
) -> list[NearestCitySchema]:
    res = await db.execute(select(City).filter(City.id != base.id))
    others = res.scalars().all()

    nearest = sorted(
        others,
        key=lambda c: haversine(base.latitude, base.longitude, c.latitude, c.longitude),
    )[:2]

    return [
        NearestCitySchema(
            name=c.name,
            latitude=c.latitude,
            longitude=c.longitude,
            distance_km=round(
                haversine(base.latitude, base.longitude, c.latitude, c.longitude), 3
            ),
        )
        for c in nearest
    ]
