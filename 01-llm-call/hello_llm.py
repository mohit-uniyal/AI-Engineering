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
    role = GroqMessageRole.USER
    content = "Answer in on word, which is best programming language currently?"

    # message = dict(GroqMessage(role, content))
    message = GroqMessage(role, content).get_message()

    messages = [message]

    # 3. Send to LLM

    response = client.chat.completions.create(model=model, messages=messages)

    # print(response)

    print(f"Answer: {response.choices[0].message.content}")


    


main()