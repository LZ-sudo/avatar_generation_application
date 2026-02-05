"""
Image picker component.

Provides a file picker with image preview functionality.
"""

import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
from typing import Callable, Optional
from PIL import Image


class ImagePicker(ctk.CTkFrame):
    """
    Image picker component with preview.

    Displays a clickable area that opens a file picker dialog.
    Shows a preview of the selected image.
    """

    ALLOWED_EXTENSIONS = [
        ("Image files", "*.png *.jpg *.jpeg *.bmp *.webp"),
        ("PNG files", "*.png"),
        ("JPEG files", "*.jpg *.jpeg"),
        ("All files", "*.*"),
    ]

    COLORS = {
        "border_default": "#9ca3af",
        "border_selected": "#22c55e",
        "bg": "#f3f4f6",
        "text_primary": "#374151",
        "text_secondary": "#6b7280",
        "text_hint": "#60a5fa",
    }

    def __init__(
        self,
        parent: ctk.CTkFrame,
        label: str,
        description: str = "",
        on_image_selected: Optional[Callable[[Path], None]] = None,
        width: int = 300,
        height: int = 350,
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            corner_radius=10,
            border_width=2,
            border_color=self.COLORS["border_default"],
            fg_color=self.COLORS["bg"],
        )
        self.pack_propagate(False)

        self.label = label
        self.description = description
        self.on_image_selected = on_image_selected
        self._selected_path: Optional[Path] = None
        self._width = width
        self._height = height
        self._enabled = True

        self._build()
        self.bind("<Button-1>", self._open_file_picker)

    def _build(self) -> None:
        """Build the image picker component."""
        self._placeholder_frame = self._create_placeholder()
        self._preview_frame = self._create_preview()

        self._placeholder_frame.pack(expand=True, fill="both")
        self._preview_frame.pack_forget()

    def _create_placeholder(self) -> ctk.CTkFrame:
        """Create the placeholder content shown before image selection."""
        frame = ctk.CTkFrame(self, fg_color="transparent")

        icon_label = ctk.CTkLabel(
            frame,
            text="+",
            font=ctk.CTkFont(size=48),
            text_color=self.COLORS["text_secondary"],
        )
        icon_label.pack(pady=(40, 10))
        icon_label.bind("<Button-1>", self._open_file_picker)

        title_label = ctk.CTkLabel(
            frame,
            text=self.label,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.COLORS["text_primary"],
        )
        title_label.pack(pady=(0, 5))
        title_label.bind("<Button-1>", self._open_file_picker)

        desc_label = ctk.CTkLabel(
            frame,
            text=self.description,
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["text_secondary"],
        )
        desc_label.pack(pady=(0, 10))
        desc_label.bind("<Button-1>", self._open_file_picker)

        hint_label = ctk.CTkLabel(
            frame,
            text="Click to select",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color=self.COLORS["text_hint"],
        )
        hint_label.pack()
        hint_label.bind("<Button-1>", self._open_file_picker)

        frame.bind("<Button-1>", self._open_file_picker)
        return frame

    def _create_preview(self) -> ctk.CTkFrame:
        """Create the preview content shown after image selection."""
        frame = ctk.CTkFrame(self, fg_color="transparent")

        self._image_label = ctk.CTkLabel(
            frame,
            text="",
            width=self._width - 20,
            height=self._height - 60,
        )
        self._image_label.pack(pady=(10, 5))
        self._image_label.bind("<Button-1>", self._open_file_picker)

        self._filename_label = ctk.CTkLabel(
            frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=self.COLORS["text_secondary"],
        )
        self._filename_label.pack(pady=(0, 2))
        self._filename_label.bind("<Button-1>", self._open_file_picker)

        hint_label = ctk.CTkLabel(
            frame,
            text="Click to change",
            font=ctk.CTkFont(size=10, slant="italic"),
            text_color=self.COLORS["text_hint"],
        )
        hint_label.pack()
        hint_label.bind("<Button-1>", self._open_file_picker)

        frame.bind("<Button-1>", self._open_file_picker)
        return frame

    def _open_file_picker(self, event=None) -> None:
        """Open the file picker dialog."""
        if not self._enabled:
            return

        file_path = filedialog.askopenfilename(
            title=f"Select {self.label}",
            filetypes=self.ALLOWED_EXTENSIONS,
        )

        if file_path:
            path = Path(file_path)
            self.set_image(path)

            if self.on_image_selected:
                self.on_image_selected(path)

    def set_image(self, path: Path) -> None:
        """Set the selected image and update preview."""
        self._selected_path = path

        try:
            pil_image = Image.open(path)

            max_width = self._width - 20
            max_height = self._height - 60

            pil_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            ctk_image = ctk.CTkImage(
                light_image=pil_image,
                dark_image=pil_image,
                size=(pil_image.width, pil_image.height),
            )

            self._image_label.configure(image=ctk_image, text="")
            self._image_label._image = ctk_image

        except Exception:
            self._image_label.configure(image=None, text="Preview unavailable")

        self._filename_label.configure(text=path.name)
        self.configure(border_color=self.COLORS["border_selected"])

        self._placeholder_frame.pack_forget()
        self._preview_frame.pack(expand=True, fill="both")

    def clear_image(self) -> None:
        """Clear the selected image."""
        self._selected_path = None
        self.configure(border_color=self.COLORS["border_default"])

        self._preview_frame.pack_forget()
        self._placeholder_frame.pack(expand=True, fill="both")

    @property
    def selected_path(self) -> Optional[Path]:
        """Get the currently selected image path."""
        return self._selected_path

    @property
    def has_image(self) -> bool:
        """Check if an image has been selected."""
        return self._selected_path is not None

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the image picker."""
        self._enabled = enabled
        if enabled:
            self.configure(cursor="hand2")
        else:
            self.configure(cursor="arrow")
