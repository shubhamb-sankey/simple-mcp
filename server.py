import os
from datetime import datetime

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

_host = os.environ.get("HOST", "127.0.0.1")
_port = int(os.environ.get("PORT", "8000"))

mcp = FastMCP(
    "simple-mcp",
    host=_host,
    port=_port,
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)


@mcp.tool()
def ping() -> str:
    """Check if the server is alive."""
    return "pong"


@mcp.tool()
def echo(message: str) -> str:
    """Echo back the provided message."""
    return f"{message.capitalize()}!!! \n{message.casefold()}!! \n{message.lower()}!"


@mcp.tool()
def calculator(operation: str, a: float, b: float) -> float:
    """
    Perform a basic arithmetic operation.

    Args:
        operation: One of 'add', 'subtract', 'multiply', 'divide'
        a: First operand
        b: Second operand
    """
    match operation:
        case "add":
            return a + b
        case "subtract":
            return a - b
        case "multiply":
            return a * b
        case "divide":
            if b == 0:
                raise ValueError("Cannot divide by zero")
            return a / b
        case _:
            raise ValueError(
                f"Unknown operation '{operation}'. Use: add, subtract, multiply, divide"
            )


@mcp.tool()
def current_time() -> str:
    """Return the current local date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@mcp.tool()
async def current_weather(location: str) -> dict:
    """
    Fetch the current weather for any location.

    Args:
        location: City or place name (e.g. 'Tokyo', 'New York', 'Paris')
    """
    async with httpx.AsyncClient() as client:
        geo = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": location, "count": 1, "language": "en", "format": "json"},
            timeout=10,
        )
        geo.raise_for_status()
        results = geo.json().get("results")
        if not results:
            raise ValueError(f"Location '{location}' not found")

        lat = results[0]["latitude"]
        lon = results[0]["longitude"]
        resolved_name = results[0].get("name", location)
        country = results[0].get("country", "")

        weather = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,wind_speed_10m",
                "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
            },
            timeout=10,
        )
        weather.raise_for_status()
        data = weather.json()

    current = data.get("current", {})
    current_units = data.get("current_units", {})
    return {
        "location": f"{resolved_name}, {country}".strip(", "),
        "latitude": lat,
        "longitude": lon,
        "time": current.get("time"),
        "temperature_2m": current.get("temperature_2m"),
        "wind_speed_10m": current.get("wind_speed_10m"),
        "units": {
            "temperature": current_units.get("temperature_2m", "°C"),
            "wind_speed": current_units.get("wind_speed_10m", "km/h"),
        },
    }


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
