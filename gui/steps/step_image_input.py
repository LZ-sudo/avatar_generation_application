"""
Step 1: Image Input and Measurement Extraction

Allows the user to select a front photograph, enter height, and extract measurements.
Displays status indicators for required configurations.
"""

import customtkinter as ctk
from pathlib import Path
from typing import Callable, Optional
import threading

from ..app_state import AppState
from ..backend_interface import BackendInterface
from ..components.image_picker import ImagePicker


class StatusIndicator(ctk.CTkFrame):
    """A small status indicator with icon and label."""

    COLORS = {
        "valid": "#16a34a",
        "invalid": "#dc2626",
        "label": "#374151",
        "bg": "#f9fafb",
        "border": "#e5e7eb",
    }

    def __init__(
        self,
        parent: ctk.CTkFrame,
        label: str,
        is_valid: bool = False,
    ):
        super().__init__(
            parent,
            fg_color=self.COLORS["bg"],
            border_width=1,
            border_color=self.COLORS["border"],
            corner_radius=6,
        )
        self.label_text = label
        self._is_valid = is_valid
        self._build()

    def _build(self) -> None:
        """Build the status indicator."""
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(padx=12, pady=8)

        self._icon_label = ctk.CTkLabel(
            content,
            text="",
            font=ctk.CTkFont(size=14),
            width=20,
        )
        self._icon_label.pack(side="left")

        self._text_label = ctk.CTkLabel(
            content,
            text=self.label_text,
            font=ctk.CTkFont(size=13),
            text_color=self.COLORS["label"],
        )
        self._text_label.pack(side="left", padx=(6, 0))

        self._update_display()

    def _update_display(self) -> None:
        """Update the icon based on validity."""
        if self._is_valid:
            self._icon_label.configure(
                text="\u2713",
                text_color=self.COLORS["valid"],
            )
        else:
            self._icon_label.configure(
                text="\u2717",
                text_color=self.COLORS["invalid"],
            )

    def set_valid(self, is_valid: bool) -> None:
        """Set the validity status."""
        self._is_valid = is_valid
        self._update_display()

    @property
    def is_valid(self) -> bool:
        """Get the current validity status."""
        return self._is_valid


