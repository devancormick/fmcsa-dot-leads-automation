#!/usr/bin/env python3
"""
Main entry point for FMCSA DOT Leads Automation
"""
import sys
import logging
from datetime import datetime, timedelta
from typing import Optional
from config import DATE_FORMAT
from dot_fetcher import DOTFetcher
from data_processor import DataProcessor
from google_sheets_handler import GoogleSheetsHandler
from csv_handler import CSVHandler
from email_handler import EmailHandler

logger = logging.getLogger(__name__)


def main(target_date: Optional[str] = None):
    """
    Main function to fetch, process, and deliver DOT leads
    
    Args:
        target_date: Optional date in YYYY-MM-DD format. If None, uses yesterday's date.
    """
    dot_fetcher = None
    try:
        # Determine target date
        if target_date is None:
            target_date = (datetime.now() - timedelta(days=1)).strftime(DATE_FORMAT)
        
        logger.info(f"Starting DOT Leads Automation for date: {target_date}")
        
        # Step 1: Fetch new DOT records
        logger.info("Step 1: Fetching DOT records from Socrata API...")
        dot_fetcher = DOTFetcher()
        raw_records = dot_fetcher.fetch_new_dots(target_date)
        
        if not raw_records:
            logger.info(f"No new DOT records found for {target_date}")
            return
        
        logger.info(f"Fetched {len(raw_records)} raw records")
        
        # Step 2: Process records (extract fields, deduplicate)
        logger.info("Step 2: Processing and deduplicating records...")
        processed_records = DataProcessor.process_records(raw_records)
        
        logger.info(f"Processed {len(processed_records)} unique records")
        
        if not processed_records:
            logger.info("No records after processing")
            return
        
        # Step 3: Save to CSV
        logger.info("Step 3: Saving records to CSV...")
        csv_handler = CSVHandler()
        csv_path = csv_handler.save_records(processed_records, target_date)
        
        # Step 4: Upload to Google Sheets
        logger.info("Step 4: Creating Google Sheet tab...")
        sheets_handler = GoogleSheetsHandler()
        sheet_url = sheets_handler.create_daily_tab(target_date, processed_records)
        
        # Step 5: Send email notification
        logger.info("Step 5: Sending email notification...")
        email_handler = EmailHandler()
        email_handler.send_daily_report(
            date=target_date,
            record_count=len(processed_records),
            sheet_url=sheet_url,
            csv_path=csv_path
        )
        
        logger.info(f"Successfully completed DOT Leads Automation for {target_date}")
        logger.info(f"Records processed: {len(processed_records)}")
        logger.info(f"Google Sheet: {sheet_url}")
        logger.info(f"CSV file: {csv_path}")
        
    except Exception as e:
        error_msg = f"Error in DOT Leads Automation: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # Send error notification
        try:
            email_handler = EmailHandler()
            email_handler.send_error_notification(error_msg)
        except Exception as email_error:
            logger.error(f"Failed to send error notification: {str(email_error)}")
        
        sys.exit(1)
    
    finally:
        if dot_fetcher:
            dot_fetcher.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="FMCSA DOT Leads Automation")
    parser.add_argument(
        "--date",
        type=str,
        help="Target date in YYYY-MM-DD format (default: yesterday)",
        default=None
    )
    
    args = parser.parse_args()
    main(target_date=args.date)
