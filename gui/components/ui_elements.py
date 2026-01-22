"""
Reusable UI elements for the Avatar Generator application.

This module provides common UI components used across wizard steps
to ensure consistent styling and reduce code duplication.
"""

import customtkinter as ctk
from typing import Callable, Optional


class ThemeColors:
    """Centralized color palette for the application."""

    # Text colors
    TITLE = "#1f2937"
    SUBTITLE = "#6b7280"
    LABEL = "#374151"
    INFO_TEXT = "#6b7280"

    # Panel colors
    PANEL_BG = "#ffffff"
    PANEL_BORDER = "#d1d5db"

    # Header colors
    HEADER_BG = "#f3f4f6"
    HEADER_TEXT = "#6b7280"

    # Status colors
    STATUS_BLUE = "#2563eb"
    STATUS_GREEN = "#16a34a"
    STATUS_RED = "#dc2626"
    STATUS_ORANGE = "#ea580c"

    # Row colors (for tables)
    ROW_BG = "#ffffff"
    ROW_ALT_BG = "#f9fafb"

    # Icon colors
    INFO_ICON = "#2563eb"

    @classmethod
    def get_colors_dict(cls) -> dict:
        """Return colors as a dictionary for backward compatibility."""
        return {
            "title": cls.TITLE,
            "subtitle": cls.SUBTITLE,
            "label": cls.LABEL,
            "info_text": cls.INFO_TEXT,
            "panel_bg": cls.PANEL_BG,
            "panel_border": cls.PANEL_BORDER,
            "header_bg": cls.HEADER_BG,
            "header_text": cls.HEADER_TEXT,
            "status_blue": cls.STATUS_BLUE,
            "status_green": cls.STATUS_GREEN,
            "status_red": cls.STATUS_RED,
            "status_orange": cls.STATUS_ORANGE,
            "row_bg": cls.ROW_BG,
            "row_alt_bg": cls.ROW_ALT_BG,
            "info_icon": cls.INFO_ICON,
            "section_title": cls.LABEL,
            "converged": cls.STATUS_GREEN,
            "not_converged": cls.STATUS_RED,
            "text": cls.LABEL,
            "summary_green": cls.STATUS_GREEN,
            "summary_red": cls.STATUS_RED,
            "summary_blue": cls.STATUS_BLUE,
        }


class PageHeader(ctk.CTkFrame):
    """
    Page header component with title and optional subtitle.

    Provides consistent styling for wizard step headers.
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        title: str,
        subtitle: Optional[str] = None,
        title_size: int = 20,
        subtitle_size: int = 12,
    ):
        super().__init__(parent, fg_color="transparent")

        self._title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=title_size, weight="bold"),
            text_color=ThemeColors.TITLE,
        )
        self._title_label.pack()

        if subtitle:
            self._subtitle_label = ctk.CTkLabel(
                self,
                text=subtitle,
                font=ctk.CTkFont(size=subtitle_size),
                text_color=ThemeColors.SUBTITLE,
            )
            self._subtitle_label.pack(pady=(4, 0))

    def set_title(self, title: str) -> None:
        """Update the title text."""
        self._title_label.configure(text=title)

    def set_subtitle(self, subtitle: str) -> None:
        """Update the subtitle text."""
        if hasattr(self, "_subtitle_label"):
            self._subtitle_label.configure(text=subtitle)


class Card(ctk.CTkFrame):
    """
    Card/Panel component with consistent border and background styling.

    Use this for grouping related content within wizard steps.
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        width: Optional[int] = None,
        height: Optional[int] = None,
        corner_radius: int = 10,
        padding: tuple = (20, 15),
    ):
        kwargs = {
            "fg_color": ThemeColors.PANEL_BG,
            "border_width": 1,
            "border_color": ThemeColors.PANEL_BORDER,
            "corner_radius": corner_radius,
        }
        if width is not None:
            kwargs["width"] = width
        if height is not None:
            kwargs["height"] = height

        super().__init__(parent, **kwargs)

        self._content = ctk.CTkFrame(self, fg_color="transparent")
        self._content.pack(padx=padding[0], pady=padding[1])

    @property
    def content(self) -> ctk.CTkFrame:
        """Return the content frame for adding child widgets."""
        return self._content


