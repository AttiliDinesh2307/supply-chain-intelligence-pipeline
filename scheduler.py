import schedule
import time
from data_fetch import (
    fetch_weather,
    fetch_exchange_rate,
    fetch_country_data,
    fetch_fuel_prices,
    fetch_route_distance
)
from db_handler import create_tables, insert_weather, insert_exchange_rate, insert_country_data
from analyzer import generate_risk_report
from report_generator import generate_pdf_report
from email_sender import send_report_email
from logger_config import get_logger

logger = get_logger(__name__)


def run_pipeline():
    """
    Runs the complete pipeline: fetch -> store -> analyze -> PDF -> email.
    """
    logger.info("=== Scheduled pipeline run started ===")

    try:
        create_tables()

        weather_result = fetch_weather("Bengaluru")
        insert_weather(weather_result)

        exchange_result = fetch_exchange_rate("USD")
        insert_exchange_rate(exchange_result)

        country_result = fetch_country_data("India")
        insert_country_data(country_result)

        # Fuel prices fetched but not stored (unreliable source, used for reference only)
        fetch_fuel_prices("Karnataka", "Bengaluru")

        # Generate the risk report (this internally also calls fetch_route_distance)
        report = generate_risk_report()
        logger.info(f"Risk report generated: {report['risk_level']} risk level")

        # Generate the PDF
        pdf_path = generate_pdf_report(report)
        logger.info(f"PDF report generated at {pdf_path}")

        # Send the email (will skip gracefully if credentials are missing)
        send_report_email(pdf_path)

        logger.info("=== Scheduled pipeline run completed successfully ===")

    except Exception as e:
        logger.error(f"Pipeline run failed with an unexpected error: {e}")


def start_scheduler(run_time="08:00"):
    """
    Schedules the pipeline to run daily at the specified time (24-hour format).
    """
    schedule.every().day.at(run_time).do(run_pipeline)
    logger.info(f"Scheduler started. Pipeline will run daily at {run_time}.")

    print(f"Scheduler is running. Pipeline will execute daily at {run_time}.")
    print("Press Ctrl+C to stop.")

    while True:
        schedule.run_pending()
        time.sleep(60)  # check every 60 seconds


if __name__ == "__main__":
    # Run once immediately to confirm everything works
    print("Running pipeline once immediately as a test...")
    run_pipeline()

    # Then start the daily schedule
    start_scheduler(run_time="08:00")