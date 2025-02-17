from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel
from typing import Dict
import os

app = FastAPI()

# Set your free API keys
OPENWEATHER_API_KEY = "your_openweathermap_api_key"
HF_LLM_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct"
HF_API_KEY = "your_huggingface_api_key"

class WeatherQuery(BaseModel):
    city: str
    question: str

@app.get("/weather/{city}")
def get_weather(city: str):
    """Fetch current weather data for a city."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="City not found")
    return response.json()

@app.post("/ai-weather")
def ai_weather_query(query: WeatherQuery):
    """Answer weather-related questions using an AI model."""
    weather_data = get_weather(query.city)
    prompt = f"City: {query.city}\nWeather: {weather_data}\nUser Question: {query.question}\nAnswer:"
    
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    llm_response = requests.post(HF_LLM_API_URL, headers=headers, json={"inputs": prompt})
    
    if llm_response.status_code != 200:
        raise HTTPException(status_code=500, detail="AI service error")
    
    return {"response": llm_response.json()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
