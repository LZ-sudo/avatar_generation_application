"""
Progress display component.

Shows generation progress with status messages.
"""

import customtkinter as ctk


class ProgressDisplay(ctk.CTkFrame):
    """
    Progress display component for showing generation status.

    Displays:
    - Progress bar with percentage
    - Status message
    - Optional error state
    """

    COLORS = {
        "progress_normal": "#2563eb",
        "progress_error": "#dc2626",
        "progress_complete": "#16a34a",
        "bg": "#d1d5db",
        "text_normal": "#374151",
        "text_error": "#dc2626",
        "text_complete": "#16a34a",
        "text_secondary": "#6b7280",
    }

    def __init__(
        self,
        parent: ctk.CTkFrame,
        width: int = 400,
    ):
        super().__init__(parent, fg_color="transparent")
        self._width = width
        self._progress = 0.0
        self._status = ""
        self._is_error = False
        self._build()

    def _build(self) -> None:
        """Build the progress display component."""
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.pack(pady=(0, 10))

        self._status_label = ctk.CTkLabel(
            status_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["text_secondary"],
        )
        self._status_label.pack()

        progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        progress_frame.pack()

        self._progress_bar = ctk.CTkProgressBar(
            progress_frame,
            width=self._width,
            height=8,
            progress_color=self.COLORS["progress_normal"],
            fg_color=self.COLORS["bg"],
        )
        self._progress_bar.pack(side="left", padx=(0, 10))
        self._progress_bar.set(0)

        self._percentage_label = ctk.CTkLabel(
            progress_frame,
            text="0%",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.COLORS["text_normal"],
            width=50,
        )
        self._percentage_label.pack(side="left")

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

        self._progress_bar.set(self._progress)
        self._progress_bar.configure(progress_color=self.COLORS["progress_normal"])
        self._percentage_label.configure(
            text=f"{int(self._progress * 100)}%",
            text_color=self.COLORS["text_normal"],
        )
        self._status_label.configure(
            text=status,
            text_color=self.COLORS["text_secondary"],
        )

    def set_error(self, error_message: str) -> None:
        """
        Display an error state.

        Args:
            error_message: Error message to display
        """
        self._is_error = True
        self._progress_bar.configure(progress_color=self.COLORS["progress_error"])
        self._status_label.configure(
            text=error_message,
            text_color=self.COLORS["text_error"],
        )
        self._percentage_label.configure(text_color=self.COLORS["text_error"])

    def set_complete(self, message: str = "Complete!") -> None:
        """
        Display completion state.

        Args:
            message: Completion message to display
        """
        self._progress = 1.0
        self._is_error = False

        self._progress_bar.set(1.0)
        self._progress_bar.configure(progress_color=self.COLORS["progress_complete"])
        self._percentage_label.configure(
            text="100%",
            text_color=self.COLORS["text_complete"],
        )
        self._status_label.configure(
            text=message,
            text_color=self.COLORS["text_complete"],
        )

    def reset(self) -> None:
        """Reset the progress display to initial state."""
        self.set_progress(0.0, "")

    @property
    def progress(self) -> float:
        """Get current progress value."""
        return self._progress

    @property
    def is_error(self) -> bool:
        """Check if currently in error state."""
        return self._is_error
