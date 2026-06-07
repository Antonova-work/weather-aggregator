from pydantic import BaseModel
from typing import List

class WeatherInfo(BaseModel):
    temperature: float
    humidity: int
    wind_speed: float
    pressure: int
    cloud_cover: int
    provider_name: str

class AggregatedWeather(BaseModel):
    lat: float
    lon: float
    average_temperature: float
    average_humidity: float
    average_wind_speed: float
    average_pressure: float
    average_cloud_cover: float
    raw_data: List[WeatherInfo]