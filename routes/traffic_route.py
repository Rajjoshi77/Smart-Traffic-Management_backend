from fastapi import APIRouter
from services.weather_services import fetch_current_weather

router = APIRouter()

@router.get("/traffic-status")
def traffic_status():
    weather = fetch_current_weather()

    # Simple rule-based logic (replace with ML later)
    congestion_level = "Low"

    if weather.weather == "Rain":
        congestion_level = "High"
    elif weather.weather == "Clouds":
        congestion_level = "Medium"

    return {
        "weather": weather.dict(),
        "traffic_prediction": congestion_level
    }
