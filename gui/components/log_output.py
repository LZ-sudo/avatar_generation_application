"""
Log output component.

Displays streaming process output in a scrollable text area.
"""

import queue

import customtkinter as ctk


class LogOutput(ctk.CTkFrame):
    """
    Log output component for displaying streaming process output.

    Displays:
    - Scrollable text area with process output lines
    - Status label showing running / complete / error state

    Lines fed from background threads via feed_line() are batched and
    inserted every _POLL_INTERVAL_MS milliseconds to avoid flooding the
    Tkinter event loop with individual callbacks.
    """

    COLORS = {
        "text_normal": "#374151",
        "text_error": "#dc2626",
        "text_complete": "#16a34a",
        "text_secondary": "#6b7280",
    }

    _POLL_INTERVAL_MS = 50

    def __init__(
        self,
        parent: ctk.CTkFrame,
        width: int = 400,
        height: int = 75,
    ):
        super().__init__(parent, fg_color="transparent")
        self._width = width
        self._height = height
        self._queue: queue.Queue = queue.Queue()
        self._build()
        self._poll_queue()

    def _build(self) -> None:
        """Build the log output component."""
        self._textbox = ctk.CTkTextbox(
            self,
            width=self._width,
            height=self._height,
            font=ctk.CTkFont(family="Courier New", size=11),
            state="disabled",
            wrap="word",
        )
        self._textbox.pack(pady=(0, 6))

        self._status_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["text_secondary"],
        )
        self._status_label.pack()

    def _poll_queue(self) -> None:
        """Drain the line queue and batch-insert into the textbox."""
        lines = []
        try:
            while True:
                lines.append(self._queue.get_nowait())
        except queue.Empty:
            pass

        if lines:
            self._textbox.configure(state="normal")
            self._textbox.insert("end", "\n".join(lines) + "\n")
            self._textbox.configure(state="disabled")
            self._textbox.see("end")

        self.after(self._POLL_INTERVAL_MS, self._poll_queue)

    def feed_line(self, text: str) -> None:
        """
        Thread-safe: queue a line for display.

        Safe to call from background threads. The line will be inserted
        into the textbox on the next poll cycle.
        """
        self._queue.put(text)

    def append_line(self, text: str) -> None:
        """
        Append a line directly to the textbox.

        Must be called from the main thread. Use feed_line() from
        background threads instead.
        """
        self._textbox.configure(state="normal")
        self._textbox.insert("end", text + "\n")
        self._textbox.configure(state="disabled")
        self._textbox.see("end")

    def set_complete(self, message: str = "Complete!") -> None:
        """Display completion state in the status label."""
        self._status_label.configure(
            text=message,
            text_color=self.COLORS["text_complete"],
        )

    def set_error(self, error_message: str) -> None:
        """Append the error to the log and show it in the status label."""
        self.append_line(f"ERROR: {error_message}")
        self._status_label.configure(
            text=error_message,
            text_color=self.COLORS["text_error"],
        )

    def reset(self) -> None:
        """Clear the log, drain any pending queued lines, and reset the status label."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        self._textbox.configure(state="disabled")
        self._status_label.configure(
            text="",
            text_color=self.COLORS["text_secondary"],
        )
