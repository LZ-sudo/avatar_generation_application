"""
ArUco Settings Feature View

Provides UI for configuring ArUco marker positions and size.
"""

import customtkinter as ctk
from pathlib import Path

from PIL import Image

from ..app_state import AppState
from ..components.ui_elements import (
    ThemeColors,
    PageHeader,
    SectionTitle,
    ActionButton,
    StatusLabel,
)


class ArucoSettingsView(ctk.CTkFrame):
    """
    ArUco settings view component.

    Allows users to configure ArUco marker positions and size for measurement calibration.
    """

    GUIDE_IMAGE_SIZE = (466, 400)

    def __init__(self, parent: ctk.CTkFrame, app_state: AppState):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state

        self._build()
        self._load_existing_settings()

    def _build(self) -> None:
        """Build the view content."""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=30, pady=30)

        header = PageHeader(
            content_frame,
            title="ArUco Marker Settings",
            subtitle="Configure the positions and size of ArUco markers on your backdrop.",
            title_size=24,
            subtitle_size=14,
        )
        header.pack(pady=(0, 20))

        panels_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        panels_frame.pack(fill="both", expand=True)

        image_panel = self._create_image_panel(panels_frame)
        image_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_frame = ctk.CTkFrame(panels_frame, fg_color="transparent")
        right_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))

        current_settings_panel = self._create_current_settings_panel(right_frame)
        current_settings_panel.pack(fill="both", expand=True, pady=(0, 10))

        update_settings_panel = self._create_update_settings_panel(right_frame)
        update_settings_panel.pack(fill="both", expand=True, pady=(10, 0))

    def _create_image_panel(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create the ArUco guide image panel."""
        panel = ctk.CTkFrame(
            parent,
            fg_color=ThemeColors.PANEL_BG,
            border_width=1,
            border_color=ThemeColors.PANEL_BORDER,
            corner_radius=10,
        )

        content = ctk.CTkFrame(panel, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=15)

        title = SectionTitle(content, text="Marker Positioning Guide", font_size=16)
        title.pack(anchor="w")

        separator = ctk.CTkFrame(content, height=1, fg_color=ThemeColors.PANEL_BORDER)
        separator.pack(fill="x", pady=(10, 12))

        image_frame = ctk.CTkFrame(content, fg_color="transparent")
        image_frame.pack(fill="both", expand=True)

        guide_image_path = Path(__file__).parent.parent / "images" / "ArUco_guide.png"
        if guide_image_path.exists():
            original_image = Image.open(guide_image_path)
            guide_ctk_image = ctk.CTkImage(
                light_image=original_image,
                dark_image=original_image,
                size=self.GUIDE_IMAGE_SIZE,
            )
            image_label = ctk.CTkLabel(
                image_frame,
                image=guide_ctk_image,
                text="",
            )
            image_label.pack(expand=True)
            image_label._ctk_image = guide_ctk_image

        return panel

    def _create_current_settings_panel(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create the current settings display panel."""
        panel = ctk.CTkFrame(
            parent,
            fg_color=ThemeColors.PANEL_BG,
            border_width=1,
            border_color=ThemeColors.PANEL_BORDER,
            corner_radius=10,
        )

        content = ctk.CTkFrame(panel, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=15)

        title = SectionTitle(content, text="Current Settings", font_size=16)
        title.pack(anchor="w")

        separator = ctk.CTkFrame(content, height=1, fg_color=ThemeColors.PANEL_BORDER)
        separator.pack(fill="x", pady=(10, 12))

        settings_frame = ctk.CTkFrame(content, fg_color="transparent")
        settings_frame.pack(fill="both", expand=True)

        self._current_marker_size_label = ctk.CTkLabel(
            settings_frame,
            text="Marker Size: -- cm",
            font=ctk.CTkFont(size=14),
            text_color=ThemeColors.LABEL,
        )
        self._current_marker_size_label.pack(anchor="w", pady=(0, 8))

        positions_label = ctk.CTkLabel(
            settings_frame,
            text="Marker Positions (cm):",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=ThemeColors.LABEL,
        )
        positions_label.pack(anchor="w", pady=(4, 4))

        self._current_top_left_label = ctk.CTkLabel(
            settings_frame,
            text="  Top Left:       X: --    Y: --",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=ThemeColors.SUBTITLE,
        )
        self._current_top_left_label.pack(anchor="w", pady=2)

        self._current_top_right_label = ctk.CTkLabel(
            settings_frame,
            text="  Top Right:      X: --    Y: --",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=ThemeColors.SUBTITLE,
        )
        self._current_top_right_label.pack(anchor="w", pady=2)

        self._current_bottom_left_label = ctk.CTkLabel(
            settings_frame,
            text="  Bottom Left:    X: --    Y: --",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=ThemeColors.SUBTITLE,
        )
        self._current_bottom_left_label.pack(anchor="w", pady=2)

        self._current_bottom_right_label = ctk.CTkLabel(
            settings_frame,
            text="  Bottom Right:   X: --    Y: --",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=ThemeColors.SUBTITLE,
        )
        self._current_bottom_right_label.pack(anchor="w", pady=2)

        self._status_label = StatusLabel(settings_frame, text="")
        self._status_label.pack(anchor="w", pady=(8, 0))

        return panel

    def _create_update_settings_panel(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create the update settings input panel."""
        panel = ctk.CTkFrame(
            parent,
            fg_color=ThemeColors.PANEL_BG,
            border_width=1,
            border_color=ThemeColors.PANEL_BORDER,
            corner_radius=10,
        )

        content = ctk.CTkFrame(panel, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=15)

        title = SectionTitle(content, text="Update Settings", font_size=16)
        title.pack(anchor="w")

        separator = ctk.CTkFrame(content, height=1, fg_color=ThemeColors.PANEL_BORDER)
        separator.pack(fill="x", pady=(10, 12))

        fields_frame = ctk.CTkFrame(content, fg_color="transparent")
        fields_frame.pack(fill="both", expand=True)

        marker_size_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        marker_size_frame.pack(fill="x", pady=(0, 10))

        marker_size_label = ctk.CTkLabel(
            marker_size_frame,
            text="Marker Size (cm):",
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.LABEL,
            width=120,
            anchor="w",
        )
        marker_size_label.pack(side="left")

        self._marker_size_var = ctk.StringVar()
        self._marker_size_entry = ctk.CTkEntry(
            marker_size_frame,
            width=80,
            textvariable=self._marker_size_var,
        )
        self._marker_size_entry.pack(side="left", padx=(5, 0))

        positions_title = ctk.CTkLabel(
            fields_frame,
            text="Marker Positions (cm):",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ThemeColors.LABEL,
        )
        positions_title.pack(anchor="w", pady=(5, 5))

        self._top_left_x_var, self._top_left_y_var = self._create_position_row(
            fields_frame, "Top Left:"
        )
        self._top_right_x_var, self._top_right_y_var = self._create_position_row(
            fields_frame, "Top Right:"
        )
        self._bottom_left_x_var, self._bottom_left_y_var = self._create_position_row(
            fields_frame, "Bottom Left:"
        )

        bottom_right_row = ctk.CTkFrame(fields_frame, fg_color="transparent")
        bottom_right_row.pack(fill="x", pady=3)

        self._bottom_right_x_var, self._bottom_right_y_var = self._create_position_fields(
            bottom_right_row, "Bottom Right:"
        )

        self._update_button = ActionButton(
            bottom_right_row,
            text="Update Configuration",
            command=self._update_configuration,
            width=160,
            height=28,
        )
        self._update_button.pack(side="right", padx=(15, 0))

        return panel

    def _create_position_row(
        self, parent: ctk.CTkFrame, label_text: str
    ) -> tuple[ctk.StringVar, ctk.StringVar]:
        """Create a position input row with X and Y fields."""
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.pack(fill="x", pady=3)

        return self._create_position_fields(row_frame, label_text)

    def _create_position_fields(
        self, row_frame: ctk.CTkFrame, label_text: str
    ) -> tuple[ctk.StringVar, ctk.StringVar]:
        """Create position input fields (label, X entry, Y entry) within a given frame."""
        label = ctk.CTkLabel(
            row_frame,
            text=label_text,
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.LABEL,
            width=90,
            anchor="w",
        )
        label.pack(side="left")

        x_label = ctk.CTkLabel(
            row_frame,
            text="X:",
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.SUBTITLE,
        )
        x_label.pack(side="left", padx=(5, 2))

        x_var = ctk.StringVar()
        x_entry = ctk.CTkEntry(
            row_frame,
            width=70,
            textvariable=x_var,
        )
        x_entry.pack(side="left")

        y_label = ctk.CTkLabel(
            row_frame,
            text="Y:",
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.SUBTITLE,
        )
        y_label.pack(side="left", padx=(15, 2))

        y_var = ctk.StringVar()
        y_entry = ctk.CTkEntry(
            row_frame,
            width=70,
            textvariable=y_var,
        )
        y_entry.pack(side="left")

        return x_var, y_var

    def _load_existing_settings(self) -> None:
        """Load and display existing settings from marker_details.json."""
        state = self.app_state.aruco_settings
        if state.load_from_file():
            self._update_current_settings_display()
            self._populate_input_fields()
            self._status_label.set_info("Loaded from: marker_details.json")
        else:
            self._update_current_settings_display()
            self._populate_input_fields()
            self._status_label.set_info("Using default settings (no configuration file found)")

    def _update_current_settings_display(self) -> None:
        """Update the current settings display labels."""
        state = self.app_state.aruco_settings

        self._current_marker_size_label.configure(
            text=f"Marker Size: {state.marker_size_cm} cm"
        )
        self._current_top_left_label.configure(
            text=f"  Top Left:       X: {state.top_left.x}    Y: {state.top_left.y}"
        )
        self._current_top_right_label.configure(
            text=f"  Top Right:      X: {state.top_right.x}    Y: {state.top_right.y}"
        )
        self._current_bottom_left_label.configure(
            text=f"  Bottom Left:    X: {state.bottom_left.x}    Y: {state.bottom_left.y}"
        )
        self._current_bottom_right_label.configure(
            text=f"  Bottom Right:   X: {state.bottom_right.x}    Y: {state.bottom_right.y}"
        )

    def _populate_input_fields(self) -> None:
        """Populate input fields with current settings."""
        state = self.app_state.aruco_settings

        self._marker_size_var.set(str(state.marker_size_cm))
        self._top_left_x_var.set(str(state.top_left.x))
        self._top_left_y_var.set(str(state.top_left.y))
        self._top_right_x_var.set(str(state.top_right.x))
        self._top_right_y_var.set(str(state.top_right.y))
        self._bottom_left_x_var.set(str(state.bottom_left.x))
        self._bottom_left_y_var.set(str(state.bottom_left.y))
        self._bottom_right_x_var.set(str(state.bottom_right.x))
        self._bottom_right_y_var.set(str(state.bottom_right.y))

    def _update_configuration(self) -> None:
        """Update the configuration file with new settings."""
        state = self.app_state.aruco_settings

        try:
            state.marker_size_cm = float(self._marker_size_var.get())
            state.top_left.x = float(self._top_left_x_var.get())
            state.top_left.y = float(self._top_left_y_var.get())
            state.top_right.x = float(self._top_right_x_var.get())
            state.top_right.y = float(self._top_right_y_var.get())
            state.bottom_left.x = float(self._bottom_left_x_var.get())
            state.bottom_left.y = float(self._bottom_left_y_var.get())
            state.bottom_right.x = float(self._bottom_right_x_var.get())
            state.bottom_right.y = float(self._bottom_right_y_var.get())
        except ValueError:
            self._status_label.set_error("Error: Please enter valid numbers")
            return

        if state.save_to_file():
            self._update_current_settings_display()
            self._status_label.set_success("Configuration updated successfully")
        else:
            self._status_label.set_error("Error: Failed to save configuration")
