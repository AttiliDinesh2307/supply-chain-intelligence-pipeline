# Supply Chain Intelligence Pipeline

An automated, API-driven data pipeline that monitors live weather, currency, country, and logistics-routing data to generate a real-time **Supply Chain Risk Score**, compile it into a polished PDF report, and (optionally) deliver it via email — on a schedule, with zero manual intervention.

This is a follow-up project to my earlier [Supply Chain Analytics Pipeline](https://github.com/AttiliDinesh2307/supply-chain-analytics-pipeline), which focused on static dataset analysis. This project focuses on **live data ingestion, automation, and reporting** — the operational side of supply chain analytics.

---

## What it does

1. **Fetches live data** from four external APIs:
   - Weather conditions (OpenWeatherMap)
   - Currency exchange rates (ExchangeRate-API)
   - Country/region reference data (REST Countries)
   - Driving distance and duration between two cities (OSRM routing engine)
2. **Stores every fetch** in a local SQLite database with timestamps, building a historical dataset over time.
3. **Calculates a custom Supply Chain Risk Score** — a rule-based metric combining weather severity (wind speed, extreme temperature, severe conditions) and currency volatility (percentage change in exchange rate), classified as LOW / MODERATE / HIGH.
4. **Generates trend charts** (temperature over time, exchange rate over time, risk breakdown) using pandas, matplotlib, and seaborn.
5. **Compiles a multi-page PDF report** combining the risk summary, route data, and all charts into a single polished document.
6. **(Optional) Emails the report automatically** to a configured recipient.
7. **(Optional) Runs on a schedule**, so the entire pipeline executes daily without manual triggering.

---

## Tech stack

| Component | Tool |
|---|---|
| API requests | `requests` |
| Data storage | `sqlite3` |
| Data analysis | `pandas` |
| Visualization | `matplotlib`, `seaborn` |
| PDF generation | `fpdf2` |
| Email delivery | `smtplib` |
| Scheduling | `schedule` |
| Config management | `python-dotenv` |
| Logging | Python's built-in `logging` module |

---

## Project structure

```
supply-chain-intelligence/
├── main.py                  # Entry point — runs the full pipeline
├── config.py                 # Configuration constants
├── data_fetch.py              # API integration (weather, forex, country, routing)
├── db_handler.py              # SQLite table creation and insert functions
├── analyzer.py                # Risk scoring logic and chart generation
├── report_generator.py        # PDF report compilation
├── email_sender.py            # Automated email delivery (SMTP)
├── scheduler.py                # Daily automation
├── logs/                       # Runtime logs (excluded from repo)
├── reports/                    # Generated charts and PDFs (excluded from repo)
└── .env                        # API keys and credentials (excluded from repo)
```

---

## The Risk Score, explained

Rather than just displaying raw numbers, the pipeline translates live conditions into a **business-relevant risk signal** — the kind of decision-support metric a logistics or operations team would actually use.

**Weather Risk (0–10):** scored from wind speed, temperature extremes, and presence of severe weather keywords (storm, heavy rain, snow) — all factors that affect delivery reliability and warehouse operations.

**Forex Risk (0–10):** scored from the percentage change in the INR exchange rate between consecutive fetches — a proxy for import/export cost volatility.

**Overall Risk Score** is the average of the two, mapped to a LOW / MODERATE / HIGH classification.

This is intentionally a transparent, rule-based model — every threshold is explainable, not a black box. The scoring logic lives in `analyzer.py` and can be tuned as needed.

---

## Engineering notes

- **Graceful degradation:** all API calls are wrapped in try/except blocks. If one source fails (for example, a third-party fuel-price API with limited uptime guarantees), the pipeline logs the failure and continues — it never crashes due to one unreliable dependency.
- **Parameterized SQL queries** are used throughout to prevent SQL injection, even though this is a local, single-user database.
- **Environment variables** (`.env`, gitignored) keep all API keys and email credentials out of version control.
- **Historical data accumulation:** since every fetch is timestamped and stored, trend charts become more meaningful the longer the pipeline runs — this is designed for sustained, scheduled operation rather than one-off execution.

---

## Setup

```bash
# Clone the repo
git clone https://github.com/AttiliDinesh2307/supply-chain-intelligence-pipeline.git
cd supply-chain-intelligence-pipeline

# Create environment
conda create -n sci_pipeline python=3.10
conda activate sci_pipeline
pip install requests pandas matplotlib seaborn fpdf2 python-dotenv schedule

# Add your API keys
cp .env.example .env  # then fill in your own keys

# Run the pipeline
python main.py
```

### Required API keys (all free tier)

| Service | Sign up |
|---|---|
| OpenWeatherMap | [openweathermap.org/api](https://openweathermap.org/api) |
| ExchangeRate-API | [exchangerate-api.com](https://www.exchangerate-api.com) |
| REST Countries v5 | [restcountries.com/sign-up](https://restcountries.com/sign-up) |

Routing data (OSRM) requires no API key.

---

## Sample output

The pipeline generates a dated PDF report (`reports/SCM_Report_YYYY-MM-DD.pdf`) containing:
- A risk summary (city, weather condition, scores, risk level)
- Route distance and estimated travel time between two configured cities
- Temperature trend chart
- Exchange rate trend chart
- Risk breakdown bar chart

---

## Author

**Dinesh Attili**
MBA, Business Analytics & Operations — GITAM University
[LinkedIn](https://linkedin.com) · [GitHub](https://github.com/AttiliDinesh2307)