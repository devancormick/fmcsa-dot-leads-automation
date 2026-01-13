"""
CSV file handler for DOT leads backup
"""
import csv
import logging
import os
from datetime import datetime
from typing import List, Dict
from config import OUTPUT_DIR, DATE_FORMAT
from utils import ensure_output_directory
from data_processor import DataProcessor

logger = logging.getLogger(__name__)


class CSVHandler:
    """Handles CSV file operations"""
    
    def __init__(self):
        """Initialize CSV handler"""
        ensure_output_directory(OUTPUT_DIR)
    
    def save_records(self, records: List[Dict], date: str) -> str:
        """
        Save records to CSV file
        
        Args:
            records: Processed DOT records
            date: Date string in YYYY-MM-DD format
        
        Returns:
            Path to the created CSV file
        """
        filename = f"dot_leads_{date}.csv"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        try:
            # Format data for output
            rows = DataProcessor.format_for_output(records)
            
            # Write to CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(rows)
            
            logger.info(f"Saved {len(records)} records to CSV: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving CSV file: {str(e)}")
            raise
