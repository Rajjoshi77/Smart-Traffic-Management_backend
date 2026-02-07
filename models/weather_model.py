from pydantic import BaseModel

class WeatherData(BaseModel):
    temperature: float
    humidity: int
    weather: str
    wind_speed: float
    rain_1h: float = 0
    snow_1h: float = 0
    clouds_all: int = 0
