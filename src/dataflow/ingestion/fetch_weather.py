from dataclasses import fields

import requests # external library for making HTTP requests
import json # built-in library for working with JSON data
import csv # built-in library for working with CSV files
from pathlib import Path # built-in library for working with file paths

URL = "https://archive-api.open-meteo.com/v1/archive" #endpoint provided by Open-Meteo for historical weather data

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
response.raise_for_status() #checks the HTTP status code

data = response.json() # parses the JSON response into a Python dictionary
hourly = data["hourly"]
required_fields = ["time", "temperature_2m", "relative_humidity_2m", "precipitation"]
# we check if all required fields are present in the hourly data, if not we raise a ValueError
for fields in required_fields:
    if fields not in hourly:
        raise ValueError(f"Missing required field: {fields}")


timestamps = hourly["time"]
temperature = hourly["temperature_2m"]
relative_humidity = hourly["relative_humidity_2m"]
precipitation = hourly["precipitation"]

records = [] # we will implement a list of dictionaries to store the weather data in a structured format
missing_records = 0
# data validation and exporting records into a CSV file
for time, temp, humidity, precip in zip(timestamps, temperature, relative_humidity, precipitation, strict=True):
    if humidity is not None and (humidity < 0 or humidity > 100):
        raise ValueError(f"Invalid humidity value: {humidity} at time {time}")
    if temp is not None and (temp < -100 or temp > 100):
        raise ValueError(f"Invalid temperature value: {temp} at time {time}")
    if precip is not None and precip < 0:
        raise ValueError(f"Invalid precipitation value: {precip} at time {time}")
    if temp is None or humidity is None or precip is None:
        missing_records += 1
        print(f"Warning: Missing data at time {time}. Missing records count: {missing_records}")
    if not hourly["time"]:
        raise ValueError(f"No time data available for {time}.")

    record = { # create a dictionary for each record and append it to the records list
        "timestamp": time,
        "temperature_2m": temp,
        "relative_humidity_2m": humidity,
        "precipitation": precip
    }
    records.append(record)


output_dir = Path("data")
output_dir.mkdir(exist_ok=True)

output_file = output_dir / "weather_data.csv"

with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
    fieldnames = ["timestamp", "temperature_2m", "relative_humidity_2m", "precipitation"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader() # writes the header row to the CSV file
    writer.writerows(records) # writes all the records to the CSV file

total_records = len(records)
if total_records > 0:
    missing_percentage = (missing_records / total_records) * 100
    print(f"Total records: {total_records}, Missing records: {missing_records}, Missing percentage: {missing_percentage:.2f}%")
else:
    print("No records were processed.")
