"""
Camera Calibration Feature View

Provides UI for camera calibration using checkerboard pattern images.
"""

import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
import threading

from ..app_state import AppState
from ..backend_interface import BackendInterface


class CameraCalibrationView(ctk.CTkFrame):
    """
    Camera calibration view component.

    Allows users to calibrate their camera using checkerboard images.
    """

    COLORS = {
        "title": "#1f2937",
        "subtitle": "#6b7280",
        "section_title": "#374151",
        "panel_bg": "#ffffff",
        "panel_border": "#d1d5db",
        "status_bg": "#f3f4f6",
        "status_not_calibrated": "#ea580c",
        "status_calibrated": "#16a34a",
        "status_blue": "#2563eb",
        "status_red": "#dc2626",
        "status_orange": "#ea580c",
        "text": "#374151",
        "text_secondary": "#6b7280",
    }

    def __init__(self, parent: ctk.CTkFrame, app_state: AppState, backend: BackendInterface):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self.backend = backend
        self._build()

        self._load_existing_calibration()

    def _build(self) -> None:
        """Build the view content."""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=30, pady=30)

        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.pack(pady=(0, 20))

        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack()

        title_label = ctk.CTkLabel(
            title_frame,
            text="Camera Calibration",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.COLORS["title"],
        )
        title_label.pack()

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Calibrate your camera using checkerboard pattern images.",
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS["subtitle"],
        )
        subtitle_label.pack(pady=(8, 0))

        self._status_banner = self._create_status_banner(content_frame)
        self._status_banner.pack(pady=(0, 20))

        settings_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        settings_frame.pack(pady=20)

        input_settings = self._create_input_settings(settings_frame)
        input_settings.pack(side="left", padx=15)

        checkerboard_settings = self._create_checkerboard_settings(settings_frame)
        checkerboard_settings.pack(side="left", padx=15)

        self._calibrate_button = ctk.CTkButton(
            content_frame,
            text="Calibrate Camera",
            command=self._start_calibration,
            state="disabled",
            fg_color="#2563eb",
            hover_color="#1d4ed8",
        )
        self._calibrate_button.pack(pady=20)

        self._results_panel = self._create_results_panel(content_frame)

    def _create_status_banner(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create the existing calibration status banner."""
        banner = ctk.CTkFrame(
            parent,
            fg_color=self.COLORS["status_bg"],
            corner_radius=8,
            border_width=1,
            border_color=self.COLORS["panel_border"],
        )

        content = ctk.CTkFrame(banner, fg_color="transparent")
        content.pack(padx=20, pady=12)

        self._status_icon_label = ctk.CTkLabel(
            content,
            text="X",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.COLORS["status_not_calibrated"],
            width=20,
        )
        self._status_icon_label.pack(side="left")

        self._status_text_label = ctk.CTkLabel(
            content,
            text="Not calibrated",
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS["text"],
        )
        self._status_text_label.pack(side="left", padx=(10, 0))

        return banner

    def _create_input_settings(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create the image directory input section."""
        panel = ctk.CTkFrame(
            parent,
            fg_color=self.COLORS["panel_bg"],
            border_width=1,
            border_color=self.COLORS["panel_border"],
            corner_radius=10,
        )

        content = ctk.CTkFrame(panel, fg_color="transparent")
        content.pack(padx=20, pady=20)

        title = ctk.CTkLabel(
            content,
            text="Input Images",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.COLORS["section_title"],
        )
        title.pack(anchor="w")

        separator = ctk.CTkFrame(content, height=1, fg_color=self.COLORS["panel_border"])
        separator.pack(fill="x", pady=(10, 15))

        dir_frame = ctk.CTkFrame(content, fg_color="transparent")
        dir_frame.pack(anchor="w")

        self._dir_var = ctk.StringVar()
        self._dir_entry = ctk.CTkEntry(
            dir_frame,
            width=280,
            textvariable=self._dir_var,
            state="disabled",
            placeholder_text="Select folder with checkerboard images",
        )
        self._dir_entry.pack(side="left")

        browse_button = ctk.CTkButton(
            dir_frame,
            text="Browse",
            width=80,
            command=self._open_folder_picker,
        )
        browse_button.pack(side="left", padx=(10, 0))

        return panel

    def _create_checkerboard_settings(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create the checkerboard settings section."""
        panel = ctk.CTkFrame(
            parent,
            fg_color=self.COLORS["panel_bg"],
            border_width=1,
            border_color=self.COLORS["panel_border"],
            corner_radius=10,
        )

        content = ctk.CTkFrame(panel, fg_color="transparent")
        content.pack(padx=20, pady=20)

        title = ctk.CTkLabel(
            content,
            text="Checkerboard Settings",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.COLORS["section_title"],
        )
        title.pack(anchor="w")

        separator = ctk.CTkFrame(content, height=1, fg_color=self.COLORS["panel_border"])
        separator.pack(fill="x", pady=(10, 15))

        cols_label = ctk.CTkLabel(
            content,
            text="Inner Corners (Columns)",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["text_secondary"],
        )
        cols_label.pack(anchor="w")

        self._cols_var = ctk.StringVar(value=str(self.app_state.camera_calibration.checkerboard_cols))
        self._cols_var.trace_add("write", self._on_cols_change)
        self._cols_entry = ctk.CTkEntry(
            content,
            width=180,
            textvariable=self._cols_var,
        )
        self._cols_entry.pack(anchor="w", pady=(5, 15))

        rows_label = ctk.CTkLabel(
            content,
            text="Inner Corners (Rows)",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["text_secondary"],
        )
        rows_label.pack(anchor="w")

        self._rows_var = ctk.StringVar(value=str(self.app_state.camera_calibration.checkerboard_rows))
        self._rows_var.trace_add("write", self._on_rows_change)
        self._rows_entry = ctk.CTkEntry(
            content,
            width=180,
            textvariable=self._rows_var,
        )
        self._rows_entry.pack(anchor="w", pady=(5, 15))

        size_label = ctk.CTkLabel(
            content,
            text="Square Size (mm)",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["text_secondary"],
        )
        size_label.pack(anchor="w")

        self._square_size_var = ctk.StringVar(value=str(self.app_state.camera_calibration.square_size_mm))
        self._square_size_var.trace_add("write", self._on_square_size_change)
        self._square_size_entry = ctk.CTkEntry(
            content,
            width=180,
            textvariable=self._square_size_var,
        )
        self._square_size_entry.pack(anchor="w", pady=(5, 0))

        return panel

    def _create_results_panel(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create the calibration results panel."""
        panel = ctk.CTkFrame(
            parent,
            fg_color=self.COLORS["panel_bg"],
            border_width=1,
            border_color=self.COLORS["panel_border"],
            corner_radius=10,
            width=500,
        )

        content = ctk.CTkFrame(panel, fg_color="transparent")
        content.pack(padx=20, pady=20, fill="x")

        header_frame = ctk.CTkFrame(content, fg_color="transparent")
        header_frame.pack(fill="x")

        title = ctk.CTkLabel(
            header_frame,
            text="Calibration Results",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.COLORS["section_title"],
        )
        title.pack(side="left")

        self._progress_label = ctk.CTkLabel(
            header_frame,
            text="...",
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS["status_blue"],
        )

        separator = ctk.CTkFrame(content, height=1, fg_color=self.COLORS["panel_border"])
        separator.pack(fill="x", pady=(10, 15))

        self._results_status_label = ctk.CTkLabel(
            content,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self._results_status_label.pack(anchor="w")

        self._results_images_label = ctk.CTkLabel(
            content,
            text="",
            font=ctk.CTkFont(size=13),
            text_color=self.COLORS["text"],
        )
        self._results_images_label.pack(anchor="w", pady=(5, 0))

        self._results_error_label = ctk.CTkLabel(
            content,
            text="",
            font=ctk.CTkFont(size=13),
            text_color=self.COLORS["text"],
        )
        self._results_error_label.pack(anchor="w", pady=(5, 0))

        self._results_quality_label = ctk.CTkLabel(
            content,
            text="",
            font=ctk.CTkFont(size=13),
        )
        self._results_quality_label.pack(anchor="w", pady=(5, 0))

        self._results_output_label = ctk.CTkLabel(
            content,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["text_secondary"],
        )
        self._results_output_label.pack(anchor="w", pady=(5, 0))

        return panel

    def _load_existing_calibration(self) -> None:
        """Load and display existing calibration status."""
        self.app_state.camera_calibration.load_existing_calibration()

        if self.app_state.camera_calibration.existing_calibration_path:
            error = self.app_state.camera_calibration.existing_reprojection_error
            quality = self._get_quality_label(error)
            self._status_icon_label.configure(
                text="\u2713",
                text_color=self.COLORS["status_calibrated"],
            )
            self._status_text_label.configure(
                text=f"Calibrated - Error: {error:.2f} px ({quality})",
            )
        else:
            self._status_icon_label.configure(
                text="X",
                text_color=self.COLORS["status_not_calibrated"],
            )
            self._status_text_label.configure(text="Not calibrated")

    def _get_quality_label(self, error: float) -> str:
        """Get quality label based on reprojection error."""
        if error < 0.5:
            return "Excellent"
        elif error < 1.0:
            return "Good"
        elif error < 2.0:
            return "Acceptable"
        else:
            return "Poor"

    def _open_folder_picker(self) -> None:
        """Open folder picker dialog."""
        folder_path = filedialog.askdirectory(
            title="Select Checkerboard Images Directory",
        )

        if folder_path:
            self.app_state.camera_calibration.image_directory = Path(folder_path)
            self._dir_var.set(folder_path)
            self._update_calibrate_button()

    def _on_cols_change(self, *args) -> None:
        """Handle columns field change."""
        try:
            value = int(self._cols_var.get())
            if value > 0:
                self.app_state.camera_calibration.checkerboard_cols = value
        except ValueError:
            pass

    def _on_rows_change(self, *args) -> None:
        """Handle rows field change."""
        try:
            value = int(self._rows_var.get())
            if value > 0:
                self.app_state.camera_calibration.checkerboard_rows = value
        except ValueError:
            pass

    def _on_square_size_change(self, *args) -> None:
        """Handle square size field change."""
        try:
            value = float(self._square_size_var.get())
            if value > 0:
                self.app_state.camera_calibration.square_size_mm = value
        except ValueError:
            pass

    def _update_calibrate_button(self) -> None:
        """Update calibrate button enabled state."""
        has_directory = self.app_state.camera_calibration.image_directory is not None
        state = "normal" if has_directory else "disabled"
        self._calibrate_button.configure(state=state)

    def _start_calibration(self) -> None:
        """Start the camera calibration process."""
        self.app_state.camera_calibration.is_calibrating = True
        self.app_state.camera_calibration.reset_results()

        self._calibrate_button.configure(state="disabled")
        self._results_panel.pack(pady=20)
        self._progress_label.pack(side="left", padx=(10, 0))
        self._results_status_label.configure(
            text="Calibrating...",
            text_color=self.COLORS["status_blue"],
        )
        self._results_images_label.configure(text="")
        self._results_error_label.configure(text="")
        self._results_quality_label.configure(text="")
        self._results_output_label.configure(text="")

        thread = threading.Thread(target=self._run_calibration)
        thread.start()

    def _run_calibration(self) -> None:
        """Run calibration in background thread."""
        state = self.app_state.camera_calibration

        try:
            result = self.backend.calibrate_camera(
                image_dir=state.image_directory,
                checkerboard_size=(state.checkerboard_cols, state.checkerboard_rows),
                square_size_mm=state.square_size_mm,
                output_path=state.get_output_path(),
            )

            state.calibration_success = result.get("success", False)
            state.reprojection_error = result.get("reprojection_error")
            state.num_successful_images = result.get("num_successful_images", 0)
            state.num_failed_images = result.get("num_failed_images", 0)

            if not state.calibration_success:
                state.error_message = result.get("error", "Unknown error")

            self.after(0, self._on_calibration_complete)

        except Exception as ex:
            state.calibration_success = False
            state.error_message = str(ex)
            self.after(0, self._on_calibration_complete)

    def _on_calibration_complete(self) -> None:
        """Handle calibration completion."""
        state = self.app_state.camera_calibration
        state.is_calibrating = False

        self._progress_label.pack_forget()
        self._calibrate_button.configure(state="normal")

        if state.calibration_success:
            self._results_status_label.configure(
                text="Success",
                text_color=self.COLORS["status_calibrated"],
            )
            self._results_images_label.configure(
                text=f"Images processed: {state.num_successful_images}/"
                     f"{state.num_successful_images + state.num_failed_images}",
            )
            self._results_error_label.configure(
                text=f"Reprojection error: {state.reprojection_error:.4f} px",
            )

            quality = self._get_quality_label(state.reprojection_error)
            if state.reprojection_error < 1.0:
                quality_color = self.COLORS["status_calibrated"]
            elif state.reprojection_error < 2.0:
                quality_color = self.COLORS["status_orange"]
            else:
                quality_color = self.COLORS["status_red"]

            self._results_quality_label.configure(
                text=f"Quality: {quality}",
                text_color=quality_color,
            )
            self._results_output_label.configure(
                text=f"Output: {state.get_output_path()}",
            )

            self._load_existing_calibration()
        else:
            self._results_status_label.configure(
                text="Failed",
                text_color=self.COLORS["status_red"],
            )
            self._results_images_label.configure(text=f"Error: {state.error_message}")
            self._results_error_label.configure(text="")
            self._results_quality_label.configure(text="")
            self._results_output_label.configure(text="")
