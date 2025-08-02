from fastapi import FastAPI, Query
import httpx
import os
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/weather")
async def get_weather(city: str = Query(..., min_length=2)):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    encoded_city = quote(city)

    params = {
        "q": encoded_city,
        "appid": API_KEY,
        "units": "metric"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(base_url, params=params)

    print("Status:", response.status_code)
    print("Text:", response.text)

    if response.status_code != 200:
        return {
            "error": "City not found",
            "details": response.text
        }

    data = response.json()
    return {
        "city": data.get("name"),
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"],
        "icon": data["weather"][0]["icon"]
    }

def extract_keywords(temp: float, desc: str) -> list:
    tags = []

    if temp >= 35:
        tags.append("very hot")
    elif temp >= 28:
        tags.append("hot")
    elif temp >= 18:
        tags.append("warm")
    elif temp >= 10:
        tags.append("cool")
    else:
        tags.append("cold")

    desc = desc.lower()
    tags.append(desc)  

    if "cloud" in desc:
        tags.append("cloudy")
    if "rain" in desc or "drizzle" in desc:
        tags.append("rainy")
    if "clear" in desc:
        tags.append("sunny")
    if "snow" in desc:
        tags.append("snowy")
    if "humid" in desc:
        tags.append("humid")

    return tags

@app.get("/weather-tags")
async def get_weather_tags(city: str):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    async with httpx.AsyncClient() as client:
        res = await client.get("https://api.openweathermap.org/data/2.5/weather", params=params)

    if res.status_code != 200:
        return {"error": "Weather data not found"}

    data = res.json()
    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]

    tags = extract_keywords(temp, desc)

    return {
        "city": city,
        "tags": tags
    }
