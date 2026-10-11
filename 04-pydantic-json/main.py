import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from enum import StrEnum
from pydantic import BaseModel
import json

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

class ResponseFormatType(StrEnum):
    JSON_FORMAT = "json_object"
    DEFAULT_FORMAT = JSON_FORMAT

class ResponseFormat:
    response_format_type: str

    def __init__(self, response_format_type: ResponseFormatType):
        self.response_format_type = str(response_format_type)
        if self.response_format_type == "":
            print(f"[WARNING] response format type provided: {response_format_type}, setting to default type: {ResponseFormatType.DEFAULT_FORMAT}")

    def __iter__(self):
        yield "type", self.response_format_type

    def get_response_format(self):
        return dict(self)

class UserComplain(BaseModel):
    name: str | None
    email: str | None
    contact: str | None
    issue: str | None

def take_decision(user_complain_ticket: UserComplain):

    should_send_email: bool = False
    details_required: str = ""

    if not user_complain_ticket.contact or len(user_complain_ticket.contact) == 0:
        should_send_email = True
        details_required = "phone number not provided, send a follow up email for asking phone number"
    elif len(user_complain_ticket.contact) != 10:
        should_send_email = True
        details_required = "phone number not correct, send a follow up email for correct phone number"

    if not user_complain_ticket.issue:
        should_send_email = False
        details_required = "\nissue not provided, send a follow up email for asking issue"

    if should_send_email:
        print("Decision: Send Email\n")
        print(f"Reason: {details_required}")
        return

    print("Decision: Redirect ticket to customer support")

    

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

    # 3. Prepare the user complain schema

    user_complain_schema = UserComplain.model_json_schema()

    # 4. Prepare the System Role

    system_prompt = f"Parse the complain and return the message strictly in this JSON format only {user_complain_schema}. If any thing is missing, use null for the field."

    system_message = GroqMessage(GroqMessageRole.SYSTEM, system_prompt).get_message()

    # 5. User Complain

    user_complain = "My name is Mohit Uniyal. My Iphone is not working. I Live in Delhi. My E-Mail is badmosh@shaitan.com.."

    user_complain_message = GroqMessage(GroqMessageRole.USER, user_complain).get_message()

    # 6. parse the user complain and extract formatted user complain as a ticket

    response_format = ResponseFormat(response_format_type=ResponseFormatType.JSON_FORMAT).get_response_format()

    messages = [system_message, user_complain_message]

    response = client.chat.completions.create(model=model, messages=messages, response_format=response_format)

    raw_json = response.choices[0].message.content
    print(raw_json)

    ticket_file = json.loads(raw_json)

    user_complain_ticket = UserComplain(**ticket_file)

    # 7. Take decision based on the ticket

    take_decision(user_complain_ticket)

    


main()