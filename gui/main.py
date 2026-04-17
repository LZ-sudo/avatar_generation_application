"""
Avatar Generator Application

Main entry point for the CustomTkinter-based GUI application.

Usage:
    python -m gui.main
"""

import customtkinter as ctk

try:
    import pywinstyles
    _PYWINSTYLES_AVAILABLE = True
except ImportError:
    _PYWINSTYLES_AVAILABLE = False

from .app_state import AppState
from .backend_interface import get_backend
from .features.camera_calibration import CameraCalibrationView
from .features.aruco_settings import ArucoSettingsView
from .features.avatar_generation import AvatarGenerationView
from .features.c3d_converter import C3dConverterView
from .features.animation_baker import AnimationBakerView


class AvatarGeneratorApp(ctk.CTk):
    """
    Main application class for the Avatar Generator.

    Provides tab-based navigation between features:
    - Camera Calibration
    - ArUco Settings
    - C3D Converter
    - Animation Baker
    - Avatar Generation
    """

    COLORS: dict = {}

    def __init__(self):
        super().__init__()

        self.app_state = AppState()
        self.backend = get_backend()

        self._setup_window()
        self._build_ui()
        self._fix_minimize_flicker()

    def _setup_window(self) -> None:
        """Configure window settings."""
        self.title("Avatar Generator")
        self.geometry("1000x770") # width by height
        self.resizable(False, False)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

    def _build_ui(self) -> None:
        """Build the main UI structure."""
        self._tabview = ctk.CTkTabview(self)
        self._tabview.pack(expand=True, fill="both", padx=0, pady=0)

        self._tabview.add("Camera Calibration")
        self._tabview.add("ArUco Settings")
        self._tabview.add("C3D Converter")
        self._tabview.add("Animation Baker")
        self._tabview.add("Avatar Generation")

        self._tabview.set("Avatar Generation")
        self._tabview.configure(command=self._on_tab_change)

        calibration_tab = self._tabview.tab("Camera Calibration")
        self._camera_calibration = CameraCalibrationView(
            calibration_tab,
            self.app_state,
            self.backend,
        )
        self._camera_calibration.pack(expand=True, fill="both")

        aruco_tab = self._tabview.tab("ArUco Settings")
        self._aruco_settings = ArucoSettingsView(
            aruco_tab,
            self.app_state,
        )
        self._aruco_settings.pack(expand=True, fill="both")

        c3d_tab = self._tabview.tab("C3D Converter")
        self._c3d_converter = C3dConverterView(
            c3d_tab,
            set_tabs_locked=self.set_tabs_locked,
        )
        self._c3d_converter.pack(expand=True, fill="both")

        animation_baker_tab = self._tabview.tab("Animation Baker")
        self._animation_baker = AnimationBakerView(
            animation_baker_tab,
            set_tabs_locked=self.set_tabs_locked,
        )
        self._animation_baker.pack(expand=True, fill="both")

        generation_tab = self._tabview.tab("Avatar Generation")
        self._avatar_generation = AvatarGenerationView(
            generation_tab,
            self.app_state,
            self.backend,
            set_tabs_locked=self.set_tabs_locked,
        )
        self._avatar_generation.pack(expand=True, fill="both")

    def _fix_minimize_flicker(self) -> None:
        """Apply pywinstyles opacity fix to prevent widget flickering on minimize/restore."""
        if not _PYWINSTYLES_AVAILABLE:
            return
        for widget in [
            self._tabview,
            self._camera_calibration,
            self._aruco_settings,
            self._c3d_converter,
            self._animation_baker,
            self._avatar_generation,
        ]:
            pywinstyles.set_opacity(widget, value=1.0)

    def set_tabs_locked(self, locked: bool) -> None:
        """Disable or enable tab switching during script execution."""
        state = "disabled" if locked else "normal"
        self._tabview._segmented_button.configure(state=state)

    def _on_tab_change(self) -> None:
        """Refresh the active wizard step when switching back to Avatar Generation."""
        if self._tabview.get() == "Avatar Generation":
            self._avatar_generation.on_tab_enter()


def main():
    """Main entry point."""
    app = AvatarGeneratorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
