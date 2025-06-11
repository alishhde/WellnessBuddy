from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import json
import datetime
import pickle
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv


class GoogleFitAPI:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get scopes from environment variable
        self.SCOPES = os.getenv('GOOGLE_FIT_SCOPES', '').split(',')
        self.service = self._get_fitness_service()


    def _get_credentials(self) -> Credentials:
        """Gets valid user credentials from storage.
        
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, if available previously
        token_path = os.getenv('GOOGLE_FIT_TOKEN_PATH')
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available from previous run, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                client_secrets_path = os.getenv('GOOGLE_FIT_CLIENT_SECRETS_PATH') # path to json file containing secrets
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        return creds


    def _get_fitness_service(self):
        """Builds and returns the Google Fit API service."""
        creds = self._get_credentials()
        service = build('fitness', 'v1', credentials=creds)
        return service


    def extract_sleep_durations(self, sleep_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract sleep durations from Google Fit sleep data.
        
        Args:
            sleep_data (Dict): Raw sleep data from Google Fit API
            
        Returns:
            List[Dict]: List of dictionaries containing sleep duration and timestamp
        """
        durations = []
        if 'bucket' in sleep_data:
            for bucket in sleep_data['bucket']:
                if 'dataset' in bucket:
                    for dataset in bucket['dataset']:
                        if 'point' in dataset:
                            for point in dataset['point']:
                                if 'value' in point and len(point['value']) > 0:
                                    # Convert milliseconds to minutes
                                    duration = point['value'][0].get('intVal', 0) / (1000 * 60)
                                    timestamp = int(bucket['startTimeMillis'])
                                    date = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
                                    durations.append({
                                        'duration': duration,
                                        'timestamp': timestamp,
                                        'date': date
                                    })
        return durations


    def get_heart_rate_data(self, start_time: int, end_time: int) -> Dict[str, Any]:
        """Fetches heart rate data for the specified time range."""
        dataset_id = f"{start_time}-{end_time}"
        
        # Get heart rate data
        heart_rate_data = self.service.users().dataset().aggregate(
            userId='me',
            body={
                'aggregateBy': [{
                    'dataTypeName': 'com.google.heart_rate.bpm'
                }],
                'bucketByTime': {'durationMillis': 3600000},  # 1 hour
                'startTimeMillis': start_time,
                'endTimeMillis': end_time
            }
        ).execute()
        
        return heart_rate_data


    def get_sleep_data(self, start_time: int, end_time: int) -> Dict[str, Any]:
        """Fetches sleep data for the specified time range."""
        dataset_id = f"{start_time}-{end_time}"
        
        # Get sleep data
        sleep_data = self.service.users().dataset().aggregate(
            userId='me',
            body={
                'aggregateBy': [{
                    'dataTypeName': 'com.google.sleep.segment'
                }],
                'bucketByTime': {'durationMillis': 86400000},  # 24 hours
                'startTimeMillis': start_time,
                'endTimeMillis': end_time
            }
        ).execute()
        
        return sleep_data


    def get_data_for_last_n_days(self, n_days: int = 7) -> Dict[str, Any]:
        """Get fitness data for the last n days.
        
        Args:
            n_days (int): Number of days to fetch data for. Defaults to 7.
            
        Returns:
            Dict[str, Any]: Dictionary containing heart rate and sleep data
        """
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = end_time - (n_days * 24 * 60 * 60 * 1000)
        
        return {
            'heart_rate': self.get_heart_rate_data(start_time, end_time),
            'sleep': self.get_sleep_data(start_time, end_time)
        }
