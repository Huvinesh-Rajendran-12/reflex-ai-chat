import reflex as rx
from webui.models import Admin, Conversation
from webui.state import AdminState, State

def show_conversation(conversation: Conversation):
    """Show a conversation between the user and the llm in a table row."""
    return rx.tr(
        rx.td(conversation.id),
        rx.td(conversation.user_prompt),
        rx.td(conversation.llm_response),
        rx.td(conversation.time_taken),
    )

def admin_index():
    """The admin page."""
    return rx.vstack(
            rx.vstack(
                rx.hstack(
                    rx.heading("Conversational History"),
                ),
                rx.table_container(
                    rx.table(
                        rx.thead(
                            rx.tr(
                                rx.th("Id"),
                                rx.th("User Prompt"),
                                rx.th("LLM Response"),
                                rx.th("Time Taken"),
                            )
                        ),
                        rx.tbody(
                            rx.foreach(AdminState.get_all_conversations, show_conversation),
                        ),
                    ),
                    border="1px solid #ddd",
                    border_radius="25px",
                ),
                align_items="center",
            ),
        align_items="center",
        padding="1em",
        width="100%"
    )
