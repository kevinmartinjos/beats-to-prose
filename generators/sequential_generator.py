from generators import BaseGenerator
from tqdm import tqdm


class SequentialGenerator(BaseGenerator):
    """
    Makes n api calls to openrouter to expand n beats. This allows us to control the number of tokens used for
    expanding each beat.

    Each api call gets the following as context:
    1. A list of all the beats
    2. The story so far (the context length of gpt-4 is 32k, so this is ok)
    3. The next beat to generate
    """
    TEMPLATE_FINAL_PROMPT = "{preamble_and_concatenated_beats}\n{story_so_far}\nThe next prompt to expand is: {next_beat}. Write the paragraph based on this prompt."
    TEMPLATE_STORY_SO_FAR = "The story so far is: {story_so_far}"

    def generate(self) -> str:
        preamble_and_concatenated_beats = self.prompt_collection.to_text()
        beat_id_to_story_so_far = {}
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
            messages = [
                {
                    "role": "user",
                    "content": prompt_for_next_beat
                }
            ]
            beat_response = self.openrouter_generate(messages)
            assert len(beat_response["choices"]) == 1, "SequentialGenerator does not support multiple choices in the LLM response"
            expanded_beat = beat_response["choices"][0]["message"]["content"]
            beat_id_to_story_so_far[beat_id] = expanded_beat
            story_so_far.append(expanded_beat)

        return "\n".join(story_so_far)
