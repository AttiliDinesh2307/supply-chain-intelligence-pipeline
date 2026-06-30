import logging
import os
from datetime import datetime

os.makedirs("logs", exist_ok=True)

log_filename = f"logs/pipeline_{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()  # also prints to terminal, like before
    ]
)

def get_logger(name):
    return logging.getLogger(name)