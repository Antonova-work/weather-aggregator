from fastapi import APIRouter, HTTPException
from app.domain.models import AggregatedWeather
from app.services.aggregator import get_aggregated_weather

router = APIRouter()

@router.get("/weather", response_model=AggregatedWeather)
async def weather_endpoint(lat: float, lon: float):

    try:
        return await get_aggregated_weather(lat, lon)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")