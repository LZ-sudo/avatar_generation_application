"""
Avatar Generator Application Launcher

This is the entry point for running the application.

Usage:
    flet run app.py
    # or
    python app.py
"""

import flet as ft

from gui.app_state import AppState
from gui.backend_interface import get_backend
from gui.features.camera_calibration import CameraCalibrationView
from gui.features.avatar_generation import AvatarGenerationView


class AvatarGeneratorApp:
    """
    Main application class for the Avatar Generator.

    Provides tab-based navigation between features:
    - Camera Calibration
    - Avatar Generation
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.app_state = AppState()
        self.backend = get_backend(use_mock=True)

        self._setup_page()
        self._create_features()
        self._build_ui()
        self._setup_features()

    def _setup_page(self) -> None:
        """Configure page settings."""
        self.page.title = "Avatar Generator"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.window.width = 1100
        self.page.window.height = 800
        self.page.window.min_width = 800
        self.page.window.min_height = 600

    def _create_features(self) -> None:
        """Create feature views."""
        self._camera_calibration = CameraCalibrationView(
            self.app_state,
            self.backend,
        )
        self._avatar_generation = AvatarGenerationView(
            self.app_state,
            self.backend,
        )

    def _setup_features(self) -> None:
        """Set up features that require page reference."""
        self._camera_calibration.setup(self.page)
        self._avatar_generation.setup(self.page)

    def _build_ui(self) -> None:
        """Build the main UI structure."""
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
            padding=ft.Padding(top=15, bottom=15),
            bgcolor=ft.Colors.BLUE_50,
        )

        # Flet 0.80+ Tabs API: TabBar + TabBarView structure
        self._tabs = ft.Tabs(
            selected_index=1,  # Start on Avatar Generation
            length=2,
            expand=True,
            on_change=self._on_tab_change,
            content=ft.Column(
                expand=True,
                spacing=0,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Camera Calibration", icon=ft.Icons.CAMERA_ALT),
                            ft.Tab(label="Avatar Generation", icon=ft.Icons.PERSON_ADD),
                        ],
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            self._camera_calibration,
                            self._avatar_generation,
                        ],
                    ),
                ],
            ),
        )

        self.page.add(
            ft.Column(
                controls=[
                    header,
                    self._tabs,
                ],
                expand=True,
                spacing=0,
            )
        )

    def _on_tab_change(self, e) -> None:
        """Handle tab selection change."""
        pass  # TabBarView handles content switching automatically


def main(page: ft.Page):
    """Main entry point for Flet."""
    AvatarGeneratorApp(page)


if __name__ == "__main__":
    ft.run(main)
