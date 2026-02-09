import requests
from django.conf import settings

YANDEX_GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
MODEL_URI = f"gpt://{settings.YANDEX_GPT_FOLDER_ID}/yandexgpt/latest"

def generate_response_with_system(
    system_prompt: str,
    user_prompt: str,
    model: str = "yandexgpt",
    temperature: float = 0.7,
    max_tokens: int = 500
) -> str:
    headers = {
        "Authorization": f"Bearer {settings.YANDEX_GPT_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "modelUri": MODEL_URI,
        "completionOptions": {
            "stream": False,
            "temperature": min(1.0, max(0.0, temperature)),
            "maxTokens": min(max_tokens, 2000)
        },
        "messages": [
            {"role": "system", "text": system_prompt},
            {"role": "user", "text": user_prompt}
        ]
    }
    response = requests.post(YANDEX_GPT_URL, headers=headers, json=data, timeout=30)
    response.raise_for_status()
    return response.json()["result"]["alternatives"][0]["message"]["text"].strip()