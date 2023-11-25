from typing import List

class Prompt:
    """
    A simple prompt. Just a string
    """
    def __init__(self, text: str):
        self._text = text

    @property
    def text(self):
        return self._text


class PromptCollection:
    """
    A collection of prompts
    """
    DELIMITER = "\n"

    def __init__(self, prompts: List[Prompt], preamble: List[Prompt] = None):
        self.prompts = prompts
        self.preamble_prompts = preamble

    def to_text(self) -> str:
        """
        Concatenates the preamble and the prompts using newline as a delimiter.
        """
        return self.DELIMITER.join([p.text for p in self.preamble_prompts] + [p.text for p in self.prompts])

    @classmethod
    def from_beats(cls, beats: List[str], preamble: str = None) -> "PromptCollection":
        prompts = [Prompt(beat) for beat in beats]
        preamble_prompt = Prompt(preamble)

        return cls(prompts, preamble=[preamble_prompt])