class LabeledInputField(ctk.CTkFrame):
    """
    Input field with label and optional unit suffix.

    Commonly used for measurement inputs and numeric values.
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        label: str,
        unit: str = "",
        value: Optional[float] = None,
        label_width: int = 160,
        entry_width: int = 70,
        on_change: Optional[Callable[[Optional[float]], None]] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self._on_value_change = on_change

        self._label = ctk.CTkLabel(
            self,
            text=label,
            font=ctk.CTkFont(size=13),
            text_color=ThemeColors.LABEL,
            width=label_width,
            anchor="w",
        )
        self._label.pack(side="left")

        self._entry_var = ctk.StringVar(value=str(value) if value is not None else "")
        self._entry_var.trace_add("write", self._handle_change)

        entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        entry_frame.pack(side="left")

        self._entry = ctk.CTkEntry(
            entry_frame,
            width=entry_width,
            textvariable=self._entry_var,
            justify="right",
        )
        self._entry.pack(side="left")

        if unit:
            unit_label = ctk.CTkLabel(
                entry_frame,
                text=unit,
                font=ctk.CTkFont(size=12),
                text_color=ThemeColors.LABEL,
                width=25,
            )
            unit_label.pack(side="left", padx=(5, 0))

    def _handle_change(self, *args) -> None:
        """Handle value change."""
        try:
            value = float(self._entry_var.get()) if self._entry_var.get() else None
            if self._on_value_change:
                self._on_value_change(value)
        except ValueError:
            pass

    def set_value(self, value: Optional[float]) -> None:
        """Set the field value."""
        if value is not None:
            self._entry_var.set(f"{value:.1f}")
        else:
            self._entry_var.set("")

    @property
    def value(self) -> Optional[float]:
        """Get the current value."""
        try:
            return float(self._entry_var.get()) if self._entry_var.get() else None
        except ValueError:
            return None


class LabeledDropdown(ctk.CTkFrame):
    """
    Dropdown field with label and optional icon.

    Used for selecting from predefined options.
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        label: str,
        values: list[str],
        icon: Optional[str] = None,
        placeholder: str = "Select...",
        width: int = 180,
        on_change: Optional[Callable[[str], None]] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self._on_change = on_change

        label_frame = ctk.CTkFrame(self, fg_color="transparent")
        label_frame.pack(anchor="w")

        if icon:
            icon_label = ctk.CTkLabel(
                label_frame,
                text=icon,
                font=ctk.CTkFont(size=13),
                text_color=ThemeColors.LABEL,
            )
            icon_label.pack(side="left")

        text_label = ctk.CTkLabel(
            label_frame,
            text=label,
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.LABEL,
        )
        text_label.pack(side="left", padx=(4 if icon else 0, 0))

        self._var = ctk.StringVar(value="")
        self._dropdown = ctk.CTkOptionMenu(
            self,
            width=width,
            height=28,
            values=values,
            variable=self._var,
            command=self._handle_change,
        )
        self._dropdown.set(placeholder)
        self._dropdown.pack(anchor="w", pady=(2, 0))

    def _handle_change(self, value: str) -> None:
        """Handle selection change."""
        if self._on_change:
            self._on_change(value)

    def set_value(self, value: str) -> None:
        """Set the selected value."""
        self._var.set(value)
        self._dropdown.set(value)

    def get_value(self) -> str:
        """Get the current value."""
        return self._var.get()


