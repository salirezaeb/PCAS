import os

from dotenv import load_dotenv


load_dotenv()

class Config:
    SCRAPE_INTERVAL_SECONDS = int(os.environ.get("SCRAPE_INTERVAL_SECONDS", "15"))
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "./fsched-filebase")
