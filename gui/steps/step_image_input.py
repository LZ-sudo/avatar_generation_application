"""
Step 1: Image Input

Allows the user to select front and side photographs for measurement extraction.
"""

import customtkinter as ctk
from pathlib import Path

from ..app_state import AppState
from ..components.image_picker import ImagePicker


class StepImageInput(ctk.CTkFrame):
    """
    Image input step for the avatar generation wizard.

    Provides two image pickers for front and side views.
    """

    COLORS = {
        "title": "#1f2937",
        "subtitle": "#6b7280",
        "warning": "#c2410c",
        "tip_bg": "#eff6ff",
        "tip_title": "#374151",
        "tip_text": "#6b7280",
    }

    def __init__(self, parent: ctk.CTkFrame, app_state: AppState):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self._build()

    def _build(self) -> None:
        """Build the step content."""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=30, pady=30)

        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.pack(pady=(0, 20))

        title_label = ctk.CTkLabel(
            header_frame,
            text="Select Input Images",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.COLORS["title"],
        )
        title_label.pack()

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Please provide front and side view photographs for measurement extraction.",
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS["subtitle"],
        )
        subtitle_label.pack(pady=(8, 0))

        pickers_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        pickers_frame.pack(pady=20)

        self._front_picker = ImagePicker(
            pickers_frame,
            label="Front View",
            description="Full body photo from the front",
            on_image_selected=self._on_front_image_selected,
        )
        self._front_picker.pack(side="left", padx=20)

        self._side_picker = ImagePicker(
            pickers_frame,
            label="Side View",
            description="Full body photo from the side",
            on_image_selected=self._on_side_image_selected,
        )
        self._side_picker.pack(side="left", padx=20)

        self._validation_label = ctk.CTkLabel(
            content_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["warning"],
        )
        self._validation_label.pack(pady=(10, 0))

        tips_frame = ctk.CTkFrame(
            content_frame,
            fg_color=self.COLORS["tip_bg"],
            corner_radius=8,
        )
        tips_frame.pack(pady=(20, 0), fill="x")

        tips_content = ctk.CTkFrame(tips_frame, fg_color="transparent")
        tips_content.pack(padx=15, pady=15)

        tips_title = ctk.CTkLabel(
            tips_content,
            text="Tips for best results:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.COLORS["tip_title"],
        )
        tips_title.pack(anchor="w")

        tips = [
            "- Use well-lit photos with neutral background",
            "- Ensure full body is visible in frame",
            "- Wear fitted clothing for accurate measurements",
        ]

        for tip in tips:
            tip_label = ctk.CTkLabel(
                tips_content,
                text=tip,
                font=ctk.CTkFont(size=12),
                text_color=self.COLORS["tip_text"],
            )
            tip_label.pack(anchor="w", pady=2)

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
            self._validation_label.configure(text="Please select both front and side view images")
        elif not self._front_picker.has_image:
            self._validation_label.configure(text="Please select a front view image")
        elif not self._side_picker.has_image:
            self._validation_label.configure(text="Please select a side view image")
        else:
            self._validation_label.configure(text="")

    def validate(self) -> bool:
        """Validate the step is complete."""
        return self.app_state.image_input.is_complete()
