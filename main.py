from src.models.anomaly_detector import AnomalyDetector
from src.models.ollama_client import OllamaModel
from src.utils.sample_data_generator import generate_sample_sleep_data, generate_multiple_anomalies_sleep_data
from src.apis.googleFitAPI import GoogleFitAPI
import os
import dotenv


class WellnessBuddy:
    def __init__(self, model_name: str):
        # 1. Generate sample data with multiple anomalies
        self.base_data = self.generate_sample_data(days=7)

        # 2. Add multiple anomalies to the generated data
        self.sleep_data = self.add_noise_to_sample_data(
            self.base_data,
            num_anomalies=2,
            anomaly_multipliers=[2.0, 0.1]  # One very long sleep, one very short sleep
        )

        # 3. Extract main data from the returned data
        self.sleep_records = self.extract_main_data(self.sleep_data)

        # 4. Initialize and detect anomalies
        self.result = self.detect_anomalies(self.sleep_records)

        # 5. Print results
        # self.print_stats()

        # 6. Chat with Ollama
        self.chat_with_ollama(model_name=model_name)
    
    
    def generate_sample_data(self, days: int = 7):
        """
        Generate sample data with multiple anomalies
        Samples are made based on real data structure comming from Google Fit API
        """
        return generate_sample_sleep_data(days=days)


    def add_noise_to_sample_data(self, base_data: dict, num_anomalies: int = 2, anomaly_multipliers: list[float] = [2.0, 0.1]):
        """
        Add multiple anomalies to the generated data
        """
        return generate_multiple_anomalies_sleep_data(
            base_data,
            num_anomalies=num_anomalies,
            anomaly_multipliers=anomaly_multipliers
        )


    def extract_main_data(self, sleep_data: dict):
        """
        Extract main data from the returned data
        """
        return GoogleFitAPI().extract_sleep_durations(sleep_data)


    def detect_anomalies(self, sleep_records: dict):
        """
        Detect anomalies in the sleep data
        """
        anomaly_detector = AnomalyDetector(threshold_multiplier=1.5)
        return anomaly_detector.detect_sleep_anomalies(sleep_records)


    def print_stats(self):
        print("\nSleep Anomaly Detection Results:")
        print("-" * 40)
        print(f"Message: {self.result['message']}")
        
        # Statistics
        print("\nStatistics:")
        print(f"Average Sleep Duration: {self.result['statistics']['average_duration']:.2f} minutes")
        print(f"Standard Deviation: {self.result['statistics']['std_duration']:.2f} minutes")
        print(f"Upper Threshold: {self.result['statistics']['upper_threshold']:.2f} minutes")
        print(f"Lower Threshold: {self.result['statistics']['lower_threshold']:.2f} minutes")
        
        # Anomalies
        if self.result['anomalies']:
            print("\nDetected Anomalies:")
            for anomaly in self.result['anomalies']:
                print(f"- {anomaly['message']}")
        else:
            print("\nNo anomalies detected in the sleep data.")


    def chat_with_ollama(self, model_name: str):
        """
        Chat with the Ollama model about the data
        """
        ollama_model = OllamaModel(model_name=model_name)
        prompt = ollama_model.prompt_template(data_type="sleep", results=self.result)
        response = ollama_model.chat_with_data(prompt)
        print(f"\nAssistant: {response}")


if __name__ == '__main__':

    dotenv.load_dotenv()
    model_name = os.getenv("MODEL_NAME")
    wellness_buddy = WellnessBuddy(model_name=model_name)
