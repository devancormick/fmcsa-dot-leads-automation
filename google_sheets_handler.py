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
    
    def create_daily_tab(self, date: str, records: List[Dict]) -> str:
        """
        Create a new tab for the given date and populate with records
        
        Args:
            date: Date string in YYYY-MM-DD format
            records: Processed DOT records
        
        Returns:
            URL to the new sheet tab
        """
        if not self.sheet:
            raise ValueError("Google Sheet not initialized")
        
        tab_name = f"DOT Leads {date}"
        
        try:
            # Check if tab already exists
            try:
                worksheet = self.sheet.worksheet(tab_name)
                logger.info(f"Tab '{tab_name}' already exists, clearing it")
                worksheet.clear()
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
            
            # Format header row (bold)
            worksheet.format('A1:I1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })
            
            # Auto-resize columns
            worksheet.columns_auto_resize(0, 9)
            
            logger.info(f"Populated tab '{tab_name}' with {len(records)} records")
            
            # Return URL to the worksheet
            sheet_url = f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/edit#gid={worksheet.id}"
            return sheet_url
            
        except Exception as e:
            logger.error(f"Error creating/updating tab '{tab_name}': {str(e)}")
            raise
    
    def get_sheet_url(self) -> str:
        """Get the base URL of the Google Sheet"""
        return f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/edit"
