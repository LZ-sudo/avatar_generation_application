"""
Centralized state management for the Avatar Generator application.

This module holds all shared state across wizard steps, including:
- Selected images
- Extracted measurements
- Configuration options
- Generation results

Note: This module is UI-framework agnostic and works with any GUI toolkit.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Callable
from enum import Enum, auto


class WizardStep(Enum):
    """Enum representing the wizard steps."""
    IMAGE_INPUT = 0
    MEASUREMENTS = 1
    CONFIGURE = 2
    GENERATE = 3


class RigType(Enum):
    """Available rig types for avatar generation."""
    DEFAULT = "default"
    DEFAULT_NO_TOES = "default_no_toes"
    GAME_ENGINE = "game_engine"


class HairStyle(Enum):
    """Available hair styles for avatar generation."""
    NONE = "none"
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    CUSTOM = "custom"


@dataclass
class CameraCalibrationState:
    """State for Camera Calibration feature."""
    image_directory: Optional[Path] = None
    checkerboard_cols: int = 8  # Inner corners
    checkerboard_rows: int = 6  # Inner corners
    square_size_mm: float = 40.0

    is_calibrating: bool = False
    progress_message: str = ""

    # Results from current calibration run
    calibration_success: Optional[bool] = None
    reprojection_error: Optional[float] = None
    num_successful_images: int = 0
    num_failed_images: int = 0
    error_message: Optional[str] = None

    # Existing calibration status (loaded on startup)
    existing_calibration_path: Optional[Path] = None
    existing_reprojection_error: Optional[float] = None

    def get_output_path(self) -> Path:
        """Get the calibration output path (absolute path)."""
        project_root = Path(__file__).parent.parent
        return project_root / "measurements_extraction_module" / "camera_calibration_settings" / "calibration.json"

    def load_existing_calibration(self) -> None:
        """Check if a calibration file exists and load its metadata."""
        import json
        output_path = self.get_output_path()
        if output_path.exists():
            with open(output_path) as f:
                data = json.load(f)
            if data.get("success"):
                self.existing_calibration_path = output_path
                self.existing_reprojection_error = data.get("reprojection_error")

    def reset_results(self) -> None:
        """Reset calibration results for a new run."""
        self.calibration_success = None
        self.reprojection_error = None
        self.num_successful_images = 0
        self.num_failed_images = 0
        self.error_message = None


@dataclass
class ImageInputState:
    """State for Step 1: Image Input."""
    front_image_path: Optional[Path] = None
    side_image_path: Optional[Path] = None

    def is_complete(self) -> bool:
        """Check if both images have been selected."""
        return self.front_image_path is not None and self.side_image_path is not None


@dataclass
class MeasurementsState:
    """State for Step 2: Measurements."""
    height_cm: Optional[float] = None
    shoulder_width_cm: Optional[float] = None
    chest_circumference_cm: Optional[float] = None
    waist_circumference_cm: Optional[float] = None
    hip_circumference_cm: Optional[float] = None
    arm_length_cm: Optional[float] = None
    leg_length_cm: Optional[float] = None
    head_circumference_cm: Optional[float] = None

    is_extracted: bool = False
    is_manually_edited: bool = False

    def is_complete(self) -> bool:
        """Check if measurements are available."""
        return self.is_extracted or self.is_manually_edited

    def to_dict(self) -> dict:
        """Convert measurements to dictionary format."""
        return {
            "height_cm": self.height_cm,
            "shoulder_width_cm": self.shoulder_width_cm,
            "chest_circumference_cm": self.chest_circumference_cm,
            "waist_circumference_cm": self.waist_circumference_cm,
            "hip_circumference_cm": self.hip_circumference_cm,
            "arm_length_cm": self.arm_length_cm,
            "leg_length_cm": self.leg_length_cm,
            "head_circumference_cm": self.head_circumference_cm,
        }


@dataclass
class ConfigureState:
    """State for Step 3: Configuration."""
    rig_type: RigType = RigType.DEFAULT
    hair_style: HairStyle = HairStyle.NONE
    hair_color: str = "#3d2314"
    output_directory: Optional[Path] = None
    output_filename: str = "avatar"
    export_fbx: bool = True
    export_obj: bool = False

    def is_complete(self) -> bool:
        """Check if configuration is valid."""
        return self.output_directory is not None


@dataclass
class GenerateState:
    """State for Step 4: Generation."""
    is_generating: bool = False
    progress: float = 0.0
    status_message: str = ""
    output_fbx_path: Optional[Path] = None
    output_obj_path: Optional[Path] = None
    preview_images: list[Path] = field(default_factory=list)
    error_message: Optional[str] = None

    def is_complete(self) -> bool:
        """Check if generation completed successfully."""
        return self.output_fbx_path is not None and self.error_message is None


@dataclass
class AppState:
    """
    Main application state container.

    Holds all state for the wizard steps and provides methods
    for state management and navigation.
    """
    current_step: WizardStep = WizardStep.IMAGE_INPUT

    # Camera calibration state (separate feature)
    camera_calibration: CameraCalibrationState = field(default_factory=CameraCalibrationState)

    # Avatar generation wizard states
    image_input: ImageInputState = field(default_factory=ImageInputState)
    measurements: MeasurementsState = field(default_factory=MeasurementsState)
    configure: ConfigureState = field(default_factory=ConfigureState)
    generate: GenerateState = field(default_factory=GenerateState)

    _on_state_change: Optional[Callable[[], None]] = field(default=None, repr=False)

    def set_on_state_change(self, callback: Callable[[], None]) -> None:
        """Set callback to be called when state changes."""
        self._on_state_change = callback

    def notify_change(self) -> None:
        """Notify listeners of state change."""
        if self._on_state_change:
            self._on_state_change()

    def can_go_next(self) -> bool:
        """Check if we can proceed to the next step."""
        if self.current_step == WizardStep.IMAGE_INPUT:
            return self.image_input.is_complete()
        elif self.current_step == WizardStep.MEASUREMENTS:
            return self.measurements.is_complete()
        elif self.current_step == WizardStep.CONFIGURE:
            return self.configure.is_complete()
        elif self.current_step == WizardStep.GENERATE:
            return False  # Last step
        return False

    def can_go_back(self) -> bool:
        """Check if we can go back to the previous step."""
        return self.current_step != WizardStep.IMAGE_INPUT

    def go_next(self) -> bool:
        """Advance to the next step if possible."""
        if self.can_go_next():
            next_value = self.current_step.value + 1
            if next_value <= WizardStep.GENERATE.value:
                self.current_step = WizardStep(next_value)
                self.notify_change()
                return True
        return False

    def go_back(self) -> bool:
        """Go back to the previous step if possible."""
        if self.can_go_back():
            prev_value = self.current_step.value - 1
            if prev_value >= WizardStep.IMAGE_INPUT.value:
                self.current_step = WizardStep(prev_value)
                self.notify_change()
                return True
        return False

    def go_to_step(self, step: WizardStep) -> bool:
        """Navigate directly to a specific step."""
        if step.value <= self.current_step.value:
            self.current_step = step
            self.notify_change()
            return True
        return False

    def reset(self) -> None:
        """Reset all state to initial values."""
        self.current_step = WizardStep.IMAGE_INPUT
        self.image_input = ImageInputState()
        self.measurements = MeasurementsState()
        self.configure = ConfigureState()
        self.generate = GenerateState()
        self.notify_change()
