"""
Configuration file for the report generation system
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

# ChromaDB Configuration
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "sales_marketing_data"

# AutoGen Configuration
AUTOGEN_CONFIG = {
    "config_list": [
        {
            "model": "gpt-4o-mini",
            "api_key": OPENAI_API_KEY,
        }
    ],
    "temperature": 0.7,
}

# Email Configuration
GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "")

# Scheduler Configuration
SCHEDULE_TIME = "09:00"  # 9 AM IST
TIMEZONE = "Asia/Kolkata"

# Telegram Configuration
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "20250063"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "9c47ded49531aaa11a3fb6be0e0b1236")
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE", "+919176072251")

