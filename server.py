import os
from datetime import datetime

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

# ---------------------------------------------------------------------------
# Server setup
# HOST / PORT are read from environment variables so the same code works in
# local dev (127.0.0.1:8000) and in Docker / cloud deployments without edits.
# dns_rebinding_protection is disabled so reverse-proxy tools like ngrok can
# forward requests without triggering the host-header security check.
# ---------------------------------------------------------------------------
_host = os.environ.get("HOST", "127.0.0.1")
_port = int(os.environ.get("PORT", "8000"))

mcp = FastMCP(
    "simple-mcp",
    host=_host,
    port=_port,
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)


# ---------------------------------------------------------------------------
# Tool 1 — ping
# Purpose  : Health-check / connectivity test.
# Input    : None
# Output   : The string "pong"
# Why      : The simplest possible MCP tool. Useful to verify the server is
#            reachable before testing anything more complex. Also a great
#            first example to show the decorator pattern.
# ---------------------------------------------------------------------------
@mcp.tool()
def ping() -> str:
    """
    Check if the server is alive.

    Args:
        None — this tool takes no input.

    Returns:
        str: Always returns the literal string "pong".

    Raises:
        Nothing — if the server is unreachable, the call itself will fail
        before this function is ever executed.

    Example:
        AI prompt  : "Are you there?" / "ping"
        Tool call  : ping()
        Response   : "pong"
    """
    return "pong"


# ---------------------------------------------------------------------------
# Tool 2 — echo
# Purpose  : Return the caller's message in three case variants.
# Input    : message (str) — any text string
# Output   : Three lines: Capitalized, lowercased (casefold), and lower
# Why      : Demonstrates that tools can accept typed string parameters.
#            The AI reads the type hint and docstring to know what to pass.
#            casefold() is the Unicode-aware lower used for comparisons.
# ---------------------------------------------------------------------------
@mcp.tool()
def echo(message: str) -> str:
    """
    Echo back the provided message in three case formats.

    Args:
        message (str): Any text string to be echoed back.
                       No length limit enforced.

    Returns:
        str: Three lines separated by newline characters:
             Line 1 — message.capitalize()  : first letter upper, rest lower  (!!!)
             Line 2 — message.casefold()    : aggressive Unicode lowercase     (!!)
             Line 3 — message.lower()       : standard ASCII lowercase         (!)

    Note:
        casefold() vs lower(): casefold() handles special Unicode characters
        (e.g. German 'ß' → 'ss') making it safer for multilingual input.

    Example:
        AI prompt  : "Echo the word Hello"
        Tool call  : echo(message="Hello")
        Response   : "Hello!!!\nhello!!\nhello!"
    """
    return f"{message.capitalize()}!!! \n{message.casefold()}!! \n{message.lower()}!"


