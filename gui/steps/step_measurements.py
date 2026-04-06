"""
Step 2: Measurements Review

Displays extracted measurements with visualization and allows manual corrections.
"""

import json
import customtkinter as ctk
from typing import Callable, Optional
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
    Card,
)


class StepMeasurements(ctk.CTkFrame):
    """
    Measurements review step for the avatar generation wizard.

    Displays extracted measurements with visualization and allows manual editing.
    """

    VISUALIZATION_SIZE = (280, 360)  # Fixed size for visualization image
    VISUALIZATION_HEIGHT = 450  # Fixed height for visualization container
    MEASUREMENTS_WIDTH = 320  # Fixed width for measurements container

    def __init__(
        self,
        parent: ctk.CTkFrame,
        app_state: AppState,
        backend: BackendInterface,
        on_navigate_next: Callable[[], None] = None,
        set_tabs_locked: Optional[Callable[[bool], None]] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self.backend = backend
        self.on_navigate_next = on_navigate_next
        self._set_tabs_locked = set_tabs_locked
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
        vis_panel = Card(
            main_frame,
            width=self.VISUALIZATION_SIZE[0] + 40,  # Image width + padding
            height=self.VISUALIZATION_HEIGHT,
        )
        vis_panel.pack(side="left", padx=(0, 20))
        vis_panel.pack_propagate(False)

        vis_title = SectionTitle(vis_panel.content, text="Detection Visualization")
        vis_title.pack(pady=(5, 10))

        self._vis_label = ctk.CTkLabel(
            vis_panel.content,
            text="No visualization available",
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.SUBTITLE,
            width=self.VISUALIZATION_SIZE[0],
            height=self.VISUALIZATION_SIZE[1],
        )
        self._vis_label.pack(pady=(0, 5))

        # Right column - Measurements
        measurements_panel = Card(
            main_frame,
            width=self.MEASUREMENTS_WIDTH,
            height=self.VISUALIZATION_HEIGHT,
        )
        measurements_panel.pack(side="left")
        measurements_panel.pack_propagate(False)

        measurements_content = measurements_panel.content

        # Button area pinned to bottom (must be packed before top items)
        button_area = ctk.CTkFrame(measurements_content, fg_color="transparent")
        button_area.pack(side="bottom", fill="x", pady=(12, 0))

        self._status_label = StatusLabel(button_area, text="")
        self._status_label.pack(side="bottom")

        self._configure_button = ActionButton(
            button_area,
            text="Configure Mesh",
            width=200,
            height=40,
            command=self._compute_parameters,
        )
        self._configure_button.pack(side="bottom", pady=(5, 2))

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
        ]

        for field_name, label in all_measurements:
            field = LabeledInputField(
                measurements_content,
                label=label,
                unit="cm",
                on_change=lambda v, fn=field_name: self._on_field_change(fn, v),
            )
            field.pack(anchor="w", pady=2)
            self._fields[field_name] = field

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
                    f"{converged}/{total} measurements converged, Mean error: {mean_error:.2f}cm"
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

    def _on_field_change(self, field_name: str, value: Optional[float]) -> None:
        """Handle field value change."""
        setattr(self.app_state.measurements, field_name, value)
        self.app_state.measurements.is_manually_edited = True
        self.app_state.notify_change()

    def _compute_parameters(self) -> None:
        """Start the mesh parameter computation process."""
        if self._set_tabs_locked:
            self._set_tabs_locked(True)
        self.app_state.measurements.is_computing_parameters = True
        self.app_state.measurements.parameters_error = None
        # Disable all input fields during processing
        for field in self._fields.values():
            field.set_enabled(False)
        # Disable button and show processing state
        self._configure_button.start_processing("Configuring Mesh...")
        self._status_label.set_info("This process will take 2-3 minutes")
        self.app_state.notify_change()

        thread = threading.Thread(target=self._run_parameter_computation)
        thread.start()

    def _sync_measurements_to_file(self) -> None:
        """Write current app state measurements back to measurements.json on disk.

        Ensures user edits (including manually filled missing fields) are
        persisted before the mesh parameter computation reads the file.
        """
        measurements_path = self.app_state.measurements.get_measurements_path()
        if not measurements_path.exists():
            return

        with open(measurements_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        body = data.get("body_measurements", {})
        m = self.app_state.measurements
        for field_name in [
            "height_cm", "head_width_cm", "shoulder_width_cm", "hip_width_cm",
            "shoulder_to_waist_cm", "upper_arm_length_cm", "forearm_length_cm",
            "upper_leg_length_cm", "lower_leg_length_cm", "hand_length_cm",
        ]:
            value = getattr(m, field_name, None)
            if value is not None:
                body[field_name] = value
            else:
                body.pop(field_name, None)

        data["body_measurements"] = body
        with open(measurements_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _run_parameter_computation(self) -> None:
        """Run parameter computation in background thread."""
        try:
            self._sync_measurements_to_file()
            measurements_path = self.app_state.measurements.get_measurements_path()
            result = self.backend.compute_mesh_parameters(measurements_path)
            self.after(0, lambda: self._on_computation_complete(result))
        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: self._on_computation_error(error_msg))

    def _on_computation_complete(self, result: dict) -> None:
        """Handle computation completion on main thread."""
        self.app_state.measurements.is_computing_parameters = False
        if self._set_tabs_locked:
            self._set_tabs_locked(False)
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

        # Update button text and re-enable for navigation
        self._configure_button.stop_processing("Review Accuracy")
        self._configure_button.configure(command=self._navigate_to_accuracy_review)

        self._status_label.set_success(
            f"{converged}/{total} measurements converged, Mean error: {mean_error:.2f}cm"
        )
        self.app_state.notify_change()

    def _navigate_to_accuracy_review(self) -> None:
        """Navigate to the Accuracy Review step."""
        if self.on_navigate_next:
            self.on_navigate_next()

    def _on_computation_error(self, error_message: str) -> None:
        """Handle computation error on main thread."""
        self.app_state.measurements.is_computing_parameters = False
        if self._set_tabs_locked:
            self._set_tabs_locked(False)
        self.app_state.measurements.parameters_error = error_message
        # Re-enable all input fields
        for field in self._fields.values():
            field.set_enabled(True)

        self._configure_button.stop_processing("Configure Mesh")

        # Show error message
        error_text = f"Error: {error_message[:80]}..." if len(error_message) > 80 else f"Error: {error_message}"
        self._status_label.set_error(error_text)
        self.app_state.notify_change()

    def validate(self) -> bool:
        """Validate the step is complete."""
        return self.app_state.measurements.is_complete()
