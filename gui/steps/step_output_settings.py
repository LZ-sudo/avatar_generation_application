"""
Step 5: Output Settings

Allows the user to configure output directory and export format options.
"""

import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
from typing import Optional, Callable

from ..app_state import AppState
from ..components.ui_elements import ThemeColors, PageHeader, SectionTitle


class StepOutputSettings(ctk.CTkFrame):
    """
    Output settings step for the avatar generation wizard.

    Provides options for output directory, filename, and export formats.
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        app_state: AppState,
        on_generate: Optional[Callable[[], None]] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self.on_generate = on_generate
        self._build()

    def _build(self) -> None:
        """Build the step content."""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=30, pady=30)

        # Header
        header = PageHeader(
            content_frame,
            title="Output Settings",
            subtitle="Configure where and how to save the generated avatar.",
            title_size=24,
            subtitle_size=14,
        )
        header.pack(pady=(0, 20))

        # Center the output options panel
        output_options = self._create_output_options(content_frame)
        output_options.pack(pady=20)

        self._validation_label = ctk.CTkLabel(
            content_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.WARNING,
        )
        self._validation_label.pack(pady=(10, 0))

        # Generate Avatar button
        self._generate_button = ctk.CTkButton(
            content_frame,
            text="Generate Avatar",
            command=self._on_generate_click,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self._generate_button.pack(pady=(20, 0))
        self._update_generate_button()

    def _create_output_options(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create the output options panel."""
        panel = ctk.CTkFrame(
            parent,
            fg_color=ThemeColors.PANEL_BG,
            border_width=1,
            border_color=ThemeColors.PANEL_BORDER,
            corner_radius=10,
        )

        content = ctk.CTkFrame(panel, fg_color="transparent")
        content.pack(padx=20, pady=20)

        title = SectionTitle(content, text="Output Settings", font_size=16)
        title.pack(anchor="w")

        separator = ctk.CTkFrame(content, height=1, fg_color=ThemeColors.PANEL_BORDER)
        separator.pack(fill="x", pady=(10, 15))

        # Output Directory
        dir_label = ctk.CTkLabel(
            content,
            text="Output Directory",
            font=ctk.CTkFont(size=13),
            text_color=ThemeColors.SUBTITLE,
        )
        dir_label.pack(anchor="w")

        dir_frame = ctk.CTkFrame(content, fg_color="transparent")
        dir_frame.pack(anchor="w", pady=(5, 15), fill="x")

        self._dir_var = ctk.StringVar(
            value=str(self.app_state.output_settings.output_directory) if self.app_state.output_settings.output_directory else ""
        )
        self._dir_entry = ctk.CTkEntry(
            dir_frame,
            width=380,
            textvariable=self._dir_var,
            state="disabled",
            placeholder_text="Click 'Browse' to select output folder",
        )
        self._dir_entry.pack(side="left")

        browse_button = ctk.CTkButton(
            dir_frame,
            text="Browse",
            width=80,
            command=self._open_folder_picker,
        )
        browse_button.pack(side="left", padx=(10, 0))

        # Output Filename
        filename_label = ctk.CTkLabel(
            content,
            text="Output Filename",
            font=ctk.CTkFont(size=13),
            text_color=ThemeColors.SUBTITLE,
        )
        filename_label.pack(anchor="w")

        filename_frame = ctk.CTkFrame(content, fg_color="transparent")
        filename_frame.pack(anchor="w", pady=(5, 15))

        self._filename_var = ctk.StringVar(value=self.app_state.output_settings.output_filename)
        self._filename_var.trace_add("write", self._on_filename_change)

        self._filename_entry = ctk.CTkEntry(
            filename_frame,
            width=200,
            textvariable=self._filename_var,
            placeholder_text="avatar",
        )
        self._filename_entry.pack(side="left")

        extension_label = ctk.CTkLabel(
            filename_frame,
            text=".fbx",
            font=ctk.CTkFont(size=13),
            text_color=ThemeColors.SUBTITLE,
        )
        extension_label.pack(side="left", padx=(5, 0))

        return panel

    def _open_folder_picker(self) -> None:
        """Open folder picker dialog."""
        folder_path = filedialog.askdirectory(
            title="Select Output Directory",
        )

        if folder_path:
            self.app_state.output_settings.output_directory = Path(folder_path)
            self._dir_var.set(folder_path)
            self._update_validation()
            self._update_generate_button()
            self.app_state.notify_change()

    def _on_filename_change(self, *args) -> None:
        """Handle filename change."""
        self.app_state.output_settings.output_filename = self._filename_var.get() or "avatar"
        self._update_generate_button()
        self.app_state.notify_change()

    def _update_validation(self) -> None:
        """Update validation message."""
        if not self.app_state.output_settings.output_directory:
            self._validation_label.configure(text="Please select an output directory")
        else:
            self._validation_label.configure(text="")

    def _update_generate_button(self) -> None:
        """Update generate button state based on validation."""
        if self.validate():
            self._generate_button.configure(state="normal")
        else:
            self._generate_button.configure(state="disabled")

    def _on_generate_click(self) -> None:
        """Handle generate button click."""
        if self.validate() and self.on_generate:
            self.on_generate()

    def validate(self) -> bool:
        """Validate the step is complete."""
        # Always export as FBX only
        self.app_state.output_settings.export_fbx = True
        self.app_state.output_settings.export_obj = False
        self._update_validation()
        return self.app_state.output_settings.is_complete()
