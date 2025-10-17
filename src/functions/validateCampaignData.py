"""
Campaign Data Validation Function

This module provides validation for marketing campaign data from various sources.
It ensures data quality before the data enters the analytics pipeline.
"""

import logging
from datetime import datetime, timedelta
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_campaign_data(campaign_data: dict) -> dict:
    """
    Validates marketing campaign data against business rules and data quality checks.
    
    This function validates:
    - Required fields are present
    - Data types are correct
    - Values are within acceptable ranges
    - Business logic constraints (e.g., clicks <= impressions)
    - Anomalies that might indicate data quality issues
    
    Args:
        campaign_data: Dictionary containing campaign metrics with the following structure:
            {
                "campaign_id": str,
                "campaign_name": str (optional),
                "source": str,  # e.g., 'google_ads', 'facebook_ads'
                "date": str,  # YYYY-MM-DD format
                "spend": float,
                "impressions": int,
                "clicks": int,
                "conversions": int (optional),
                "revenue": float (optional),
                "currency": str (optional)
            }
    
    Returns:
        Dictionary with validation results:
        {
            "valid": bool,  # Overall validation status
            "errors": List[str],  # List of error messages (validation failures)
            "warnings": List[str],  # List of warning messages (anomalies)
            "campaign_id": str or None,  # Campaign ID if present
            "validated_at": str  # ISO timestamp of validation
        }
    
    Examples:
        >>> result = validate_campaign_data({
        ...     "campaign_id": "camp_123",
        ...     "source": "google_ads",
        ...     "date": "2024-10-15",
        ...     "spend": 1000.0,
        ...     "impressions": 50000,
        ...     "clicks": 1000
        ... })
        >>> result["valid"]
        True
        
        >>> result = validate_campaign_data({
        ...     "campaign_id": "camp_456",
        ...     "source": "facebook_ads",
        ...     "date": "2024-10-15",
        ...     "spend": 500.0,
        ...     "impressions": 0,
        ...     "clicks": 100
        ... })
        >>> result["valid"]
        False
        >>> "clicks cannot exceed impressions" in result["errors"][0].lower()
        True
    """
    # Initialize result structure
    errors = []
    warnings = []
    campaign_id = campaign_data.get("campaign_id")
    
    # Log validation start
    logger.info(f"Starting validation for campaign: {campaign_id}")
    
    # Validate required fields
    required_field_errors = validate_required_fields(campaign_data)
    errors.extend(required_field_errors)
    
    # Validate data types
    type_errors = validate_data_types(campaign_data)
    errors.extend(type_errors)
    
    # Only proceed with business rules and anomaly detection if basic validation passes
    if not errors:
        # Validate business rules
        business_errors, business_warnings = validate_business_rules(campaign_data)
        errors.extend(business_errors)
        warnings.extend(business_warnings)
        
        # Detect anomalies
        anomaly_errors, anomaly_warnings = detect_anomalies(campaign_data)
        errors.extend(anomaly_errors)
        warnings.extend(anomaly_warnings)
    else:
        logger.warning(f"Basic validation failed for campaign {campaign_id}, skipping advanced checks")
    
    # Log validation results
    if errors:
        logger.error(f"Validation failed for campaign {campaign_id}: {len(errors)} errors")
        for error in errors:
            logger.error(f"  Error: {error}")
    else:
        logger.info(f"Validation passed for campaign {campaign_id}")
    
    if warnings:
        logger.warning(f"Validation warnings for campaign {campaign_id}: {len(warnings)} warnings")
        for warning in warnings:
            logger.warning(f"  Warning: {warning}")
    
    # Return validation result
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "campaign_id": campaign_id,
        "validated_at": datetime.now().isoformat()
    }


def validate_required_fields(campaign_data: dict) -> List[str]:
    """
    Validate that all required fields are present.
    
    Args:
        campaign_data: Campaign data dictionary
        
    Returns:
        List of error messages for missing required fields
    """
    errors = []
    required_fields = ["campaign_id", "source", "date", "spend", "impressions", "clicks"]
    
    # Check for missing fields
    for field in required_fields:
        if field not in campaign_data:
            errors.append(f"Missing required field: {field}")
        elif campaign_data[field] is None:
            errors.append(f"Required field {field} cannot be None")
        elif (isinstance(campaign_data[field], str) and 
              campaign_data[field].strip() == ""):
            errors.append(f"Required field {field} cannot be empty")
    
    return errors


def validate_data_types(campaign_data: dict) -> List[str]:
    """
    Validate that field data types are correct.
    
    Args:
        campaign_data: Campaign data dictionary
        
    Returns:
        List of error messages for incorrect data types
    """
    errors = []
    
    # Validate types for each field
    type_validations = {
        "campaign_id": (str, "string"),
        "campaign_name": (str, "string"),
        "source": (str, "string"),
        "date": (str, "string"),
        "spend": (float, "float"),
        "impressions": (int, "integer"),
        "clicks": (int, "integer"),
        "conversions": (int, "integer"),
        "revenue": (float, "float"),
        "currency": (str, "string")
    }
    
    for field, (expected_type, type_name) in type_validations.items():
        if field in campaign_data and campaign_data[field] is not None:
            if not isinstance(campaign_data[field], expected_type):
                errors.append(
                    f"Field {field} must be {type_name}, "
                    f"got {type(campaign_data[field]).__name__}"
                )
    
    # Special validation for date format
    if "date" in campaign_data and campaign_data["date"] is not None:
        try:
            datetime.strptime(campaign_data["date"], "%Y-%m-%d")
        except ValueError:
            errors.append("Field date must be in YYYY-MM-DD format")
    
    return errors


