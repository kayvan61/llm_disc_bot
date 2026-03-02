import python_weather

import asyncio

async def call_api(location) -> str:
  # Declare the client. The measuring unit used defaults to the metric system (celcius, km/h, etc.)
  async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
    
    # Fetch a weather forecast from a city.
    weather = await client.get(location)
    
    # Fetch the temperature for today.
    return str(weather.temperature)
    
async def call_tool(location: str) -> str:
    res = await call_api(location)
    return [("tempurature", res)]

