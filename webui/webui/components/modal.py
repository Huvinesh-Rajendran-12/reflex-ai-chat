import reflex as rx
from webui.state import UserFeedbackState


def user_feedback_modal() -> rx.Component:
    return rx.modal(
        rx.modal_overlay(
            rx.modal_content(
                rx.modal_header(
                    rx.hstack(
                        rx.text("Provide Feedback"),
                        align_items="center",
                        justify_content="space-between"
                    )
                ),
                rx.modal_body(
                    rx.vstack(
                        rx.hstack(
                            rx.slider(
                                on_change=UserFeedbackState.set_rating
                            ),
                            rx.text(f"{UserFeedbackState.rating} / 5")
                        ),
                        rx.text_area(
                            on_change=UserFeedbackState.set_user_feedback
                        )
                    )
                ),
                rx.modal_footer(
                    rx.button(
                        name="Submit",
                        on_click=UserFeedbackState.submit
                    ),

                ),
            )
        ),
        is_open=UserFeedbackState.user_feedback_modal_open,
    )
