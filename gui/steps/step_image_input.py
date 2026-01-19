"""
Step 1: Image Input

Allows the user to select front and side photographs for measurement extraction.
"""

import flet as ft
from pathlib import Path

from ..app_state import AppState
from ..components.image_picker import ImagePicker


class StepImageInput(ft.Container):
    """
    Image input step for the avatar generation wizard.

    Provides two image pickers for front and side views.
    """

    def __init__(self, app_state: AppState):
        super().__init__()
        self.app_state = app_state
        self._build()

    def _build(self) -> None:
        """Build the step content."""
        self._front_picker = ImagePicker(
            label="Front View",
            description="Full body photo from the front",
            on_image_selected=self._on_front_image_selected,
        )

        self._side_picker = ImagePicker(
            label="Side View",
            description="Full body photo from the side",
            on_image_selected=self._on_side_image_selected,
        )

        self._validation_text = ft.Text(
            "",
            size=12,
            color=ft.Colors.ORANGE_700,
            text_align=ft.TextAlign.CENTER,
        )

        header = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Select Input Images",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_800,
                    ),
                    ft.Text(
                        "Please provide front and side view photographs for measurement extraction.",
                        size=14,
                        color=ft.Colors.GREY_600,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=ft.Padding.only(bottom=20),
        )

        tips = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Tips for best results:",
                        size=13,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_700,
                    ),
                    ft.Text(
                        "- Use well-lit photos with neutral background",
                        size=12,
                        color=ft.Colors.GREY_600,
                    ),
                    ft.Text(
                        "- Ensure full body is visible in frame",
                        size=12,
                        color=ft.Colors.GREY_600,
                    ),
                    ft.Text(
                        "- Wear fitted clothing for accurate measurements",
                        size=12,
                        color=ft.Colors.GREY_600,
                    ),
                ],
                spacing=4,
            ),
            bgcolor=ft.Colors.BLUE_50,
            padding=15,
            border_radius=8,
            margin=ft.Margin.only(top=20),
        )

        image_pickers = ft.Row(
            controls=[
                self._front_picker,
                self._side_picker,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=40,
        )

        self.content = ft.Column(
            controls=[
                header,
                image_pickers,
                self._validation_text,
                tips,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        )

        self.padding = 30
        self.expand = True

    def setup(self, page: ft.Page) -> None:
        """
        Set up the step after adding to page.

        Must be called after the step is added to the page.
        """
        self._front_picker.setup_file_picker(page)
        self._side_picker.setup_file_picker(page)

        if self.app_state.image_input.front_image_path:
            self._front_picker.set_image(self.app_state.image_input.front_image_path)
        if self.app_state.image_input.side_image_path:
            self._side_picker.set_image(self.app_state.image_input.side_image_path)

    def _on_front_image_selected(self, path: Path) -> None:
        """Handle front image selection."""
        self.app_state.image_input.front_image_path = path
        self._update_validation()
        self.app_state.notify_change()

    def _on_side_image_selected(self, path: Path) -> None:
        """Handle side image selection."""
        self.app_state.image_input.side_image_path = path
        self._update_validation()
        self.app_state.notify_change()

    def _update_validation(self) -> None:
        """Update validation message based on current state."""
        if not self._front_picker.has_image and not self._side_picker.has_image:
            self._validation_text.value = "Please select both front and side view images"
        elif not self._front_picker.has_image:
            self._validation_text.value = "Please select a front view image"
        elif not self._side_picker.has_image:
            self._validation_text.value = "Please select a side view image"
        else:
            self._validation_text.value = ""

        self._validation_text.update()

    def validate(self) -> bool:
        """Validate the step is complete."""
        return self.app_state.image_input.is_complete()
