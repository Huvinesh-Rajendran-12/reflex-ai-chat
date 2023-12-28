import os
import requests
import json
import reflex as rx


AI_CHATBOT_URL = os.getenv("AI_CHATBOT_URL", "http://127.0.0.1:8080/v1/chat/completions")

# def get_access_token():
#     """
#     :return: access_token
#     """
#     url = "https://aip.baidubce.com/oauth/2.0/token"
#     params = {
#         "grant_type": "client_credentials",
#         "client_id": BAIDU_API_KEY,
#         "client_secret": BAIDU_SECRET_KEY,
#     }
#     return str(requests.post(url, params=params).json().get("access_token"))


class QA(rx.Base):
    """A question and answer pair."""

    question: str
    answer: str


DEFAULT_CHATS = {
    "Intros": [],
}


class State(rx.State):
    """The app state."""

    # A dict from the chat name to the list of questions and answers.
    chats: dict[str, list[QA]] = DEFAULT_CHATS

    # The current chat name.
    current_chat = "Intros"

    # The current question.
    question: str

    # Whether we are processing the question.
    processing: bool = False

    # The name of the new chat.
    new_chat_name: str = ""

    # Whether the drawer is open.
    drawer_open: bool = False

    # Whether the modal is open.
    modal_open: bool = False

    api_type: str = "openai"

    def create_chat(self):
        """Create a new chat."""
        # Add the new chat to the list of chats.
        self.current_chat = self.new_chat_name
        self.chats[self.new_chat_name] = []

        # Toggle the modal.
        self.modal_open = False

    def toggle_modal(self):
        """Toggle the new chat modal."""
        self.modal_open = not self.modal_open

    def toggle_drawer(self):
        """Toggle the drawer."""
        self.drawer_open = not self.drawer_open

    def delete_chat(self):
        """Delete the current chat."""
        del self.chats[self.current_chat]
        if len(self.chats) == 0:
            self.chats = DEFAULT_CHATS
        self.current_chat = list(self.chats.keys())[0]
        self.toggle_drawer()

    def set_chat(self, chat_name: str):
        """Set the name of the current chat.

        Args:
            chat_name: The name of the chat.
        """
        self.current_chat = chat_name
        self.toggle_drawer()

    @rx.var
    def chat_titles(self) -> list[str]:
        """Get the list of chat titles.

        Returns:
            The list of chat names.
        """
        return list(self.chats.keys())

    async def process_question(self, form_data: dict[str, str]):
        # Get the question from the form
        question = form_data["question"]

        # Check if the question is empty
        if question == "":
            return

        if self.api_type == "openai":
            model = self.llm_process_question

        async for value in model(question):
            yield value

    async def llm_process_question(self, question: str):
        """Get the response from the API.

        Args:
            form_data: A dict with the current question.
        """

        # Add the question to the list of questions.
        qa = QA(question=question, answer="")
        self.chats[self.current_chat].append(qa)

        # Clear the input and start the processing.
        self.processing = True
        yield

        # Build the messages.
        messages = [
            {"role": "system", "content": "You are a friendly chatbot named Reflex."}
        ]
        for qa in self.chats[self.current_chat]:
            messages.append({"role": "user", "content": qa.question})
            messages.append({"role": "assistant", "content": qa.answer})

        # Remove the last mock answer.
        messages = messages[:-1]

        # Start a new session to answer the question.
        response = requests.post(
            url=AI_CHATBOT_URL,
            headers={"Content-Type": "application/json"},
            stream=True,
            data=json.dumps({
                "model": "Phi2",
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
                    print(answer_text)
                    self.chats[self.current_chat][-1].answer += answer_text
                    self.chats = self.chats
                    yield
        # Toggle the processing flag.
        self.processing = False
