from fastapi import FastAPI
from pydantic import BaseModel
from backend.services.ai_services import predict_traffic
from backend.services.weather_services import fetch_weather_for_datetime
from backend.services.spark_services import get_peak_hours
from fastapi.middleware.cors import CORSMiddleware
import os


app = FastAPI(title="Smart Traffic Management Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

class PredictInput(BaseModel):
    date: str  # YYYY-MM-DD
    hour: int  # 0-23
    holiday: str = "None"
    rain_1h: float = 0
    snow_1h: float = 0
    clouds_all: int = 0
    lat: float = 12.9716
    lon: float = 77.5946

@app.get("/")
def home():
    return {"status": "Backend is running"}

@app.post("/predict")
def predict(data: PredictInput):
    from datetime import datetime, timezone
    dt = datetime.strptime(f"{data.date} {data.hour}", "%Y-%m-%d %H")
    dt = dt.replace(tzinfo=timezone.utc)
    unix_time = int(dt.timestamp())

    # Fetch weather for that datetime and location
    weather = fetch_weather_for_datetime(unix_time, lat=data.lat, lon=data.lon)

    day_of_week = dt.weekday()
    is_weekend = 1 if day_of_week in [5, 6] else 0
    # Normalize weather_main to match model training (capitalize, map to known classes)
    weather_main = str(weather.weather).capitalize()
    # Map common OWM weather to model classes
    weather_map = {
        "Clear": "Clear",
        "Clouds": "Clouds",
        "Rain": "Rain",
        "Drizzle": "Rain",
        "Thunderstorm": "Rain",
        "Snow": "Snow",
        "Mist": "Clouds",
        "Smoke": "Clouds",
        "Haze": "Clouds",
        "Dust": "Clouds",
        "Fog": "Clouds",
        "Sand": "Clouds",
        "Ash": "Clouds",
        "Squall": "Clouds",
        "Tornado": "Clouds",
    }
    mapped_weather = weather_map.get(weather_main, "Clear")

    # Ensure temperature is in Kelvin for the model
    temp_kelvin = weather.temperature + 273.15 if weather.temperature < 100 else weather.temperature

    # Ensure rain/snow/clouds are numbers
    rain_1h = weather.rain_1h if weather.rain_1h is not None else 0
    snow_1h = weather.snow_1h if weather.snow_1h is not None else 0
    clouds_all = weather.clouds_all if weather.clouds_all is not None else 0

    model_input = {
        "hour": data.hour,
        "day_of_week": day_of_week,
        "is_weekend": is_weekend,
        "holiday": data.holiday,
        "temp": temp_kelvin,
        "rain_1h": rain_1h,
        "snow_1h": snow_1h,
        "clouds_all": clouds_all,
        "weather_main": mapped_weather,
    }
    result = predict_traffic(model_input)
    # Attach weather details for frontend history (show what was actually used)
    result["weather_main"] = mapped_weather
    result["temp"] = temp_kelvin
    result["rain_1h"] = rain_1h
    result["snow_1h"] = snow_1h
    result["clouds_all"] = clouds_all
    return result

@app.get("/peak-hours")
def peak_hours():
    return get_peak_hours()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
    )