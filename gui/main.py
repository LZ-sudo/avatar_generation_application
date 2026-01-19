"""
Avatar Generator Application

Main entry point for the Flet-based GUI application.

Usage:
    python -m gui.main
    # or
    flet run gui/main.py
"""

import flet as ft

from .app_state import AppState, WizardStep
from .components.wizard_nav import WizardNav
from .steps.step_image_input import StepImageInput
from .steps.step_measurements import StepMeasurements
from .steps.step_configure import StepConfigure
from .steps.step_generate import StepGenerate
from .backend_interface import get_backend


class AvatarGeneratorApp:
    """
    Main application class for the Avatar Generator.

    Manages the wizard flow and coordinates between steps.
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.app_state = AppState()
        self.backend = get_backend(use_mock=True)

        self._setup_page()
        self._create_steps()
        self._build_ui()
        self._setup_steps()

        self.app_state.set_on_state_change(self._on_state_change)

    def _setup_page(self) -> None:
        """Configure page settings."""
        self.page.title = "Avatar Generator"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.window.width = 1100
        self.page.window.height = 800
        self.page.window.min_width = 800
        self.page.window.min_height = 600

    def _create_steps(self) -> None:
        """Create step views."""
        self.steps = {
            WizardStep.IMAGE_INPUT: StepImageInput(self.app_state),
            WizardStep.MEASUREMENTS: StepMeasurements(self.app_state, self.backend),
            WizardStep.CONFIGURE: StepConfigure(self.app_state),
            WizardStep.GENERATE: StepGenerate(self.app_state, self.backend),
        }

    def _setup_steps(self) -> None:
        """Set up steps that require page reference."""
        self.steps[WizardStep.IMAGE_INPUT].setup(self.page)
        self.steps[WizardStep.CONFIGURE].setup(self.page)

    def _build_ui(self) -> None:
        """Build the main UI structure."""
        self.wizard_nav = WizardNav(
            app_state=self.app_state,
            on_step_click=self._on_step_click,
        )

        self._step_container = ft.Container(
            content=self.steps[WizardStep.IMAGE_INPUT],
            expand=True,
        )

        self._back_button = ft.Button(
            "Back",
            icon=ft.Icons.ARROW_BACK,
            on_click=self._go_back,
            disabled=True,
        )

        self._next_button = ft.Button(
            "Next",
            icon=ft.Icons.ARROW_FORWARD,
            on_click=self._go_next,
            disabled=True,
        )

        navigation_buttons = ft.Container(
            content=ft.Row(
                controls=[
                    self._back_button,
                    ft.Container(expand=True),
                    self._next_button,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.Padding.symmetric(horizontal=30, vertical=15),
            bgcolor=ft.Colors.GREY_100,
        )

        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.PERSON, size=32, color=ft.Colors.BLUE_600),
                    ft.Text(
                        "Avatar Generator",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_800,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=ft.Padding.symmetric(vertical=15),
            bgcolor=ft.Colors.BLUE_50,
        )

        self.page.add(
            ft.Column(
                controls=[
                    header,
                    self.wizard_nav,
                    ft.Divider(height=1),
                    self._step_container,
                    ft.Divider(height=1),
                    navigation_buttons,
                ],
                expand=True,
                spacing=0,
            )
        )

        self._update_navigation_buttons()

    def _on_state_change(self) -> None:
        """Handle state changes."""
        self._update_navigation_buttons()
        self.wizard_nav.update_indicators()

    def _update_navigation_buttons(self) -> None:
        """Update navigation button states."""
        self._back_button.disabled = not self.app_state.can_go_back()
        self._next_button.disabled = not self.app_state.can_go_next()

        if self.app_state.current_step == WizardStep.CONFIGURE:
            self._next_button.text = "Generate"
            self._next_button.icon = ft.Icons.PLAY_ARROW
        elif self.app_state.current_step == WizardStep.GENERATE:
            self._next_button.visible = False
        else:
            self._next_button.text = "Next"
            self._next_button.icon = ft.Icons.ARROW_FORWARD
            self._next_button.visible = True

        self._back_button.update()
        self._next_button.update()

    def _show_step(self, step: WizardStep) -> None:
        """Display the specified step."""
        self._step_container.content = self.steps[step]
        self._step_container.update()

        if step == WizardStep.MEASUREMENTS:
            self.steps[step].on_enter()
        elif step == WizardStep.GENERATE:
            self.steps[step].on_enter()

    def _go_next(self, e) -> None:
        """Navigate to the next step."""
        if self.app_state.go_next():
            self._show_step(self.app_state.current_step)

    def _go_back(self, e) -> None:
        """Navigate to the previous step."""
        if self.app_state.go_back():
            self._show_step(self.app_state.current_step)

    def _on_step_click(self, step: WizardStep) -> None:
        """Handle direct step navigation."""
        if self.app_state.go_to_step(step):
            self._show_step(step)


def main(page: ft.Page):
    """Main entry point for Flet."""
    AvatarGeneratorApp(page)


if __name__ == "__main__":
    ft.run(main)
