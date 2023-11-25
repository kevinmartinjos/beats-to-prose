from typing import List, Dict
from collections import defaultdict
import pprint
import json
import requests
from tqdm import tqdm

from common.utils import get_openrouter_api_key
from generators import BaseGenerator


class InteractiveGenerator(BaseGenerator):
    """
    Very similar to SequentialGenerator. Expands beats one by one, feeding all the expanded beats as context in the
    subsequent call. The main difference is that each beat is expanded n times (configurable) with different sampling
    temperatures

    - 0.2 - for a focused expansion
    - 1.0 - the default
    - 1.8 - Induces the model make a more unlikely/random expansion

    This allows the user to intervene and pick a coherent/safe expansion where it's warranted, while allowing to pick a
    more creative expansion at other places.
    """
    TEMPLATE_FINAL_PROMPT = "{preamble_and_concatenated_beats}\n{story_so_far}\nThe next prompt to expand is: {next_beat}. Write the paragraph based on this prompt."
    TEMPLATE_STORY_SO_FAR = "The story so far is: {story_so_far}"

    def generate(self) -> str:
        preamble_and_concatenated_beats = self.prompt_collection.to_text()
        beat_id_to_story_so_far = defaultdict(list)
        story_so_far = []

        for beat_id, beat in tqdm(enumerate(self.prompt_collection.prompts), desc='Expanding beats', total=len(self.prompt_collection.prompts)):
            if beat_id > 0:
                prompt_story_so_far = self.TEMPLATE_STORY_SO_FAR.format(story_so_far=beat_id_to_story_so_far[beat_id-1])
            else:
                prompt_story_so_far = ""

            prompt_for_next_beat = self.TEMPLATE_FINAL_PROMPT.format(
                preamble_and_concatenated_beats=preamble_and_concatenated_beats, story_so_far=prompt_story_so_far,
                next_beat=beat.text
            )

            if len(story_so_far):
                # Sorry about the ugly nested if..else and the print statements. I wanted to build something
                # interactive and this is the only way if I don't want to deal with jupyter notebooks.
                print("The previous paragraph was:")
                print("*" * 100)
                pprint.pprint(story_so_far[-1])
                print("*" * 100)
            print(f"The next beat to be expanded is: {beat.text}")

            # If this was production code, I would have validated the user input below
            temperature = float(input("Enter a temperature value between 0.1 and 2. The lower the value, the safer/predictable the expansions\n"))

            messages = [
                {
                    "role": "user",
                    "content": prompt_for_next_beat
                }
            ]
            beat_response = self.openrouter_generate(messages, temperature)

            expanded_beat = beat_response["choices"][0]["message"]["content"]
            pprint.pprint(expanded_beat)
            retry_temperature = float(input("Type -1 to continue with this expansion. Type a temperature value between 0 and 2 to retry generation with the supplied temperature\n"))
            while retry_temperature > 0:
                beat_response = self.openrouter_generate(messages, retry_temperature)
                expanded_beat = beat_response["choices"][0]["message"]["content"]
                pprint.pprint(expanded_beat)
                retry_temperature = float(input("Type -1 to continue with this expansion. Type a temperature value between 0 and 2 to retry generation with the supplied temperature\n"))

            beat_id_to_story_so_far[beat_id] = expanded_beat
            story_so_far.append(expanded_beat)

        return "\n".join(story_so_far)

    def openrouter_generate(self, messages: List[Dict[str, str]], temperature: float) -> Dict:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f'Bearer {get_openrouter_api_key()}'
            },
            data=json.dumps({
                "model": self.model_name,  # Optional
                "messages": messages,
                "n": self.num_choices,
                "max_tokens": self.max_tokens_per_beat,
                "seed": self.seed,
                "temperature": temperature
            })
        )

        return response.json()

