"""
Wizard navigation component.

Displays the step indicator bar and handles navigation between steps.
"""

import customtkinter as ctk
from typing import Callable, Optional

from ..app_state import AppState, WizardStep


class WizardNav(ctk.CTkFrame):
    """
    Navigation component showing wizard progress and step indicators.

    Displays a horizontal bar with step indicators that show:
    - Completed steps (checkmark)
    - Current step (highlighted)
    - Upcoming steps (numbered)
    """

    STEP_LABELS = {
        WizardStep.IMAGE_INPUT: "Image Input",
        WizardStep.MEASUREMENTS: "Measurements",
        WizardStep.ACCURACY_REVIEW: "Accuracy",
        WizardStep.CONFIGURE: "Configure",
        WizardStep.OUTPUT_SETTINGS: "Output",
        WizardStep.GENERATE: "Generate",
    }

    COLORS = {
        "completed_bg": "#16a34a",
        "current_bg": "#2563eb",
        "upcoming_bg": "#d1d5db",
        "completed_fg": "#ffffff",
        "current_fg": "#ffffff",
        "upcoming_fg": "#4b5563",
        "current_label": "#2563eb",
        "other_label": "#6b7280",
    }

    def __init__(
        self,
        parent: ctk.CTkFrame,
        app_state: AppState,
        on_step_click: Optional[Callable[[WizardStep], None]] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self.on_step_click = on_step_click
        self._indicator_widgets: list = []
        self._build()

    def _build(self) -> None:
        """Build the navigation component."""
        self._create_step_indicators()

    def _create_step_indicators(self) -> None:
        """Create step indicator controls."""
        for widget in self._indicator_widgets:
            widget.destroy()
        self._indicator_widgets.clear()

        for child in self.winfo_children():
            child.destroy()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(pady=20, padx=10)

        steps = list(WizardStep)

        for i, step in enumerate(steps):
            is_current = step == self.app_state.current_step
            is_completed = step.value < self.app_state.current_step.value
            is_clickable = step.value <= self.app_state.current_step.value

            indicator = self._create_step_indicator(
                parent=container,
                step=step,
                number=i + 1,
                is_current=is_current,
                is_completed=is_completed,
                is_clickable=is_clickable,
            )
            indicator.pack(side="left", padx=15)
            self._indicator_widgets.append(indicator)

    def _create_step_indicator(
        self,
        parent: ctk.CTkFrame,
        step: WizardStep,
        number: int,
        is_current: bool,
        is_completed: bool,
        is_clickable: bool,
    ) -> ctk.CTkFrame:
        """Create a single step indicator."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")

        if is_completed:
            bg_color = self.COLORS["completed_bg"]
            text = "\u2713"
            text_color = self.COLORS["completed_fg"]
        elif is_current:
            bg_color = self.COLORS["current_bg"]
            text = str(number)
            text_color = self.COLORS["current_fg"]
        else:
            bg_color = self.COLORS["upcoming_bg"]
            text = str(number)
            text_color = self.COLORS["upcoming_fg"]

        circle = ctk.CTkLabel(
            frame,
            text=text,
            width=36,
            height=36,
            corner_radius=18,
            fg_color=bg_color,
            text_color=text_color,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        circle.pack()

        label_color = self.COLORS["current_label"] if is_current else self.COLORS["other_label"]
        label_weight = "bold" if is_current else "normal"

        label = ctk.CTkLabel(
            frame,
            text=self.STEP_LABELS[step],
            font=ctk.CTkFont(size=12, weight=label_weight),
            text_color=label_color,
        )
        label.pack(pady=(8, 0))

        if is_clickable:
            circle.bind("<Button-1>", lambda e, s=step: self._handle_step_click(s))
            label.bind("<Button-1>", lambda e, s=step: self._handle_step_click(s))
            circle.configure(cursor="hand2")
            label.configure(cursor="hand2")

        return frame

    def _handle_step_click(self, step: WizardStep) -> None:
        """Handle click on a step indicator."""
        if self.on_step_click:
            self.on_step_click(step)

    def update_indicators(self) -> None:
        """Refresh the step indicators based on current state."""
        self._create_step_indicators()
