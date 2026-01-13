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
    
    def send_daily_report(self, date: str, record_count: int, sheet_url: str, csv_path: Optional[str] = None) -> bool:
        """
        Send daily report email with Google Sheet link and CSV attachment
        
        Args:
            date: Date string in YYYY-MM-DD format
            record_count: Number of records found
            sheet_url: URL to the Google Sheet
            csv_path: Path to CSV file to attach
        
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
            msg['Subject'] = f"Daily DOT Leads Report - {date}"
            
            # Create email body
            body = f"""
Daily FMCSA DOT Leads Report

Date: {date}
New DOT Numbers Found: {record_count}

Google Sheet Link:
{sheet_url}

This report contains all newly registered USDOT numbers for {date}.

---
This is an automated message from the FMCSA DOT Leads Automation system.
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach CSV file if provided
            if csv_path:
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
                    logger.info(f"Attached CSV file: {csv_path}")
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
