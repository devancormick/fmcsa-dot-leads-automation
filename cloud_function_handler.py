#!/usr/bin/env python3
"""
Google Cloud Function handler for FMCSA DOT Leads Automation
"""
import logging
from main import main

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def cloud_function_handler(request):
    """
    Google Cloud Function handler
    
    Args:
        request: Flask request object (can contain JSON with 'date' key)
    
    Returns:
        dict: Response with status and results
    """
    try:
        # Extract target date from request if provided
        target_date = None
        if request and hasattr(request, 'get_json'):
            json_data = request.get_json(silent=True)
            if json_data and 'date' in json_data:
                target_date = json_data['date']
        
        logger.info(f"Cloud Function invoked for date: {target_date or 'yesterday'}")
        
        # Run the main automation
        main(target_date=target_date)
        
        return {
            'status': 'success',
            'message': 'DOT Leads Automation completed successfully',
            'date': target_date or 'yesterday'
        }, 200
    
    except Exception as e:
        logger.error(f"Cloud Function execution failed: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'error': str(e),
            'message': 'DOT Leads Automation failed'
        }, 500
