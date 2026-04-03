"""
C3D Converter Feature View

Provides UI for converting Cometa C3D joint angle files to BVH animation format.
"""

import os
import subprocess
import sys
import threading
from pathlib import Path
from typing import Callable, Optional

import customtkinter as ctk

from ..components.ui_elements import (
    ThemeColors,
    PageHeader,
    SectionHeader,
    Card,
    FilePicker,
    FolderPicker,
    OpenFolderButton,
    ActionButton,
)
from ..components.log_output import LogOutput

_SUBPROCESS_FLAGS = {"creationflags": subprocess.CREATE_NO_WINDOW} if sys.platform == "win32" else {}


class C3dConverterView(ctk.CTkFrame):
    """
    C3D to BVH converter view.

    Converts Cometa C3D joint angle files to BVH animation format
    using the c3d_to_bvh.py script in the mesh_rigging_animation module.
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        set_tabs_locked: Optional[Callable[[bool], None]] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self._set_tabs_locked = set_tabs_locked
        self._is_converting = False
        self._build()

    def _build(self) -> None:
        """Build the view content."""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=30, pady=30)

        header = PageHeader(
            content_frame,
            title="C3D Converter",
            subtitle="Convert Cometa C3D joint angle files to BVH animation format.",
            title_size=24,
            subtitle_size=14,
        )
        header.pack(pady=(0, 20))

        panel = self._create_converter_panel(content_frame)
        panel.pack(pady=5)

        self._validation_label = ctk.CTkLabel(
            content_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.WARNING,
        )
        self._validation_label.pack(pady=(0, 5))

        self._log_output = LogOutput(content_frame, width=480, height=75)
        self._log_output.pack(pady=(0, 0))

        self._update_validation()

    def _create_converter_panel(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create the converter settings panel."""
        panel = Card(parent)
        content = panel.content

        header = SectionHeader(content, text="Conversion Settings", font_size=16)
        header.pack(anchor="w", fill="x")

        self._input_picker = FilePicker(
            content,
            label="Input C3D File",
            filetypes=[("C3D files", "*.c3d"), ("All files", "*.*")],
            entry_width=380,
            on_file_selected=self._on_input_selected,
        )
        self._input_picker.pack(anchor="w", fill="x", pady=(0, 15))

        self._output_folder_picker = FolderPicker(
            content,
            label="Output Directory",
            entry_width=380,
            on_folder_selected=self._on_folder_selected,
        )
        self._output_folder_picker.pack(anchor="w", fill="x", pady=(0, 15))

        filename_label = ctk.CTkLabel(
            content,
            text="Output Filename",
            font=ctk.CTkFont(size=13),
            text_color=ThemeColors.SUBTITLE,
        )
        filename_label.pack(anchor="w")

        filename_frame = ctk.CTkFrame(content, fg_color="transparent")
        filename_frame.pack(anchor="w", pady=(5, 15))

        self._filename_var = ctk.StringVar(value="animation")
        self._filename_entry = ctk.CTkEntry(
            filename_frame,
            width=200,
            textvariable=self._filename_var,
            placeholder_text="animation",
        )
        self._filename_entry.pack(side="left")

        extension_label = ctk.CTkLabel(
            filename_frame,
            text=".bvh",
            font=ctk.CTkFont(size=13),
            text_color=ThemeColors.SUBTITLE,
        )
        extension_label.pack(side="left", padx=(5, 0))

        fps_label = ctk.CTkLabel(
            content,
            text="Frame Rate (FPS)",
            font=ctk.CTkFont(size=13),
            text_color=ThemeColors.SUBTITLE,
        )
        fps_label.pack(anchor="w")

        fps_frame = ctk.CTkFrame(content, fg_color="transparent")
        fps_frame.pack(anchor="w", pady=(5, 15))

        self._fps_var = ctk.StringVar(value="120")
        self._fps_entry = ctk.CTkEntry(
            fps_frame,
            width=80,
            textvariable=self._fps_var,
            justify="right",
            state="disabled",
        )
        self._fps_entry.pack(side="left")

        fps_unit_label = ctk.CTkLabel(
            fps_frame,
            text="fps",
            font=ctk.CTkFont(size=13),
            text_color=ThemeColors.SUBTITLE,
        )
        fps_unit_label.pack(side="left", padx=(8, 0))

        button_row = ctk.CTkFrame(content, fg_color="transparent")
        button_row.pack(fill="x", pady=(15, 0))

        self._open_folder_button = OpenFolderButton(button_row, height=40)
        # Shown only after a successful conversion

        self._convert_button = ActionButton(
            button_row,
            text="Convert",
            command=self._on_convert_click,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            height=40,
        )
        self._convert_button.configure(state="disabled")
        self._convert_button.pack(side="right")

        return panel

    def _on_input_selected(self, file_path: Path) -> None:
        """Handle input file selection. Auto-populates filename from input stem."""
        self._filename_var.set(file_path.stem)
        self._update_validation()
        self._update_convert_button()

    def _on_folder_selected(self, folder_path: Path) -> None:
        """Handle output folder selection."""
        self._update_validation()
        self._update_convert_button()

    def _update_validation(self) -> None:
        """Update the validation message for missing required inputs."""
        input_path = self._input_picker.get_path()
        output_dir = self._output_folder_picker.get_path()
        missing = []
        if not input_path:
            missing.append("C3D input file")
        if not output_dir:
            missing.append("output directory")
        if missing:
            self._validation_label.configure(text=f"Missing: {', '.join(missing)}")
        else:
            self._validation_label.configure(text="")

    def _update_convert_button(self) -> None:
        """Enable convert button only when required inputs are set."""
        input_path = self._input_picker.get_path()
        output_dir = self._output_folder_picker.get_path()
        if input_path and output_dir and not self._is_converting:
            self._convert_button.configure(state="normal")
        else:
            self._convert_button.configure(state="disabled")

    def _on_convert_click(self) -> None:
        """Handle convert button click."""
        input_path = self._input_picker.get_path()
        output_dir = self._output_folder_picker.get_path()
        filename = self._filename_var.get().strip() or "animation"
        fps_text = self._fps_var.get().strip()

        try:
            fps = float(fps_text) if fps_text else 120.0
        except ValueError:
            self._log_output.set_error("Invalid FPS value. Please enter a number.")
            return

        output_path = output_dir / f"{filename}.bvh"

        self._is_converting = True
        if self._set_tabs_locked:
            self._set_tabs_locked(True)
        self._convert_button.configure(state="disabled", text="Converting...")
        self._log_output.reset()
        self._log_output.append_line("Starting conversion...")

        thread = threading.Thread(
            target=self._run_conversion,
            args=(input_path, output_path, fps),
            daemon=True,
        )
        thread.start()

    def _run_conversion(self, input_path: Path, output_path: Path, fps: float) -> None:
        """Run the C3D to BVH conversion in a background thread."""
        try:
            project_root = Path(__file__).resolve().parent.parent.parent
            script_path = (
                project_root
                / "mesh_generation_module"
                / "mesh_rigging_animation"
                / "c3d_to_bvh.py"
            )

            if sys.platform == "win32":
                python_path = (
                    project_root / "mesh_generation_module" / "myenv" / "Scripts" / "python.exe"
                )
            else:
                python_path = (
                    project_root / "mesh_generation_module" / "myenv" / "bin" / "python"
                )

            if not python_path.exists():
                raise RuntimeError(
                    f"Virtual environment not found at {python_path}. "
                    "Please set up the mesh_generation_module myenv."
                )

            output_path.parent.mkdir(parents=True, exist_ok=True)

            cmd = [
                str(python_path),
                "-u",
                str(script_path),
                "-i", str(input_path),
                "-o", str(output_path),
                "--fps", str(fps),
            ]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(script_path.parent),
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
                **_SUBPROCESS_FLAGS,
            )

            for line in iter(process.stdout.readline, ""):
                self._log_output.feed_line(line.rstrip("\n"))

            process.wait()

            if process.returncode != 0:
                raise RuntimeError(f"Conversion failed (exit code {process.returncode})")

            self.after(0, lambda: self._on_conversion_complete(output_path))

        except Exception as ex:
            error_msg = str(ex)
            self.after(0, lambda e=error_msg: self._on_conversion_error(e))

    def _on_conversion_complete(self, output_path: Path) -> None:
        """Handle conversion completion."""
        self._is_converting = False
        if self._set_tabs_locked:
            self._set_tabs_locked(False)
        self._open_folder_button.set_path(output_path.parent)
        self._open_folder_button.pack(side="left", padx=(0, 5))
        self._convert_button.configure(text="Convert Again")
        self._update_convert_button()
        self._log_output.set_complete(f"Saved: {output_path.name}")

    def _on_conversion_error(self, error: str) -> None:
        """Handle conversion error."""
        self._is_converting = False
        if self._set_tabs_locked:
            self._set_tabs_locked(False)
        self._convert_button.configure(text="Convert")
        self._update_convert_button()
        self._log_output.set_error(f"Error: {error}")

