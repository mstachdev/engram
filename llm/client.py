import openai
import os
import requests
from typing import Optional

class LLMClient:
    """
    A client for interacting with a local vLLM server that mimics the OpenAI API.
    """
    def __init__(self, base_url="http://localhost:8000/v1", api_key="not-needed", module_name="shared"):
        """
        Initializes the client to connect to the specified server endpoint.
        
        Args:
            base_url: The URL of the vLLM server
            api_key: Not used for local servers, but required by the openai library
            module_name: Name of the module using this client (for logging/debugging)
        """
        self.base_url = base_url
        self.module_name = module_name
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
            print(f"Warning ({self.module_name}): Could not fetch model name from server, using fallback")
            return "local-vllm-model"
        except Exception as e:
            print(f"Warning ({self.module_name}): Could not connect to server to get model name: {e}")
            return "local-vllm-model"

    def _prepare_messages(self, prompt: str, system_message: Optional[str] = None):
        """
        Prepares the message payload for the chat completions API.
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        else:
            messages.append({"role": "system", "content": "You are a helpful assistant."})
        
        messages.append({"role": "user", "content": prompt})
        return messages

    def query(self, prompt: str, system_message: Optional[str] = None, max_tokens: int = 1000, temperature: float = 0.7):
        """
        Sends a prompt to the local vLLM server and returns the completion.
        """
        messages = self._prepare_messages(prompt, system_message)
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            response = completion.choices[0].message.content
            return response
        except Exception as e:
            print(f"Error in {self.module_name} LLM query: {e}")
            print("Please ensure the vLLM server is running at the specified endpoint.")
            return None

    def get_available_models(self):
        """
        Get list of available models from the vLLM server.
        """
        try:
            response = requests.get(f"{self.base_url}/models")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error fetching models for {self.module_name}: {e}")
            return None

# Create client instances for different modules
def create_llm_client(module_name: str):
    """Create an LLM client for a specific module."""
    return LLMClient(module_name=module_name) 