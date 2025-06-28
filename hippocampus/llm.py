import openai
import os
import requests

class LLMClient:
    """
    A client for interacting with a local vLLM server that mimics the OpenAI API.
    """
    def __init__(self, base_url="http://localhost:8000/v1", api_key="not-needed"):
        """
        Initializes the client to connect to the specified server endpoint.
        
        Args:
            base_url: The URL of the vLLM server
            api_key: Not used for local servers, but required by the openai library
        """
        self.base_url = base_url
        self.client = openai.OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        # Fetch the actual model name from the server
        self.model_name = self._get_model_name()

    def _get_model_name(self):
        """
        Fetch the actual model name from the vLLM server's /v1/models endpoint.
        """
        try:
            response = requests.get(f"{self.base_url}/models")
            if response.status_code == 200:
                models_data = response.json()
                if models_data.get("data") and len(models_data["data"]) > 0:
                    return models_data["data"][0]["id"]
            print("Warning: Could not fetch model name from server, using fallback")
            return "local-vllm-model"
        except Exception as e:
            print(f"Warning: Could not connect to server to get model name: {e}")
            return "local-vllm-model"

    def _prepare_messages(self, prompt: str):
        """
        Prepares the message payload for the chat completions API.
        This is where you can define the structure of your prompt, including any system messages.
        """
        return [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]

    def query(self, prompt: str):
        """
        Sends a prompt to the local vLLM server and returns the completion.
        """
        messages = self._prepare_messages(prompt)
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,  # Uses the actual model name from the server
                messages=messages
            )
            response = completion.choices[0].message.content
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please ensure the vLLM server is running at the specified endpoint.")
            return None

# Global client instance
llm_client = LLMClient()

def complete_memory(fragments, max_tokens=128):
    """
    Given a list of fragments/words, generate a structured memory using the LLM.
    """
    prompt = (
        "You are an assistant that helps users log memories. "
        "Given the following unordered words or fragments, reconstruct a coherent, embellished memory or story. "
        "Fragments: " + ", ".join(fragments) + "\nMemory: "
    )
    
    return llm_client.query(prompt) 