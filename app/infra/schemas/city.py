from pydantic import BaseModel


class CityCreateSchema(BaseModel):
    name: str


class CitySelectSchema(BaseModel):
    osm_type: str
    osm_id: int


class CitySuggestion(CityCreateSchema, CitySelectSchema):
    display_name: str
    lat: float
    lon: float


class CityDBSchema(BaseModel):
    name: str
    latitude: float
    longitude: float

    class Config:
        from_attributes = True


class NearestCitySchema(CityDBSchema):
    distance_km: float
