"""
Utility functions for FMCSA DOT Leads Automation
"""
import logging
import os
from datetime import datetime
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dot_leads_automation.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def ensure_output_directory(output_dir: str) -> None:
    """Ensure output directory exists"""
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Output directory ensured: {output_dir}")


def format_date(date_str: str, input_format: str = "%Y-%m-%dT%H:%M:%S.000") -> str:
    """Format date string to standard format"""
    try:
        dt = datetime.strptime(date_str, input_format)
        return dt.strftime("%Y-%m-%d")
    except (ValueError, AttributeError):
        # Try alternative formats
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except (ValueError, AttributeError):
            logger.warning(f"Could not parse date: {date_str}")
            return date_str


def deduplicate_by_dot_number(records: List[Dict]) -> List[Dict]:
    """Remove duplicate records based on DOT number, keeping the first occurrence"""
    seen = set()
    unique_records = []
    
    for record in records:
        dot_number = record.get("dot_number")
        if dot_number and dot_number not in seen:
            seen.add(dot_number)
            unique_records.append(record)
        elif not dot_number:
            logger.warning(f"Record missing DOT number: {record}")
    
    logger.info(f"Deduplicated {len(records)} records to {len(unique_records)} unique records")
    return unique_records
