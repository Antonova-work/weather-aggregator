import httpx
import logging
from typing import Optional
from app.domain.models import WeatherInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_open_meteo_weather(lat: float, lon: float) -> Optional[WeatherInfo]:

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,pressure_msl,cloud_cover",
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            current = data.get("current", {})
            
            return WeatherInfo(
                temperature=float(current.get("temperature_2m", 0)),
                humidity=int(current.get("relative_humidity_2m", 0)),
                wind_speed=float(current.get("wind_speed_10m", 0)),
                pressure=int(current.get("pressure_msl", 0)),
                cloud_cover=int(current.get("cloud_cover", 0)),
                provider_name="Open-Meteo"
            )
    except Exception as e:
        logger.error(f"Error fetching from Open-Meteo: {e}")
        return None

async def get_wttr_weather(lat: float, lon: float) -> Optional[WeatherInfo]:

    url = f"https://wttr.in/{lat},{lon}?format=j1"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            current = data.get("current_condition", [{}])[0]

            wind_speed_kmh = float(current.get("windspeedKmph", 0))
            
            return WeatherInfo(
                temperature=float(current.get("temp_C", 0)),
                humidity=int(current.get("humidity", 0)),
                wind_speed=wind_speed_kmh / 3.6,
                pressure=int(current.get("pressure", 0)),
                cloud_cover=int(current.get("cloudcover", 0)),
                provider_name="wttr.in"
            )
    except Exception as e:
        logger.error(f"Error fetching from wttr.in: {e}")
        return None

async def get_7timer_weather(lat: float, lon: float) -> Optional[WeatherInfo]:

    url = "https://www.7timer.info/bin/civil.php"
    params = {
        "lon": lon,
        "lat": lat,
        "ac": 0,
        "unit": "metric",
        "output": "json",
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            first_forecast = data.get("dataseries", [{}])[0]

            rh_raw = first_forecast.get("rh2m", 0)
            wind_data = first_forecast.get("wind10m", {})
            wind_level = int(wind_data.get("speed", 2))
            wind_speed = float(wind_level * 1.5)

            cloud_index = int(first_forecast.get("cloudcover", 0))
            cloud_cover_pct = min(100, int((cloud_index / 9) * 100))

            return WeatherInfo(
                temperature=float(first_forecast.get("temp2m", 0)),
                humidity=int(rh_raw.replace("%", "")) if isinstance(rh_raw, str) else int(rh_raw),
                wind_speed=wind_speed,
                pressure=0,
                cloud_cover=cloud_cover_pct,
                provider_name="7Timer!"
            )
    except Exception as e:
        logger.error(f"Error fetching from 7Timer!: {e}")
        return None

async def get_norwegian_weather(lat: float, lon: float) -> Optional[WeatherInfo]:
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
    headers = {"User-Agent": "WeatherAggregatorUniversityProject/1.0 (student_project@example.com)"}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=5.0)
            if response.status_code != 200:
                return None

            data = response.json()
            details = data["properties"]["timeseries"][0]["data"]["instant"]["details"]

            return WeatherInfo(
                provider_name="Yr.no (Norway)",
                temperature=details["air_temperature"],
                humidity=int(details["relative_humidity"]),
                wind_speed=details["wind_speed"],
                pressure=int(details["air_pressure_at_sea_level"]),
                cloud_cover=int(details["cloud_area_fraction"])
            )
    except Exception as e:
        logger.error(f"Error fetching from Norway API: {e}")
        return None
