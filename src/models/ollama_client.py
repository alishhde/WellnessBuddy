from ollama import Client

class OllamaModel:
    def __init__(self, model_name: str):
        self.client = Client()
        self.model_name = model_name
    

    def chat_with_data(self, prompt: str):
        """
        Chat with the Ollama model about the data
        """
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt
            )
            return response.response
        except Exception as e:
            return f"Error: {str(e)}"


    def chat(self):
        print(f"Chat with {self.model_name} (type 'quit' to exit)")
        
        while True:
            prompt = input("\nYou: ").strip()
            if prompt.lower() == 'quit':
                break
                
            try:
                response = self.client.generate(
                    model=self.model_name,
                    prompt=prompt
                )
                print(f"\n{response.response}")
            except Exception as e:
                print(f"Error: {str(e)}")


    def prompt_template(self, data_type: str, results: dict):
        """
        Template for the prompt to be sent to the Ollama model containing the health data
        """
        if data_type == "sleep":
            data_stats = f"""
            Sleep Anomaly Detection Results:
            {results['message']}
            
            Statistics:
            Average Sleep Duration: {results['statistics']['average_duration']:.2f} minutes
            Standard Deviation: {results['statistics']['std_duration']:.2f} minutes
            Upper Threshold: {results['statistics']['upper_threshold']:.2f} minutes
            Lower Threshold: {results['statistics']['lower_threshold']:.2f} minutes
            
            Anomalies:
            {results['anomalies']}
            """

            template = f"""
            You are a wellness buddy responsible for analyzing sleep data and providing recommendations.
            You are given a sleep data and you need to analyze it and provide a recommendation to your buddy.

            The stats of the data is as follows:
            {data_stats}

            First analyze the data and the detected anomalies. Then, provide a recommendation to your buddy about what to do in order to
            improve their sleep and health and become a better version of themselves.
            """
        return template
