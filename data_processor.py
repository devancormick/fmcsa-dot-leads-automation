"""
Data processing and formatting for DOT records
"""
import logging
from datetime import datetime
from typing import List, Dict
from utils import format_date, deduplicate_by_dot_number
from config import DATE_FORMAT, REQUIRED_FIELDS

logger = logging.getLogger(__name__)


class DataProcessor:
    """Processes and formats DOT records"""
    
    @staticmethod
    def extract_required_fields(records: List[Dict]) -> List[Dict]:
        """
        Extract and format required fields from raw DOT records
        
        Args:
            records: Raw records from Socrata API
        
        Returns:
            List of formatted records with required fields
        """
        formatted_records = []
        date_pulled = datetime.now().strftime(DATE_FORMAT)
        
        for record in records:
            try:
                formatted_record = {
                    "dot_number": str(record.get("dot_number", "")).strip(),
                    "legal_name": str(record.get("legal_name", "")).strip(),
                    "dba_name": str(record.get("dba_name", "")).strip(),
                    "phy_city": str(record.get("phy_city", "")).strip(),
                    "phy_state": str(record.get("phy_state", "")).strip(),
                    "phy_zip": str(record.get("phy_zip", "")).strip(),
                    "telephone": str(record.get("telephone", "")).strip(),
                    "add_date": format_date(str(record.get("add_date", ""))),
                    "date_pulled": date_pulled
                }
                
                # Only include records with DOT number
                if formatted_record["dot_number"]:
                    formatted_records.append(formatted_record)
                    
            except Exception as e:
                logger.warning(f"Error processing record: {record}. Error: {str(e)}")
                continue
        
        logger.info(f"Extracted {len(formatted_records)} records with required fields")
        return formatted_records
    
    @staticmethod
    def process_records(records: List[Dict]) -> List[Dict]:
        """
        Process records: extract fields, deduplicate, and format
        
        Args:
            records: Raw records from API
        
        Returns:
            Processed and deduplicated records
        """
        # Extract required fields
        formatted = DataProcessor.extract_required_fields(records)
        
        # Deduplicate by DOT number
        unique = deduplicate_by_dot_number(formatted)
        
        return unique
    
    @staticmethod
    def get_column_headers() -> List[str]:
        """Get column headers for output"""
        return [
            "DOT Number",
            "Legal Company Name",
            "DBA Name",
            "City",
            "State",
            "ZIP Code",
            "Phone",
            "ADD_DATE",
            "Date Pulled"
        ]
    
    @staticmethod
    def format_for_output(records: List[Dict]) -> List[List]:
        """
        Format records for CSV/Sheets output
        
        Args:
            records: Processed records
        
        Returns:
            List of lists (rows) for output
        """
        headers = DataProcessor.get_column_headers()
        rows = [headers]
        
        for record in records:
            row = [
                record.get("dot_number", ""),
                record.get("legal_name", ""),
                record.get("dba_name", ""),
                record.get("phy_city", ""),
                record.get("phy_state", ""),
                record.get("phy_zip", ""),
                record.get("telephone", ""),
                record.get("add_date", ""),
                record.get("date_pulled", "")
            ]
            rows.append(row)
        
        return rows
