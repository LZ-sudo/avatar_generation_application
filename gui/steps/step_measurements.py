"""
Step 2: Measurements Review

Displays extracted measurements and allows manual corrections.
"""

import customtkinter as ctk
from typing import Callable, Optional
import threading

from ..app_state import AppState
from ..backend_interface import BackendInterface


class MeasurementField(ctk.CTkFrame):
    """A single measurement input field with label and unit."""

    COLORS = {
        "label": "#374151",
    }

    def __init__(
        self,
        parent: ctk.CTkFrame,
        label: str,
        unit: str = "cm",
        value: Optional[float] = None,
        on_change: Optional[Callable[[Optional[float]], None]] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self.label_text = label
        self.unit = unit
        self.on_value_change = on_change

        self._label = ctk.CTkLabel(
            self,
            text=label,
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS["label"],
            width=180,
            anchor="w",
        )
        self._label.pack(side="left")

        self._entry_var = ctk.StringVar(value=str(value) if value is not None else "")
        self._entry_var.trace_add("write", self._handle_change)

        entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        entry_frame.pack(side="left")

        self._entry = ctk.CTkEntry(
            entry_frame,
            width=80,
            textvariable=self._entry_var,
            justify="right",
        )
        self._entry.pack(side="left")

        unit_label = ctk.CTkLabel(
            entry_frame,
            text=unit,
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["label"],
            width=30,
        )
        unit_label.pack(side="left", padx=(5, 0))

    def _handle_change(self, *args) -> None:
        """Handle value change."""
        try:
            value = float(self._entry_var.get()) if self._entry_var.get() else None
            if self.on_value_change:
                self.on_value_change(value)
        except ValueError:
            pass

    def set_value(self, value: Optional[float]) -> None:
        """Set the field value."""
        self._entry_var.set(str(value) if value is not None else "")

    @property
    def value(self) -> Optional[float]:
        """Get the current value."""
        try:
            return float(self._entry_var.get()) if self._entry_var.get() else None
        except ValueError:
            return None


class StepMeasurements(ctk.CTkFrame):
    """
    Measurements review step for the avatar generation wizard.

    Displays extracted measurements and allows manual editing.
    """

    COLORS = {
        "title": "#1f2937",
        "subtitle": "#6b7280",
        "status_blue": "#2563eb",
        "status_green": "#16a34a",
        "panel_bg": "#ffffff",
        "panel_border": "#d1d5db",
        "info_icon": "#2563eb",
        "info_text": "#6b7280",
    }

    def __init__(self, parent: ctk.CTkFrame, app_state: AppState, backend: BackendInterface):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self.backend = backend
        self._fields: dict[str, MeasurementField] = {}
        self._build()

    def _build(self) -> None:
        """Build the step content."""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=30, pady=30)

        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.pack(pady=(0, 20))

        title_label = ctk.CTkLabel(
            header_frame,
            text="Review Measurements",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.COLORS["title"],
        )
        title_label.pack()

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Verify the extracted measurements and make corrections if needed.",
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS["subtitle"],
        )
        subtitle_label.pack(pady=(8, 0))

        self._status_label = ctk.CTkLabel(
            content_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["status_blue"],
        )
        self._status_label.pack(pady=(0, 10))

        self._extract_button = ctk.CTkButton(
            content_frame,
            text="Extract Measurements",
            command=self._extract_measurements,
        )
        self._extract_button.pack(pady=(0, 20))

        measurements_data = [
            ("height_cm", "Height", "cm"),
            ("shoulder_width_cm", "Shoulder Width", "cm"),
            ("chest_circumference_cm", "Chest Circumference", "cm"),
            ("waist_circumference_cm", "Waist Circumference", "cm"),
            ("hip_circumference_cm", "Hip Circumference", "cm"),
            ("arm_length_cm", "Arm Length", "cm"),
            ("leg_length_cm", "Leg Length", "cm"),
            ("head_circumference_cm", "Head Circumference", "cm"),
        ]

        for field_name, label, unit in measurements_data:
            field = MeasurementField(
                content_frame,
                label=label,
                unit=unit,
                on_change=lambda v, fn=field_name: self._on_field_change(fn, v),
            )
            self._fields[field_name] = field

        fields_panel = ctk.CTkFrame(
            content_frame,
            fg_color=self.COLORS["panel_bg"],
            border_width=1,
            border_color=self.COLORS["panel_border"],
            corner_radius=10,
        )
        fields_panel.pack(pady=10)

        left_column = ctk.CTkFrame(fields_panel, fg_color="transparent")
        left_column.pack(side="left", padx=20, pady=20)

        self._fields["height_cm"].pack(in_=left_column, pady=8)
        self._fields["shoulder_width_cm"].pack(in_=left_column, pady=8)
        self._fields["chest_circumference_cm"].pack(in_=left_column, pady=8)
        self._fields["waist_circumference_cm"].pack(in_=left_column, pady=8)

        separator = ctk.CTkFrame(fields_panel, width=1, fg_color=self.COLORS["panel_border"])
        separator.pack(side="left", fill="y", pady=20)

        right_column = ctk.CTkFrame(fields_panel, fg_color="transparent")
        right_column.pack(side="left", padx=20, pady=20)

        self._fields["hip_circumference_cm"].pack(in_=right_column, pady=8)
        self._fields["arm_length_cm"].pack(in_=right_column, pady=8)
        self._fields["leg_length_cm"].pack(in_=right_column, pady=8)
        self._fields["head_circumference_cm"].pack(in_=right_column, pady=8)

        info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_frame.pack(pady=(20, 0))

        info_icon = ctk.CTkLabel(
            info_frame,
            text="i",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.COLORS["info_icon"],
            width=20,
        )
        info_icon.pack(side="left")

        info_text = ctk.CTkLabel(
            info_frame,
            text="Measurements are automatically extracted from images. You can manually adjust values if needed.",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["info_text"],
        )
        info_text.pack(side="left", padx=(8, 0))

    def on_enter(self) -> None:
        """Called when entering this step."""
        if not self.app_state.measurements.is_extracted:
            self._extract_measurements()
        else:
            self._populate_fields()

    def _extract_measurements(self) -> None:
        """Extract measurements from images."""
        self._status_label.configure(
            text="Extracting measurements...",
            text_color=self.COLORS["status_blue"],
        )
        self._extract_button.configure(state="disabled")

        thread = threading.Thread(target=self._run_extraction)
        thread.start()

    def _run_extraction(self) -> None:
        """Run extraction in background thread."""
        measurements = self.backend.extract_measurements(
            front_image=self.app_state.image_input.front_image_path,
            side_image=self.app_state.image_input.side_image_path,
        )

        self.after(0, lambda: self._on_extraction_complete(measurements))

    def _on_extraction_complete(self, measurements: dict) -> None:
        """Handle extraction completion on main thread."""
        self.app_state.measurements.height_cm = measurements.get("height_cm")
        self.app_state.measurements.shoulder_width_cm = measurements.get("shoulder_width_cm")
        self.app_state.measurements.chest_circumference_cm = measurements.get("chest_circumference_cm")
        self.app_state.measurements.waist_circumference_cm = measurements.get("waist_circumference_cm")
        self.app_state.measurements.hip_circumference_cm = measurements.get("hip_circumference_cm")
        self.app_state.measurements.arm_length_cm = measurements.get("arm_length_cm")
        self.app_state.measurements.leg_length_cm = measurements.get("leg_length_cm")
        self.app_state.measurements.head_circumference_cm = measurements.get("head_circumference_cm")
        self.app_state.measurements.is_extracted = True

        self._populate_fields()

        self._status_label.configure(
            text="Measurements extracted successfully",
            text_color=self.COLORS["status_green"],
        )
        self._extract_button.configure(state="normal")
        self.app_state.notify_change()

    def _populate_fields(self) -> None:
        """Populate fields from app state."""
        m = self.app_state.measurements
        self._fields["height_cm"].set_value(m.height_cm)
        self._fields["shoulder_width_cm"].set_value(m.shoulder_width_cm)
        self._fields["chest_circumference_cm"].set_value(m.chest_circumference_cm)
        self._fields["waist_circumference_cm"].set_value(m.waist_circumference_cm)
        self._fields["hip_circumference_cm"].set_value(m.hip_circumference_cm)
        self._fields["arm_length_cm"].set_value(m.arm_length_cm)
        self._fields["leg_length_cm"].set_value(m.leg_length_cm)
        self._fields["head_circumference_cm"].set_value(m.head_circumference_cm)

    def _on_field_change(self, field_name: str, value: Optional[float]) -> None:
        """Handle field value change."""
        setattr(self.app_state.measurements, field_name, value)
        self.app_state.measurements.is_manually_edited = True
        self.app_state.notify_change()

    def validate(self) -> bool:
        """Validate the step is complete."""
        return self.app_state.measurements.is_complete()
