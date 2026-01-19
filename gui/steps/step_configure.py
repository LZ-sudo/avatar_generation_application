"""
Step 3: Avatar Configuration

Allows the user to configure avatar generation options.
"""

import flet as ft
from pathlib import Path

from ..app_state import AppState, RigType, HairStyle


class StepConfigure(ft.Container):
    """
    Configuration step for the avatar generation wizard.

    Provides options for rig type, hair style, and output settings.
    """

    def __init__(self, app_state: AppState):
        super().__init__()
        self.app_state = app_state
        self._folder_picker = None
        self._build()

    def _build(self) -> None:
        """Build the step content."""
        header = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Configure Avatar",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_800,
                    ),
                    ft.Text(
                        "Set avatar options and output preferences.",
                        size=14,
                        color=ft.Colors.GREY_600,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=ft.Padding.only(bottom=20),
        )

        self._rig_dropdown = ft.Dropdown(
            label="Rig Type",
            width=300,
            options=[
                ft.DropdownOption(key=RigType.DEFAULT.value, text="Default"),
                ft.DropdownOption(key=RigType.DEFAULT_NO_TOES.value, text="Default (No Toes)"),
                ft.DropdownOption(key=RigType.GAME_ENGINE.value, text="Game Engine"),
            ],
            value=self.app_state.configure.rig_type.value,
            on_select=self._on_rig_change,
        )

        self._hair_dropdown = ft.Dropdown(
            label="Hair Style",
            width=300,
            options=[
                ft.DropdownOption(key=HairStyle.NONE.value, text="None"),
                ft.DropdownOption(key=HairStyle.SHORT.value, text="Short"),
                ft.DropdownOption(key=HairStyle.MEDIUM.value, text="Medium"),
                ft.DropdownOption(key=HairStyle.LONG.value, text="Long"),
            ],
            value=self.app_state.configure.hair_style.value,
            on_select=self._on_hair_change,
        )

        self._output_path_field = ft.TextField(
            label="Output Directory",
            width=400,
            read_only=True,
            value=str(self.app_state.configure.output_directory) if self.app_state.configure.output_directory else "",
            hint_text="Click 'Browse' to select output folder",
        )

        self._browse_button = ft.Button(
            "Browse",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=self._open_folder_picker,
        )

        self._filename_field = ft.TextField(
            label="Output Filename",
            width=300,
            value=self.app_state.configure.output_filename,
            on_change=self._on_filename_change,
            hint_text="avatar",
            suffix=ft.Text(".fbx"),
        )

        self._export_fbx_checkbox = ft.Checkbox(
            label="Export FBX",
            value=self.app_state.configure.export_fbx,
            on_change=self._on_export_fbx_change,
        )

        self._export_obj_checkbox = ft.Checkbox(
            label="Export OBJ",
            value=self.app_state.configure.export_obj,
            on_change=self._on_export_obj_change,
        )

        avatar_options = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Avatar Options",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_700,
                    ),
                    ft.Divider(height=1),
                    self._rig_dropdown,
                    self._hair_dropdown,
                ],
                spacing=15,
            ),
            bgcolor=ft.Colors.WHITE,
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            padding=20,
            width=400,
        )

        output_options = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Output Settings",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_700,
                    ),
                    ft.Divider(height=1),
                    ft.Row(
                        controls=[
                            self._output_path_field,
                            self._browse_button,
                        ],
                        spacing=10,
                    ),
                    self._filename_field,
                    ft.Row(
                        controls=[
                            self._export_fbx_checkbox,
                            self._export_obj_checkbox,
                        ],
                        spacing=20,
                    ),
                ],
                spacing=15,
            ),
            bgcolor=ft.Colors.WHITE,
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            padding=20,
            width=550,
        )

        self._validation_text = ft.Text(
            "",
            size=12,
            color=ft.Colors.ORANGE_700,
            text_align=ft.TextAlign.CENTER,
        )

        self.content = ft.Column(
            controls=[
                header,
                ft.Row(
                    controls=[avatar_options, output_options],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=30,
                    wrap=True,
                ),
                self._validation_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        )

        self.padding = 30
        self.expand = True

    def setup(self, page: ft.Page) -> None:
        """Set up the step after adding to page."""
        self._folder_picker = ft.FilePicker()
        self._folder_picker.on_result = self._on_folder_picked
        page.services.append(self._folder_picker)
        page.update()

    async def _open_folder_picker(self, e) -> None:
        """Open folder picker dialog."""
        if self._folder_picker:
            await self._folder_picker.get_directory_path(
                dialog_title="Select Output Directory",
            )

    def _on_folder_picked(self, e) -> None:
        """Handle folder picker result."""
        if e.path:
            self.app_state.configure.output_directory = Path(e.path)
            self._output_path_field.value = e.path
            self._update_validation()
            self.app_state.notify_change()
            self.update()

    def _on_rig_change(self, e: ft.ControlEvent) -> None:
        """Handle rig type change."""
        self.app_state.configure.rig_type = RigType(e.control.value)
        self.app_state.notify_change()

    def _on_hair_change(self, e: ft.ControlEvent) -> None:
        """Handle hair style change."""
        self.app_state.configure.hair_style = HairStyle(e.control.value)
        self.app_state.notify_change()

    def _on_filename_change(self, e: ft.ControlEvent) -> None:
        """Handle filename change."""
        self.app_state.configure.output_filename = e.control.value or "avatar"
        self.app_state.notify_change()

    def _on_export_fbx_change(self, e: ft.ControlEvent) -> None:
        """Handle export FBX checkbox change."""
        self.app_state.configure.export_fbx = e.control.value
        self.app_state.notify_change()

    def _on_export_obj_change(self, e: ft.ControlEvent) -> None:
        """Handle export OBJ checkbox change."""
        self.app_state.configure.export_obj = e.control.value
        self.app_state.notify_change()

    def _update_validation(self) -> None:
        """Update validation message."""
        if not self.app_state.configure.output_directory:
            self._validation_text.value = "Please select an output directory"
        else:
            self._validation_text.value = ""
        self._validation_text.update()

    def validate(self) -> bool:
        """Validate the step is complete."""
        self._update_validation()
        return self.app_state.configure.is_complete()
