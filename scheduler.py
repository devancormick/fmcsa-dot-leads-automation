#!/usr/bin/env python3
"""
Scheduler script that runs the DOT leads automation on a schedule
This keeps the container running and executes tasks at specified intervals
"""
import time
import logging
import subprocess
import sys
import os
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


def calculate_next_run_time(test_mode=False, test_interval_minutes=5):
    """
    Calculate the next run time
    
    Args:
        test_mode: If True, use test interval (5 minutes). If False, use daily schedule (2 AM)
        test_interval_minutes: Interval in minutes for test mode (default: 5)
    
    Returns:
        datetime: Next run time
    """
    now = datetime.now()
    
    if test_mode:
        # Test mode: run every N minutes
        next_run = now + timedelta(minutes=test_interval_minutes)
        return next_run
    else:
        # Production mode: run daily at 2:00 AM
        target_time = now.replace(hour=2, minute=0, second=0, microsecond=0)
        
        # If it's already past 2 AM today, schedule for tomorrow
        if now >= target_time:
            target_time += timedelta(days=1)
        
        return target_time


def scheduler_loop(test_mode=False, test_interval_minutes=5):
    """
    Main scheduler loop that runs continuously
    
    Args:
        test_mode: If True, run every N minutes. If False, run daily at 2 AM
        test_interval_minutes: Interval in minutes for test mode (default: 5)
    """
    logger.info("=" * 60)
    logger.info("FMCSA DOT Leads Automation Scheduler Started")
    logger.info("=" * 60)
    
    if test_mode:
        logger.info(f"🧪 TEST MODE: Running every {test_interval_minutes} minutes")
        logger.info("⚠️  WARNING: This is for testing only!")
    else:
        logger.info("📅 PRODUCTION MODE: Running daily at 2:00 AM UTC")
    
    logger.info("Container will continue running until stopped")
    logger.info("=" * 60)
    
    # Run immediately on startup
    run_on_startup = True
    
    if run_on_startup:
        logger.info("Running initial execution on startup...")
        run_automation()
        logger.info("Initial execution completed")
    
    # Main scheduling loop
    while True:
        try:
            # Calculate next run time
            next_run = calculate_next_run_time(test_mode, test_interval_minutes)
            wait_seconds = (next_run - datetime.now()).total_seconds()
            
            if test_mode:
                logger.info(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"Waiting {wait_seconds/60:.1f} minutes until next run...")
            else:
                logger.info(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"Waiting {wait_seconds/3600:.2f} hours until next run...")
            
            # Wait until next run time
            time.sleep(wait_seconds)
            
            # Run the automation
            logger.info("=" * 60)
            logger.info(f"Executing scheduled run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            if test_mode:
                logger.info("🧪 TEST MODE ACTIVE")
            logger.info("=" * 60)
            
            run_automation()
            
            logger.info("Scheduled run completed. Waiting for next scheduled time...")
            
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in scheduler loop: {str(e)}", exc_info=True)
            # Wait a bit before retrying
            wait_time = 60 if test_mode else 3600  # 1 minute in test mode, 1 hour in production
            logger.info(f"Waiting {wait_time/60 if test_mode else wait_time/3600:.1f} {'minutes' if test_mode else 'hours'} before retrying...")
            time.sleep(wait_time)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="FMCSA DOT Leads Automation Scheduler")
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Enable test mode (runs every 5 minutes instead of daily)"
    )
    parser.add_argument(
        "--test-interval",
        type=int,
        default=5,
        help="Interval in minutes for test mode (default: 5)"
    )
    
    args = parser.parse_args()
    
    # Also check environment variable
    test_mode = args.test_mode or os.getenv("TEST_MODE", "").lower() in ("true", "1", "yes")
    test_interval = int(os.getenv("TEST_INTERVAL_MINUTES", args.test_interval))
    
    scheduler_loop(test_mode=test_mode, test_interval_minutes=test_interval)
