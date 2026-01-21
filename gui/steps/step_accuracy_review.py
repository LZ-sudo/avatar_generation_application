"""
Step 3: Mesh Accuracy Review

Displays the comparison between target measurements and actual mesh measurements
to help users decide whether to proceed with the generated parameters.
"""

import customtkinter as ctk
from typing import Callable, Optional

from ..app_state import AppState
from ..components.ui_elements import ThemeColors, PageHeader, ActionButton


class MeasurementRow(ctk.CTkFrame):
    """A single row in the measurement comparison table."""

    # Row width matches table width
    ROW_WIDTH = 455

    def __init__(
        self,
        parent: ctk.CTkFrame,
        measurement_name: str,
        target: float,
        actual: float,
        error: float,
        converged: bool,
        is_alternate: bool = False,
    ):
        bg_color = ThemeColors.ROW_ALT_BG if is_alternate else ThemeColors.ROW_BG
        super().__init__(parent, fg_color=bg_color, height=32, width=self.ROW_WIDTH)
        self.pack_propagate(False)

        # Measurement name
        name_label = ctk.CTkLabel(
            self,
            text=measurement_name,
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.LABEL,
            width=150,
            anchor="w",
        )
        name_label.pack(side="left", padx=(10, 5))

        # Target value
        target_label = ctk.CTkLabel(
            self,
            text=f"{target:.2f}",
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.LABEL,
            width=70,
            anchor="e",
        )
        target_label.pack(side="left", padx=5)

        # Actual value
        actual_label = ctk.CTkLabel(
            self,
            text=f"{actual:.2f}",
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.LABEL,
            width=70,
            anchor="e",
        )
        actual_label.pack(side="left", padx=5)

        # Error value
        error_color = ThemeColors.STATUS_GREEN if converged else ThemeColors.STATUS_RED
        error_text = f"{error:+.3f}"
        error_label = ctk.CTkLabel(
            self,
            text=error_text,
            font=ctk.CTkFont(size=12),
            text_color=error_color,
            width=70,
            anchor="e",
        )
        error_label.pack(side="left", padx=5)

        # Status indicator
        status_text = "OK" if converged else "!"
        status_color = ThemeColors.STATUS_GREEN if converged else ThemeColors.STATUS_RED
        status_label = ctk.CTkLabel(
            self,
            text=status_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=status_color,
            width=40,
            anchor="center",
        )
        status_label.pack(side="left", padx=5)


