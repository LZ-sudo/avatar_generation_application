"""
Avatar Generator Application

Main entry point for the CustomTkinter-based GUI application.

Usage:
    python -m gui.main
"""

import customtkinter as ctk

from .app_state import AppState
from .backend_interface import get_backend
from .features.camera_calibration import CameraCalibrationView
from .features.avatar_generation import AvatarGenerationView


class AvatarGeneratorApp(ctk.CTk):
    """
    Main application class for the Avatar Generator.

    Provides tab-based navigation between features:
    - Camera Calibration
    - Avatar Generation
    """

    COLORS = {
        "header_bg": "#eff6ff",
        "header_icon": "#2563eb",
        "header_title": "#1e40af",
    }

    def __init__(self):
        super().__init__()

        self.app_state = AppState()
        self.backend = get_backend(use_mock=False)

        self._setup_window()
        self._build_ui()

    def _setup_window(self) -> None:
        """Configure window settings."""
        self.title("Avatar Generator")
        self.geometry("1200x900")
        self.resizable(False, False)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

    def _build_ui(self) -> None:
        """Build the main UI structure."""
        header = ctk.CTkFrame(self, fg_color=self.COLORS["header_bg"])
        header.pack(fill="x")

        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(pady=15)

        title_label = ctk.CTkLabel(
            header_content,
            text="Avatar Generator",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.COLORS["header_title"],
        )
        title_label.pack()

        self._tabview = ctk.CTkTabview(self)
        self._tabview.pack(expand=True, fill="both", padx=0, pady=0)

        self._tabview.add("Camera Calibration")
        self._tabview.add("Avatar Generation")

        self._tabview.set("Avatar Generation")

        calibration_tab = self._tabview.tab("Camera Calibration")
        self._camera_calibration = CameraCalibrationView(
            calibration_tab,
            self.app_state,
            self.backend,
        )
        self._camera_calibration.pack(expand=True, fill="both")

        generation_tab = self._tabview.tab("Avatar Generation")
        self._avatar_generation = AvatarGenerationView(
            generation_tab,
            self.app_state,
            self.backend,
        )
        self._avatar_generation.pack(expand=True, fill="both")


def main():
    """Main entry point."""
    app = AvatarGeneratorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
