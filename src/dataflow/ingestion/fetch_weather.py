import requests

URL = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": 46.77,
    "longitude": 23.59,
    "start_date": "2026-10-01",
    "end_date": "2026-10-07",
    "hourly": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation"
    ],
    "timezone": "Europe/Bucharest"
}

response = requests.get(URL, params=params, timeout=30)
response.raise_for_status()

data = response.json()

print(data["hourly"]["time"][:5])
print(data["hourly"]["temperature_2m"][:5])