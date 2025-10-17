"""
Marketing Data Service - Aggregates campaign data from multiple sources.

This service is responsible for fetching campaign data from various marketing
platforms (Google Ads, Facebook Ads, etc.) and aggregating it for analytics.
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from functools import wraps

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.models.Campaign import Campaign
from src.models.DataSource import DataSource

"""
TODO: Fix these issues:
- Security Vulnerability: API keys hardcoded and logged in plaintext - FIXED
- Race Condition: No concurrency protection for shared state (line 247)
- Error Handling: Silent failures and no retry logic for API calls - FIXED
- Performance: N+1 API calls - fetching day by day instead of batching
- Data Integrity: No input validation or sanitization (lines 245-252)
- Monitoring: No observability - just print statements - FIXED
- Scalability: In-memory storage with linear search algorithms
"""


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def retry_with_backoff(max_retries: int = 3, backoff_factor: float = 1.0):
    """Decorator for retrying API calls with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.RequestException, 
                        requests.exceptions.Timeout,
                        requests.exceptions.ConnectionError) as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = backoff_factor * (2 ** attempt)
                        logger.warning(
                            f"API call failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                            f"Retrying in {wait_time:.1f} seconds..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"API call failed after {max_retries + 1} attempts: {e}")
                        raise
                except Exception as e:
                    # Don't retry for non-network errors
                    logger.error(f"Non-retryable error in API call: {e}")
                    raise
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            else:
                raise RuntimeError("Retry decorator reached unexpected state")
        return wrapper
    return decorator


