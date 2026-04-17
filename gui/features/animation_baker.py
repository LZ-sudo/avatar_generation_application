"""
Animation Baker Feature View

Provides UI for baking a BVH animation into an FBX avatar's CMU MB rig
and exporting the result as a new animated FBX file.
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
    StatusLabel,
)
from ..components.log_output import LogOutput

_SUBPROCESS_FLAGS = {"creationflags": subprocess.CREATE_NO_WINDOW} if sys.platform == "win32" else {}


class AnimationBakerView(ctk.CTkFrame):
    """
    Animation baker view.

    Imports an FBX avatar with a CMU MB rig, retargets a BVH animation
    onto the rig via Blender's retarget_bvh addon, and exports the result
    as an animated FBX file.
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        set_tabs_locked: Optional[Callable[[bool], None]] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self._set_tabs_locked = set_tabs_locked
        self._is_baking = False
        self._build()

    def _build(self) -> None:
        """Build the view content."""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=30, pady=30)

        header = PageHeader(
            content_frame,
            title="Animation Baker",
            subtitle="Bake a BVH animation onto an FBX avatar's CMU MB rig.",
            title_size=24,
            subtitle_size=14,
        )
        header.pack(pady=(0, 20))

        panel = self._create_baker_panel(content_frame)
        panel.pack(pady=5)

        self._validation_label = StatusLabel(content_frame, text="")
        self._validation_label.pack(pady=(0, 5))

        self._log_output = LogOutput(content_frame, width=480, height=75)
        self._log_output.pack(pady=(0, 0))

        self._update_validation()

    def _create_baker_panel(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create the baker settings panel."""
        panel = Card(parent)
        content = panel.content

        header = SectionHeader(content, text="Baking Settings", font_size=16)
        header.pack(anchor="w", fill="x")

        self._fbx_picker = FilePicker(
            content,
            label="Input FBX Avatar",
            filetypes=[("FBX files", "*.fbx"), ("All files", "*.*")],
            entry_width=380,
            on_file_selected=self._on_fbx_selected,
        )
        self._fbx_picker.pack(anchor="w", fill="x", pady=(0, 15))

        self._bvh_picker = FilePicker(
            content,
            label="Input BVH Animation",
            filetypes=[("BVH files", "*.bvh"), ("All files", "*.*")],
            entry_width=380,
            on_file_selected=self._on_bvh_selected,
        )
        self._bvh_picker.pack(anchor="w", fill="x", pady=(0, 15))

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

        self._filename_var = ctk.StringVar(value="avatar_animated")
        self._filename_entry = ctk.CTkEntry(
            filename_frame,
            width=200,
            textvariable=self._filename_var,
            placeholder_text="avatar_animated",
        )
        self._filename_entry.pack(side="left")

        extension_label = ctk.CTkLabel(
            filename_frame,
            text=".fbx",
            font=ctk.CTkFont(size=13),
            text_color=ThemeColors.SUBTITLE,
        )
        extension_label.pack(side="left", padx=(5, 0))

        button_row = ctk.CTkFrame(content, fg_color="transparent")
        button_row.pack(fill="x", pady=(15, 0))

        self._open_folder_button = OpenFolderButton(button_row, height=40)
        # Shown only after a successful bake

        self._bake_button = ActionButton(
            button_row,
            text="Bake Animation",
            command=self._on_bake_click,
            height=40,
        )
        self._bake_button.configure(state="disabled")
        self._bake_button.pack(side="right")

        return panel

    def _on_fbx_selected(self, file_path: Path) -> None:
        """Handle FBX file selection. Auto-populates filename from input stem."""
        self._filename_var.set(f"{file_path.stem}_animated")
        self._update_validation()
        self._update_bake_button()

    def _on_bvh_selected(self, file_path: Path) -> None:
        """Handle BVH file selection."""
        self._update_validation()
        self._update_bake_button()

    def _on_folder_selected(self, folder_path: Path) -> None:
        """Handle output folder selection."""
        self._update_validation()
        self._update_bake_button()

    def _update_validation(self) -> None:
        """Update the validation message for missing required inputs."""
        fbx_path = self._fbx_picker.get_path()
        bvh_path = self._bvh_picker.get_path()
        output_dir = self._output_folder_picker.get_path()
        missing = []
        if not fbx_path:
            missing.append("FBX avatar")
        if not bvh_path:
            missing.append("BVH animation")
        if not output_dir:
            missing.append("output directory")
        if missing:
            self._validation_label.set_error(f"Missing: {', '.join(missing)}")
        else:
            self._validation_label.clear()

    def _update_bake_button(self) -> None:
        """Enable bake button only when all required inputs are set."""
        fbx_path = self._fbx_picker.get_path()
        bvh_path = self._bvh_picker.get_path()
        output_dir = self._output_folder_picker.get_path()
        if fbx_path and bvh_path and output_dir and not self._is_baking:
            self._bake_button.configure(state="normal")
        else:
            self._bake_button.configure(state="disabled")

    def _on_bake_click(self) -> None:
        """Handle bake button click."""
        fbx_path = self._fbx_picker.get_path()
        bvh_path = self._bvh_picker.get_path()
        output_dir = self._output_folder_picker.get_path()
        filename = self._filename_var.get().strip() or "avatar_animated"
        output_path = output_dir / f"{filename}.fbx"

        self._is_baking = True
        if self._set_tabs_locked:
            self._set_tabs_locked(True)
        self._bake_button.configure(state="disabled", text="Baking...")
        self._log_output.reset()
        self._log_output.append_line("Starting animation bake...")

        thread = threading.Thread(
            target=self._run_bake,
            args=(fbx_path, bvh_path, output_path),
            daemon=True,
        )
        thread.start()

    def _run_bake(self, fbx_path: Path, bvh_path: Path, output_path: Path) -> None:
        """Run the animation bake in a background thread."""
        try:
            project_root = Path(__file__).resolve().parent.parent.parent
            script_path = (
                project_root
                / "mesh_generation_module"
                / "mesh_rigging_animation"
                / "bake_animation.py"
            )
            run_blender_path = project_root / "mesh_generation_module" / "run_blender.py"

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
                str(run_blender_path),
                "--script", str(script_path),
                "--",
                "--fbx", str(fbx_path),
                "--bvh", str(bvh_path),
                "--output", str(output_path),
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(run_blender_path.parent),
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
                **_SUBPROCESS_FLAGS,
            )

            for line in iter(process.stdout.readline, ""):
                self._log_output.feed_line(line.rstrip("\n"))

            process.wait()

            if process.returncode != 0:
                raise RuntimeError(f"Bake failed (exit code {process.returncode})")

            self.after(0, lambda: self._on_bake_complete(output_path))

        except Exception as ex:
            error_msg = str(ex)
            self.after(0, lambda e=error_msg: self._on_bake_error(e))

    def _on_bake_complete(self, output_path: Path) -> None:
        """Handle bake completion."""
        self._is_baking = False
        if self._set_tabs_locked:
            self._set_tabs_locked(False)
        self._open_folder_button.set_path(output_path.parent)
        self._open_folder_button.pack(side="left", padx=(0, 5))
        self._bake_button.configure(text="Bake Again")
        self._update_bake_button()
        self._validation_label.set_success(f"Saved: {output_path.name}")

    def _on_bake_error(self, error: str) -> None:
        """Handle bake error."""
        self._is_baking = False
        if self._set_tabs_locked:
            self._set_tabs_locked(False)
        self._bake_button.configure(text="Bake Animation")
        self._update_bake_button()
        self._validation_label.set_error(f"Error: {error}")
