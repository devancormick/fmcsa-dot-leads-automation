"""
Socrata API client for fetching FMCSA DOT records
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sodapy import Socrata
from config import SOCRATA_DOMAIN, SOCRATA_DATASET_ID, SOCRATA_APP_TOKEN, DATE_FORMAT

logger = logging.getLogger(__name__)


class DOTFetcher:
    """Fetches DOT records from FMCSA Socrata API"""
    
    def __init__(self):
        """Initialize Socrata client"""
        self.client = Socrata(SOCRATA_DOMAIN, SOCRATA_APP_TOKEN, timeout=60)
        self.dataset_id = SOCRATA_DATASET_ID
        
    def fetch_new_dots(self, target_date: Optional[str] = None) -> List[Dict]:
        """
        Fetch new DOT records for a specific date
        
        Args:
            target_date: Date in YYYY-MM-DD format. If None, uses yesterday's date.
        
        Returns:
            List of DOT records
        """
        if target_date is None:
            # Default to yesterday's date
            target_date = (datetime.now() - timedelta(days=1)).strftime(DATE_FORMAT)
        
        logger.info(f"Fetching DOT records for date: {target_date}")
        
        # Build query: filter by ADD_DATE
        # Socrata uses $where clause for date filtering
        where_clause = f"add_date >= '{target_date}T00:00:00.000' AND add_date < '{target_date}T23:59:59.999'"
        
        all_records = []
        limit = 50000  # Socrata default limit
        offset = 0
        
        try:
            while True:
                logger.info(f"Fetching records: offset={offset}, limit={limit}")
                
                # Fetch records with pagination
                results = self.client.get(
                    self.dataset_id,
                    where=where_clause,
                    limit=limit,
                    offset=offset,
                    order="dot_number"
                )
                
                if not results:
                    break
                
                all_records.extend(results)
                logger.info(f"Fetched {len(results)} records (total: {len(all_records)})")
                
                # If we got fewer than the limit, we've reached the end
                if len(results) < limit:
                    break
                
                offset += limit
            
            logger.info(f"Total records fetched: {len(all_records)}")
            return all_records
            
        except Exception as e:
            logger.error(f"Error fetching DOT records: {str(e)}")
            raise
    
    def close(self):
        """Close the Socrata client"""
        if self.client:
            self.client.close()
