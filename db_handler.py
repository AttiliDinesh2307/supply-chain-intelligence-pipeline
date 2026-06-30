import sqlite3
import os
from datetime import datetime

DB_NAME = "supply_chain.db"


def get_connection():
    """Creates and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    return conn


def create_tables():
    """Creates all required tables if they don't already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            temperature REAL,
            feels_like REAL,
            humidity INTEGER,
            weather_condition TEXT,
            wind_speed REAL,
            fetched_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exchange_rate_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            base_currency TEXT,
            inr REAL,
            eur REAL,
            gbp REAL,
            jpy REAL,
            fetched_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS country_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            region TEXT,
            subregion TEXT,
            population INTEGER,
            capital TEXT,
            currencies TEXT,
            fetched_at TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Tables created successfully (or already exist).")


def insert_weather(weather_data):
    """Inserts a weather record into the database."""
    if weather_data is None:
        print("No weather data to insert.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO weather_log (city, temperature, feels_like, humidity, weather_condition, wind_speed, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        weather_data["city"],
        weather_data["temperature"],
        weather_data["feels_like"],
        weather_data["humidity"],
        weather_data["weather_condition"],
        weather_data["wind_speed"],
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()
    print("Weather data inserted.")


def insert_exchange_rate(exchange_data):
    """Inserts an exchange rate record into the database."""
    if exchange_data is None:
        print("No exchange rate data to insert.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    rates = exchange_data["rates"]

    cursor.execute("""
        INSERT INTO exchange_rate_log (base_currency, inr, eur, gbp, jpy, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        exchange_data["base_currency"],
        rates.get("INR"),
        rates.get("EUR"),
        rates.get("GBP"),
        rates.get("JPY"),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()
    print("Exchange rate data inserted.")


def insert_country_data(country_data):
    """Inserts a country record into the database."""
    if country_data is None:
        print("No country data to insert.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO country_data (name, region, subregion, population, capital, currencies, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        country_data["name"],
        country_data["region"],
        country_data["subregion"],
        country_data["population"],
        country_data["capital"],
        ", ".join(country_data["currencies"]),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()
    print("Country data inserted.")


if __name__ == "__main__":
    create_tables()