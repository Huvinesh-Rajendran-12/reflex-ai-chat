import os
import time
from typing import List, Optional, Sequence
from uuid import uuid4 
import requests
import json
import reflex as rx
from webui.models import Admin, Chat, Conversation, UserFeedback
from qdrant import Qdrant

AI_CHATBOT_URL = os.getenv("AI_CHATBOT_URL", "http://127.0.0.1:8080/v1/chat/completions")

class State(rx.State):
    """The app state."""

    # Whether we are processing the question.
    processing: bool = False

    user_feedback_modal_open: bool = False
    
    def toggle_feedback_modal(self):
        """Togggle the user feedback modal."""
        self.user_feedback_modal_open = not self.user_feedback_modal_open


    def update_user_feedback(self) -> None:
        """

        """
        pass



class LLM(rx.State):
    async def process_question(self, form_data: dict):
        # Get the question from the form
        question = form_data["user_prompt"]

        # Check if the question is empty
        if question == "":
            return

        model = self.llm_process_question

        async for value in model(question):
            yield value

    async def llm_process_question(self, question: str):
        """Get the response from the API.

        Args:
            form_data: A dict with the current question.
        """

        with rx.session() as session:

            conver = Conversation(session_id=self.router.session.session_id, user_prompt=question) 
            session.add(conver)
            session.commit()
            session.refresh(conver)
            State.processing = True
            yield

            # Build the messages.
            messages = [
                {"role": "system", "content": "You are a friendly health assistant named Teleme AI."}
            ]

            context = Qdrant().query(question=question)
           
            full_prompt = f"""
                    User's question: {question}.
                    Below is the context, delimited by three dashes (-), use that to answer the user's question.
                    ---
                    {context}
                    ---
            """
            conversations = session.exec(Conversation.select.where(
                Conversation.session_id == self.router.session.session_id
            )).all()
            for conversation in conversations:
                messages.append({"role": "user", "content": conversation.user_prompt})
                messages.append({"role": "assistant", "content": conversation.llm_response})

            # Remove the last mock answer.
            messages = messages[:-1]
            messages.append({"role": "user", "content": full_prompt})
            start_time = time.time()
            # Start a new session to answer the question.
            response = requests.post(
                url=AI_CHATBOT_URL,
                headers={"Content-Type": "application/json"},
                stream=True,
                data=json.dumps({
                    "model": "Llama2",
                    "messages": messages,
                    "response_format": {
                        "type": "json_object"
                    },
                    "stream": True
                }),
            )

            # Stream the results, yielding after every word.
            for item in response.iter_content(chunk_size=2000, decode_unicode=True):
                if item.strip()[6:] != "[DONE]":
                    json_response = json.loads(s=item[6:])
                    if 'content' in json_response['choices'][0]['delta']:
                        answer_text = json_response['choices'][0]['delta']['content']
                        conver.llm_response += answer_text
                        yield

            end_time = time.time()
            time_taken = end_time - start_time
            conver.time_taken = time_taken
            session.add(conver)
            session.commit()
            # Toggle the processing flag.
            State.processing = False

class ChatState(rx.State):

    current_chat: Chat = Chat(session_id="")
    conversations: List[Conversation] = []

    def create_chat(self): 
        with rx.session() as session:
            session_id = uuid4().hex
            chat = Chat(session_id=session_id)
            print(chat)
            session.add(chat)
            session.commit()
            self.current_chat = chat
    
    def create_conversation(self):
        with rx.session() as session:
            session.add(ChatState.conversations[-1])
            session.commit()

    @rx.var
    def get_conversations(self) -> Sequence[Conversation]:
        with rx.session() as session:
            chat_conversations = session.exec(Conversation.select).all()
            return chat_conversations


class AdminState(rx.State):
    logged_in: bool = False

    def login(self, form_data: dict) -> None:
        with rx.session() as session:
            admin = session.exec(Admin.select.where(Admin.username == form_data.get('username'))).first()
            if admin is not None:
                self.logged_in = True if (admin.password == form_data.get('password')) else False

    @rx.var
    def get_all_conversations(self) -> Sequence[Conversation]:
        """Get all the conversations from chats. 

        Returns:
            The list of conversations. 
        """
        with rx.session() as session:
            results = session.exec(Conversation.select)
            return results.all()

class UserFeedbackState(rx.State):
    rating: int = 0 
    user_feedback: str = ""
    user_feedback_modal_open: bool = False 
    def set_rating(self, rating: int) -> None:
        self.rating = rating

    def set_user_feedback(self, user_feedback: str) -> None:
        self.user_feedback = user_feedback

    def set_feedback_modal_open(self) -> None:
        self.user_feedback_modal_open = not self.user_feedback_modal_open

    def submit(self) -> None:
        user_feedback = UserFeedback(
            conversation_id=ChatState.conversations[-1].id,
            ratings=self.rating,
            user_feedback=self.user_feedback
        )
        with rx.session() as session:
            session.add(user_feedback)
            session.commit()

