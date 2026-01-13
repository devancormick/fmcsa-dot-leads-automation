#!/usr/bin/env python3
"""
Scheduler script that runs the DOT leads automation on a schedule
This keeps the container running and executes tasks at specified intervals
"""
import time
import logging
import subprocess
import sys
from datetime import datetime, timedelta
from config import DATE_FORMAT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def run_automation(target_date=None):
    """Run the main automation script"""
    try:
        logger.info(f"Starting automation for date: {target_date or 'yesterday'}")
        
        # Build command
        cmd = [sys.executable, 'main.py']
        if target_date:
            cmd.extend(['--date', target_date])
        
        # Run the script
        result = subprocess.run(
            cmd,
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("Automation completed successfully")
        else:
            logger.error(f"Automation failed with exit code: {result.returncode}")
        
        return result.returncode == 0
        
    except Exception as e:
        logger.error(f"Error running automation: {str(e)}", exc_info=True)
        return False


def calculate_next_run_time():
    """Calculate the next run time (2:00 AM daily)"""
    now = datetime.now()
    target_time = now.replace(hour=2, minute=0, second=0, microsecond=0)
    
    # If it's already past 2 AM today, schedule for tomorrow
    if now >= target_time:
        target_time += timedelta(days=1)
    
    return target_time


def scheduler_loop():
    """Main scheduler loop that runs continuously"""
    logger.info("=" * 60)
    logger.info("FMCSA DOT Leads Automation Scheduler Started")
    logger.info("=" * 60)
    logger.info("Scheduler will run the automation daily at 2:00 AM")
    logger.info("Container will continue running until stopped")
    logger.info("=" * 60)
    
    # Run immediately on startup (optional - can be disabled)
    run_on_startup = True
    
    if run_on_startup:
        logger.info("Running initial execution on startup...")
        run_automation()
        logger.info("Initial execution completed")
    
    # Main scheduling loop
    while True:
        try:
            # Calculate next run time
            next_run = calculate_next_run_time()
            wait_seconds = (next_run - datetime.now()).total_seconds()
            
            logger.info(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"Waiting {wait_seconds/3600:.2f} hours until next run...")
            
            # Wait until next run time
            time.sleep(wait_seconds)
            
            # Run the automation
            logger.info("=" * 60)
            logger.info(f"Executing scheduled run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 60)
            
            run_automation()
            
            logger.info("Scheduled run completed. Waiting for next scheduled time...")
            
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in scheduler loop: {str(e)}", exc_info=True)
            # Wait a bit before retrying
            logger.info("Waiting 1 hour before retrying...")
            time.sleep(3600)


if __name__ == "__main__":
    scheduler_loop()
