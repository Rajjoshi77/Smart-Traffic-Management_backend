import requests
from ..config import WEATHER_API_KEY, WEATHER_API_URL, LATITUDE, LONGITUDE
from ..models.weather_model import WeatherData
import time

def fetch_weather_for_datetime(dt: int, lat=None, lon=None):
    """
    Fetch weather for a given unix timestamp (dt, in seconds) and location.
    Uses OpenWeatherMap One Call API (timemachine for past),
    falls back to current weather endpoint for future or if fails.
    """
    lat = lat if lat is not None else LATITUDE
    lon = lon if lon is not None else LONGITUDE
    url = "https://api.openweathermap.org/data/2.5/onecall/timemachine"
    params = {
        "lat": lat,
        "lon": lon,
        "dt": dt,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        hourly = data.get("hourly", [{}])[0]
        rain_1h = 0
        snow_1h = 0
        clouds_all = hourly.get('clouds', 0)
        # Use rain/snow if available, else estimate from pop * clouds_all
        if 'rain' in hourly and isinstance(hourly['rain'], dict):
            rain_1h = hourly['rain'].get('1h', 0)
        elif 'pop' in hourly:
            rain_1h = float(hourly.get('pop', 0)) * float(clouds_all) / 100.0
        if 'snow' in hourly and isinstance(hourly['snow'], dict):
            snow_1h = hourly['snow'].get('1h', 0)
        # No good proxy for snow, but if pop is high and temp < 273.15K, estimate snow
        elif 'pop' in hourly and hourly.get('temp', 300) < 273.15:
            snow_1h = float(hourly.get('pop', 0)) * float(clouds_all) / 100.0
        return WeatherData(
            temperature=hourly.get("temp", 25),
            humidity=hourly.get("humidity", 50),
            weather=hourly.get("weather", [{}])[0].get("main", "Clear"),
            wind_speed=hourly.get("wind_speed", 2),
            rain_1h=rain_1h,
            snow_1h=snow_1h,
            clouds_all=clouds_all
        )
    # fallback: use current weather endpoint
    params2 = {
        "lat": lat,
        "lon": lon,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }
    resp2 = requests.get(WEATHER_API_URL, params=params2)
    if resp2.status_code != 200:
        raise Exception("Weather API failed: " + resp2.text)
    d = resp2.json()
    rain_1h = 0
    snow_1h = 0
    clouds_all = 0
    # OpenWeatherMap current endpoint may provide rain/snow as dicts with '1h' key
    if 'rain' in d and isinstance(d['rain'], dict):
        rain_1h = d['rain'].get('1h', 0)
    elif 'clouds' in d:
        # Use cloudiness as a proxy for rain if pop is not available
        if isinstance(d['clouds'], dict):
            clouds_all = d['clouds'].get('all', 0)
        else:
            clouds_all = d['clouds']
        rain_1h = float(clouds_all) / 100.0
    if 'snow' in d and isinstance(d['snow'], dict):
        snow_1h = d['snow'].get('1h', 0)
    elif 'clouds' in d and d.get('main', {}).get('temp', 300) < 273.15:
        # Estimate snow if cold and cloudy
        snow_1h = float(clouds_all) / 100.0
    return WeatherData(
        temperature=d["main"]["temp"],
        humidity=d["main"]["humidity"],
        weather=d["weather"][0]["main"],
        wind_speed=d["wind"]["speed"],
        rain_1h=rain_1h,
        snow_1h=snow_1h,
        clouds_all=clouds_all
    )
