import os

from dotenv import load_dotenv


load_dotenv()

class Config:
    SCRAPE_INTERVAL_SECONDS = int(os.environ.get("SCRAPE_INTERVAL_SECONDS", "5"))
    UPDATE_INTERVAL_SECONDS = int(os.environ.get("UPDATE_INTERVAL_SECONDS", "5"))
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "./fsched-filebase")
    MANAGER_HOST = os.environ.get("MANAGER_HOST", "http://localhost:8100")
    SCHEDULER_HOST = os.environ.get("SCHEDULER_HOST", "http://localhost:8000")
    PREDICTOR_HOST = os.environ.get("PREDICTOR_HOST", "http://localhost:8300")
    DB_CSV_PATH = os.environ.get("DB_CSV_PATH", "./data.csv")
    COS_COUNT = int(os.environ.get("COS_COUNT", "10"))
