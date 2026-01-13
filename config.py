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
SOCRATA_DATASET_ID = os.getenv("SOCRATA_DATASET_ID", "az4n-8mr2")  # FMCSA Company Census File
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

# Scheduler Configuration
MODE = os.getenv("MODE", "production").lower()  # "test" or "production"

# Test interval in seconds - must be a positive number
# Supports mathematical expressions like "60*1", "300", "60*5", etc.
def safe_eval_interval(value, default=300):
    """Safely evaluate TEST_INTERVAL_SECONDS, supporting expressions like 60*1"""
    if not value:
        return default
    
    try:
        # First try direct integer conversion
        return int(value)
    except ValueError:
        # If that fails, try evaluating as mathematical expression
        try:
            # Only allow numbers, operators, spaces, and parentheses for safety
            allowed_chars = set('0123456789+-*/(). ')
            if all(c in allowed_chars for c in value):
                result = eval(value)
                result_int = int(result)
                if result_int <= 0:
                    raise ValueError("Result must be positive")
                return result_int
            else:
                raise ValueError("Invalid characters in expression")
        except (ValueError, TypeError, SyntaxError, ZeroDivisionError):
            return default

try:
    test_interval_str = os.getenv("TEST_INTERVAL_SECONDS", "300")
    TEST_INTERVAL_SECONDS = safe_eval_interval(test_interval_str, 300)
    if TEST_INTERVAL_SECONDS <= 0:
        TEST_INTERVAL_SECONDS = 300
except Exception:
    # Default to 300 seconds (5 minutes) if invalid
    TEST_INTERVAL_SECONDS = 300

# Production cron schedule - must be valid hour (0-23) and minute (0-59)
try:
    PRODUCTION_CRON_HOUR = int(os.getenv("PRODUCTION_CRON_HOUR", "2"))
    if not (0 <= PRODUCTION_CRON_HOUR <= 23):
        raise ValueError("PRODUCTION_CRON_HOUR must be between 0 and 23")
except (ValueError, TypeError):
    PRODUCTION_CRON_HOUR = 2  # Default: 2 AM UTC

try:
    PRODUCTION_CRON_MINUTE = int(os.getenv("PRODUCTION_CRON_MINUTE", "0"))
    if not (0 <= PRODUCTION_CRON_MINUTE <= 59):
        raise ValueError("PRODUCTION_CRON_MINUTE must be between 0 and 59")
except (ValueError, TypeError):
    PRODUCTION_CRON_MINUTE = 0  # Default: 0 minutes

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
