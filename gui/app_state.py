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
    ACCURACY_REVIEW = 2
    CONFIGURE = 3
    OUTPUT_SETTINGS = 4
    GENERATE = 5


class RigType(Enum):
    """Available rig types for avatar generation."""
    DEFAULT = "default"
    DEFAULT_NO_TOES = "default_no_toes"
    GAME_ENGINE = "game_engine"


class HairStyle(Enum):
    """Available hair styles for avatar generation (legacy - will be replaced by hair assets)."""
    NONE = "none"
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    CUSTOM = "custom"


class InstrumentedArm(Enum):
    """Which arm has IMU sensors attached."""
    LEFT = "left"
    RIGHT = "right"


@dataclass
class MarkerPosition:
    """Position of a single ArUco marker."""
    x: float = 0.0
    y: float = 0.0


@dataclass
class ArucoSettingsState:
    """State for ArUco marker settings."""
    marker_size_cm: float = 16.4
    top_left: MarkerPosition = field(default_factory=lambda: MarkerPosition(0, 203.2))
    top_right: MarkerPosition = field(default_factory=lambda: MarkerPosition(83, 203.2))
    bottom_left: MarkerPosition = field(default_factory=lambda: MarkerPosition(0, 8.2))
    bottom_right: MarkerPosition = field(default_factory=lambda: MarkerPosition(83, 8.2))

    def get_config_dir(self) -> Path:
        """Get the user_configurations directory path."""
        project_root = Path(__file__).parent.parent
        return project_root / "user_configurations"

    def get_config_path(self) -> Path:
        """Get the marker_details.json path."""
        return self.get_config_dir() / "marker_details.json"

    def ensure_config_dir_exists(self) -> None:
        """Create the configuration directory if it doesn't exist."""
        self.get_config_dir().mkdir(parents=True, exist_ok=True)

    def load_from_file(self) -> bool:
        """Load settings from marker_details.json. Returns True if successful."""
        import json
        config_path = self.get_config_path()
        if not config_path.exists():
            return False
        try:
            with open(config_path) as f:
                data = json.load(f)
            self.marker_size_cm = data.get("marker_size_cm", self.marker_size_cm)
            positions = data.get("marker_positions_cm", {})
            if "top_left" in positions:
                self.top_left = MarkerPosition(
                    positions["top_left"].get("x", 0),
                    positions["top_left"].get("y", 0)
                )
            if "top_right" in positions:
                self.top_right = MarkerPosition(
                    positions["top_right"].get("x", 0),
                    positions["top_right"].get("y", 0)
                )
            if "bottom_left" in positions:
                self.bottom_left = MarkerPosition(
                    positions["bottom_left"].get("x", 0),
                    positions["bottom_left"].get("y", 0)
                )
            if "bottom_right" in positions:
                self.bottom_right = MarkerPosition(
                    positions["bottom_right"].get("x", 0),
                    positions["bottom_right"].get("y", 0)
                )
            return True
        except (json.JSONDecodeError, KeyError):
            return False

    def save_to_file(self) -> bool:
        """Save settings to marker_details.json. Returns True if successful."""
        import json
        self.ensure_config_dir_exists()
        config_path = self.get_config_path()
        try:
            data = {
                "marker_size_cm": self.marker_size_cm,
                "marker_positions_cm": {
                    "top_left": {"x": self.top_left.x, "y": self.top_left.y},
                    "top_right": {"x": self.top_right.x, "y": self.top_right.y},
                    "bottom_left": {"x": self.bottom_left.x, "y": self.bottom_left.y},
                    "bottom_right": {"x": self.bottom_right.x, "y": self.bottom_right.y},
                },
                "_comment": "Marker details file for ArUco backdrop calibration",
                "_explanation": {
                    "marker_size_cm": "Physical size of printed ArUco markers in cm",
                    "marker_positions_cm": "Physical positions of marker centers in cm from floor",
                    "horizontal": "x values represent horizontal position in cm (0cm = left edge)",
                    "vertical": "y values represent vertical position in cm from floor"
                }
            }
            with open(config_path, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False


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
        return project_root / "user_configurations" / "calibration.json"

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
    """State for Step 1: Image Input and Measurement Extraction."""
    front_image_path: Optional[Path] = None
    height_cm: Optional[float] = None
    gender: Optional[str] = None  # "male" or "female"
    race: Optional[str] = None  # "asian" or "caucasian"

    # Status of required configurations
    camera_calibration_valid: bool = False
    aruco_settings_valid: bool = False

    # Extraction state
    is_extracting: bool = False
    extraction_error: Optional[str] = None

    def is_complete(self) -> bool:
        """Check if image input is ready for extraction."""
        return (
            self.front_image_path is not None
            and self.height_cm is not None
            and self.gender is not None
            and self.race is not None
            and self.camera_calibration_valid
            and self.aruco_settings_valid
        )

    def can_extract(self) -> bool:
        """Check if all requirements are met for measurement extraction."""
        return self.is_complete() and not self.is_extracting


@dataclass
class MeasurementsState:
    """State for Step 2: Measurements Review."""
    # Body measurements from extraction script
    height_cm: Optional[float] = None
    head_width_cm: Optional[float] = None
    shoulder_width_cm: Optional[float] = None
    hip_width_cm: Optional[float] = None
    upper_arm_length_cm: Optional[float] = None
    forearm_length_cm: Optional[float] = None
    upper_leg_length_cm: Optional[float] = None
    lower_leg_length_cm: Optional[float] = None
    shoulder_to_waist_cm: Optional[float] = None
    hand_length_cm: Optional[float] = None

    # Hair measurements from extraction script
    hair_length_cm: Optional[float] = None

    # Visualization image path
    visualization_path: Optional[Path] = None

    is_extracted: bool = False
    is_manually_edited: bool = False

    # Mesh parameters computation state
    is_computing_parameters: bool = False
    parameters_computed: bool = False
    parameters_report: Optional[dict] = None
    parameters_error: Optional[str] = None

    def is_complete(self) -> bool:
        """Check if measurements are available."""
        return self.is_extracted or self.is_manually_edited

    def to_dict(self) -> dict:
        """Convert measurements to dictionary format."""
        return {
            "height_cm": self.height_cm,
            "head_width_cm": self.head_width_cm,
            "shoulder_width_cm": self.shoulder_width_cm,
            "hip_width_cm": self.hip_width_cm,
            "upper_arm_length_cm": self.upper_arm_length_cm,
            "forearm_length_cm": self.forearm_length_cm,
            "upper_leg_length_cm": self.upper_leg_length_cm,
            "lower_leg_length_cm": self.lower_leg_length_cm,
            "shoulder_to_waist_cm": self.shoulder_to_waist_cm,
            "hand_length_cm": self.hand_length_cm,
            "hair_length_cm": self.hair_length_cm,
        }

    def get_intermediates_dir(self) -> Path:
        """Get the intermediates directory path."""
        project_root = Path(__file__).parent.parent
        return project_root / "intermediates"

    def get_measurements_path(self) -> Path:
        """Get the measurements.json file path."""
        return self.get_intermediates_dir() / "measurements.json"

    def ensure_intermediates_dir_exists(self) -> None:
        """Create the intermediates directory if it doesn't exist."""
        self.get_intermediates_dir().mkdir(parents=True, exist_ok=True)


@dataclass
class ConfigureState:
    """State for Step 4: Avatar Configuration."""
    rig_type: RigType = RigType.DEFAULT_NO_TOES
    fk_ik_hybrid: bool = False
    instrumented_arm: InstrumentedArm = InstrumentedArm.LEFT
    hair_asset: Optional[str] = None  # Name of hair asset from mpfb_hair_assets folder
    t_pose: bool = True

    def is_complete(self) -> bool:
        """Check if configuration is valid."""
        return True  # All fields have defaults


@dataclass
class OutputSettingsState:
    """State for Step 5: Output Settings."""
    output_directory: Optional[Path] = None
    output_filename: str = "avatar"
    export_fbx: bool = True
    export_obj: bool = False

    def is_complete(self) -> bool:
        """Check if output settings are valid."""
        return self.output_directory is not None


@dataclass
class GenerateState:
    """State for Step 6: Generation."""
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

    # ArUco marker settings state
    aruco_settings: ArucoSettingsState = field(default_factory=ArucoSettingsState)

    # Avatar generation wizard states
    image_input: ImageInputState = field(default_factory=ImageInputState)
    measurements: MeasurementsState = field(default_factory=MeasurementsState)
    configure: ConfigureState = field(default_factory=ConfigureState)
    output_settings: OutputSettingsState = field(default_factory=OutputSettingsState)
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
        elif self.current_step == WizardStep.ACCURACY_REVIEW:
            return self.measurements.parameters_computed
        elif self.current_step == WizardStep.CONFIGURE:
            return self.configure.is_complete()
        elif self.current_step == WizardStep.OUTPUT_SETTINGS:
            return self.output_settings.is_complete()
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
        self.output_settings = OutputSettingsState()
        self.generate = GenerateState()
        self.notify_change()
