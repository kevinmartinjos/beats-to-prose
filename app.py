import requests
import json

if __name__ == "__main__":
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": 'Bearer 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'
        },
        data=json.dumps({
            "model": "openai/gpt-3.5-turbo", # Optional
            "messages": [
            {"role": "user", "content": "What is the meaning of life?"}
            ]
        })
    )
    print(response)