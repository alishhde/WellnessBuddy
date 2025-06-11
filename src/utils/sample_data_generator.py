import random
import datetime
import json


def generate_sample_sleep_data(days: int = 7, base_sleep_hours: float = 7.5, std_dev_hours: float = 1.0) -> dict:
    """
    Generate sample sleep data that MIMICS the Google Fit API response structure.
    
    Args:
        days (int): Number of days of data to generate
        base_sleep_hours (float): Base sleep duration in hours
        std_dev_hours (float): Standard deviation of sleep duration in hours
    
    Returns:
        dict: Sample sleep data in Google Fit API format
    """
    end_time = int(datetime.datetime.now().timestamp() * 1000)
    buckets = []
    
    for i in range(days):
        # Generate random sleep duration with normal distribution
        sleep_hours = random.gauss(base_sleep_hours, std_dev_hours)
        # Ensure sleep duration is between 3 and 12 hours
        sleep_hours = max(3, min(12, sleep_hours))
        sleep_minutes = int(sleep_hours * 60)
        
        # Calculate time range for this bucket
        bucket_end = end_time - (i * 24 * 60 * 60 * 1000)
        bucket_start = bucket_end - (24 * 60 * 60 * 1000)
        
        # Create a bucket with sleep data
        bucket = {
            "startTimeMillis": str(bucket_start),
            "endTimeMillis": str(bucket_end),
            "dataset": [
                {
                    "dataSourceId": "derived:com.google.sleep.segment:com.google.android.gms:merged",
                    "point": [
                        {
                            "startTimeNanos": str(bucket_start * 1000000),
                            "endTimeNanos": str(bucket_end * 1000000),
                            "value": [
                                {
                                    "intVal": sleep_minutes * 60 * 1000  # Convert to milliseconds
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        buckets.append(bucket)
    
    return {"bucket": buckets}


def generate_multiple_anomalies_sleep_data(base_data: dict, num_anomalies: int = 2, 
                                         anomaly_multipliers: list = None) -> dict:
    """
    Generate sleep data with multiple anomalies by modifying random data points.
    
    Args:
        base_data (dict): Base sleep data
        num_anomalies (int): Number of anomalies to create
        anomaly_multipliers (list): List of multipliers for each anomaly. If None, random multipliers will be used.
    
    Returns:
        dict: Sleep data with multiple anomalies
    """
    # Deep copy the base data
    anomaly_data = json.loads(json.dumps(base_data))
    
    # Generate random multipliers if not provided
    if anomaly_multipliers is None:
        anomaly_multipliers = [random.uniform(1.8, 2.5) for _ in range(num_anomalies)]
    
    # Select random days to create anomalies (excluding the first day)
    available_days = list(range(1, len(anomaly_data["bucket"])))
    anomaly_days = random.sample(available_days, min(num_anomalies, len(available_days)))
    
    # Create anomalies
    for day_idx, multiplier in zip(anomaly_days, anomaly_multipliers):
        bucket = anomaly_data["bucket"][day_idx]
        if bucket["dataset"] and bucket["dataset"][0]["point"]:
            point = bucket["dataset"][0]["point"][0]
            original_duration = point["value"][0]["intVal"]
            point["value"][0]["intVal"] = int(original_duration * multiplier)
    
    return anomaly_data
