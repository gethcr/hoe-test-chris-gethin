# Task 4: Practical Coding Challenge

## Background
Ask Bosco's marketing analytics platform needs a robust data validation layer. When campaign data comes in from various sources, it must be validated before being processed and shown to clients. Invalid data can lead to incorrect reports, client complaints, and loss of trust.

## Task
Implement a Python function that validates marketing campaign data. This function will be deployed as a cloud function but must be fully runnable and testable locally.

## Requirements

Implement the function in `src/functions/validateCampaignData.py` that:

1. **Accepts campaign data** as a JSON payload (Python dict)
2. **Validates data structure and business rules:**
   - Required fields are present
   - Data types are correct
   - Values are within acceptable ranges
   - Business logic constraints are met
3. **Checks for anomalies:**
   - Suspicious patterns (e.g., 0 impressions but 1000 clicks)
   - Unusual spend amounts that might indicate errors
   - Invalid date ranges
4. **Returns structured validation results:**
   - Success/failure status
   - List of specific validation errors (if any)
   - Warning messages for anomalies
   - Metadata about the validation
5. **Includes proper logging** for debugging and monitoring
6. **Has at least 2-3 unit tests** in `src/tests/test_validateCampaignData.py`

## Campaign Data Schema

A campaign data payload looks like this:

```python
{
    "campaign_id": "camp_123",
    "campaign_name": "Summer Sale 2024",
    "source": "google_ads",  # or "facebook_ads", "tiktok_ads", etc.
    "date": "2024-10-15",
    "spend": 5000.00,
    "impressions": 100000,
    "clicks": 2500,
    "conversions": 50,
    "revenue": 7500.00,
    "currency": "USD"
}
```

## Validation Rules

### Required Fields
- `campaign_id`, `source`, `date`, `spend`, `impressions`, `clicks`

### Data Types
- `campaign_id`: string
- `spend`, `revenue`: float (positive or zero)
- `impressions`, `clicks`, `conversions`: int (non-negative)
- `date`: string in YYYY-MM-DD format

### Business Rules
- `spend` must be >= 0
- `clicks` cannot exceed `impressions`
- `conversions` cannot exceed `clicks`
- `revenue` (if present) should be >= 0
- `date` cannot be in the future
- `date` should not be more than 90 days in the past (warning, not error)

### Anomaly Detection
- If `impressions` > 0 but `clicks` == 0, flag as warning (unusual but possible)
- If `impressions` == 0 but `clicks` > 0, flag as error (impossible)
- If `spend` > $100,000 in a single day, flag as warning (might be legitimate but unusual)
- If Click-Through Rate (CTR = clicks/impressions) > 50%, flag as error (likely data quality issue)
- If `conversions` > 0 but `revenue` == 0 or missing, flag as warning

## Expected Function Signature

```python
def validate_campaign_data(campaign_data: dict) -> dict:
    """
    Validates marketing campaign data.
    
    Args:
        campaign_data: Dictionary containing campaign metrics
        
    Returns:
        Dictionary with validation results:
        {
            "valid": bool,
            "errors": [list of error messages],
            "warnings": [list of warning messages],
            "campaign_id": str or None,
            "validated_at": str (ISO timestamp)
        }
    """
    pass
```

## Test Data Provided

Mock campaign data fixtures are provided in the test file with various scenarios:
- Valid campaigns (happy path)
- Missing required fields
- Invalid data types
- Business rule violations
- Anomalies and edge cases

## Evaluation Criteria

- **Functionality (30%):** Does the code correctly validate according to the rules?
- **Code Quality (25%):** Is the code clean, well-organized, and maintainable?
- **Error Handling (20%):** Are edge cases handled gracefully?
- **Testing (15%):** Are critical paths tested? Do tests cover edge cases?
- **Documentation (10%):** Is the code well-documented for other engineers?

## Time
You should spend approximately 40 minutes on this task.

## Running the Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest src/tests/test_validateCampaignData.py -v

# Run with coverage
pytest src/tests/test_validateCampaignData.py --cov=src/functions --cov-report=term
```

## What We're Looking For

- **Practical coding skills:** Can you write clean, working Python code?
- **Testing mindset:** Do you think about edge cases and test coverage?
- **Code organization:** Is your code easy to understand and maintain?
- **Error handling:** Do you handle errors gracefully?
- **Documentation:** Would another engineer understand your code?

**Remember:** This is a VP Engineering role, so we're not expecting perfect code in 40 minutes. We want to see your thought process, priorities, and how you balance speed with quality. It's better to have working, well-tested code for core validation than perfect code for every edge case.

## Bonus (If Time Permits)
- Add logging with appropriate log levels
- Consider how this would scale to validate 1000s of campaigns per minute
- Think about how you'd monitor this in production