class StepAccuracyReview(ctk.CTkFrame):
    """
    Mesh accuracy review step for the avatar generation wizard.

    Displays the comparison between target measurements and actual mesh measurements.
    """

    # Table width: columns (150+70+70+70+40=400) + padding (~55) = 455px
    TABLE_WIDTH = 455

    # Measurement display names
    MEASUREMENT_LABELS = {
        "height_cm": "Height",
        "head_width_cm": "Head Width",
        "shoulder_width_cm": "Shoulder Width",
        "hip_width_cm": "Hip Width",
        "shoulder_to_waist_cm": "Shoulder to Waist",
        "upper_arm_length_cm": "Upper Arm Length",
        "forearm_length_cm": "Forearm Length",
        "upper_leg_length_cm": "Upper Leg Length",
        "lower_leg_length_cm": "Lower Leg Length",
        "hand_length_cm": "Hand Length",
    }

    def __init__(
        self,
        parent: ctk.CTkFrame,
        app_state: AppState,
        on_navigate_next: Callable[[], None] = None,
        on_navigate_back: Callable[[], None] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self.on_navigate_next = on_navigate_next
        self.on_navigate_back = on_navigate_back
        self._measurement_rows: list[MeasurementRow] = []
        self._build()

    def _build(self) -> None:
        """Build the step content."""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=30, pady=20)

        # Header
        header = PageHeader(
            content_frame,
            title="Mesh Accuracy Review",
            subtitle="Review the accuracy of the generated mesh parameters before proceeding.",
        )
        header.pack(pady=(0, 10))

        # Main content panel - centered with content-fitting width
        main_panel = ctk.CTkFrame(
            content_frame,
            fg_color=ThemeColors.PANEL_BG,
            border_width=1,
            border_color=ThemeColors.PANEL_BORDER,
            corner_radius=10,
        )
        main_panel.pack(pady=10)

        panel_content = ctk.CTkFrame(main_panel, fg_color="transparent")
        panel_content.pack(padx=20, pady=15)

        # Summary section
        self._summary_frame = ctk.CTkFrame(panel_content, fg_color="transparent")
        self._summary_frame.pack(fill="x", pady=(0, 15))

        # Table header
        header_row = ctk.CTkFrame(
            panel_content,
            fg_color=ThemeColors.HEADER_BG,
            height=32,
            width=self.TABLE_WIDTH,
        )
        header_row.pack()
        header_row.pack_propagate(False)

        headers = [
            ("Measurement", 150, "w"),
            ("Target (cm)", 70, "e"),
            ("Actual (cm)", 70, "e"),
            ("Error (cm)", 70, "e"),
            ("Status", 40, "center"),
        ]

        for text, width, anchor in headers:
            label = ctk.CTkLabel(
                header_row,
                text=text,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=ThemeColors.HEADER_TEXT,
                width=width,
                anchor=anchor,
            )
            label.pack(side="left", padx=5 if text != "Measurement" else (10, 5))

        # Measurement rows container
        self._rows_container = ctk.CTkFrame(
            panel_content,
            fg_color="transparent",
            width=self.TABLE_WIDTH,
        )
        self._rows_container.pack()

        # Button frame - centered with same width as panel
        button_frame = ctk.CTkFrame(
            content_frame,
            fg_color="transparent",
            width=self.TABLE_WIDTH + 40,  # Account for panel padding
            height=40,
        )
        button_frame.pack(pady=(10, 0))
        button_frame.pack_propagate(False)

        # Back button
        self._back_button = ActionButton(
            button_frame,
            text="Back to Measurements",
            command=self._on_back_click,
            primary=False,
            fg_color="#6b7280",
            hover_color="#4b5563",
        )
        self._back_button.pack(side="left")

        # Proceed button
        self._proceed_button = ActionButton(
            button_frame,
            text="Proceed to Configure",
            command=self._on_proceed_click,
            primary=True,
        )
        self._proceed_button.pack(side="right")

    def on_enter(self) -> None:
        """Called when entering this step."""
        self._populate_data()

    def _populate_data(self) -> None:
        """Populate the table with measurement comparison data."""
        # Clear existing rows
        for row in self._measurement_rows:
            row.destroy()
        self._measurement_rows.clear()

        # Clear summary
        for widget in self._summary_frame.winfo_children():
            widget.destroy()

        report = self.app_state.measurements.parameters_report
        if not report:
            no_data_label = ctk.CTkLabel(
                self._rows_container,
                text="No parameters report available. Please compute mesh parameters first.",
                font=ctk.CTkFont(size=12),
                text_color=ThemeColors.SUBTITLE,
            )
            no_data_label.pack(pady=20)
            return

        measurements = report.get("measurements", {})
        summary = report.get("summary", {})

        # Populate summary
        self._create_summary(summary)

        # Populate measurement rows
        for i, (key, label) in enumerate(self.MEASUREMENT_LABELS.items()):
            if key in measurements:
                data = measurements[key]
                row = MeasurementRow(
                    self._rows_container,
                    measurement_name=label,
                    target=data.get("target", 0),
                    actual=data.get("actual", 0),
                    error=data.get("error", 0),
                    converged=data.get("converged", False),
                    is_alternate=(i % 2 == 1),
                )
                row.pack()
                self._measurement_rows.append(row)

    def _create_summary(self, summary: dict) -> None:
        """Create the summary section."""
        converged_count = summary.get("converged_count", 0)
        total_measurements = summary.get("total_measurements", 0)
        mean_error = summary.get("mean_absolute_error", 0)
        max_error = summary.get("max_absolute_error", 0)
        all_converged = summary.get("all_converged", False)

        # Summary row
        summary_row = ctk.CTkFrame(self._summary_frame, fg_color="transparent")
        summary_row.pack(fill="x")

        # Convergence status
        conv_color = ThemeColors.STATUS_GREEN if all_converged else ThemeColors.STATUS_BLUE
        conv_text = f"Converged: {converged_count}/{total_measurements}"
        conv_label = ctk.CTkLabel(
            summary_row,
            text=conv_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=conv_color,
        )
        conv_label.pack(side="left", padx=(0, 20))

        # Mean Absolute Error
        mae_label = ctk.CTkLabel(
            summary_row,
            text=f"Mean Error: {mean_error:.3f} cm",
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.LABEL,
        )
        mae_label.pack(side="left", padx=(0, 20))

        # Max Error
        max_color = ThemeColors.STATUS_RED if max_error > 1.0 else ThemeColors.LABEL
        max_label = ctk.CTkLabel(
            summary_row,
            text=f"Max Error: {max_error:.3f} cm",
            font=ctk.CTkFont(size=12),
            text_color=max_color,
        )
        max_label.pack(side="left")

        # Info text
        if not all_converged:
            info_text = "Some measurements did not converge. You may proceed or go back to adjust measurements."
            info_label = ctk.CTkLabel(
                self._summary_frame,
                text=info_text,
                font=ctk.CTkFont(size=11),
                text_color=ThemeColors.SUBTITLE,
            )
            info_label.pack(anchor="w", pady=(8, 0))

    def _on_back_click(self) -> None:
        """Handle back button click."""
        if self.on_navigate_back:
            self.on_navigate_back()

    def _on_proceed_click(self) -> None:
        """Handle proceed button click."""
        if self.on_navigate_next:
            self.on_navigate_next()

    def validate(self) -> bool:
        """Validate the step is complete."""
        return self.app_state.measurements.parameters_computed
