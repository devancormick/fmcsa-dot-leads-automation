"""
Configuration management for FMCSA DOT Leads Automation
"""
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Socrata API Configuration
SOCRATA_DOMAIN = os.getenv("SOCRATA_DOMAIN", "data.transportation.gov")
SOCRATA_DATASET_ID = os.getenv("SOCRATA_DATASET_ID", "49yn-d2k2")  # FMCSA Company Census File
SOCRATA_APP_TOKEN = os.getenv("SOCRATA_APP_TOKEN", "")

# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_PATH = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "service_account.json")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")

# Email Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "")
EMAIL_TO = os.getenv("EMAIL_TO", "").split(",") if os.getenv("EMAIL_TO") else []

# Output Configuration
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output/csv")
DATE_FORMAT = "%Y-%m-%d"

# Required Fields
REQUIRED_FIELDS = [
    "dot_number",
    "legal_name",
    "dba_name",
    "phy_city",
    "phy_state",
    "phy_zip",
    "telephone",
    "add_date",
    "date_pulled"
]
