import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # AO3 Credentials
    AO3_USERNAME = os.getenv("AO3_USERNAME")
    AO3_PASSWORD = os.getenv("AO3_PASSWORD")

    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

    # Search Configuration - только фандомы, теги убраны
    SEARCH_FANDOMS = ["Икар - Круглов/Макуни | Icarus - Kruglov/Makuni"]
    # "Russian Musical Theatre RPF"

    # Crawler Settings
    REQUEST_DELAY = int(os.getenv("REQUEST_DELAY", "20"))
    MAX_WORKS_PER_RUN = int(os.getenv("MAX_WORKS_PER_RUN", "10"))

    # Database file for tracking posted works
    DATABASE_FILE = "posted_works.db"

    # Tag parsing configuration
    WARNING_TAGS = [
        "Choose Not To Use Archive Warnings",
        "Creator Chose Not To Use Archive Warnings",
        "No Archive Warnings Apply",
        "Graphic Depictions Of Violence",
        "Major Character Death",
        "Rape/Non-Con",
        "Underage",
    ]

    # Tags with "/" that should NOT go to relationships (exceptions)
    RELATIONSHIP_EXCEPTIONS = ["Rape/Non", "Hurt/Comfort", "Parent/Child"]
