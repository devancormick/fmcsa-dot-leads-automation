"""
Email notification handler
"""
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import List, Optional
from config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM, EMAIL_TO

logger = logging.getLogger(__name__)


class EmailHandler:
    """Handles email notifications"""
    
    def __init__(self):
        """Initialize email handler"""
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.smtp_username = SMTP_USERNAME
        self.smtp_password = SMTP_PASSWORD
        self.email_from = EMAIL_FROM or SMTP_USERNAME
        self.email_to = EMAIL_TO
    
    def send_daily_report(self, date: str, new_record_count: int, total_record_count: int, 
                         existing_count: int, sheet_url: str, csv_path: Optional[str] = None) -> bool:
        """
        Send daily report email with Google Sheet link and CSV attachment
        Only includes information about NEW records
        
        Args:
            date: Date string in YYYY-MM-DD format
            new_record_count: Number of NEW records added
            total_record_count: Total number of records found for this date
            existing_count: Number of existing records in sheet
            sheet_url: URL to the Google Sheet
            csv_path: Path to CSV file to attach (should contain only new records)
        
        Returns:
            True if email sent successfully
        """
        if not self.email_to:
            logger.warning("No email recipients configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = ', '.join(self.email_to)
            
            # Subject line indicates if there are new records
            if new_record_count > 0:
                msg['Subject'] = f"Daily DOT Leads Report - {date} ({new_record_count} NEW records)"
            else:
                msg['Subject'] = f"Daily DOT Leads Report - {date} (No new records)"
            
            # Create email body
            body = f"""
Daily FMCSA DOT Leads Report

Date: {date}

Summary:
- Total records found for {date}: {total_record_count}
- Existing records in sheet: {existing_count}
- NEW records added: {new_record_count}

"""
            
            if new_record_count > 0:
                body += f"""
✅ {new_record_count} new DOT number(s) have been added to the Google Sheet.

Google Sheet Link:
{sheet_url}

The CSV attachment contains only the NEW records that were added today.
"""
            else:
                body += f"""
ℹ️  No new records found. All {total_record_count} records for {date} already exist in the sheet.

Google Sheet Link:
{sheet_url}
"""
            
            body += f"""
---
This is an automated message from the FMCSA DOT Leads Automation system.
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach CSV file if provided and contains new records
            if csv_path and new_record_count > 0:
                try:
                    with open(csv_path, 'rb') as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                    
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(csv_path)}'
                    )
                    msg.attach(part)
                    logger.info(f"Attached CSV file with {new_record_count} new records: {csv_path}")
                except Exception as e:
                    logger.warning(f"Could not attach CSV file: {str(e)}")
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Daily report email sent successfully to {', '.join(self.email_to)}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise
    
    def send_error_notification(self, error_message: str) -> bool:
        """
        Send error notification email
        
        Args:
            error_message: Error message to send
        
        Returns:
            True if email sent successfully
        """
        if not self.email_to:
            logger.warning("No email recipients configured for error notifications")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = ', '.join(self.email_to)
            msg['Subject'] = "ERROR: FMCSA DOT Leads Automation Failed"
            
            body = f"""
The FMCSA DOT Leads Automation job has failed.

Error Details:
{error_message}

Please check the logs and system status.

---
This is an automated error notification from the FMCSA DOT Leads Automation system.
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Error notification email sent to {', '.join(self.email_to)}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending error notification email: {str(e)}")
            return False
