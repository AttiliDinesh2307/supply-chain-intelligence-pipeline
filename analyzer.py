import pandas as pd
import sqlite3
from db_handler import get_connection
from data_fetch import fetch_route_distance


def load_weather_data():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM weather_log ORDER BY fetched_at", conn)
    conn.close()
    return df


def load_exchange_data():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM exchange_rate_log ORDER BY fetched_at", conn)
    conn.close()
    return df


def load_country_data():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM country_data ORDER BY fetched_at", conn)
    conn.close()
    return df


def calculate_weather_risk(row):
    """
    Scores weather risk 0-10 based on wind speed and extreme temperature.
    Higher wind speed and extreme temps = higher risk.
    """
    risk = 0
    
    # Wind speed risk (logistics/delivery disruption)
    if row["wind_speed"] > 15:
        risk += 5
    elif row["wind_speed"] > 8:
        risk += 2
    
    # Temperature extremes (affects perishables, warehouse operations)
    if row["temperature"] > 40 or row["temperature"] < 0:
        risk += 5
    elif row["temperature"] > 35:
        risk += 2
    
    # Severe weather conditions
    severe_keywords = ["storm", "thunderstorm", "snow", "heavy rain", "tornado"]
    condition = row["weather_condition"].lower()
    if any(keyword in condition for keyword in severe_keywords):
        risk += 3
    
    return min(risk, 10)  # cap at 10


def calculate_forex_risk(df):
    """
    Scores currency volatility risk 0-10 based on how much INR rate
    has changed compared to the previous record.
    """
    df = df.copy()
    df["inr_change_pct"] = df["inr"].pct_change().abs() * 100
    
    def score(change_pct):
        if pd.isna(change_pct):
            return 0  # first record, no comparison possible
        if change_pct > 2:
            return 10
        elif change_pct > 1:
            return 6
        elif change_pct > 0.5:
            return 3
        else:
            return 1
    
    df["forex_risk"] = df["inr_change_pct"].apply(score)
    return df


def generate_risk_report():
    """
    Combines weather and forex risk into one supply chain risk score.
    Returns a summary DataFrame.
    """
    weather_df = load_weather_data()
    exchange_df = load_exchange_data()
    
    weather_df["weather_risk"] = weather_df.apply(calculate_weather_risk, axis=1)
    exchange_df = calculate_forex_risk(exchange_df)
    
    # Take the latest record from each for the current snapshot
    latest_weather = weather_df.iloc[-1]
    latest_exchange = exchange_df.iloc[-1]
    
    overall_risk = round((latest_weather["weather_risk"] + latest_exchange["forex_risk"]) / 2, 1)
    
    if overall_risk <= 3:
        risk_level = "LOW"
    elif overall_risk <= 6:
        risk_level = "MODERATE"
    else:
        risk_level = "HIGH"
    
    route_data = fetch_route_distance(
        origin_coords=(77.5946, 12.9716),
        destination_coords=(80.2707, 13.0827),
        origin_name="Bengaluru",
        destination_name="Chennai"
    )

    summary = {
        "city": latest_weather["city"],
        "weather_condition": latest_weather["weather_condition"],
        "weather_risk_score": latest_weather["weather_risk"],
        "base_currency": latest_exchange["base_currency"],
        "inr_rate": latest_exchange["inr"],
        "forex_risk_score": latest_exchange["forex_risk"],
        "overall_risk_score": overall_risk,
        "risk_level": risk_level,
        "route_origin": route_data["origin"] if route_data else "N/A",
        "route_destination": route_data["destination"] if route_data else "N/A",
        "route_distance_km": route_data["distance_km"] if route_data else "N/A",
        "route_duration_min": route_data["duration_minutes"] if route_data else "N/A"
    }
    
    return summary


import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_style("whitegrid")


def plot_temperature_trend(weather_df, save_path="reports/temperature_trend.png"):
    """Plots temperature over time."""
    os.makedirs("reports", exist_ok=True)
    
    weather_df["fetched_at"] = pd.to_datetime(weather_df["fetched_at"])
    
    plt.figure(figsize=(10, 5))
    plt.plot(weather_df["fetched_at"], weather_df["temperature"], marker="o", color="#E07A5F", linewidth=2)
    plt.title(f"Temperature Trend — {weather_df['city'].iloc[0]}", fontsize=14, fontweight="bold")
    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def plot_exchange_rate_trend(exchange_df, save_path="reports/exchange_rate_trend.png"):
    """Plots INR exchange rate over time."""
    os.makedirs("reports", exist_ok=True)
    
    exchange_df["fetched_at"] = pd.to_datetime(exchange_df["fetched_at"])
    
    plt.figure(figsize=(10, 5))
    plt.plot(exchange_df["fetched_at"], exchange_df["inr"], marker="o", color="#3D5A80", linewidth=2)
    plt.title("USD to INR Exchange Rate Trend", fontsize=14, fontweight="bold")
    plt.xlabel("Time")
    plt.ylabel("INR per USD")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def plot_risk_breakdown(report, save_path="reports/risk_breakdown.png"):
    """Plots a simple bar chart comparing weather risk vs forex risk."""
    os.makedirs("reports", exist_ok=True)
    
    categories = ["Weather Risk", "Forex Risk", "Overall Risk"]
    scores = [report["weather_risk_score"], report["forex_risk_score"], report["overall_risk_score"]]
    colors = ["#E07A5F", "#3D5A80", "#81B29A"]
    
    plt.figure(figsize=(8, 5))
    bars = plt.bar(categories, scores, color=colors)
    plt.title("Supply Chain Risk Breakdown", fontsize=14, fontweight="bold")
    plt.ylabel("Risk Score (0-10)")
    plt.ylim(0, 10)
    
    for bar, score in zip(bars, scores):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, str(score), ha="center", fontweight="bold")
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")

if __name__ == "__main__":
    weather_df = load_weather_data()
    exchange_df = load_exchange_data()
    
    report = generate_risk_report()
    print("\n=== SUPPLY CHAIN RISK REPORT ===")
    for key, value in report.items():
        print(f"{key}: {value}")
    
    plot_temperature_trend(weather_df)
    plot_exchange_rate_trend(exchange_df)
    plot_risk_breakdown(report)