"""
Google Sheets integration for DOT leads
"""
import logging
from datetime import datetime
from typing import List, Dict
import gspread
from google.oauth2.service_account import Credentials
from config import GOOGLE_SHEETS_CREDENTIALS_PATH, GOOGLE_SHEET_ID, DATE_FORMAT
from data_processor import DataProcessor

logger = logging.getLogger(__name__)


class GoogleSheetsHandler:
    """Handles Google Sheets operations"""
    
    def __init__(self):
        """Initialize Google Sheets client"""
        try:
            # Authenticate using service account
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            credentials = Credentials.from_service_account_file(
                GOOGLE_SHEETS_CREDENTIALS_PATH,
                scopes=scope
            )
            self.client = gspread.authorize(credentials)
            self.sheet_id = GOOGLE_SHEET_ID
            self.sheet = None
            
            if self.sheet_id:
                self.sheet = self.client.open_by_key(self.sheet_id)
                logger.info(f"Connected to Google Sheet: {self.sheet.title}")
            else:
                logger.warning("No Google Sheet ID configured")
                
        except FileNotFoundError:
            logger.error(f"Service account credentials not found at: {GOOGLE_SHEETS_CREDENTIALS_PATH}")
            raise
        except Exception as e:
            logger.error(f"Error initializing Google Sheets client: {str(e)}")
            raise
    
    def get_existing_dot_numbers(self, worksheet) -> set:
        """
        Get existing DOT numbers from the worksheet
        
        Args:
            worksheet: Google Sheets worksheet object
        
        Returns:
            Set of existing DOT numbers
        """
        try:
            # Get all values from the sheet (skip header row)
            all_values = worksheet.get_all_values()
            if len(all_values) <= 1:
                return set()
            
            # Extract DOT numbers from first column (skip header)
            existing_dots = set()
            for row in all_values[1:]:  # Skip header row
                if row and row[0]:  # Check if row has data and DOT number exists
                    dot_number = str(row[0]).strip()
                    if dot_number:
                        existing_dots.add(dot_number)
            
            logger.info(f"Found {len(existing_dots)} existing DOT numbers in sheet")
            return existing_dots
            
        except Exception as e:
            logger.warning(f"Error reading existing data: {str(e)}. Treating as empty sheet.")
            return set()
    
    def create_daily_tab(self, date: str, records: List[Dict]) -> tuple:
        """
        Create or update a tab for the given date and add only new records
        
        Args:
            date: Date string in YYYY-MM-DD format
            records: Processed DOT records
        
        Returns:
            Tuple of (URL to the sheet tab, new_records list, existing_count)
        """
        if not self.sheet:
            raise ValueError("Google Sheet not initialized")
        
        tab_name = f"DOT Leads {date}"
        
        try:
            # Check if tab already exists
            try:
                worksheet = self.sheet.worksheet(tab_name)
                logger.info(f"Tab '{tab_name}' already exists")
                
                # Get existing DOT numbers
                existing_dots = self.get_existing_dot_numbers(worksheet)
                
                # Filter out records that already exist
                new_records = []
                for record in records:
                    dot_number = str(record.get("dot_number", "")).strip()
                    if dot_number and dot_number not in existing_dots:
                        new_records.append(record)
                
                logger.info(f"Found {len(new_records)} new records out of {len(records)} total")
                
                if new_records:
                    # Get current data to append new records
                    all_values = worksheet.get_all_values()
                    current_row_count = len(all_values)
                    
                    # Format new records for output (without headers)
                    new_rows = DataProcessor.format_for_output(new_records)
                    # Remove header row since we're appending
                    new_rows = new_rows[1:]
                    
                    # Append new records
                    if new_rows:
                        worksheet.append_rows(new_rows)
                        logger.info(f"Added {len(new_rows)} new records to existing tab")
                else:
                    logger.info("No new records to add - all records already exist")
                
                existing_count = len(existing_dots)
                
            except gspread.exceptions.WorksheetNotFound:
                # Create new worksheet
                worksheet = self.sheet.add_worksheet(
                    title=tab_name,
                    rows=len(records) + 100,
                    cols=10
                )
                logger.info(f"Created new tab: {tab_name}")
                
                # Format data for output
                rows = DataProcessor.format_for_output(records)
                
                # Write data to sheet
                worksheet.update('A1', rows)
                
                # All records are new for a new tab
                new_records = records
                existing_count = 0
                logger.info(f"Populated new tab '{tab_name}' with {len(records)} records")
            
            # Format header row (bold)
            worksheet.format('A1:I1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })
            
            # Auto-resize columns
            worksheet.columns_auto_resize(0, 9)
            
            # Return URL to the worksheet
            sheet_url = f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/edit#gid={worksheet.id}"
            return sheet_url, new_records, existing_count
            
        except Exception as e:
            logger.error(f"Error creating/updating tab '{tab_name}': {str(e)}")
            raise
    
    def get_sheet_url(self) -> str:
        """Get the base URL of the Google Sheet"""
        return f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/edit"
