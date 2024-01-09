from typing import Optional
import reflex as rx
from sqlmodel import Field 

class Chat(rx.Model, table=True):
    session_id: str = Field(primary_key=True)

class Conversation(rx.Model, table=True):
    id: Optional[int] = Field(primary_key=True)
    session_id: str = Field(foreign_key="chat.session_id") 
    user_prompt: str
    llm_response: str = Field(default="")
    time_taken: float = Field(default=0.0)

class UserFeedback(rx.Model, table=True):
    id: Optional[int] = Field(primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    ratings: int = Field(default=0)
    user_feedback: str = Field(default="")

class Admin(rx.Model, table=True):
    id: Optional[int] = Field(primary_key=True)
    username: str
    password: str


