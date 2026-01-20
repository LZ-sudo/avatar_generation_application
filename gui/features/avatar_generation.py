"""
Avatar Generation Feature View

Wraps the existing wizard flow for avatar generation.
"""

import customtkinter as ctk

from ..app_state import AppState, WizardStep
from ..backend_interface import BackendInterface
from ..components.wizard_nav import WizardNav
from ..steps.step_image_input import StepImageInput
from ..steps.step_measurements import StepMeasurements
from ..steps.step_configure import StepConfigure
from ..steps.step_generate import StepGenerate


class AvatarGenerationView(ctk.CTkFrame):
    """
    Avatar generation view component.

    Contains the wizard flow for generating avatars from photographs.
    """

    COLORS = {
        "nav_bg": "#f3f4f6",
        "divider": "#e5e7eb",
    }

    def __init__(self, parent: ctk.CTkFrame, app_state: AppState, backend: BackendInterface):
        super().__init__(parent, fg_color="transparent")
        self.app_state = app_state
        self.backend = backend

        self._create_steps()
        self._build()

        self.app_state.set_on_state_change(self._on_state_change)

    def _create_steps(self) -> None:
        """Create step views."""
        self._step_container = ctk.CTkFrame(self, fg_color="transparent")

        self.steps = {
            WizardStep.IMAGE_INPUT: StepImageInput(
                self._step_container,
                self.app_state,
                self.backend,
                on_navigate_next=self._go_next,
            ),
            WizardStep.MEASUREMENTS: StepMeasurements(self._step_container, self.app_state),
            WizardStep.CONFIGURE: StepConfigure(self._step_container, self.app_state),
            WizardStep.GENERATE: StepGenerate(self._step_container, self.app_state, self.backend),
        }

    def _build(self) -> None:
        """Build the view content."""
        self.wizard_nav = WizardNav(
            self,
            app_state=self.app_state,
            on_step_click=self._on_step_click,
        )
        self.wizard_nav.pack(fill="x")

        divider1 = ctk.CTkFrame(self, height=1, fg_color=self.COLORS["divider"])
        divider1.pack(fill="x")

        self._step_container.pack(expand=True, fill="both")

        self._current_step_widget = self.steps[WizardStep.IMAGE_INPUT]
        self._current_step_widget.pack(expand=True, fill="both")

        divider2 = ctk.CTkFrame(self, height=1, fg_color=self.COLORS["divider"])
        divider2.pack(fill="x")

        nav_frame = ctk.CTkFrame(self, fg_color=self.COLORS["nav_bg"])
        nav_frame.pack(fill="x")

        nav_content = ctk.CTkFrame(nav_frame, fg_color="transparent")
        nav_content.pack(fill="x", padx=30, pady=15)

        self._back_button = ctk.CTkButton(
            nav_content,
            text="Back",
            command=self._go_back,
            state="disabled",
        )
        self._back_button.pack(side="left")

        self._next_button = ctk.CTkButton(
            nav_content,
            text="Next",
            command=self._go_next,
            state="disabled",
        )
        self._next_button.pack(side="right")

        self._update_navigation_buttons()

    def _on_state_change(self) -> None:
        """Handle state changes."""
        self._update_navigation_buttons()
        self.wizard_nav.update_indicators()

    def _update_navigation_buttons(self) -> None:
        """Update navigation button states."""
        back_state = "normal" if self.app_state.can_go_back() else "disabled"
        next_state = "normal" if self.app_state.can_go_next() else "disabled"

        self._back_button.configure(state=back_state)

        if self.app_state.current_step == WizardStep.CONFIGURE:
            self._next_button.configure(text="Generate", state=next_state)
            self._next_button.pack(side="right")
        elif self.app_state.current_step == WizardStep.GENERATE:
            self._next_button.pack_forget()
        else:
            self._next_button.configure(text="Next", state=next_state)
            self._next_button.pack(side="right")

    def _show_step(self, step: WizardStep) -> None:
        """Display the specified step."""
        self._current_step_widget.pack_forget()

        self._current_step_widget = self.steps[step]
        self._current_step_widget.pack(expand=True, fill="both")

        if step == WizardStep.IMAGE_INPUT:
            self.steps[step].on_enter()
        elif step == WizardStep.MEASUREMENTS:
            self.steps[step].on_enter()
        elif step == WizardStep.GENERATE:
            self.steps[step].on_enter()

    def _go_next(self) -> None:
        """Navigate to the next step."""
        if self.app_state.go_next():
            self._show_step(self.app_state.current_step)

    def _go_back(self) -> None:
        """Navigate to the previous step."""
        if self.app_state.go_back():
            self._show_step(self.app_state.current_step)

    def _on_step_click(self, step: WizardStep) -> None:
        """Handle direct step navigation."""
        if self.app_state.go_to_step(step):
            self._show_step(step)
