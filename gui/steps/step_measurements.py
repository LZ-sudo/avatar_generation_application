"""
Step 2: Measurements Review

Displays extracted measurements with visualization and allows manual corrections.
"""

import customtkinter as ctk
from typing import Callable, Optional
from pathlib import Path
from PIL import Image
import threading

from ..app_state import AppState
from ..backend_interface import BackendInterface
from ..components.ui_elements import (
    ThemeColors,
    PageHeader,
    SectionTitle,
    LabeledInputField,
    ActionButton,
    StatusLabel,
)


class StepMeasurements(ctk.CTkFrame):
    """
    Measurements review step for the avatar generation wizard.

    Displays extracted measurements with visualization and allows manual editing.
    """

    VISUALIZATION_SIZE = (350, 450)

    def __init__(
        self,
        parent: ctk.CTkFrame,
        app_state: AppState,
        backend: BackendInterface,
        on_navigate_next: Callable[[], None] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self.backend = backend
        self.on_navigate_next = on_navigate_next
        self._fields: dict[str, LabeledInputField] = {}
        self._computation_complete = False
        self._build()

    def _build(self) -> None:
        """Build the step content."""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=30, pady=20)

        # Header
        header = PageHeader(
            content_frame,
            title="Review Measurements",
            subtitle="Verify the extracted measurements and make corrections if needed.",
        )
        header.pack(pady=(0, 10))

        # Main content (two columns)
        main_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        main_frame.pack(pady=10)

        # Left column - Visualization
        vis_panel = ctk.CTkFrame(
            main_frame,
            fg_color=ThemeColors.PANEL_BG,
            border_width=1,
            border_color=ThemeColors.PANEL_BORDER,
            corner_radius=10,
            width=self.VISUALIZATION_SIZE[0] + 20,
            height=self.VISUALIZATION_SIZE[1] + 60,
        )
        vis_panel.pack(side="left", padx=(0, 20))
        vis_panel.pack_propagate(False)

        vis_title = SectionTitle(vis_panel, text="Detection Visualization")
        vis_title.pack(pady=(15, 10))

        self._vis_label = ctk.CTkLabel(
            vis_panel,
            text="No visualization available",
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.SUBTITLE,
            width=self.VISUALIZATION_SIZE[0],
            height=self.VISUALIZATION_SIZE[1],
        )
        self._vis_label.pack(padx=10, pady=(0, 10))

        # Right column - Measurements
        right_column = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_column.pack(side="left", fill="y")

        # Extracted measurements panel
        measurements_panel = ctk.CTkFrame(
            right_column,
            fg_color=ThemeColors.PANEL_BG,
            border_width=1,
            border_color=ThemeColors.PANEL_BORDER,
            corner_radius=10,
        )
        measurements_panel.pack(fill="x")

        measurements_content = ctk.CTkFrame(measurements_panel, fg_color="transparent")
        measurements_content.pack(padx=20, pady=15)

        measurements_title = SectionTitle(measurements_content, text="Extracted Measurements")
        measurements_title.pack(anchor="w", pady=(0, 10))

        # All measurement fields
        all_measurements = [
            ("height_cm", "Height"),
            ("head_width_cm", "Head Width"),
            ("shoulder_width_cm", "Shoulder Width"),
            ("hip_width_cm", "Hip Width"),
            ("shoulder_to_waist_cm", "Shoulder to Waist"),
            ("upper_arm_length_cm", "Upper Arm Length"),
            ("forearm_length_cm", "Forearm Length"),
            ("upper_leg_length_cm", "Upper Leg Length"),
            ("lower_leg_length_cm", "Lower Leg Length"),
            ("hand_length_cm", "Hand Length"),
            ("hair_length_cm", "Hair Length"),
        ]

        for field_name, label in all_measurements:
            field = LabeledInputField(
                measurements_content,
                label=label,
                unit="cm",
                on_change=lambda v, fn=field_name: self._on_field_change(fn, v),
            )
            field.pack(anchor="w", pady=3)
            self._fields[field_name] = field

        # Info text below measurements
        info_label = ctk.CTkLabel(
            measurements_content,
            text="You can manually adjust values if needed.",
            font=ctk.CTkFont(size=11),
            text_color=ThemeColors.INFO_TEXT,
        )
        info_label.pack(anchor="w", pady=(8, 0))

        # Configure Mesh button (inside right column, below measurements panel)
        button_frame = ctk.CTkFrame(right_column, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        self._configure_button = ActionButton(
            button_frame,
            text="Configure Mesh",
            width=180,
            height=40,
            command=self._compute_parameters,
        )
        self._configure_button.pack()

        # Status label for parameter computation
        self._status_label = StatusLabel(button_frame, text="")
        self._status_label.pack(pady=(8, 0))

    def on_enter(self) -> None:
        """Called when entering this step."""
        self._populate_fields()
        self._load_visualization()
        self._update_button_state()

    def _update_button_state(self) -> None:
        """Update button state based on computation status."""
        if self.app_state.measurements.parameters_computed:
            self._computation_complete = True
            self._configure_button.configure(
                text="Review Accuracy",
                state="normal",
                command=self._navigate_to_accuracy_review,
            )
            # Show previous result summary if available
            report = self.app_state.measurements.parameters_report
            if report:
                summary = report.get("summary", {})
                converged = summary.get("converged_count", 0)
                total = summary.get("total_measurements", 0)
                mean_error = summary.get("mean_absolute_error", 0)
                self._status_label.set_success(
                    f"Parameters computed! {converged}/{total} converged, MAE: {mean_error:.2f}cm"
                )
        else:
            self._computation_complete = False
            self._configure_button.configure(
                text="Configure Mesh",
                state="normal",
                command=self._compute_parameters,
            )
            self._status_label.clear()

    def _load_visualization(self) -> None:
        """Load and display the visualization image."""
        vis_path = self.app_state.measurements.visualization_path

        if vis_path and vis_path.exists():
            try:
                pil_image = Image.open(vis_path)

                # Scale to fit while maintaining aspect ratio
                max_w, max_h = self.VISUALIZATION_SIZE
                pil_image.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)

                ctk_image = ctk.CTkImage(
                    light_image=pil_image,
                    dark_image=pil_image,
                    size=(pil_image.width, pil_image.height),
                )

                self._vis_label.configure(image=ctk_image, text="")
                self._vis_label._image = ctk_image
            except Exception:
                self._vis_label.configure(
                    image=None,
                    text="Could not load visualization"
                )
        else:
            self._vis_label.configure(
                image=None,
                text="No visualization available"
            )

    def _populate_fields(self) -> None:
        """Populate fields from app state."""
        m = self.app_state.measurements
        self._fields["height_cm"].set_value(m.height_cm)
        self._fields["head_width_cm"].set_value(m.head_width_cm)
        self._fields["shoulder_width_cm"].set_value(m.shoulder_width_cm)
        self._fields["hip_width_cm"].set_value(m.hip_width_cm)
        self._fields["shoulder_to_waist_cm"].set_value(m.shoulder_to_waist_cm)
        self._fields["upper_arm_length_cm"].set_value(m.upper_arm_length_cm)
        self._fields["forearm_length_cm"].set_value(m.forearm_length_cm)
        self._fields["upper_leg_length_cm"].set_value(m.upper_leg_length_cm)
        self._fields["lower_leg_length_cm"].set_value(m.lower_leg_length_cm)
        self._fields["hand_length_cm"].set_value(m.hand_length_cm)
        self._fields["hair_length_cm"].set_value(m.hair_length_cm)

    def _on_field_change(self, field_name: str, value: Optional[float]) -> None:
        """Handle field value change."""
        setattr(self.app_state.measurements, field_name, value)
        self.app_state.measurements.is_manually_edited = True
        self.app_state.notify_change()

    def _compute_parameters(self) -> None:
        """Start the mesh parameter computation process."""
        self.app_state.measurements.is_computing_parameters = True
        self.app_state.measurements.parameters_error = None
        # Disable all input fields during processing
        for field in self._fields.values():
            field.set_enabled(False)
        self._configure_button.start_processing("Configuring Mesh...")
        self._status_label.set_info("Computing mesh parameters...")
        self.app_state.notify_change()

        thread = threading.Thread(target=self._run_parameter_computation)
        thread.start()

    def _run_parameter_computation(self) -> None:
        """Run parameter computation in background thread."""
        try:
            measurements_path = self.app_state.measurements.get_measurements_path()
            result = self.backend.compute_mesh_parameters(measurements_path)
            self.after(0, lambda: self._on_computation_complete(result))
        except Exception as e:
            self.after(0, lambda: self._on_computation_error(str(e)))

    def _on_computation_complete(self, result: dict) -> None:
        """Handle computation completion on main thread."""
        self.app_state.measurements.is_computing_parameters = False
        self.app_state.measurements.parameters_computed = True
        self.app_state.measurements.parameters_report = result
        self.app_state.measurements.parameters_error = None
        self._computation_complete = True
        # Re-enable all input fields
        for field in self._fields.values():
            field.set_enabled(True)

        # Show summary from report
        summary = result.get("summary", {})
        converged = summary.get("converged_count", 0)
        total = summary.get("total_measurements", 0)
        mean_error = summary.get("mean_absolute_error", 0)

        # Change button to "Review Accuracy" for navigation
        self._configure_button.stop_processing("Review Accuracy", self._navigate_to_accuracy_review)
        self._status_label.set_success(
            f"Parameters computed! {converged}/{total} converged, MAE: {mean_error:.2f}cm"
        )
        self.app_state.notify_change()

    def _navigate_to_accuracy_review(self) -> None:
        """Navigate to the Accuracy Review step."""
        if self.on_navigate_next:
            self.on_navigate_next()

    def _on_computation_error(self, error_message: str) -> None:
        """Handle computation error on main thread."""
        self.app_state.measurements.is_computing_parameters = False
        self.app_state.measurements.parameters_error = error_message
        # Re-enable all input fields
        for field in self._fields.values():
            field.set_enabled(True)

        self._configure_button.stop_processing()
        error_text = f"Error: {error_message[:50]}..." if len(error_message) > 50 else f"Error: {error_message}"
        self._status_label.set_error(error_text)
        self.app_state.notify_change()

    def validate(self) -> bool:
        """Validate the step is complete."""
        return self.app_state.measurements.is_complete()
