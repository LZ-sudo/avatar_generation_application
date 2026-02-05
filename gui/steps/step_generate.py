"""
Step 5: Generate Avatar

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
from ..components.ui_elements import ThemeColors, PageHeader, SectionTitle


class StepGenerate(ctk.CTkFrame):
    """
    Generation step for the avatar generation wizard.

    Triggers avatar generation and displays progress and results.
    """

    def __init__(self, parent: ctk.CTkFrame, app_state: AppState, backend: BackendInterface):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self.backend = backend
        self._build()

    def _build(self) -> None:
        """Build the step content."""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=30, pady=30)

        # Header
        header = PageHeader(
            content_frame,
            title="Generate Avatar",
            subtitle="Review your settings and generate the avatar.",
            title_size=24,
            subtitle_size=14,
        )
        header.pack(pady=(0, 20))

        self._summary_frame = self._create_summary(content_frame)
        self._summary_frame.pack(pady=20)

        self._progress_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self._progress_frame.pack(pady=20)
        self._progress_display = ProgressDisplay(self._progress_frame, width=400)
        self._progress_display.pack()

        self._preview_frame = ctk.CTkFrame(content_frame, fg_color="transparent")

        preview_title = SectionTitle(self._preview_frame, text="Preview", font_size=16)
        preview_title.pack(pady=(0, 10))

        self._preview_label = ctk.CTkLabel(
            self._preview_frame,
            text="Preview will appear here after generation",
            width=300,
            height=300,
            fg_color=ThemeColors.PREVIEW_BG,
            corner_radius=10,
            text_color=ThemeColors.SUBTITLE,
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
            fg_color=ThemeColors.HEADER_BG,
            corner_radius=8,
            width=200,
        )
        measurements_panel.pack(side="left", padx=10, fill="y")
        measurements_panel.pack_propagate(False)

        measurements_content = ctk.CTkFrame(measurements_panel, fg_color="transparent")
        measurements_content.pack(padx=15, pady=15, fill="both", expand=True)

        SectionTitle(measurements_content, text="Measurements").pack(anchor="w")

        self._summary_measurements = ctk.CTkLabel(
            measurements_content,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.LABEL,
            justify="left",
        )
        self._summary_measurements.pack(anchor="w", pady=(5, 0))

        config_panel = ctk.CTkFrame(
            frame,
            fg_color=ThemeColors.HEADER_BG,
            corner_radius=8,
            width=200,
        )
        config_panel.pack(side="left", padx=10, fill="y")
        config_panel.pack_propagate(False)

        config_content = ctk.CTkFrame(config_panel, fg_color="transparent")
        config_content.pack(padx=15, pady=15, fill="both", expand=True)

        SectionTitle(config_content, text="Configuration").pack(anchor="w")

        self._summary_config = ctk.CTkLabel(
            config_content,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.LABEL,
            justify="left",
        )
        self._summary_config.pack(anchor="w", pady=(5, 0))

        output_panel = ctk.CTkFrame(
            frame,
            fg_color=ThemeColors.HEADER_BG,
            corner_radius=8,
            width=200,
        )
        output_panel.pack(side="left", padx=10, fill="y")
        output_panel.pack_propagate(False)

        output_content = ctk.CTkFrame(output_panel, fg_color="transparent")
        output_content.pack(padx=15, pady=15, fill="both", expand=True)

        SectionTitle(output_content, text="Output").pack(anchor="w")

        self._summary_output = ctk.CTkLabel(
            output_content,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.LABEL,
            justify="left",
        )
        self._summary_output.pack(anchor="w", pady=(5, 0))

        return frame

    def on_enter(self) -> None:
        """Called when entering this step."""
        self._update_summary()
        # Start generation automatically if not already running
        if not self.app_state.generate.is_generating and not self.app_state.generate.is_complete():
            self._start_generation()

    def _update_summary(self) -> None:
        """Update the summary display."""
        m = self.app_state.measurements
        if m.height_cm:
            measurements_text = (
                f"Height: {m.height_cm:.1f} cm\n"
                f"Shoulder: {m.shoulder_width_cm:.1f} cm\n"
                f"Hip: {m.hip_width_cm:.1f} cm"
            )
        else:
            measurements_text = "Not extracted"
        self._summary_measurements.configure(text=measurements_text)

        c = self.app_state.configure
        hair_display = c.hair_asset if c.hair_asset else "None"
        config_text = (
            f"Rig: {c.rig_type.value}\n"
            f"Hair: {hair_display}\n"
            f"FK/IK: {'Yes' if c.fk_ik_hybrid else 'No'}\n"
            f"T-Pose: {'Yes' if c.t_pose else 'No'}"
        )
        self._summary_config.configure(text=config_text)

        o = self.app_state.output_settings
        formats = []
        if o.export_fbx:
            formats.append("FBX")
        if o.export_obj:
            formats.append("OBJ")
        format_text = ", ".join(formats) if formats else "None"

        output_text = (
            f"Directory: {o.output_directory.name if o.output_directory else 'Not set'}\n"
            f"Filename: {o.output_filename}\n"
            f"Formats: {format_text}"
        )
        self._summary_output.configure(text=output_text)

    def _start_generation(self) -> None:
        """Start the avatar generation process."""
        self._progress_display.reset()
        self.app_state.generate.is_generating = True

        thread = threading.Thread(target=self._run_generation, daemon=True)
        thread.start()

    def _run_generation(self) -> None:
        """Run the generation process in a background thread."""
        def progress_callback(progress: float, status: str):
            self.after(0, lambda p=progress, s=status: self._progress_display.set_progress(p, s))
            self.app_state.generate.progress = progress
            self.app_state.generate.status_message = status

        try:
            result = self.backend.generate_avatar(
                measurements=self.app_state.measurements.to_dict(),
                config={
                    "rig_type": self.app_state.configure.rig_type.value,
                    "fk_ik_hybrid": self.app_state.configure.fk_ik_hybrid,
                    "instrumented_arm": self.app_state.configure.instrumented_arm.value,
                    "hair_asset": self.app_state.configure.hair_asset,
                    "t_pose": self.app_state.configure.t_pose,
                    "output_directory": str(self.app_state.output_settings.output_directory),
                    "output_filename": self.app_state.output_settings.output_filename,
                    "export_fbx": self.app_state.output_settings.export_fbx,
                    "export_obj": self.app_state.output_settings.export_obj,
                },
                progress_callback=progress_callback,
            )

            self.app_state.generate.output_fbx_path = result.get("fbx_path")
            self.app_state.generate.output_obj_path = result.get("obj_path")
            self.app_state.generate.preview_images = result.get("preview_images", [])

            self.after(0, self._on_generation_complete)

        except Exception as ex:
            error_msg = str(ex)
            self.after(0, lambda e=error_msg: self._on_generation_error(e))

    def _on_generation_complete(self) -> None:
        """Handle generation completion."""
        self.app_state.generate.is_generating = False
        self._progress_display.set_complete("Avatar generated successfully!")
        self._buttons_frame.pack(pady=20)

        if self.app_state.generate.preview_images:
            self._show_preview(self.app_state.generate.preview_images[0])

        self.app_state.notify_change()

    def _on_generation_error(self, error: str) -> None:
        """Handle generation error."""
        self.app_state.generate.is_generating = False
        self.app_state.generate.error_message = error
        self._progress_display.set_error(f"Error: {error}")

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
        if self.app_state.output_settings.output_directory:
            if sys.platform == "win32":
                subprocess.run(["explorer", str(self.app_state.output_settings.output_directory)])
            elif sys.platform == "darwin":
                subprocess.run(["open", str(self.app_state.output_settings.output_directory)])
            else:
                subprocess.run(["xdg-open", str(self.app_state.output_settings.output_directory)])

    def _open_in_blender(self) -> None:
        """Open the generated file in Blender."""
        if self.app_state.generate.output_fbx_path:
            self.backend.open_in_blender(self.app_state.generate.output_fbx_path)
