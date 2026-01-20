"""
Step 2: Measurements Review

Displays extracted measurements with visualization and allows manual corrections.
"""

import customtkinter as ctk
from typing import Callable, Optional
from pathlib import Path
from PIL import Image

from ..app_state import AppState


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
            font=ctk.CTkFont(size=13),
            text_color=self.COLORS["label"],
            width=160,
            anchor="w",
        )
        self._label.pack(side="left")

        self._entry_var = ctk.StringVar(value=str(value) if value is not None else "")
        self._entry_var.trace_add("write", self._handle_change)

        entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        entry_frame.pack(side="left")

        self._entry = ctk.CTkEntry(
            entry_frame,
            width=70,
            textvariable=self._entry_var,
            justify="right",
        )
        self._entry.pack(side="left")

        unit_label = ctk.CTkLabel(
            entry_frame,
            text=unit,
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["label"],
            width=25,
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
        if value is not None:
            self._entry_var.set(f"{value:.1f}")
        else:
            self._entry_var.set("")

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

    Displays extracted measurements with visualization and allows manual editing.
    """

    COLORS = {
        "title": "#1f2937",
        "subtitle": "#6b7280",
        "panel_bg": "#ffffff",
        "panel_border": "#d1d5db",
        "info_icon": "#2563eb",
        "info_text": "#6b7280",
        "section_title": "#374151",
    }

    VISUALIZATION_SIZE = (350, 450)

    def __init__(self, parent: ctk.CTkFrame, app_state: AppState):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self._fields: dict[str, MeasurementField] = {}
        self._build()

    def _build(self) -> None:
        """Build the step content."""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=30, pady=30)

        # Header
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

        # Main content (two columns)
        main_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        main_frame.pack(pady=10)

        # Left column - Visualization
        vis_panel = ctk.CTkFrame(
            main_frame,
            fg_color=self.COLORS["panel_bg"],
            border_width=1,
            border_color=self.COLORS["panel_border"],
            corner_radius=10,
            width=self.VISUALIZATION_SIZE[0] + 20,
            height=self.VISUALIZATION_SIZE[1] + 60,
        )
        vis_panel.pack(side="left", padx=(0, 20))
        vis_panel.pack_propagate(False)

        vis_title = ctk.CTkLabel(
            vis_panel,
            text="Detection Visualization",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.COLORS["section_title"],
        )
        vis_title.pack(pady=(15, 10))

        self._vis_label = ctk.CTkLabel(
            vis_panel,
            text="No visualization available",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["subtitle"],
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
            fg_color=self.COLORS["panel_bg"],
            border_width=1,
            border_color=self.COLORS["panel_border"],
            corner_radius=10,
        )
        measurements_panel.pack(fill="x")

        measurements_content = ctk.CTkFrame(measurements_panel, fg_color="transparent")
        measurements_content.pack(padx=20, pady=15)

        measurements_title = ctk.CTkLabel(
            measurements_content,
            text="Extracted Measurements",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.COLORS["section_title"],
        )
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
            field = MeasurementField(
                measurements_content,
                label=label,
                unit="cm",
                on_change=lambda v, fn=field_name: self._on_field_change(fn, v),
            )
            field.pack(anchor="w", pady=3)
            self._fields[field_name] = field

        # Info frame
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
            text="Measurements were automatically extracted. You can manually adjust values if needed.",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["info_text"],
        )
        info_text.pack(side="left", padx=(8, 0))

    def on_enter(self) -> None:
        """Called when entering this step."""
        self._populate_fields()
        self._load_visualization()

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

    def validate(self) -> bool:
        """Validate the step is complete."""
        return self.app_state.measurements.is_complete()
