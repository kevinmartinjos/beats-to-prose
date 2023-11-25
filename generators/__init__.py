from typing import List, Dict
import json
import requests

from common.utils import get_openrouter_api_key
from data_structures.prompt import PromptCollection


class BaseGenerator:
    """
    Base class for a generator.
    A generator takes in a list of beats and converts them to prose
    """
    def __init__(self, model_name: str, prompt_collection: PromptCollection):
        self.model_name = model_name
        self.prompt_collection = prompt_collection

    def generate(self) -> str:
        raise NotImplementedError

    def openrouter_generate(self, messages: List[Dict[str, str]]) -> Dict:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f'Bearer {get_openrouter_api_key()}'
            },
            data=json.dumps({
                "model": self.model_name, # Optional
                "messages": messages
            })
        )

        return response.json()