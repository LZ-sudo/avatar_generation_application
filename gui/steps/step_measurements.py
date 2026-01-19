"""
Step 2: Measurements Review

Displays extracted measurements and allows manual corrections.
"""

import flet as ft
from typing import Callable

from ..app_state import AppState
from ..backend_interface import BackendInterface


class MeasurementField(ft.Row):
    """A single measurement input field with label and unit."""

    def __init__(
        self,
        label: str,
        unit: str = "cm",
        value: float = None,
        on_change: Callable[[float], None] = None,
    ):
        super().__init__()
        self.label_text = label
        self.unit = unit
        self.on_value_change = on_change

        self._text_field = ft.TextField(
            value=str(value) if value is not None else "",
            width=100,
            text_align=ft.TextAlign.RIGHT,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._handle_change,
            suffix=ft.Text(unit),
            dense=True,
        )

        self.controls = [
            ft.Text(label, size=14, width=180, color=ft.Colors.GREY_700),
            self._text_field,
        ]
        self.alignment = ft.MainAxisAlignment.SPACE_BETWEEN
        self.width = 320

    def _handle_change(self, e: ft.ControlEvent) -> None:
        """Handle value change."""
        try:
            value = float(e.control.value) if e.control.value else None
            if self.on_value_change:
                self.on_value_change(value)
        except ValueError:
            pass

    def set_value(self, value: float) -> None:
        """Set the field value."""
        self._text_field.value = str(value) if value is not None else ""
        self._text_field.update()

    @property
    def value(self) -> float:
        """Get the current value."""
        try:
            return float(self._text_field.value) if self._text_field.value else None
        except ValueError:
            return None


class StepMeasurements(ft.Container):
    """
    Measurements review step for the avatar generation wizard.

    Displays extracted measurements and allows manual editing.
    """

    def __init__(self, app_state: AppState, backend: BackendInterface):
        super().__init__()
        self.app_state = app_state
        self.backend = backend
        self._fields: dict[str, MeasurementField] = {}
        self._build()

    def _build(self) -> None:
        """Build the step content."""
        header = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Review Measurements",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_800,
                    ),
                    ft.Text(
                        "Verify the extracted measurements and make corrections if needed.",
                        size=14,
                        color=ft.Colors.GREY_600,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=ft.Padding.only(bottom=20),
        )

        self._status_text = ft.Text(
            "",
            size=12,
            color=ft.Colors.BLUE_600,
            text_align=ft.TextAlign.CENTER,
        )

        self._extract_button = ft.Button(
            "Extract Measurements",
            icon=ft.Icons.AUTO_FIX_HIGH,
            on_click=self._extract_measurements,
        )

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
                label=label,
                unit=unit,
                on_change=lambda v, fn=field_name: self._on_field_change(fn, v),
            )
            self._fields[field_name] = field

        left_column = ft.Column(
            controls=[
                self._fields["height_cm"],
                self._fields["shoulder_width_cm"],
                self._fields["chest_circumference_cm"],
                self._fields["waist_circumference_cm"],
            ],
            spacing=15,
        )

        right_column = ft.Column(
            controls=[
                self._fields["hip_circumference_cm"],
                self._fields["arm_length_cm"],
                self._fields["leg_length_cm"],
                self._fields["head_circumference_cm"],
            ],
            spacing=15,
        )

        fields_row = ft.Row(
            controls=[
                ft.Container(content=left_column, padding=20),
                ft.VerticalDivider(width=1, color=ft.Colors.GREY_300),
                ft.Container(content=right_column, padding=20),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        fields_container = ft.Container(
            content=fields_row,
            bgcolor=ft.Colors.WHITE,
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            padding=10,
        )

        info_text = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=ft.Colors.BLUE_600),
                    ft.Text(
                        "Measurements are automatically extracted from images. "
                        "You can manually adjust values if needed.",
                        size=12,
                        color=ft.Colors.GREY_600,
                    ),
                ],
                spacing=8,
            ),
            margin=ft.Margin.only(top=20),
        )

        self.content = ft.Column(
            controls=[
                header,
                self._extract_button,
                self._status_text,
                fields_container,
                info_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        )

        self.padding = 30
        self.expand = True

    def on_enter(self) -> None:
        """Called when entering this step."""
        if not self.app_state.measurements.is_extracted:
            self._extract_measurements(None)
        else:
            self._populate_fields()

    def _extract_measurements(self, e) -> None:
        """Extract measurements from images."""
        self._status_text.value = "Extracting measurements..."
        self._status_text.color = ft.Colors.BLUE_600
        self._extract_button.disabled = True
        self.update()

        measurements = self.backend.extract_measurements(
            front_image=self.app_state.image_input.front_image_path,
            side_image=self.app_state.image_input.side_image_path,
        )

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

        self._status_text.value = "Measurements extracted successfully"
        self._status_text.color = ft.Colors.GREEN_600
        self._extract_button.disabled = False
        self.app_state.notify_change()
        self.update()

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

    def _on_field_change(self, field_name: str, value: float) -> None:
        """Handle field value change."""
        setattr(self.app_state.measurements, field_name, value)
        self.app_state.measurements.is_manually_edited = True
        self.app_state.notify_change()

    def validate(self) -> bool:
        """Validate the step is complete."""
        return self.app_state.measurements.is_complete()
