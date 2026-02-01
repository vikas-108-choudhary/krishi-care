import os
import requests
OPENWEATHER_API_KEY = "879ccc4b6fd48988ba831d2aafc5450f"
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather_advice(city, disease=None, lang="en"):
    if not city:
        return "City not provided"

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("cod") != 200:
            return f"Weather API error: {data}"

        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        desc = data["weather"][0]["description"]

        advice = (
            f"🌤 Weather in {city}: {desc}\n"
            f"🌡 Temperature: {temp}°C\n"
            f"💧 Humidity: {humidity}%"
        )

        # Disease-specific logic
        if disease and "rust" in disease.lower() and humidity > 60:
            advice += "\n⚠ High humidity increases fungal disease risk."

        return advice

    except Exception as e:
        return f"Weather service error: {str(e)}"
