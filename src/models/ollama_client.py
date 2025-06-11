from ollama import chat

class OllamaModel:
    def __init__(self, model_name: str):
        self.model_name = model_name
    

    def chat_with_data(self, prompt: str):
        """
        Chat with the Ollama model about the data
        """
        messages = [
            {"role": "user", "content": prompt}
        ]

        while True:
            try:
                response = chat(
                    model=self.model_name,
                    messages=messages
                )
                print(f"\n{response['message']['content']}")
                messages.append({"role": "assistant", "content": response["message"]["content"]})
            except Exception as e:
                return f"Error: {str(e)}"

            new_prompt = input("You: ")
            if new_prompt.lower() == "quit":
                break
            
            messages.append({"role": "user", "content": new_prompt})


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
