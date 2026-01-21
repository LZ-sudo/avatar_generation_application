"""
Step 4: Avatar Configuration

Allows the user to configure avatar generation options.
"""

import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path

from ..app_state import AppState, RigType, HairStyle
from ..components.ui_elements import ThemeColors, PageHeader, SectionTitle


class StepConfigure(ctk.CTkFrame):
    """
    Configuration step for the avatar generation wizard.

    Provides options for rig type, hair style, and output settings.
    """

    WARNING_COLOR = "#c2410c"

    RIG_OPTIONS = {
        "Default": RigType.DEFAULT.value,
        "Default (No Toes)": RigType.DEFAULT_NO_TOES.value,
        "Game Engine": RigType.GAME_ENGINE.value,
    }

    HAIR_OPTIONS = {
        "None": HairStyle.NONE.value,
        "Short": HairStyle.SHORT.value,
        "Medium": HairStyle.MEDIUM.value,
        "Long": HairStyle.LONG.value,
    }

    def __init__(self, parent: ctk.CTkFrame, app_state: AppState):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self._build()

    def _build(self) -> None:
        """Build the step content."""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=30, pady=30)

        # Header
        header = PageHeader(
            content_frame,
            title="Configure Avatar",
            subtitle="Set avatar options and output preferences.",
            title_size=24,
            subtitle_size=14,
        )
        header.pack(pady=(0, 20))

        panels_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        panels_frame.pack(pady=20)

        avatar_options = self._create_avatar_options(panels_frame)
        avatar_options.pack(side="left", padx=15, anchor="n")

        output_options = self._create_output_options(panels_frame)
        output_options.pack(side="left", padx=15, anchor="n")

        self._validation_label = ctk.CTkLabel(
            content_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.WARNING_COLOR,
        )
        self._validation_label.pack(pady=(10, 0))

    def _create_avatar_options(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create the avatar options panel."""
        panel = ctk.CTkFrame(
            parent,
            fg_color=ThemeColors.PANEL_BG,
            border_width=1,
            border_color=ThemeColors.PANEL_BORDER,
            corner_radius=10,
        )

        content = ctk.CTkFrame(panel, fg_color="transparent")
        content.pack(padx=20, pady=20)

        title = SectionTitle(content, text="Avatar Options", font_size=16)
        title.pack(anchor="w")

        separator = ctk.CTkFrame(content, height=1, fg_color=ThemeColors.PANEL_BORDER)
        separator.pack(fill="x", pady=(10, 15))

        rig_label = ctk.CTkLabel(
            content,
            text="Rig Type",
            font=ctk.CTkFont(size=13),
            text_color=ThemeColors.SUBTITLE,
        )
        rig_label.pack(anchor="w")

        rig_values = list(self.RIG_OPTIONS.keys())
        current_rig = next(
            (k for k, v in self.RIG_OPTIONS.items() if v == self.app_state.configure.rig_type.value),
            rig_values[0]
        )

        self._rig_var = ctk.StringVar(value=current_rig)
        self._rig_dropdown = ctk.CTkOptionMenu(
            content,
            width=250,
            values=rig_values,
            variable=self._rig_var,
            command=self._on_rig_change,
        )
        self._rig_dropdown.pack(anchor="w", pady=(5, 15))

        hair_label = ctk.CTkLabel(
            content,
            text="Hair Style",
            font=ctk.CTkFont(size=13),
            text_color=ThemeColors.SUBTITLE,
        )
        hair_label.pack(anchor="w")

        hair_values = list(self.HAIR_OPTIONS.keys())
        current_hair = next(
            (k for k, v in self.HAIR_OPTIONS.items() if v == self.app_state.configure.hair_style.value),
            hair_values[0]
        )

        self._hair_var = ctk.StringVar(value=current_hair)
        self._hair_dropdown = ctk.CTkOptionMenu(
            content,
            width=250,
            values=hair_values,
            variable=self._hair_var,
            command=self._on_hair_change,
        )
        self._hair_dropdown.pack(anchor="w", pady=(5, 0))

        return panel

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
            value=str(self.app_state.configure.output_directory) if self.app_state.configure.output_directory else ""
        )
        self._dir_entry = ctk.CTkEntry(
            dir_frame,
            width=300,
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

        filename_label = ctk.CTkLabel(
            content,
            text="Output Filename",
            font=ctk.CTkFont(size=13),
            text_color=ThemeColors.SUBTITLE,
        )
        filename_label.pack(anchor="w")

        filename_frame = ctk.CTkFrame(content, fg_color="transparent")
        filename_frame.pack(anchor="w", pady=(5, 15))

        self._filename_var = ctk.StringVar(value=self.app_state.configure.output_filename)
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

        export_label = ctk.CTkLabel(
            content,
            text="Export Formats",
            font=ctk.CTkFont(size=13),
            text_color=ThemeColors.SUBTITLE,
        )
        export_label.pack(anchor="w")

        checkbox_frame = ctk.CTkFrame(content, fg_color="transparent")
        checkbox_frame.pack(anchor="w", pady=(5, 0))

        self._export_fbx_var = ctk.BooleanVar(value=self.app_state.configure.export_fbx)
        self._export_fbx_checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="Export FBX",
            variable=self._export_fbx_var,
            command=self._on_export_fbx_change,
        )
        self._export_fbx_checkbox.pack(side="left", padx=(0, 20))

        self._export_obj_var = ctk.BooleanVar(value=self.app_state.configure.export_obj)
        self._export_obj_checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="Export OBJ",
            variable=self._export_obj_var,
            command=self._on_export_obj_change,
        )
        self._export_obj_checkbox.pack(side="left")

        return panel

    def _open_folder_picker(self) -> None:
        """Open folder picker dialog."""
        folder_path = filedialog.askdirectory(
            title="Select Output Directory",
        )

        if folder_path:
            self.app_state.configure.output_directory = Path(folder_path)
            self._dir_var.set(folder_path)
            self._update_validation()
            self.app_state.notify_change()

    def _on_rig_change(self, value: str) -> None:
        """Handle rig type change."""
        rig_value = self.RIG_OPTIONS[value]
        self.app_state.configure.rig_type = RigType(rig_value)
        self.app_state.notify_change()

    def _on_hair_change(self, value: str) -> None:
        """Handle hair style change."""
        hair_value = self.HAIR_OPTIONS[value]
        self.app_state.configure.hair_style = HairStyle(hair_value)
        self.app_state.notify_change()

    def _on_filename_change(self, *args) -> None:
        """Handle filename change."""
        self.app_state.configure.output_filename = self._filename_var.get() or "avatar"
        self.app_state.notify_change()

    def _on_export_fbx_change(self) -> None:
        """Handle export FBX checkbox change."""
        self.app_state.configure.export_fbx = self._export_fbx_var.get()
        self.app_state.notify_change()

    def _on_export_obj_change(self) -> None:
        """Handle export OBJ checkbox change."""
        self.app_state.configure.export_obj = self._export_obj_var.get()
        self.app_state.notify_change()

    def _update_validation(self) -> None:
        """Update validation message."""
        if not self.app_state.configure.output_directory:
            self._validation_label.configure(text="Please select an output directory")
        else:
            self._validation_label.configure(text="")

    def validate(self) -> bool:
        """Validate the step is complete."""
        self._update_validation()
        return self.app_state.configure.is_complete()
