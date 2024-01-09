"""The main Chat app."""

import reflex as rx
from reflex.state import functools

from webui import styles
from webui.components import chat, navbar, admin_index, user_feedback_modal
from webui.state import AdminState, ChatState 

@rx.page(title="Chatbot Page", route="/")
def index() -> rx.Component:
    """The main app."""
    ChatState.create_chat
    return rx.vstack(
        navbar(),
        user_feedback_modal(),
        chat.chat(),
        chat.action_bar(),
        bg=styles.bg_dark_color,
        color=styles.text_light_color,
        min_h="100vh",
        align_items="stretch",
        spacing="0",
    )

def login() -> rx.Component:
    return rx.vstack(
        rx.form(
            rx.vstack(
                rx.input(
                    placeholder="Username",
                    name="username",
                ),
                rx.input(
                    placeholder="Password",
                    name="password",
                ),
                rx.button("Submit", type_="submit"),
            ),
            on_submit=AdminState.login
        )
    )

def require_login(page) -> rx.Component:
    @functools.wraps(page)
    def _auth_wrapper() -> rx.Component:
         
        return rx.cond(
            AdminState.logged_in,
            page(),
            login()
        )
    return _auth_wrapper

@rx.page(title="admin page", route="/admin")
@require_login
def admin() -> rx.Component:
    """The admin app.
    """
    return rx.vstack(
        admin_index(),
        bg=styles.bg_dark_color,
        color=styles.text_light_color,
        min_h="100vh",
        align_items="stretch",
        spacing="0"
    ) 

# Add state and page to the app.
app = rx.App(style=styles.base_style)
app.compile()
