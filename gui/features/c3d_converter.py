"""
C3D Converter Feature View

Provides UI for converting Cometa C3D joint angle files to BVH animation format.
"""

import subprocess
import sys
import threading
from pathlib import Path

import customtkinter as ctk

from ..components.ui_elements import (
    ThemeColors,
    PageHeader,
    SectionHeader,
    Card,
    FilePicker,
    FolderPicker,
    StatusLabel,
    OpenFolderButton,
    ActionButton,
)

_SUBPROCESS_FLAGS = {"creationflags": subprocess.CREATE_NO_WINDOW} if sys.platform == "win32" else {}


class C3dConverterView(ctk.CTkFrame):
    """
    C3D to BVH converter view.

    Converts Cometa C3D joint angle files to BVH animation format
    using the c3d_to_bvh.py script in the mesh_rigging_animation module.
    """

    def __init__(self, parent: ctk.CTkFrame):
        super().__init__(parent, fg_color="transparent")
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
        panel.pack(pady=20)

        self._status_label = StatusLabel(content_frame, text="")
        self._status_label.pack(pady=(10, 0))

        self._buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self._buttons_frame.pack(pady=(20, 0))

        self._convert_button = ActionButton(
            self._buttons_frame,
            text="Convert",
            command=self._on_convert_click,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            height=40,
        )
        self._convert_button.configure(state="disabled")
        self._convert_button.pack(side="left", padx=5)

        self._open_folder_button = OpenFolderButton(
            self._buttons_frame,
            height=40,
        )
        # Shown only after a successful conversion

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
        fps_frame.pack(anchor="w", pady=(5, 0))

        self._fps_var = ctk.StringVar(value="120")
        self._fps_entry = ctk.CTkEntry(
            fps_frame,
            width=80,
            textvariable=self._fps_var,
            justify="right",
        )
        self._fps_entry.pack(side="left")

        fps_unit_label = ctk.CTkLabel(
            fps_frame,
            text="fps",
            font=ctk.CTkFont(size=13),
            text_color=ThemeColors.SUBTITLE,
        )
        fps_unit_label.pack(side="left", padx=(8, 0))

        return panel

    def _on_input_selected(self, file_path: Path) -> None:
        """Handle input file selection. Auto-populates filename from input stem."""
        self._filename_var.set(file_path.stem)
        self._update_convert_button()

    def _on_folder_selected(self, folder_path: Path) -> None:
        """Handle output folder selection."""
        self._update_convert_button()

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
            self._status_label.set_error("Invalid FPS value. Please enter a number.")
            return

        output_path = output_dir / f"{filename}.bvh"

        self._is_converting = True
        self._convert_button.configure(state="disabled", text="Converting...")
        self._status_label.set_info("Converting...")

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
                str(script_path),
                "-i", str(input_path),
                "-o", str(output_path),
                "--fps", str(fps),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(script_path.parent),
                **_SUBPROCESS_FLAGS,
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                raise RuntimeError(f"Conversion failed: {error_msg}")

            self.after(0, lambda: self._on_conversion_complete(output_path))

        except Exception as ex:
            error_msg = str(ex)
            self.after(0, lambda e=error_msg: self._on_conversion_error(e))

    def _on_conversion_complete(self, output_path: Path) -> None:
        """Handle conversion completion."""
        self._is_converting = False
        self._open_folder_button.set_path(output_path.parent)
        self._open_folder_button.pack(side="left", padx=5, before=self._convert_button)
        self._convert_button.configure(text="Convert Again")
        self._update_convert_button()
        self._status_label.set_success(f"Saved: {output_path.name}")

    def _on_conversion_error(self, error: str) -> None:
        """Handle conversion error."""
        self._is_converting = False
        self._convert_button.configure(text="Convert")
        self._update_convert_button()
        self._status_label.set_error(f"Error: {error}")