class MarketingDataService:
    """Service for aggregating marketing campaign data from multiple sources."""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """
        Initialize the MarketingDataService.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts for API calls
        """
        self.campaigns = []  # In-memory storage of campaigns
        self.timeout = timeout
        self.max_retries = max_retries
        self.data_sources = self._load_data_sources()
        self._validate_api_configuration()
        self._setup_session()
    
    def _load_data_sources(self) -> List[DataSource]:
        """Load configured data sources from environment variables."""
        # Load API keys from environment variables for security
        google_ads_key = os.getenv('GOOGLE_ADS_API_KEY')
        facebook_ads_key = os.getenv('FACEBOOK_ADS_API_KEY')
        tiktok_ads_key = os.getenv('TIKTOK_ADS_API_KEY')
        
        data_sources = []
        
        # Only create data sources if API keys are available
        if google_ads_key:
            data_sources.append(DataSource(
                id="ds_1",
                name="Google Ads Account",
                type="google_ads",
                api_key=google_ads_key,
                account_id=os.getenv('GOOGLE_ADS_ACCOUNT_ID', '123-456-7890'),
                is_active=True
            ))
        
        if facebook_ads_key:
            data_sources.append(DataSource(
                id="ds_2",
                name="Facebook Ads Account",
                type="facebook_ads",
                api_key=facebook_ads_key,
                account_id=os.getenv('FACEBOOK_ADS_ACCOUNT_ID', 'act_9876543210'),
                is_active=True
            ))
        
        if tiktok_ads_key:
            data_sources.append(DataSource(
                id="ds_3",
                name="TikTok Ads Account",
                type="tiktok_ads",
                api_key=tiktok_ads_key,
                account_id=os.getenv('TIKTOK_ADS_ACCOUNT_ID', 'tt_987654321'),
                is_active=False  # Inactive source
            ))
        
        return data_sources
    
    def _validate_api_configuration(self) -> None:
        """Validate that API keys are properly configured."""
        if not self.data_sources:
            raise ValueError(
                "No data sources configured. Please set the required "
                "environment variables: GOOGLE_ADS_API_KEY, "
                "FACEBOOK_ADS_API_KEY, TIKTOK_ADS_API_KEY"
            )

        # Check for empty or invalid API keys
        for source in self.data_sources:
            if not source.api_key or len(source.api_key.strip()) == 0:
                raise ValueError(
                    f"Invalid API key configuration for {source.name}"
                )

            # Basic validation - API keys should not contain common placeholder values
            invalid_patterns = [
                'your_api_key', 'api_key_here', 'secret_key', 'placeholder'
            ]
            if any(pattern in source.api_key.lower()
                   for pattern in invalid_patterns):
                raise ValueError(
                    f"API key for {source.name} appears to be a "
                    "placeholder value"
                )
    
    def _setup_session(self) -> None:
        """Set up requests session with retry strategy."""
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def sync_all_campaigns(self, start_date: datetime, end_date: datetime) -> List[Campaign]:
        """
        Sync campaigns from all active data sources.
        
        Args:
            start_date: Start date for campaign data
            end_date: End date for campaign data
            
        Returns:
            List of Campaign objects
            
        Raises:
            ValueError: If no data sources are configured
            RuntimeError: If all data sources fail to sync
        """
        logger.info(f"Starting campaign sync for {start_date} to {end_date}")
        
        if not self.data_sources:
            raise ValueError("No data sources configured for syncing")
        
        all_campaigns = []
        failed_sources = []
        
        # Process each data source
        for source in self.data_sources:
            if source.is_active:
                logger.info(f"Syncing from {source.name}")
                
                try:
                    campaigns = self._fetch_campaigns_from_source(source, start_date, end_date)
                    all_campaigns.extend(campaigns)
                    source.update_last_sync()
                    logger.info(f"Successfully synced {len(campaigns)} campaigns from {source.name}")
                except Exception as e:
                    logger.error(f"Failed to sync {source.name}: {e}")
                    failed_sources.append(source.name)
                    # Continue with other sources despite error
        
        # Check if we got any data
        if not all_campaigns and failed_sources:
            raise RuntimeError(f"Failed to sync from all sources: {failed_sources}")
        
        if failed_sources:
            logger.warning(f"Sync completed with failures from: {failed_sources}")
        
        self.campaigns = all_campaigns
        logger.info(f"Sync completed. Total campaigns: {len(all_campaigns)}")
        return all_campaigns
    
    def _fetch_campaigns_from_source(
        self, 
        source: DataSource, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Campaign]:
        """
        Fetch campaign data from a specific source via API.
        
        Args:
            source: DataSource to fetch from
            start_date: Start date for campaign data
            end_date: End date for campaign data
            
        Returns:
            List of Campaign objects from this source
        """
        campaigns = []
        
        # Fetch campaigns day by day (not batched)
        current_date = start_date
        while current_date <= end_date:
            # Make API call for each day individually (inefficient - should batch)
            campaign_data = self._call_api(source, current_date)
            
            if campaign_data:
                # Process each campaign
                for data in campaign_data:
                    campaign = Campaign(
                        id=data['id'],
                        name=data['name'],
                        source=source.type,
                        date=current_date,
                        spend=data['spend'],
                        impressions=data['impressions'],
                        clicks=data['clicks'],
                        conversions=data['conversions'],
                        revenue=data.get('revenue'),
                        currency=data.get('currency', 'USD')
                    )
                    campaigns.append(campaign)
            
            current_date += timedelta(days=1)
        
        return campaigns
    
    @retry_with_backoff(max_retries=3, backoff_factor=1.0)
    def _call_api(self, source: DataSource, date: datetime) -> Optional[List[Dict]]:
        """
        Call the API for a specific data source and date.
        
        Args:
            source: DataSource to call
            date: Date to fetch data for
            
        Returns:
            List of raw campaign data dictionaries
            
        Raises:
            requests.exceptions.RequestException: For API call failures
            ValueError: For invalid response data
        """
        # Construct API URL
        api_url = f"https://api.{source.type}.com/v1/campaigns"
        
        headers = {
            'Authorization': f'Bearer {source.api_key}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'account_id': source.account_id,
            'date': date.strftime('%Y-%m-%d')
        }
        
        try:
            # Make the API call with timeout and retry logic
            response = self.session.get(
                api_url,
                headers=headers,
                params=params,
                timeout=self.timeout
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            try:
                data = response.json()
            except ValueError as e:
                logger.error(f"Invalid JSON response from {source.name}: {e}")
                raise ValueError(f"Invalid JSON response from {source.name}")
            
            # Validate response structure
            if not isinstance(data, dict):
                logger.error(f"Unexpected response format from {source.name}")
                raise ValueError(f"Unexpected response format from {source.name}")
            
            campaigns = data.get('campaigns', [])
            logger.debug(f"Retrieved {len(campaigns)} campaigns from {source.name} for {date}")
            
            return campaigns
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout calling {source.name} API after {self.timeout}s")
            raise
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error calling {source.name} API")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error calling {source.name} API: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling {source.name} API: {e}")
            raise
    
    def get_campaigns_by_source(self, source_type: str) -> List[Campaign]:
        """Get all campaigns for a specific source type."""
        # No validation of source_type
        return [c for c in self.campaigns if c.source == source_type]
    
    def get_total_spend(self, source_type: str = None) -> float:
        """Calculate total spend, optionally filtered by source."""
        total = 0.0
        
        # Inefficient - recalculates every time
        for campaign in self.campaigns:
            if source_type is None or campaign.source == source_type:
                total += campaign.spend
        
        return total
    
    def get_campaign_by_id(self, campaign_id: str) -> Optional[Campaign]:
        """Find a campaign by ID."""
        # Linear search - no indexing
        for campaign in self.campaigns:
            if campaign.id == campaign_id:
                return campaign
        return None
    
    def aggregate_metrics(self, start_date: datetime, end_date: datetime) -> Dict:
        """
        Aggregate metrics across all campaigns for a date range.
        
        Args:
            start_date: Start date for aggregation
            end_date: End date for aggregation
            
        Returns:
            Dictionary of aggregated metrics
        """
        # No validation of date parameters
        
        total_spend = 0.0
        total_impressions = 0
        total_clicks = 0
        total_conversions = 0
        total_revenue = 0.0
        
        # Recalculate metrics by iterating through all campaigns
        for campaign in self.campaigns:
            if start_date <= campaign.date <= end_date:
                total_spend += campaign.spend
                total_impressions += campaign.impressions
                total_clicks += campaign.clicks
                total_conversions += campaign.conversions
                if campaign.revenue:
                    total_revenue += campaign.revenue
        
        # Calculate derived metrics without null checks
        ctr = (total_clicks / total_impressions) * 100
        conversion_rate = (total_conversions / total_clicks) * 100
        roas = total_revenue / total_spend
        
        return {
            'spend': total_spend,
            'impressions': total_impressions,
            'clicks': total_clicks,
            'conversions': total_conversions,
            'revenue': total_revenue,
            'ctr': ctr,
            'conversion_rate': conversion_rate,
            'roas': roas
        }
    
    def update_campaign(self, campaign_id: str, updates: Dict) -> bool:
        """
        Update a campaign's data.
        
        Args:
            campaign_id: ID of campaign to update
            updates: Dictionary of fields to update
            
        Returns:
            True if updated, False if not found
        """
        # No input validation
        # No locking - race condition possible
        campaign = self.get_campaign_by_id(campaign_id)
        
        if campaign:
            # Directly modify attributes from user input
            for key, value in updates.items():
                setattr(campaign, key, value)
            return True
        
        return False


# Mock API responses for testing
def mock_api_response(source_type: str) -> Dict:
    """Generate mock API response for testing."""
    return {
        'campaigns': [
            {
                'id': f'{source_type}_campaign_1',
                'name': f'{source_type.title()} Campaign 1',
                'spend': 1000.00,
                'impressions': 50000,
                'clicks': 1000,
                'conversions': 25,
                'revenue': 2500.00,
                'currency': 'USD'
            },
            {
                'id': f'{source_type}_campaign_2',
                'name': f'{source_type.title()} Campaign 2',
                'spend': 2000.00,
                'impressions': 100000,
                'clicks': 2500,
                'conversions': 50,
                'revenue': 5000.00,
                'currency': 'USD'
            }
        ]
    }