# ---------------------------------------------------------------------------
# Tool 3 — calculator
# Purpose  : Perform one of four basic arithmetic operations.
# Input    : operation (str) — 'add' | 'subtract' | 'multiply' | 'divide'
#            a, b (float)    — the two operands
# Output   : Result as a float
# Why      : Shows multi-parameter tools with mixed types. The structural
#            pattern match (Python 3.10+) is a clean alternative to if/elif.
#            Divide-by-zero raises ValueError so the AI receives a clear
#            error message rather than a crash.
# ---------------------------------------------------------------------------
@mcp.tool()
def calculator(operation: str, a: float, b: float) -> float:
    """
    Perform a basic arithmetic operation on two numbers.

    Args:
        operation (str): The arithmetic operation to perform.
                         Accepted values (case-sensitive):
                           'add'      — returns a + b
                           'subtract' — returns a - b
                           'multiply' — returns a * b
                           'divide'   — returns a / b  (b must not be 0)

        a (float): The first operand (left-hand side of the operation).
                   Accepts integers too — Python will widen them to float.

        b (float): The second operand (right-hand side of the operation).
                   Must not be 0 when operation is 'divide'.

    Returns:
        float: The result of the arithmetic operation.

    Raises:
        ValueError: If operation is 'divide' and b == 0.
        ValueError: If operation is not one of the four accepted strings.

    Example:
        AI prompt  : "What is 15 divided by 4?"
        Tool call  : calculator(operation="divide", a=15, b=4)
        Response   : 3.75
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


# ---------------------------------------------------------------------------
# Tool 4 — current_time
# Purpose  : Return the server's current local date and time.
# Input    : None
# Output   : Formatted datetime string e.g. "2026-05-05 14:30:00"
# Why      : AI models have a training cutoff and cannot know the current
#            time. This tool bridges that gap with zero external dependencies.
#            A classic example of augmenting the model with live system data.
# ---------------------------------------------------------------------------
@mcp.tool()
def current_time() -> str:
    """
    Return the server's current local date and time.

    Args:
        None — this tool takes no input.

    Returns:
        str: Current datetime formatted as "YYYY-MM-DD HH:MM:SS".
             Timezone: local system time of the machine running the server.
             Format detail:
               YYYY — 4-digit year
               MM   — 2-digit month  (01–12)
               DD   — 2-digit day    (01–31)
               HH   — 2-digit hour   (00–23, 24-hour clock)
               MM   — 2-digit minute (00–59)
               SS   — 2-digit second (00–59)

    Note:
        AI models have a knowledge cutoff and cannot know the live time.
        This tool provides real-time clock data without any external API call.

    Example:
        AI prompt  : "What time is it?" / "What's today's date?"
        Tool call  : current_time()
        Response   : "2026-05-05 14:30:00"
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------------------
# Tool 5 — current_weather
# Purpose  : Fetch live temperature and wind speed for any city.
# Input    : location (str) — city or place name e.g. "Mumbai", "Paris"
# Output   : dict with location, lat/lon, temperature, wind speed, and units
# Why      : Showcases two key MCP concepts together:
#              1. Async tools — uses httpx.AsyncClient for non-blocking I/O
#              2. Chained API calls — geocoding first, then weather forecast
#
# Step 1 — Geocoding (Open-Meteo Geocoding API, no API key required):
#   Converts the city name to latitude/longitude coordinates.
#
# Step 2 — Weather (Open-Meteo Forecast API, no API key required):
#   Uses the coordinates to fetch current temperature and wind speed.
#
# Both APIs are free and open — no signup needed, ideal for demos.
# ---------------------------------------------------------------------------
@mcp.tool()
async def current_weather(location: str) -> dict:
    """
    Fetch the current weather for any location using two chained free APIs.

    Args:
        location (str): City or place name to look up.
                        Examples: 'Tokyo', 'New York', 'Mumbai', 'Paris'
                        Partial names work (e.g. 'London' resolves to
                        'London, United Kingdom').
                        No API key required.

    Returns:
        dict: A dictionary with the following keys:
            location      (str)   — Resolved city name + country
                                    e.g. "Mumbai, India"
            latitude      (float) — Geographic latitude of the city
            longitude     (float) — Geographic longitude of the city
            time          (str)   — Timestamp of the weather reading (ISO 8601)
            temperature_2m (float)— Air temperature at 2 metres above ground
            wind_speed_10m (float)— Wind speed at 10 metres above ground
            units (dict):
                temperature (str) — Unit for temperature, default "°C"
                wind_speed  (str) — Unit for wind speed, default "km/h"

    Raises:
        ValueError: If the location string does not match any known place
                    in the Open-Meteo geocoding database.
        httpx.HTTPStatusError: If either upstream API returns a non-2xx
                               HTTP status code.

    Internal flow:
        Step 1 — Geocoding API (geocoding-api.open-meteo.com):
                 Converts location name → latitude + longitude.
        Step 2 — Forecast API (api.open-meteo.com):
                 Uses lat/lon to fetch current temperature and wind speed.

    Example:
        AI prompt  : "What's the weather in Tokyo right now?"
        Tool call  : current_weather(location="Tokyo")
        Response   : {
                       "location": "Tokyo, Japan",
                       "latitude": 35.6895,
                       "longitude": 139.6917,
                       "time": "2026-05-05T14:00",
                       "temperature_2m": 22.3,
                       "wind_speed_10m": 11.5,
                       "units": {"temperature": "°C", "wind_speed": "km/h"}
                     }
    """
    async with httpx.AsyncClient() as client:
        # Step 1: resolve city name → lat/lon
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

        # Step 2: fetch current weather using the resolved coordinates
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


# ---------------------------------------------------------------------------
# Entry point
# transport="streamable-http" exposes the MCP server over HTTP so any MCP
# client (Claude Desktop, VS Code extension, etc.) can connect via a URL
# instead of launching a subprocess (stdio transport).
# ---------------------------------------------------------------------------
def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
