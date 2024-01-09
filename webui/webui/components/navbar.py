import reflex as rx

from webui import styles


def navbar():
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.link(
                    rx.box(
                        rx.image(src="telemeicon.png", width=30, height="auto"),
                        p="1",
                        border_radius="6",
                        bg="#F0F0F0",
                        mr="2",
                    ),
                    href="/",
                ),
                rx.breadcrumb(
                    rx.breadcrumb_item(
                        rx.heading("TelemeAI", size="sm"),
                    ),
                    rx.breadcrumb_item(
                        rx.text("Chat", size="sm", font_weight="normal"),
                    ),
                ),
            ),
            rx.hstack(
                spacing="8",
            ),
            justify="space-between",
        ),
        bg=styles.bg_dark_color,
        backdrop_filter="auto",
        backdrop_blur="lg",
        p="4",
        border_bottom=f"1px solid {styles.border_color}",
        position="sticky",
        top="0",
        z_index="100",
    )
