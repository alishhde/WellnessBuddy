import numpy as np
from typing import List, Dict, Any
from src.apis.googleFitAPI import extract_sleep_durations

class AnomalyDetector:
    def __init__(self, threshold_multiplier: float = 1.5):
        """
        Initialize the AnomalyDetector with a threshold multiplier.
        
        Args:
            threshold_multiplier (float): Multiplier to determine how far from the mean
                                        a value needs to be to be considered an anomaly
        """
        self.threshold_multiplier = threshold_multiplier

    def detect_sleep_anomalies(self, sleep_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect all anomalies in the sleep data.
        
        Args:
            sleep_data (Dict): Sleep data
            
        Returns:
            Dict: Contains anomaly information and statistics
        """
        # (temporary) Extract durations with timestamps using the Google Fit API utility
        sleep_records = extract_sleep_durations(sleep_data)
        
        if not sleep_records:
            return {
                'anomalies': [],
                'message': 'Insufficient data for anomaly detection',
                'statistics': {
                    'average_duration': 0,
                    'std_duration': 0,
                    'upper_threshold': 0,
                    'lower_threshold': 0
                }
            }
        
        # Calculate statistics
        durations = [record['duration'] for record in sleep_records]
        avg_duration = np.mean(durations)
        std_duration = np.std(durations)
        
        # Calculate thresholds
        upper_threshold = avg_duration + (self.threshold_multiplier * std_duration)
        lower_threshold = avg_duration - (self.threshold_multiplier * std_duration)
        
        # Find anomalies
        anomalies = []
        for record in sleep_records:
            duration = record['duration']
            if duration > upper_threshold or duration < lower_threshold:
                anomaly_type = "high" if duration > upper_threshold else "low"
                deviation = ((duration - avg_duration) / avg_duration) * 100
                anomalies.append({
                    'date': record['date'],
                    'duration': duration,
                    'type': anomaly_type,
                    'deviation': deviation,
                    'message': f"{anomaly_type.capitalize()} sleep duration on {record['date']}: "
                             f"{duration:.2f} minutes ({deviation:+.1f}% from average)"
                })
        
        return {
            'anomalies': anomalies,
            'statistics': {
                'average_duration': avg_duration,
                'std_duration': std_duration,
                'upper_threshold': upper_threshold,
                'lower_threshold': lower_threshold
            },
            'message': f"Found {len(anomalies)} anomalies in the sleep data"
        }
