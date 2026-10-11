import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from enum import StrEnum

class Config:
    def __init__(self):
        load_dotenv()
        self.GroqAPIKey = os.getenv("GROQ_API_KEY")
        if not self.GroqAPIKey:
            raise ValueError("API Key not present")

class GroqMessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class GroqMessage:
    def __init__(self, role: GroqMessageRole, content: str):
        self.role = role
        self.content = content

    def __iter__(self):
        yield "role", self.role
        yield "content", self.content

    def get_message(self):
        return dict(self)

def main():
    # 1. Load Config

    try:
        config = Config()
    except ValueError as e:
        print(f"Error Loading Config: {e}")
        return

    # 2. Initialize Client

    client = Groq(api_key=config.GroqAPIKey)
    model = "openai/gpt-oss-120b"

    prompt1 = "Hi"
    prompt2 = "Explain time travel in 100 words"
    prompt3 = "write an essay on machine learning in 1000 words"
    prompts = [prompt1, prompt2, prompt3]

    for prompt in prompts:

        message = GroqMessage(GroqMessageRole.USER, prompt).get_message()

        messages = [message]
        response = client.chat.completions.create(model=model, messages=messages, max_tokens=500)
        usage = response.usage

        print(f"[prompt: {prompt}]\n\tYour tokens: {usage.prompt_tokens}\n\tModel tokens: {usage.completion_tokens}\n\tTotal Tokens: {usage.total_tokens}\n\tReason: {response.choices[0].finish_reason}")




main()