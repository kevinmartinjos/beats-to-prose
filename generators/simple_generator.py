from generators import BaseGenerator


class SimpleGenerator(BaseGenerator):
    """
    Concatenates all the beats to a single string and asks an LLM to convert it to prose
    """
    def generate(self) -> str:
        concatenated_prompt = self.prompt_collection.to_text()
        messages = [
            {
                "role": "user",
                "content": concatenated_prompt
            }
        ]
        response = self.openrouter_generate(messages)

        assert len(response["choices"]) == 1, "SimpleGenerator does not support multiple choices in the LLM response"
        return response["choices"][0]["message"]['content']

