import logging
import os
from datetime import datetime
from typing import Any, Dict
from zoneinfo import ZoneInfo

import requests
from google.adk.agents import Agent

logger = logging.getLogger(__name__)

MODEL = os.getenv("ADK_MODEL", "gemini-3-flash-preview")
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT = 5

# ---------------------------------------------------------
# Geocoding Helper (Supports Any City)
# ---------------------------------------------------------
def get_city_coordinates(city: str) -> Dict[str, Any]:
    """
    Uses Open-Meteo Geocoding API to get any city name
    into latitude, longitude, and timezone.
    """
    try:
        response = requests.get(
            GEOCODING_URL,
            params={"name": city, "count": 1},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        results = data.get("results")
        if not results:
            return {"status": "error", "error_message": "City not found."}

        city_data = results[0]

        return {
            "status": "success",
            "latitude": city_data["latitude"],
            "longitude": city_data["longitude"],
            "timezone": city_data["timezone"],
            "name": city_data["name"],
            "region": city_data.get("admin1", ""),
            "country": city_data.get("country", ""),
        }

    except requests.exceptions.RequestException:
        return {"status": "error", "error_message": "Failed to resolve city name."}


def _format_location(location: Dict[str, Any]) -> str:
    parts = [location["name"], location.get("region"), location.get("country")]
    return ", ".join(p for p in parts if p)


# ---------------------------------------------------------
# Weather Function
# ---------------------------------------------------------
def get_weather(city: str) -> Dict[str, Any]:
    """
    Fetch current weather data for any city using the Open-Meteo public API.

    Args:
        city: City name, e.g. "Boston".

    Returns:
        Dict with status, report (temperature_c, wind_speed_kmh, weather_code,
        plus the resolved location name/region/country) and error_message.
    """
    city = city.strip().lower()
    logger.info(f"Weather tool called for city: {city}")

    location = get_city_coordinates(city)

    if location["status"] == "error":
        return {
            "status": "error",
            "report": None,
            "error_message": location["error_message"]
        }

    try: #api call
        response = requests.get(
            FORECAST_URL,
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current_weather": True
            },
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()
        data = response.json()
        weather = data.get("current_weather")

        if not weather:
            return {
                "status": "error",
                "report": None,
                "error_message": "Weather API returned no data."
            }

        return {
            "status": "success",
            "report": {
                "location": _format_location(location),
                "temperature_c": weather["temperature"],
                "wind_speed_kmh": weather["windspeed"],
                "weather_code": weather["weathercode"]
            },
            "error_message": None
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Weather API request failed: {e}")
        return {
            "status": "error",
            "report": None,
            "error_message": "Failed to fetch weather data."
        }


# ---------------------------------------------------------
# Time Function
# ---------------------------------------------------------
def get_current_time(city: str) -> Dict[str, Any]:
    """
    Fetch the current local time for any city.

    Args:
        city: City name, e.g. "Tokyo".

    Returns:
        Dict with status, report (local_time, timezone, resolved location) and
        error_message.
    """
    city = city.strip().lower()
    logger.info(f"Time tool called for city: {city}")

    try:
        location = get_city_coordinates(city)

        if location["status"] == "error":
            return {
                "status": "error",
                "report": None,
                "error_message": location["error_message"]
            }

        tz = ZoneInfo(location["timezone"])
        now = datetime.now(tz)

        return {
            "status": "success",
            "report": {
                "location": _format_location(location),
                "local_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                "timezone": location["timezone"]
            },
            "error_message": None
        }

    except Exception as e:
        logger.error(f"Time tool failed: {e}")
        return {
            "status": "error",
            "report": None,
            "error_message": "Failed to fetch time data."
        }


# ---------------------------------------------------------
# Agent Instructions and Definition
# ---------------------------------------------------------
INSTRUCTION = """
You are a weather and time assistant.

Rules:
- If the user asks about weather, call get_weather.
- If the user asks about current time, call get_current_time.
- Always use tools instead of guessing.
- Don't use the metric system; convert to imperial units (°F, mph) before answering.
- Indicate where the location is too (example if Boston say Boston, MA, United States).
- If a tool returns an error, explain it clearly to the user.
"""

root_agent = Agent(
    name="weather_time_agent",
    model=MODEL,
    description="Provides real-time weather and time information for any city.",
    instruction=INSTRUCTION,
    tools=[get_weather, get_current_time],
)