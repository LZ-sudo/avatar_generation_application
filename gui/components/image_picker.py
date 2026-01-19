"""
Image picker component.

Provides a file picker with image preview functionality.
"""

import flet as ft
from pathlib import Path
from typing import Callable, Optional


class ImagePicker(ft.Container):
    """
    Image picker component with preview.

    Displays a clickable area that opens a file picker dialog.
    Shows a preview of the selected image.
    """

    ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "bmp", "webp"]

    def __init__(
        self,
        label: str,
        description: str = "",
        on_image_selected: Callable[[Path], None] = None,
        width: int = 300,
        height: int = 350,
    ):
        super().__init__()
        self.label = label
        self.description = description
        self.on_image_selected = on_image_selected
        self._selected_path: Optional[Path] = None
        self._width = width
        self._height = height
        self._file_picker: Optional[ft.FilePicker] = None
        self._build()

    def _build(self) -> None:
        """Build the image picker component."""
        self.width = self._width
        self.height = self._height
        self.border = ft.Border.all(2, ft.Colors.GREY_400)
        self.border_radius = 10
        self.bgcolor = ft.Colors.GREY_100
        self.ink = True
        self.on_click = self._open_file_picker
        self.alignment = ft.Alignment(0, 0)

        self._placeholder = self._create_placeholder()
        self._preview = self._create_preview()

        self.content = self._placeholder

    def _create_placeholder(self) -> ft.Control:
        """Create the placeholder content shown before image selection."""
        return ft.Column(
            controls=[
                ft.Icon(
                    ft.Icons.ADD_PHOTO_ALTERNATE_OUTLINED,
                    size=48,
                    color=ft.Colors.GREY_500,
                ),
                ft.Text(
                    self.label,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_700,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    self.description,
                    size=12,
                    color=ft.Colors.GREY_500,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Click to select",
                    size=11,
                    color=ft.Colors.BLUE_400,
                    italic=True,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        )

    def _create_preview(self) -> ft.Control:
        """Create the preview content shown after image selection."""
        self._image_control = ft.Image(
            src="",
            fit="contain",
            width=self._width - 20,
            height=self._height - 60,
        )

        self._filename_text = ft.Text(
            "",
            size=11,
            color=ft.Colors.GREY_600,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
            text_align=ft.TextAlign.CENTER,
        )

        return ft.Column(
            controls=[
                self._image_control,
                self._filename_text,
                ft.Text(
                    "Click to change",
                    size=10,
                    color=ft.Colors.BLUE_400,
                    italic=True,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=4,
        )

    def setup_file_picker(self, page: ft.Page) -> None:
        """
        Set up the file picker service.

        Must be called after the component is added to the page.
        """
        self._file_picker = ft.FilePicker()
        self._file_picker.on_result = self._on_file_picked
        page.services.append(self._file_picker)
        page.update()

    async def _open_file_picker(self, e: ft.ControlEvent) -> None:
        """Open the file picker dialog."""
        if self._file_picker:
            await self._file_picker.pick_files(
                dialog_title=f"Select {self.label}",
                allowed_extensions=self.ALLOWED_EXTENSIONS,
                allow_multiple=False,
            )

    def _on_file_picked(self, e) -> None:
        """Handle file picker result."""
        if e.files and len(e.files) > 0:
            file_path = Path(e.files[0].path)
            self.set_image(file_path)

            if self.on_image_selected:
                self.on_image_selected(file_path)

    def set_image(self, path: Path) -> None:
        """Set the selected image and update preview."""
        self._selected_path = path
        self._image_control.src = str(path)
        self._filename_text.value = path.name
        self.border = ft.Border.all(2, ft.Colors.GREEN_500)
        self.content = self._preview
        self.update()

    def clear_image(self) -> None:
        """Clear the selected image."""
        self._selected_path = None
        self.border = ft.Border.all(2, ft.Colors.GREY_400)
        self.content = self._placeholder
        self.update()

    @property
    def selected_path(self) -> Optional[Path]:
        """Get the currently selected image path."""
        return self._selected_path

    @property
    def has_image(self) -> bool:
        """Check if an image has been selected."""
        return self._selected_path is not None
