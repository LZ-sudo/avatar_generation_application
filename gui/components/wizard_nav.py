"""
Wizard navigation component.

Displays the step indicator bar and handles navigation between steps.
"""

import flet as ft
from typing import Callable

from ..app_state import AppState, WizardStep


class WizardNav(ft.Container):
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
        WizardStep.CONFIGURE: "Configure",
        WizardStep.GENERATE: "Generate",
    }

    def __init__(
        self,
        app_state: AppState,
        on_step_click: Callable[[WizardStep], None] = None,
    ):
        super().__init__()
        self.app_state = app_state
        self.on_step_click = on_step_click
        self._build()

    def _build(self) -> None:
        """Build the navigation component."""
        self.content = ft.Row(
            controls=self._create_step_indicators(),
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=0,
        )
        self.padding = ft.Padding.symmetric(vertical=20, horizontal=10)

    def _create_step_indicators(self) -> list[ft.Control]:
        """Create step indicator controls."""
        controls = []
        steps = list(WizardStep)

        for i, step in enumerate(steps):
            is_current = step == self.app_state.current_step
            is_completed = step.value < self.app_state.current_step.value
            is_clickable = step.value <= self.app_state.current_step.value

            indicator = self._create_step_indicator(
                step=step,
                number=i + 1,
                is_current=is_current,
                is_completed=is_completed,
                is_clickable=is_clickable,
            )
            controls.append(indicator)

            if i < len(steps) - 1:
                connector = self._create_connector(is_completed)
                controls.append(connector)

        return controls

    def _create_step_indicator(
        self,
        step: WizardStep,
        number: int,
        is_current: bool,
        is_completed: bool,
        is_clickable: bool,
    ) -> ft.Control:
        """Create a single step indicator."""
        if is_completed:
            icon_content = ft.Icon(
                ft.Icons.CHECK,
                color=ft.Colors.WHITE,
                size=20,
            )
            bg_color = ft.Colors.GREEN_600
        elif is_current:
            icon_content = ft.Text(
                str(number),
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.BOLD,
                size=14,
            )
            bg_color = ft.Colors.BLUE_600
        else:
            icon_content = ft.Text(
                str(number),
                color=ft.Colors.GREY_600,
                size=14,
            )
            bg_color = ft.Colors.GREY_300

        circle = ft.Container(
            content=icon_content,
            width=36,
            height=36,
            border_radius=18,
            bgcolor=bg_color,
            alignment=ft.Alignment(0, 0),
        )

        label = ft.Text(
            self.STEP_LABELS[step],
            size=12,
            color=ft.Colors.BLUE_600 if is_current else ft.Colors.GREY_600,
            weight=ft.FontWeight.BOLD if is_current else ft.FontWeight.NORMAL,
            text_align=ft.TextAlign.CENTER,
        )

        indicator = ft.Container(
            content=ft.Column(
                controls=[circle, label],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            on_click=lambda e, s=step: self._handle_step_click(s) if is_clickable else None,
            ink=is_clickable,
            padding=10,
        )

        return indicator

    def _create_connector(self, is_completed: bool) -> ft.Control:
        """Create a connector line between step indicators."""
        return ft.Container(
            content=ft.Divider(
                color=ft.Colors.GREEN_600 if is_completed else ft.Colors.GREY_300,
                thickness=2,
            ),
            width=60,
            padding=ft.Padding.only(bottom=30),
        )

    def _handle_step_click(self, step: WizardStep) -> None:
        """Handle click on a step indicator."""
        if self.on_step_click:
            self.on_step_click(step)

    def update_indicators(self) -> None:
        """Refresh the step indicators based on current state."""
        self.content.controls = self._create_step_indicators()
        self.update()
