"""
Step 4: Generate Avatar

Handles avatar generation and displays results with preview.
"""

import flet as ft
from pathlib import Path
import threading

from ..app_state import AppState
from ..components.progress_display import ProgressDisplay
from ..backend_interface import BackendInterface


class StepGenerate(ft.Container):
    """
    Generation step for the avatar generation wizard.

    Triggers avatar generation and displays progress and results.
    """

    def __init__(self, app_state: AppState, backend: BackendInterface):
        super().__init__()
        self.app_state = app_state
        self.backend = backend
        self._build()

    def _build(self) -> None:
        """Build the step content."""
        header = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Generate Avatar",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_800,
                    ),
                    ft.Text(
                        "Review your settings and generate the avatar.",
                        size=14,
                        color=ft.Colors.GREY_600,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=ft.Padding.only(bottom=20),
        )

        self._summary = self._create_summary()

        self._generate_button = ft.Button(
            "Generate Avatar",
            icon=ft.Icons.PLAY_ARROW,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
                padding=ft.Padding.symmetric(horizontal=30, vertical=15),
            ),
            on_click=self._start_generation,
        )

        self._progress_display = ProgressDisplay(width=400)
        self._progress_display.visible = False

        self._preview_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Preview",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_700,
                    ),
                    ft.Container(
                        content=ft.Text(
                            "Preview will appear here after generation",
                            color=ft.Colors.GREY_500,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        width=300,
                        height=300,
                        bgcolor=ft.Colors.GREY_200,
                        border_radius=10,
                        alignment=ft.Alignment(0, 0),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            visible=False,
        )

        self._result_container = ft.Container(visible=False)

        self._open_folder_button = ft.Button(
            "Open Output Folder",
            icon=ft.Icons.FOLDER_OPEN,
            visible=False,
            on_click=self._open_output_folder,
        )

        self._open_blender_button = ft.Button(
            "Open in Blender",
            icon=ft.Icons.VIEW_IN_AR,
            visible=False,
            on_click=self._open_in_blender,
        )

        self.content = ft.Column(
            controls=[
                header,
                self._summary,
                ft.Container(height=20),
                self._generate_button,
                ft.Container(height=20),
                self._progress_display,
                self._preview_container,
                ft.Row(
                    controls=[
                        self._open_folder_button,
                        self._open_blender_button,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
                self._result_container,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        )

        self.padding = 30
        self.expand = True

    def _create_summary(self) -> ft.Control:
        """Create the settings summary panel."""
        self._summary_measurements = ft.Text("", size=12, color=ft.Colors.GREY_700)
        self._summary_config = ft.Text("", size=12, color=ft.Colors.GREY_700)
        self._summary_output = ft.Text("", size=12, color=ft.Colors.GREY_700)

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("Measurements", size=14, weight=ft.FontWeight.BOLD),
                                self._summary_measurements,
                            ],
                            spacing=5,
                        ),
                        bgcolor=ft.Colors.GREY_100,
                        padding=15,
                        border_radius=8,
                        width=200,
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("Configuration", size=14, weight=ft.FontWeight.BOLD),
                                self._summary_config,
                            ],
                            spacing=5,
                        ),
                        bgcolor=ft.Colors.GREY_100,
                        padding=15,
                        border_radius=8,
                        width=200,
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("Output", size=14, weight=ft.FontWeight.BOLD),
                                self._summary_output,
                            ],
                            spacing=5,
                        ),
                        bgcolor=ft.Colors.GREY_100,
                        padding=15,
                        border_radius=8,
                        width=200,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
                wrap=True,
            ),
        )

    def on_enter(self) -> None:
        """Called when entering this step."""
        self._update_summary()

    def _update_summary(self) -> None:
        """Update the summary display."""
        m = self.app_state.measurements
        self._summary_measurements.value = (
            f"Height: {m.height_cm:.1f} cm\n"
            f"Shoulder: {m.shoulder_width_cm:.1f} cm\n"
            f"Chest: {m.chest_circumference_cm:.1f} cm"
        ) if m.height_cm else "Not extracted"

        c = self.app_state.configure
        self._summary_config.value = (
            f"Rig: {c.rig_type.value}\n"
            f"Hair: {c.hair_style.value}"
        )

        self._summary_output.value = (
            f"Directory: {c.output_directory.name if c.output_directory else 'Not set'}\n"
            f"Filename: {c.output_filename}.fbx"
        )

        self.update()

    def _start_generation(self, e) -> None:
        """Start the avatar generation process."""
        self._generate_button.disabled = True
        self._progress_display.visible = True
        self._progress_display.reset()
        self.app_state.generate.is_generating = True
        self.update()

        thread = threading.Thread(target=self._run_generation)
        thread.start()

    def _run_generation(self) -> None:
        """Run the generation process in a background thread."""
        def progress_callback(progress: float, status: str):
            self._progress_display.set_progress(progress, status)
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

            self._on_generation_complete()

        except Exception as ex:
            self._on_generation_error(str(ex))

    def _on_generation_complete(self) -> None:
        """Handle generation completion."""
        self.app_state.generate.is_generating = False
        self._progress_display.set_complete("Avatar generated successfully!")
        self._generate_button.disabled = False
        self._generate_button.text = "Regenerate"
        self._open_folder_button.visible = True
        self._open_blender_button.visible = True

        if self.app_state.generate.preview_images:
            self._show_preview(self.app_state.generate.preview_images[0])

        self.app_state.notify_change()
        self.update()

    def _on_generation_error(self, error: str) -> None:
        """Handle generation error."""
        self.app_state.generate.is_generating = False
        self.app_state.generate.error_message = error
        self._progress_display.set_error(f"Error: {error}")
        self._generate_button.disabled = False
        self.update()

    def _show_preview(self, image_path: Path) -> None:
        """Display preview image."""
        self._preview_container.content = ft.Column(
            controls=[
                ft.Text(
                    "Preview",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_700,
                ),
                ft.Image(
                    src=str(image_path),
                    width=300,
                    height=300,
                    fit="contain",
                    border_radius=10,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        self._preview_container.visible = True
        self.update()

    def _open_output_folder(self, e) -> None:
        """Open the output folder in file explorer."""
        if self.app_state.configure.output_directory:
            import subprocess
            import sys
            if sys.platform == "win32":
                subprocess.run(["explorer", str(self.app_state.configure.output_directory)])
            elif sys.platform == "darwin":
                subprocess.run(["open", str(self.app_state.configure.output_directory)])
            else:
                subprocess.run(["xdg-open", str(self.app_state.configure.output_directory)])

    def _open_in_blender(self, e) -> None:
        """Open the generated file in Blender."""
        if self.app_state.generate.output_fbx_path:
            self.backend.open_in_blender(self.app_state.generate.output_fbx_path)