class StepImageInput(ctk.CTkFrame):
    """
    Image input step for the avatar generation wizard.

    Provides front image picker, height input, and configuration status indicators.
    """

    COLORS = {
        "title": "#1f2937",
        "subtitle": "#6b7280",
        "warning": "#c2410c",
        "panel_bg": "#ffffff",
        "panel_border": "#d1d5db",
        "label": "#374151",
        "status_blue": "#2563eb",
        "status_green": "#16a34a",
        "status_red": "#dc2626",
    }

    def __init__(
        self,
        parent: ctk.CTkFrame,
        app_state: AppState,
        backend: BackendInterface,
        on_navigate_next: Optional[Callable[[], None]] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self.backend = backend
        self.on_navigate_next = on_navigate_next
        self._extraction_complete = False
        self._build()
        self._update_config_status()

    def _build(self) -> None:
        """Build the step content."""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=30, pady=30)

        # Header
        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.pack(pady=(0, 20))

        title_label = ctk.CTkLabel(
            header_frame,
            text="Image Input & Measurement Extraction",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.COLORS["title"],
        )
        title_label.pack()

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Select a front view photograph and enter your height to extract body measurements.",
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS["subtitle"],
        )
        subtitle_label.pack(pady=(8, 0))

        # Main content area (two columns)
        main_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        main_frame.pack(pady=20)

        # Left column - Front image picker
        self._front_picker = ImagePicker(
            main_frame,
            label="Front View",
            description="Full body photo from the front",
            on_image_selected=self._on_front_image_selected,
            width=300,
            height=350,
        )
        self._front_picker.pack(side="left", padx=(0, 30))

        # Right column - Height input and status indicators
        right_column = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_column.pack(side="left", fill="y")

        # Height input panel
        height_panel = ctk.CTkFrame(
            right_column,
            fg_color=self.COLORS["panel_bg"],
            border_width=1,
            border_color=self.COLORS["panel_border"],
            corner_radius=10,
        )
        height_panel.pack(fill="x", pady=(0, 15))

        height_content = ctk.CTkFrame(height_panel, fg_color="transparent")
        height_content.pack(padx=20, pady=15)

        height_label = ctk.CTkLabel(
            height_content,
            text="Subject Height",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.COLORS["label"],
        )
        height_label.pack(anchor="w")

        height_desc = ctk.CTkLabel(
            height_content,
            text="Enter the subject's actual height in centimeters",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["subtitle"],
        )
        height_desc.pack(anchor="w", pady=(2, 10))

        height_input_frame = ctk.CTkFrame(height_content, fg_color="transparent")
        height_input_frame.pack(anchor="w")

        self._height_var = ctk.StringVar()
        self._height_var.trace_add("write", self._on_height_change)

        self._height_entry = ctk.CTkEntry(
            height_input_frame,
            width=120,
            textvariable=self._height_var,
            placeholder_text="e.g., 170",
            justify="right",
        )
        self._height_entry.pack(side="left")

        height_unit = ctk.CTkLabel(
            height_input_frame,
            text="cm",
            font=ctk.CTkFont(size=13),
            text_color=self.COLORS["label"],
        )
        height_unit.pack(side="left", padx=(8, 0))

        # Configuration status panel
        status_panel = ctk.CTkFrame(
            right_column,
            fg_color=self.COLORS["panel_bg"],
            border_width=1,
            border_color=self.COLORS["panel_border"],
            corner_radius=10,
        )
        status_panel.pack(fill="x", pady=(0, 15))

        status_content = ctk.CTkFrame(status_panel, fg_color="transparent")
        status_content.pack(padx=20, pady=15)

        status_label = ctk.CTkLabel(
            status_content,
            text="Configuration Status",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.COLORS["label"],
        )
        status_label.pack(anchor="w", pady=(0, 10))

        self._camera_status = StatusIndicator(
            status_content,
            label="Camera Calibration",
            is_valid=False,
        )
        self._camera_status.pack(anchor="w", pady=(0, 8))

        self._aruco_status = StatusIndicator(
            status_content,
            label="ArUco Settings",
            is_valid=False,
        )
        self._aruco_status.pack(anchor="w")

        # Validation message
        self._validation_label = ctk.CTkLabel(
            content_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["warning"],
        )
        self._validation_label.pack(pady=(10, 0))

        # Extract button
        self._extract_button = ctk.CTkButton(
            content_frame,
            text="Extract Measurements",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=200,
            height=40,
            command=self._extract_measurements,
            state="disabled",
        )
        self._extract_button.pack(pady=(15, 0))

        # Status label for extraction
        self._status_label = ctk.CTkLabel(
            content_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["status_blue"],
        )
        self._status_label.pack(pady=(10, 0))

        # Restore existing state
        if self.app_state.image_input.front_image_path:
            self._front_picker.set_image(self.app_state.image_input.front_image_path)
        if self.app_state.image_input.height_cm:
            self._height_var.set(str(self.app_state.image_input.height_cm))

    def _on_front_image_selected(self, path: Path) -> None:
        """Handle front image selection."""
        self.app_state.image_input.front_image_path = path
        self._update_validation()
        self.app_state.notify_change()

    def _on_height_change(self, *args) -> None:
        """Handle height value change."""
        try:
            value = float(self._height_var.get()) if self._height_var.get() else None
            self.app_state.image_input.height_cm = value
        except ValueError:
            self.app_state.image_input.height_cm = None
        self._update_validation()
        self.app_state.notify_change()

    def _update_config_status(self) -> None:
        """Update configuration status indicators."""
        # Check camera calibration
        cal_path = self.app_state.camera_calibration.get_output_path()
        camera_valid = cal_path.exists()
        self._camera_status.set_valid(camera_valid)
        self.app_state.image_input.camera_calibration_valid = camera_valid

        # Check ArUco settings
        aruco_path = self.app_state.aruco_settings.get_config_path()
        aruco_valid = aruco_path.exists()
        self._aruco_status.set_valid(aruco_valid)
        self.app_state.image_input.aruco_settings_valid = aruco_valid

        self._update_validation()

    def _update_validation(self) -> None:
        """Update validation message and button state."""
        state = self.app_state.image_input
        missing = []

        if not state.front_image_path:
            missing.append("front view image")
        if not state.height_cm:
            missing.append("subject height")
        if not state.camera_calibration_valid:
            missing.append("camera calibration")
        if not state.aruco_settings_valid:
            missing.append("ArUco settings")

        if missing:
            self._validation_label.configure(
                text=f"Missing: {', '.join(missing)}"
            )
            self._extract_button.configure(state="disabled")
            # Reset to extract mode if inputs changed
            if self._extraction_complete:
                self._extraction_complete = False
                self._extract_button.configure(
                    text="Extract Measurements",
                    command=self._extract_measurements,
                )
        else:
            self._validation_label.configure(text="")
            self._extract_button.configure(state="normal")

    def _extract_measurements(self) -> None:
        """Start the measurement extraction process."""
        self.app_state.image_input.is_extracting = True
        self._extract_button.configure(state="disabled")
        self._status_label.configure(
            text="Extracting measurements...",
            text_color=self.COLORS["status_blue"],
        )
        self.app_state.notify_change()

        thread = threading.Thread(target=self._run_extraction)
        thread.start()

    def _run_extraction(self) -> None:
        """Run extraction in background thread."""
        try:
            result = self.backend.extract_measurements(
                front_image=self.app_state.image_input.front_image_path,
                height_cm=self.app_state.image_input.height_cm,
                camera_calibration_path=self.app_state.camera_calibration.get_output_path(),
                marker_details_path=self.app_state.aruco_settings.get_config_path(),
            )
            self.after(0, lambda: self._on_extraction_complete(result))
        except Exception as e:
            self.after(0, lambda: self._on_extraction_error(str(e)))

    def _on_extraction_complete(self, result: dict) -> None:
        """Handle extraction completion on main thread."""
        self.app_state.image_input.is_extracting = False
        self.app_state.image_input.extraction_error = None

        # Update measurements state
        body = result.get("body_measurements", {})
        hair = result.get("hair_measurements", {})

        m = self.app_state.measurements
        m.height_cm = body.get("height_cm")
        m.head_width_cm = body.get("head_width_cm")
        m.shoulder_width_cm = body.get("shoulder_width_cm")
        m.hip_width_cm = body.get("hip_width_cm")
        m.upper_arm_length_cm = body.get("upper_arm_length_cm")
        m.forearm_length_cm = body.get("forearm_length_cm")
        m.upper_leg_length_cm = body.get("upper_leg_length_cm")
        m.lower_leg_length_cm = body.get("lower_leg_length_cm")
        m.shoulder_to_waist_cm = body.get("shoulder_to_waist_cm")
        m.hand_length_cm = body.get("hand_length_cm")
        m.hair_length_cm = hair.get("hair_length_cm")

        # Store visualization path if available
        if result.get("visualization_path"):
            m.visualization_path = Path(result["visualization_path"])

        m.is_extracted = True
        self._extraction_complete = True

        # Change button to "Review Measurements" mode
        self._extract_button.configure(
            state="normal",
            text="Review Measurements",
            command=self._go_to_review,
        )
        self._status_label.configure(
            text="Measurements extracted successfully!",
            text_color=self.COLORS["status_green"],
        )
        self.app_state.notify_change()

    def _on_extraction_error(self, error_message: str) -> None:
        """Handle extraction error on main thread."""
        self.app_state.image_input.is_extracting = False
        self.app_state.image_input.extraction_error = error_message

        self._extract_button.configure(state="normal")
        self._status_label.configure(
            text=f"Error: {error_message}",
            text_color=self.COLORS["status_red"],
        )
        self.app_state.notify_change()

    def _go_to_review(self) -> None:
        """Navigate to the measurements review step."""
        if self.on_navigate_next:
            self.on_navigate_next()
        else:
            self.app_state.go_next()

    def on_enter(self) -> None:
        """Called when entering this step."""
        self._update_config_status()

        # Restore button state based on extraction status
        if self.app_state.measurements.is_extracted:
            self._extraction_complete = True
            self._extract_button.configure(
                text="Review Measurements",
                command=self._go_to_review,
                state="normal",
            )
            self._status_label.configure(
                text="Measurements extracted successfully!",
                text_color=self.COLORS["status_green"],
            )
        else:
            self._extraction_complete = False
            self._extract_button.configure(
                text="Extract Measurements",
                command=self._extract_measurements,
            )

    def validate(self) -> bool:
        """Validate the step is complete."""
        return self.app_state.measurements.is_extracted
