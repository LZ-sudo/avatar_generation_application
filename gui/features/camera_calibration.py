"""
Camera Calibration Feature View

Provides UI for camera calibration using checkerboard pattern images.
"""

import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
import threading

from PIL import Image

from ..app_state import AppState
from ..backend_interface import BackendInterface
from ..components.ui_elements import ThemeColors, PageHeader, SectionTitle, ActionButton


class CameraCalibrationView(ctk.CTkFrame):
    """
    Camera calibration view component.

    Allows users to calibrate their camera using checkerboard images.
    """

    PANEL_WIDTH = 340

    # Fixed image size for the checkerboard example (maintains ~0.76 aspect ratio)
    EXAMPLE_IMAGE_SIZE = (250, 340)

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

        header = PageHeader(
            content_frame,
            title="Camera Calibration",
            subtitle="Calibrate your camera using checkerboard pattern images.",
            title_size=24,
            subtitle_size=14,
        )
        header.pack(pady=(0, 20))

        input_panel = self._create_input_panel(content_frame)
        input_panel.pack(fill="x", pady=(0, 15))

        panels_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        panels_frame.pack(fill="both", expand=True, pady=(0, 15))

        checkerboard_panel = self._create_checkerboard_panel(panels_frame)
        checkerboard_panel.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self._results_panel = self._create_results_panel(panels_frame)
        self._results_panel.pack(side="left", fill="both", expand=True, padx=(8, 0))

        self._calibrate_button = ActionButton(
            content_frame,
            text="Calibrate Camera",
            command=self._start_calibration,
            width=200,
        )
        self._calibrate_button.configure(state="disabled")
        self._calibrate_button.pack(pady=15)

    def _create_input_panel(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create the image directory input panel."""
        panel = ctk.CTkFrame(
            parent,
            fg_color=ThemeColors.PANEL_BG,
            border_width=1,
            border_color=ThemeColors.PANEL_BORDER,
            corner_radius=10,
        )

        content = ctk.CTkFrame(panel, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=15)

        title = SectionTitle(content, text="Input Directory of Calibration Images", font_size=16)
        title.pack(anchor="w")

        separator = ctk.CTkFrame(content, height=1, fg_color=ThemeColors.PANEL_BORDER)
        separator.pack(fill="x", pady=(10, 12))

        dir_frame = ctk.CTkFrame(content, fg_color="transparent")
        dir_frame.pack(fill="x")

        self._dir_var = ctk.StringVar()
        self._dir_entry = ctk.CTkEntry(
            dir_frame,
            textvariable=self._dir_var,
            state="disabled",
            placeholder_text="Select folder containing checkerboard images",
        )
        self._dir_entry.pack(side="left", fill="x", expand=True)

        browse_button = ctk.CTkButton(
            dir_frame,
            text="Browse",
            width=80,
            command=self._open_folder_picker,
        )
        browse_button.pack(side="left", padx=(10, 0))

        return panel

    def _create_checkerboard_panel(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create the checkerboard settings panel."""
        panel = ctk.CTkFrame(
            parent,
            fg_color=ThemeColors.PANEL_BG,
            border_width=1,
            border_color=ThemeColors.PANEL_BORDER,
            corner_radius=10,
        )

        content = ctk.CTkFrame(panel, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=15)

        title = SectionTitle(content, text="Checkerboard Settings", font_size=16)
        title.pack(anchor="w")

        separator = ctk.CTkFrame(content, height=1, fg_color=ThemeColors.PANEL_BORDER)
        separator.pack(fill="x", pady=(10, 12))

        body_frame = ctk.CTkFrame(content, fg_color="transparent")
        body_frame.pack(fill="both", expand=True)

        fields_frame = ctk.CTkFrame(body_frame, fg_color="transparent")
        fields_frame.pack(side="right", fill="y", padx=(15, 0))

        cols_label = ctk.CTkLabel(
            fields_frame,
            text="Inner Corners (Columns)",
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.SUBTITLE,
        )
        cols_label.pack(anchor="w")

        self._cols_var = ctk.StringVar(value=str(self.app_state.camera_calibration.checkerboard_cols))
        self._cols_var.trace_add("write", self._on_cols_change)
        self._cols_entry = ctk.CTkEntry(
            fields_frame,
            width=140,
            textvariable=self._cols_var,
        )
        self._cols_entry.pack(anchor="w", pady=(5, 12))

        rows_label = ctk.CTkLabel(
            fields_frame,
            text="Inner Corners (Rows)",
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.SUBTITLE,
        )
        rows_label.pack(anchor="w")

        self._rows_var = ctk.StringVar(value=str(self.app_state.camera_calibration.checkerboard_rows))
        self._rows_var.trace_add("write", self._on_rows_change)
        self._rows_entry = ctk.CTkEntry(
            fields_frame,
            width=140,
            textvariable=self._rows_var,
        )
        self._rows_entry.pack(anchor="w", pady=(5, 12))

        size_label = ctk.CTkLabel(
            fields_frame,
            text="Square Size (mm)",
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.SUBTITLE,
        )
        size_label.pack(anchor="w")

        self._square_size_var = ctk.StringVar(value=str(self.app_state.camera_calibration.square_size_mm))
        self._square_size_var.trace_add("write", self._on_square_size_change)
        self._square_size_entry = ctk.CTkEntry(
            fields_frame,
            width=140,
            textvariable=self._square_size_var,
        )
        self._square_size_entry.pack(anchor="w", pady=(5, 0))

        example_frame = ctk.CTkFrame(body_frame, fg_color="transparent")
        example_frame.pack(side="left", fill="both", expand=True)

        example_image_path = Path(__file__).parent.parent / "images" / "checkerboard_example.png"
        if example_image_path.exists():
            original_image = Image.open(example_image_path)
            example_ctk_image = ctk.CTkImage(
                light_image=original_image,
                dark_image=original_image,
                size=self.EXAMPLE_IMAGE_SIZE,
            )
            example_image_label = ctk.CTkLabel(
                example_frame,
                image=example_ctk_image,
                text="",
            )
            example_image_label.pack(expand=True)
            # Keep reference to prevent garbage collection
            example_image_label._ctk_image = example_ctk_image

        return panel

    def _create_results_panel(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create the calibration results panel."""
        panel = ctk.CTkFrame(
            parent,
            fg_color=ThemeColors.PANEL_BG,
            border_width=1,
            border_color=ThemeColors.PANEL_BORDER,
            corner_radius=10,
        )

        content = ctk.CTkFrame(panel, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=15)

        title = SectionTitle(content, text="Calibration Results", font_size=16)
        title.pack(anchor="w")

        separator = ctk.CTkFrame(content, height=1, fg_color=ThemeColors.PANEL_BORDER)
        separator.pack(fill="x", pady=(10, 12))

        self._results_status_label = ctk.CTkLabel(
            content,
            text="No calibration run yet",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=ThemeColors.SUBTITLE,
        )
        self._results_status_label.pack(anchor="w")

        self._results_images_label = ctk.CTkLabel(
            content,
            text="",
            font=ctk.CTkFont(size=13),
            text_color=ThemeColors.LABEL,
        )
        self._results_images_label.pack(anchor="w", pady=(8, 0))

        self._results_error_label = ctk.CTkLabel(
            content,
            text="",
            font=ctk.CTkFont(size=13),
            text_color=ThemeColors.LABEL,
        )
        self._results_error_label.pack(anchor="w", pady=(4, 0))

        self._results_quality_label = ctk.CTkLabel(
            content,
            text="",
            font=ctk.CTkFont(size=13),
        )
        self._results_quality_label.pack(anchor="w", pady=(4, 0))

        self._results_output_label = ctk.CTkLabel(
            content,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.SUBTITLE,
            wraplength=280,
        )
        self._results_output_label.pack(anchor="w", pady=(8, 0))

        return panel

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

    def _load_existing_calibration(self) -> None:
        """Load and display existing calibration if available."""
        import json

        output_path = self.app_state.camera_calibration.get_output_path()
        if not output_path.exists():
            return

        try:
            with open(output_path) as f:
                data = json.load(f)

            if not data.get("success"):
                return

            reprojection_error = data.get("reprojection_error")
            num_successful = data.get("num_successful_images", 0)
            num_failed = data.get("num_failed_images", 0)

            self._results_status_label.configure(
                text="Calibrated",
                text_color=ThemeColors.STATUS_GREEN,
            )
            self._results_images_label.configure(
                text=f"Images processed: {num_successful}/{num_successful + num_failed}",
            )
            self._results_error_label.configure(
                text=f"Reprojection error: {reprojection_error:.4f} px",
            )

            quality = self._get_quality_label(reprojection_error)
            if reprojection_error < 1.0:
                quality_color = ThemeColors.STATUS_GREEN
            elif reprojection_error < 2.0:
                quality_color = ThemeColors.STATUS_ORANGE
            else:
                quality_color = ThemeColors.STATUS_RED

            self._results_quality_label.configure(
                text=f"Quality: {quality}",
                text_color=quality_color,
            )
            self._results_output_label.configure(
                text=f"Loaded from: {output_path.name}",
            )
        except (json.JSONDecodeError, KeyError):
            pass

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

        self._calibrate_button.start_processing("Calibrating...")
        self._results_status_label.configure(
            text="Calibrating...",
            text_color=ThemeColors.STATUS_BLUE,
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

        self._calibrate_button.stop_processing()

        if state.calibration_success:
            self._results_status_label.configure(
                text="Success",
                text_color=ThemeColors.STATUS_GREEN,
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
                quality_color = ThemeColors.STATUS_GREEN
            elif state.reprojection_error < 2.0:
                quality_color = ThemeColors.STATUS_ORANGE
            else:
                quality_color = ThemeColors.STATUS_RED

            self._results_quality_label.configure(
                text=f"Quality: {quality}",
                text_color=quality_color,
            )
            self._results_output_label.configure(
                text=f"Saved to: {state.get_output_path().name}",
            )
        else:
            self._results_status_label.configure(
                text="Failed",
                text_color=ThemeColors.STATUS_RED,
            )
            self._results_images_label.configure(text=f"Error: {state.error_message}")
            self._results_error_label.configure(text="")
            self._results_quality_label.configure(text="")
            self._results_output_label.configure(text="")
