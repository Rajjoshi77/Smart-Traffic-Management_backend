import os
import joblib
import pandas as pd

# Absolute path handling
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "traffic_model.pkl")
WEATHER_ENCODER_PATH = os.path.join(BASE_DIR, "models", "weather_encoder.pkl")
HOLIDAY_ENCODER_PATH = os.path.join(BASE_DIR, "models", "holiday_encoder.pkl")

# Load model and encoders
model = joblib.load(MODEL_PATH)
weather_encoder = joblib.load(WEATHER_ENCODER_PATH)
holiday_encoder = joblib.load(HOLIDAY_ENCODER_PATH)

def predict_traffic(data: dict):
    try:
        # --- SAFE HOLIDAY ENCODING ---
        holiday_value = data.get("holiday", "None")
        if holiday_value not in holiday_encoder.classes_:
            holiday_value = holiday_encoder.classes_[0]

        # --- SAFE WEATHER ENCODING ---
        weather_value = data.get("weather_main", "Clear")
        if weather_value not in weather_encoder.classes_:
            weather_value = weather_encoder.classes_[0]

        df = pd.DataFrame([{
            "hour": int(data["hour"]),
            "day_of_week": int(data["day_of_week"]),
            "is_weekend": int(data["is_weekend"]),
            "holiday": holiday_encoder.transform([holiday_value])[0],
            "temp": float(data.get("temp", 25)),
            "rain_1h": float(data.get("rain_1h", 0)),
            "snow_1h": float(data.get("snow_1h", 0)),
            "clouds_all": float(data.get("clouds_all", 0)),
            "weather_main": weather_encoder.transform([weather_value])[0],
        }])

        prediction = model.predict(df)[0]

        prediction = float(model.predict(df)[0])

        if prediction < 2000:
            label = "Low Traffic"
        elif prediction < 4500:
            label = "Medium Traffic"
        else:
            label = "High Traffic"

        return {
            "traffic_volume": round(prediction),
            "traffic_level": label
        }


    except Exception as e:
        print("❌ Prediction Error:", e)
        return {"error": str(e)}
