import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Vereinfachte Zuordnung der WMO-Wettercodes von Open-Meteo.
WEATHER_CODES = {
    0: "klarem Himmel",
    1: "überwiegend klarem Himmel",
    2: "teilweise bewölktem Himmel",
    3: "bedecktem Himmel",
    45: "Nebel",
    48: "gefrierendem Nebel",
    51: "leichtem Nieselregen",
    53: "mäßigem Nieselregen",
    55: "starkem Nieselregen",
    61: "leichtem Regen",
    63: "mäßigem Regen",
    65: "starkem Regen",
    71: "leichtem Schneefall",
    73: "mäßigem Schneefall",
    75: "starkem Schneefall",
    80: "Regenschauern",
    81: "kräftigen Regenschauern",
    82: "heftigen Regenschauern",
    95: "einem Gewitter",
    96: "einem Gewitter mit Hagel",
    99: "einem schweren Gewitter mit Hagel",
}


def get_weather(location: str) -> str:
    geo_response = requests.get(
        GEOCODING_URL,
        params={"name": location, "count": 1, "language": "de"},
        timeout=10,
    )
    geo_response.raise_for_status()
    results = geo_response.json().get("results")
    if not results:
        return f"Ich konnte den Ort '{location}' nicht finden."

    place = results[0]
    forecast_response = requests.get(
        FORECAST_URL,
        params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current_weather": True,
        },
        timeout=10,
    )
    forecast_response.raise_for_status()
    current = forecast_response.json().get("current_weather", {})

    temperature = current.get("temperature")
    code = current.get("weathercode")
    description = WEATHER_CODES.get(code, "unbekanntem Wetter")
    place_name = place.get("name", location)

    return f"In {place_name} sind es aktuell {temperature}°C bei {description}."
