import asyncio
from typing import List
from app.domain.models import WeatherInfo, AggregatedWeather
from app.infrastructure.weather_clients import (
    get_open_meteo_weather,
    get_wttr_weather,
    get_7timer_weather,
    get_norwegian_weather,
)

async def get_aggregated_weather(lat: float, lon: float) -> AggregatedWeather:

    results = await asyncio.gather(
        get_open_meteo_weather(lat, lon),
        get_wttr_weather(lat, lon),
        get_7timer_weather(lat, lon),
        get_norwegian_weather(lat, lon),
    )

    successful_results: List[WeatherInfo] = [res for res in results if res is not None]

    if not successful_results:
        raise ValueError("Все погодные сервисы недоступны")

    count = len(successful_results)

    avg_temp = sum(w.temperature for w in successful_results) / count
    avg_wind = sum(w.wind_speed for w in successful_results) / count
    avg_cloud = sum(w.cloud_cover for w in successful_results) / count

    humidity_values = [w.humidity for w in successful_results if w.humidity > 0]
    avg_humidity = sum(humidity_values) / len(humidity_values) if humidity_values else 0.0

    pressure_values = [w.pressure for w in successful_results if w.pressure > 0]
    avg_pressure = sum(pressure_values) / len(pressure_values) if pressure_values else 0.0

    return AggregatedWeather(
        lat=lat,
        lon=lon,
        average_temperature=avg_temp,
        average_humidity=avg_humidity,
        average_wind_speed=avg_wind,
        average_pressure=avg_pressure,
        average_cloud_cover=avg_cloud,
        raw_data=successful_results
    )