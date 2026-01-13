#!/usr/bin/env python3
"""
AWS Lambda handler for FMCSA DOT Leads Automation
"""
import json
import logging
from main import main

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    AWS Lambda handler function
    
    Args:
        event: Lambda event (can contain 'date' key for specific date)
        context: Lambda context
    
    Returns:
        dict: Response with status and results
    """
    try:
        # Extract target date from event if provided
        target_date = event.get('date') if isinstance(event, dict) else None
        
        logger.info(f"Lambda invoked for date: {target_date or 'yesterday'}")
        
        # Run the main automation
        main(target_date=target_date)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'DOT Leads Automation completed successfully',
                'date': target_date or 'yesterday'
            })
        }
    
    except Exception as e:
        logger.error(f"Lambda execution failed: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'DOT Leads Automation failed'
            })
        }
