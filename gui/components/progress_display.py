"""
Progress display component.

Shows generation progress with status messages.
"""

import flet as ft
from typing import Optional


class ProgressDisplay(ft.Container):
    """
    Progress display component for showing generation status.

    Displays:
    - Progress bar with percentage
    - Status message
    - Optional error state
    """

    def __init__(
        self,
        width: int = 400,
    ):
        super().__init__()
        self._width = width
        self._progress = 0.0
        self._status = ""
        self._is_error = False
        self._build()

    def _build(self) -> None:
        """Build the progress display component."""
        self._progress_bar = ft.ProgressBar(
            value=0,
            width=self._width,
            bar_height=8,
            color=ft.Colors.BLUE_600,
            bgcolor=ft.Colors.GREY_300,
        )

        self._percentage_text = ft.Text(
            "0%",
            size=14,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.GREY_700,
        )

        self._status_text = ft.Text(
            "",
            size=12,
            color=ft.Colors.GREY_600,
            text_align=ft.TextAlign.CENTER,
        )

        self._progress_ring = ft.ProgressRing(
            width=20,
            height=20,
            stroke_width=2,
            visible=False,
        )

        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        self._progress_ring,
                        self._status_text,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                ft.Row(
                    controls=[
                        self._progress_bar,
                        self._percentage_text,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        self.padding = 20
        self.width = self._width + 80

    def set_progress(self, progress: float, status: str = "") -> None:
        """
        Update the progress display.

        Args:
            progress: Progress value between 0.0 and 1.0
            status: Status message to display
        """
        self._progress = max(0.0, min(1.0, progress))
        self._status = status
        self._is_error = False

        self._progress_bar.value = self._progress
        self._progress_bar.color = ft.Colors.BLUE_600
        self._percentage_text.value = f"{int(self._progress * 100)}%"
        self._percentage_text.color = ft.Colors.GREY_700
        self._status_text.value = status
        self._status_text.color = ft.Colors.GREY_600
        self._progress_ring.visible = self._progress < 1.0 and self._progress > 0

        self.update()

    def set_error(self, error_message: str) -> None:
        """
        Display an error state.

        Args:
            error_message: Error message to display
        """
        self._is_error = True
        self._progress_bar.color = ft.Colors.RED_600
        self._status_text.value = error_message
        self._status_text.color = ft.Colors.RED_600
        self._percentage_text.color = ft.Colors.RED_600
        self._progress_ring.visible = False

        self.update()

    def set_complete(self, message: str = "Complete!") -> None:
        """
        Display completion state.

        Args:
            message: Completion message to display
        """
        self._progress = 1.0
        self._is_error = False

        self._progress_bar.value = 1.0
        self._progress_bar.color = ft.Colors.GREEN_600
        self._percentage_text.value = "100%"
        self._percentage_text.color = ft.Colors.GREEN_600
        self._status_text.value = message
        self._status_text.color = ft.Colors.GREEN_600
        self._progress_ring.visible = False

        self.update()

    def reset(self) -> None:
        """Reset the progress display to initial state."""
        self.set_progress(0.0, "")
        self._progress_ring.visible = False
        self.update()

    @property
    def progress(self) -> float:
        """Get current progress value."""
        return self._progress

    @property
    def is_error(self) -> bool:
        """Check if currently in error state."""
        return self._is_error
