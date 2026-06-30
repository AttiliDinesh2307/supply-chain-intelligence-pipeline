import requests
import os
from dotenv import load_dotenv
from db_handler import create_tables, insert_weather, insert_exchange_rate, insert_country_data

# Load environment variables from .env file
load_dotenv()


def fetch_weather(city="Mumbai"):
    """
    Fetches current weather data for a given city.
    Returns a dictionary with weather info, or None if it fails.
    """
    api_key = os.getenv("WEATHER_API_KEY")
    url = "https://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        weather_info = {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "weather_condition": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }
        return weather_info
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None


def fetch_exchange_rate(base_currency="USD"):
    """
    Fetches exchange rates for a given base currency.
    Returns a dictionary with rates, or None if it fails.
    """
    api_key = os.getenv("EXCHANGE_API_KEY")
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        exchange_info = {
            "base_currency": data["base_code"],
            "last_updated": data["time_last_update_utc"],
            "rates": {
                "INR": data["conversion_rates"].get("INR"),
                "EUR": data["conversion_rates"].get("EUR"),
                "GBP": data["conversion_rates"].get("GBP"),
                "JPY": data["conversion_rates"].get("JPY")
            }
        }
        return exchange_info
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching exchange rate data: {e}")
        return None


def fetch_country_data(country_name="India"):
    """
    Fetches country details like region, currency, population.
    Returns a dictionary, or None if it fails.
    """
    api_key = os.getenv("COUNTRY_API_KEY")
    url = f"https://api.restcountries.com/countries/v5/names.common/{country_name}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        raw_data = response.json()
        data = raw_data["data"]["objects"][0]
        
        country_info = {
            "name": data["names"]["common"],
            "region": data.get("region"),
            "subregion": data.get("subregion"),
            "population": data.get("population"),
            "capital": data.get("capitals", [{}])[0].get("name", "N/A"),
            "currencies": [c["code"] for c in data.get("currencies", [])]
        }
        return country_info
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching country data: {e}")
        return None


def fetch_fuel_prices(state="Karnataka", district="Bengaluru"):
    """
    Fetches petrol/diesel prices for a given Indian state and district.
    Returns a dictionary, or None if it fails (community-maintained API,
    may occasionally be slow or unavailable).
    """
    url = f"https://fuelprice-api-india.herokuapp.com/price/{state}/{district}"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        fuel_info = {
            "district": data.get("district", district),
            "products": data.get("products", [])
        }
        return fuel_info
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching fuel price data (non-critical, continuing): {e}")
        return None


def fetch_route_distance(origin_coords, destination_coords, origin_name="Origin", destination_name="Destination"):
    """
    Fetches driving distance and duration between two coordinate pairs using OSRM.
    Coordinates must be (longitude, latitude) tuples.
    Returns a dictionary, or None if it fails.
    """
    origin_str = f"{origin_coords[0]},{origin_coords[1]}"
    dest_str = f"{destination_coords[0]},{destination_coords[1]}"
    url = f"http://router.project-osrm.org/route/v1/driving/{origin_str};{dest_str}"
    
    params = {"overview": "false"}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        route = data["routes"][0]
        
        route_info = {
            "origin": origin_name,
            "destination": destination_name,
            "distance_km": round(route["distance"] / 1000, 2),
            "duration_minutes": round(route["duration"] / 60, 1)
        }
        return route_info
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching route data: {e}")
        return None


if __name__ == "__main__":
    create_tables()

    weather_result = fetch_weather("Bengaluru")
    print("Weather:", weather_result)
    insert_weather(weather_result)

    exchange_result = fetch_exchange_rate("USD")
    print("Exchange Rate:", exchange_result)
    insert_exchange_rate(exchange_result)

    country_result = fetch_country_data("India")
    print("Country Data:", country_result)
    insert_country_data(country_result)

    fuel_result = fetch_fuel_prices("Karnataka", "Bengaluru")
    print("Fuel Prices:", fuel_result)

    route_result = fetch_route_distance(
        origin_coords=(77.5946, 12.9716),
        destination_coords=(80.2707, 13.0827),
        origin_name="Bengaluru",
        destination_name="Chennai"
    )
    print("Route Data:", route_result)