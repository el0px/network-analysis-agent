import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2"

def generate(messages: list, max_new_tokens: int = 300, temperature: float = 0.4) -> str:
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_new_tokens
        }
    }
    response = requests.post(OLLAMA_URL, json=payload)
    return response.json()["message"]["content"].strip()

def extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except:
        return {}