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
from config import DATE_FORMAT, MODE, TEST_INTERVAL_SECONDS, PRODUCTION_CRON_HOUR, PRODUCTION_CRON_MINUTE

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


def calculate_next_run_time(test_mode=False, test_interval_seconds=None):
    """
    Calculate the next run time
    
    Args:
        test_mode: If True, use test interval. If False, use daily schedule
        test_interval_seconds: Interval in seconds for test mode (from config if None)
    
    Returns:
        datetime: Next run time
    """
    now = datetime.now()
    
    if test_mode:
        # Test mode: run every N seconds
        interval = test_interval_seconds if test_interval_seconds is not None else TEST_INTERVAL_SECONDS
        next_run = now + timedelta(seconds=interval)
        return next_run
    else:
        # Production mode: run daily at configured time (default: 2:00 AM UTC)
        target_time = now.replace(hour=PRODUCTION_CRON_HOUR, minute=PRODUCTION_CRON_MINUTE, second=0, microsecond=0)
        
        # If it's already past the scheduled time today, schedule for tomorrow
        if now >= target_time:
            target_time += timedelta(days=1)
        
        return target_time


def scheduler_loop(test_mode=None, test_interval_seconds=None):
    """
    Main scheduler loop that runs continuously
    
    Args:
        test_mode: If True, run in test mode. If None, use MODE from config
        test_interval_seconds: Interval in seconds for test mode (from config if None)
    """
    # Use config MODE if test_mode not explicitly provided
    if test_mode is None:
        test_mode = (MODE == "test")
    
    # Use config interval if not provided
    if test_interval_seconds is None:
        test_interval_seconds = TEST_INTERVAL_SECONDS
    
    logger.info("=" * 60)
    logger.info("FMCSA DOT Leads Automation Scheduler Started")
    logger.info("=" * 60)
    
    if test_mode:
        interval_minutes = test_interval_seconds / 60
        logger.info(f"🧪 TEST MODE: Running every {test_interval_seconds} seconds ({interval_minutes:.1f} minutes)")
        logger.info("⚠️  WARNING: This is for testing only!")
    else:
        logger.info(f"📅 PRODUCTION MODE: Running daily at {PRODUCTION_CRON_HOUR:02d}:{PRODUCTION_CRON_MINUTE:02d} UTC")
    
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
            next_run = calculate_next_run_time(test_mode, test_interval_seconds)
            wait_seconds = (next_run - datetime.now()).total_seconds()
            
            if test_mode:
                interval_minutes = test_interval_seconds / 60
                logger.info(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"Waiting {wait_seconds:.0f} seconds ({wait_seconds/60:.1f} minutes) until next run...")
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
        help="Enable test mode (overrides MODE from .env)"
    )
    parser.add_argument(
        "--test-interval",
        type=int,
        default=None,
        help="Interval in seconds for test mode (overrides TEST_INTERVAL_SECONDS from .env)"
    )
    
    args = parser.parse_args()
    
    # Determine test mode: command line arg > environment variable > config MODE
    if args.test_mode:
        test_mode = True
    elif os.getenv("TEST_MODE", "").lower() in ("true", "1", "yes"):
        test_mode = True
    else:
        test_mode = None  # Will use MODE from config
    
    # Determine test interval: command line arg > environment variable > config
    if args.test_interval is not None:
        test_interval_seconds = args.test_interval
    elif os.getenv("TEST_INTERVAL_SECONDS"):
        test_interval_seconds = int(os.getenv("TEST_INTERVAL_SECONDS"))
    else:
        test_interval_seconds = None  # Will use TEST_INTERVAL_SECONDS from config
    
    scheduler_loop(test_mode=test_mode, test_interval_seconds=test_interval_seconds)
