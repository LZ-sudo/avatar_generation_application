"""
Step 4: Generate Avatar

Handles avatar generation and displays results with preview.
"""

import customtkinter as ctk
from pathlib import Path
import threading
import subprocess
import sys

from PIL import Image

from ..app_state import AppState
from ..components.progress_display import ProgressDisplay
from ..backend_interface import BackendInterface


class StepGenerate(ctk.CTkFrame):
    """
    Generation step for the avatar generation wizard.

    Triggers avatar generation and displays progress and results.
    """

    COLORS = {
        "title": "#1f2937",
        "subtitle": "#6b7280",
        "panel_bg": "#f3f4f6",
        "section_title": "#374151",
        "text": "#374151",
        "preview_bg": "#e5e7eb",
        "preview_text": "#6b7280",
    }

    def __init__(self, parent: ctk.CTkFrame, app_state: AppState, backend: BackendInterface):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self.backend = backend
        self._build()

    def _build(self) -> None:
        """Build the step content."""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=30, pady=30)

        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.pack(pady=(0, 20))

        title_label = ctk.CTkLabel(
            header_frame,
            text="Generate Avatar",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.COLORS["title"],
        )
        title_label.pack()

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Review your settings and generate the avatar.",
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS["subtitle"],
        )
        subtitle_label.pack(pady=(8, 0))

        self._summary_frame = self._create_summary(content_frame)
        self._summary_frame.pack(pady=20)

        self._generate_button = ctk.CTkButton(
            content_frame,
            text="Generate Avatar",
            command=self._start_generation,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
        )
        self._generate_button.pack(pady=(0, 20))

        self._progress_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self._progress_display = ProgressDisplay(self._progress_frame, width=400)
        self._progress_display.pack()

        self._preview_frame = ctk.CTkFrame(content_frame, fg_color="transparent")

        preview_title = ctk.CTkLabel(
            self._preview_frame,
            text="Preview",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.COLORS["section_title"],
        )
        preview_title.pack(pady=(0, 10))

        self._preview_label = ctk.CTkLabel(
            self._preview_frame,
            text="Preview will appear here after generation",
            width=300,
            height=300,
            fg_color=self.COLORS["preview_bg"],
            corner_radius=10,
            text_color=self.COLORS["preview_text"],
        )
        self._preview_label.pack()

        self._buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent")

        self._open_folder_button = ctk.CTkButton(
            self._buttons_frame,
            text="Open Output Folder",
            command=self._open_output_folder,
        )
        self._open_folder_button.pack(side="left", padx=10)

        self._open_blender_button = ctk.CTkButton(
            self._buttons_frame,
            text="Open in Blender",
            command=self._open_in_blender,
        )
        self._open_blender_button.pack(side="left", padx=10)

    def _create_summary(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create the settings summary panel."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")

        measurements_panel = ctk.CTkFrame(
            frame,
            fg_color=self.COLORS["panel_bg"],
            corner_radius=8,
            width=200,
        )
        measurements_panel.pack(side="left", padx=10, fill="y")
        measurements_panel.pack_propagate(False)

        measurements_content = ctk.CTkFrame(measurements_panel, fg_color="transparent")
        measurements_content.pack(padx=15, pady=15, fill="both", expand=True)

        ctk.CTkLabel(
            measurements_content,
            text="Measurements",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w")

        self._summary_measurements = ctk.CTkLabel(
            measurements_content,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["text"],
            justify="left",
        )
        self._summary_measurements.pack(anchor="w", pady=(5, 0))

        config_panel = ctk.CTkFrame(
            frame,
            fg_color=self.COLORS["panel_bg"],
            corner_radius=8,
            width=200,
        )
        config_panel.pack(side="left", padx=10, fill="y")
        config_panel.pack_propagate(False)

        config_content = ctk.CTkFrame(config_panel, fg_color="transparent")
        config_content.pack(padx=15, pady=15, fill="both", expand=True)

        ctk.CTkLabel(
            config_content,
            text="Configuration",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w")

        self._summary_config = ctk.CTkLabel(
            config_content,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["text"],
            justify="left",
        )
        self._summary_config.pack(anchor="w", pady=(5, 0))

        output_panel = ctk.CTkFrame(
            frame,
            fg_color=self.COLORS["panel_bg"],
            corner_radius=8,
            width=200,
        )
        output_panel.pack(side="left", padx=10, fill="y")
        output_panel.pack_propagate(False)

        output_content = ctk.CTkFrame(output_panel, fg_color="transparent")
        output_content.pack(padx=15, pady=15, fill="both", expand=True)

        ctk.CTkLabel(
            output_content,
            text="Output",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w")

        self._summary_output = ctk.CTkLabel(
            output_content,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["text"],
            justify="left",
        )
        self._summary_output.pack(anchor="w", pady=(5, 0))

        return frame

    def on_enter(self) -> None:
        """Called when entering this step."""
        self._update_summary()

    def _update_summary(self) -> None:
        """Update the summary display."""
        m = self.app_state.measurements
        if m.height_cm:
            measurements_text = (
                f"Height: {m.height_cm:.1f} cm\n"
                f"Shoulder: {m.shoulder_width_cm:.1f} cm\n"
                f"Chest: {m.chest_circumference_cm:.1f} cm"
            )
        else:
            measurements_text = "Not extracted"
        self._summary_measurements.configure(text=measurements_text)

        c = self.app_state.configure
        config_text = (
            f"Rig: {c.rig_type.value}\n"
            f"Hair: {c.hair_style.value}"
        )
        self._summary_config.configure(text=config_text)

        output_text = (
            f"Directory: {c.output_directory.name if c.output_directory else 'Not set'}\n"
            f"Filename: {c.output_filename}.fbx"
        )
        self._summary_output.configure(text=output_text)

    def _start_generation(self) -> None:
        """Start the avatar generation process."""
        self._generate_button.configure(state="disabled")
        self._progress_frame.pack(pady=20)
        self._progress_display.reset()
        self.app_state.generate.is_generating = True

        thread = threading.Thread(target=self._run_generation)
        thread.start()

    def _run_generation(self) -> None:
        """Run the generation process in a background thread."""
        def progress_callback(progress: float, status: str):
            self.after(0, lambda: self._progress_display.set_progress(progress, status))
            self.app_state.generate.progress = progress
            self.app_state.generate.status_message = status

        try:
            result = self.backend.generate_avatar(
                measurements=self.app_state.measurements.to_dict(),
                config={
                    "rig_type": self.app_state.configure.rig_type.value,
                    "hair_style": self.app_state.configure.hair_style.value,
                    "output_directory": str(self.app_state.configure.output_directory),
                    "output_filename": self.app_state.configure.output_filename,
                    "export_fbx": self.app_state.configure.export_fbx,
                    "export_obj": self.app_state.configure.export_obj,
                },
                progress_callback=progress_callback,
            )

            self.app_state.generate.output_fbx_path = result.get("fbx_path")
            self.app_state.generate.output_obj_path = result.get("obj_path")
            self.app_state.generate.preview_images = result.get("preview_images", [])

            self.after(0, self._on_generation_complete)

        except Exception as ex:
            self.after(0, lambda: self._on_generation_error(str(ex)))

    def _on_generation_complete(self) -> None:
        """Handle generation completion."""
        self.app_state.generate.is_generating = False
        self._progress_display.set_complete("Avatar generated successfully!")
        self._generate_button.configure(state="normal", text="Regenerate")
        self._buttons_frame.pack(pady=20)

        if self.app_state.generate.preview_images:
            self._show_preview(self.app_state.generate.preview_images[0])

        self.app_state.notify_change()

    def _on_generation_error(self, error: str) -> None:
        """Handle generation error."""
        self.app_state.generate.is_generating = False
        self.app_state.generate.error_message = error
        self._progress_display.set_error(f"Error: {error}")
        self._generate_button.configure(state="normal")

    def _show_preview(self, image_path: Path) -> None:
        """Display preview image."""
        try:
            pil_image = Image.open(image_path)
            pil_image.thumbnail((300, 300), Image.Resampling.LANCZOS)

            ctk_image = ctk.CTkImage(
                light_image=pil_image,
                dark_image=pil_image,
                size=(pil_image.width, pil_image.height),
            )

            self._preview_label.configure(image=ctk_image, text="")
            self._preview_label._image = ctk_image

        except Exception:
            self._preview_label.configure(text="Preview unavailable")

        self._preview_frame.pack(pady=20)

    def _open_output_folder(self) -> None:
        """Open the output folder in file explorer."""
        if self.app_state.configure.output_directory:
            if sys.platform == "win32":
                subprocess.run(["explorer", str(self.app_state.configure.output_directory)])
            elif sys.platform == "darwin":
                subprocess.run(["open", str(self.app_state.configure.output_directory)])
            else:
                subprocess.run(["xdg-open", str(self.app_state.configure.output_directory)])

    def _open_in_blender(self) -> None:
        """Open the generated file in Blender."""
        if self.app_state.generate.output_fbx_path:
            self.backend.open_in_blender(self.app_state.generate.output_fbx_path)