class IconLabel(ctk.CTkFrame):
    """
    Label with an icon prefix.

    Used for status indicators and labeled information.
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        icon: str,
        text: str,
        icon_color: Optional[str] = None,
        text_color: Optional[str] = None,
        font_size: int = 12,
    ):
        super().__init__(parent, fg_color="transparent")

        self._icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=ctk.CTkFont(size=font_size),
            text_color=icon_color or ThemeColors.LABEL,
        )
        self._icon_label.pack(side="left")

        self._text_label = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=font_size),
            text_color=text_color or ThemeColors.LABEL,
        )
        self._text_label.pack(side="left", padx=(4, 0))

    def set_text(self, text: str) -> None:
        """Update the text."""
        self._text_label.configure(text=text)

    def set_colors(self, icon_color: str = None, text_color: str = None) -> None:
        """Update the colors."""
        if icon_color:
            self._icon_label.configure(text_color=icon_color)
        if text_color:
            self._text_label.configure(text_color=text_color)


class StatusBadge(ctk.CTkFrame):
    """
    Status indicator badge with icon and label.

    Shows valid/invalid or success/error states.
    """

    ICONS = {
        "valid": "\u2713",
        "invalid": "\u2717",
        "pending": "\u25CB",
        "processing": "\u25CF",
    }

    def __init__(
        self,
        parent: ctk.CTkFrame,
        label: str,
        is_valid: bool = False,
    ):
        super().__init__(parent, fg_color="transparent")
        self._label_text = label

        self._icon_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            width=16,
        )
        self._icon_label.pack(side="left")

        self._text_label = ctk.CTkLabel(
            self,
            text=label,
            font=ctk.CTkFont(size=12),
            text_color=ThemeColors.LABEL,
        )
        self._text_label.pack(side="left", padx=(4, 0))

        self.set_valid(is_valid)

    def set_valid(self, is_valid: bool) -> None:
        """Update the validity state."""
        if is_valid:
            self._icon_label.configure(
                text=self.ICONS["valid"],
                text_color=ThemeColors.STATUS_GREEN,
            )
        else:
            self._icon_label.configure(
                text=self.ICONS["invalid"],
                text_color=ThemeColors.STATUS_RED,
            )

    def set_status(self, status: str) -> None:
        """Set status to: valid, invalid, pending, or processing."""
        icon = self.ICONS.get(status, self.ICONS["pending"])
        if status == "valid":
            color = ThemeColors.STATUS_GREEN
        elif status == "invalid":
            color = ThemeColors.STATUS_RED
        elif status == "processing":
            color = ThemeColors.STATUS_BLUE
        else:
            color = ThemeColors.SUBTITLE

        self._icon_label.configure(text=icon, text_color=color)


class ActionButton(ctk.CTkButton):
    """
    Styled action button with consistent sizing.

    Primary buttons have bold text, secondary buttons have normal weight.
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        text: str,
        command: Optional[Callable[[], None]] = None,
        width: int = 160,
        height: int = 36,
        primary: bool = True,
        fg_color: Optional[str] = None,
        hover_color: Optional[str] = None,
    ):
        font_weight = "bold" if primary else "normal"
        font_size = 14 if primary else 13

        super().__init__(
            parent,
            text=text,
            font=ctk.CTkFont(size=font_size, weight=font_weight),
            width=width,
            height=height,
            command=command,
            fg_color=fg_color,
            hover_color=hover_color,
        )


class SectionTitle(ctk.CTkLabel):
    """
    Section title label within cards/panels.

    Used for labeling groups of related content.
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        text: str,
        font_size: int = 14,
    ):
        super().__init__(
            parent,
            text=text,
            font=ctk.CTkFont(size=font_size, weight="bold"),
            text_color=ThemeColors.LABEL,
        )


class StatusLabel(ctk.CTkLabel):
    """
    Status message label with color support.

    Used for showing operation status, errors, or success messages.
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        text: str = "",
        status: str = "info",
    ):
        color = self._get_color(status)
        super().__init__(
            parent,
            text=text,
            font=ctk.CTkFont(size=12),
            text_color=color,
        )

    def _get_color(self, status: str) -> str:
        """Get color for status type."""
        if status == "success":
            return ThemeColors.STATUS_GREEN
        elif status == "error":
            return ThemeColors.STATUS_RED
        elif status == "info":
            return ThemeColors.STATUS_BLUE
        return ThemeColors.SUBTITLE

    def set_status(self, text: str, status: str = "info") -> None:
        """Update the status message and color."""
        self.configure(text=text, text_color=self._get_color(status))

    def set_success(self, text: str) -> None:
        """Set a success message."""
        self.set_status(text, "success")

    def set_error(self, text: str) -> None:
        """Set an error message."""
        self.set_status(text, "error")

    def set_info(self, text: str) -> None:
        """Set an info message."""
        self.set_status(text, "info")

    def clear(self) -> None:
        """Clear the status message."""
        self.configure(text="")