def validate_business_rules(campaign_data: dict) -> tuple[List[str], List[str]]:
    """
    Validate business logic rules.
    
    Args:
        campaign_data: Campaign data dictionary
        
    Returns:
        Tuple of (errors, warnings)
    """
    errors = []
    warnings = []
    
    # Validate business constraints
    try:
        # Convert values to appropriate types for validation
        spend = float(campaign_data.get("spend", 0))
        impressions = int(float(campaign_data.get("impressions", 0)))
        clicks = int(float(campaign_data.get("clicks", 0)))
        conversions = int(float(campaign_data.get("conversions", 0))) if campaign_data.get("conversions") is not None else None
        revenue = float(campaign_data.get("revenue", 0)) if campaign_data.get("revenue") is not None else None
        
        # spend must be >= 0
        if spend < 0:
            errors.append("Spend must be non-negative")
        
        # clicks cannot exceed impressions
        if clicks > impressions:
            errors.append("Clicks cannot exceed impressions")
        
        # conversions cannot exceed clicks (if conversions present)
        if conversions is not None and conversions > clicks:
            errors.append("Conversions cannot exceed clicks")
        
        # revenue should be >= 0 (if revenue present)
        if revenue is not None and revenue < 0:
            errors.append("Revenue must be non-negative")
        
        # date cannot be in the future
        if "date" in campaign_data and campaign_data["date"]:
            try:
                campaign_date = datetime.strptime(campaign_data["date"], "%Y-%m-%d").date()
                today = datetime.now().date()
                
                if campaign_date > today:
                    errors.append("Campaign date cannot be in the future")
                elif campaign_date < today - timedelta(days=90):
                    warnings.append("Campaign date is more than 90 days old")
            except ValueError:
                # Date format error already handled in validate_data_types
                pass
                
    except (ValueError, TypeError) as e:
        errors.append(f"Invalid numeric values in campaign data: {str(e)}")
    
    return errors, warnings


def detect_anomalies(campaign_data: dict) -> tuple[List[str], List[str]]:
    """
    Detect anomalies that might indicate data quality issues.
    
    Args:
        campaign_data: Campaign data dictionary
        
    Returns:
        Tuple of (errors, warnings)
    """
    errors = []
    warnings = []
    
    # Check for suspicious patterns
    try:
        # Convert values to appropriate types for validation
        spend = float(campaign_data.get("spend", 0))
        impressions = int(float(campaign_data.get("impressions", 0)))
        clicks = int(float(campaign_data.get("clicks", 0)))
        conversions = int(float(campaign_data.get("conversions", 0))) if campaign_data.get("conversions") is not None else None
        revenue = float(campaign_data.get("revenue", 0)) if campaign_data.get("revenue") is not None else None
        
        # If impressions > 0 but clicks == 0, flag as warning (unusual but possible)
        if impressions > 0 and clicks == 0:
            warnings.append("Campaign has impressions but zero clicks - unusual but possible")
        
        # If impressions == 0 but clicks > 0, flag as error (impossible)
        if impressions == 0 and clicks > 0:
            errors.append("Campaign has zero impressions but positive clicks - impossible")
        
        # If spend > $100,000 in a single day, flag as warning (might be legitimate but unusual)
        if spend > 100000:
            warnings.append(f"Campaign spend of ${spend:,.2f} is unusually high for a single day")
        
        # If Click-Through Rate (CTR = clicks/impressions) > 50%, flag as error (likely data quality issue)
        if impressions > 0:
            ctr = (clicks / impressions) * 100
            if ctr > 50:
                errors.append(f"Click-through rate of {ctr:.1f}% is impossibly high - likely data quality issue")
        
        # If conversions > 0 but revenue == 0 or missing, flag as warning
        if conversions is not None and conversions > 0:
            if revenue is None or revenue == 0:
                warnings.append("Campaign has conversions but no revenue reported")
        
    except (ValueError, TypeError, ZeroDivisionError) as e:
        # Handle any conversion errors gracefully
        logger.warning(f"Error in anomaly detection: {str(e)}")
    
    return errors, warnings


# Mock data for testing purposes
VALID_CAMPAIGN = {
    "campaign_id": "camp_123",
    "campaign_name": "Summer Sale 2024",
    "source": "google_ads",
    "date": "2024-10-15",
    "spend": 5000.00,
    "impressions": 100000,
    "clicks": 2500,
    "conversions": 50,
    "revenue": 7500.00,
    "currency": "USD"
}

INVALID_CAMPAIGN_MISSING_FIELDS = {
    "campaign_id": "camp_456",
    "source": "facebook_ads",
    # Missing date, spend, impressions, clicks
}

INVALID_CAMPAIGN_BAD_DATA = {
    "campaign_id": "camp_789",
    "source": "tiktok_ads",
    "date": "2024-10-15",
    "spend": 1000.00,
    "impressions": 0,  # 0 impressions
    "clicks": 500,  # but 500 clicks - impossible!
    "conversions": 10
}


if __name__ == "__main__":
    # Quick test of the validation function
    print("Testing validation function...\n")
    
    print("Test 1: Valid campaign")
    result = validate_campaign_data(VALID_CAMPAIGN)
    print(f"Result: {result}\n")
    
    print("Test 2: Missing required fields")
    result = validate_campaign_data(INVALID_CAMPAIGN_MISSING_FIELDS)
    print(f"Result: {result}\n")
    
    print("Test 3: Bad data (impossible metrics)")
    result = validate_campaign_data(INVALID_CAMPAIGN_BAD_DATA)
    print(f"Result: {result}\n")

