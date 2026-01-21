"""
Backend interface for the Avatar Generator application.

This module defines the interface between the GUI and the backend modules.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable
import subprocess
import json


class BackendInterface(ABC):
    """
    Abstract interface for backend operations.

    Defines the contract between GUI and backend modules.
    """

    @abstractmethod
    def extract_measurements(
        self,
        front_image: Path,
        height_cm: float,
        camera_calibration_path: Path,
        marker_details_path: Path,
        gender: str,
        race: str,
    ) -> dict:
        """
        Extract body measurements from front image using calibration data.

        Args:
            front_image: Path to front view image
            height_cm: Subject's known height in centimeters
            camera_calibration_path: Path to camera calibration JSON
            marker_details_path: Path to ArUco marker details JSON
            gender: Subject's gender ("male" or "female")
            race: Subject's race ("asian" or "caucasian")

        Returns:
            Dictionary containing gender, race, body_measurements, hair_measurements, and visualization_path
        """
        pass

    @abstractmethod
    def generate_avatar(
        self,
        measurements: dict,
        config: dict,
        progress_callback: Callable[[float, str], None] = None,
    ) -> dict:
        """
        Generate avatar mesh from measurements and configuration.

        Args:
            measurements: Dictionary of body measurements
            config: Dictionary of configuration options
            progress_callback: Optional callback for progress updates (progress, status)

        Returns:
            Dictionary containing output paths and preview images
        """
        pass

    @abstractmethod
    def open_in_blender(self, file_path: Path) -> None:
        """
        Open a file in Blender.

        Args:
            file_path: Path to the file to open
        """
        pass

    @abstractmethod
    def calibrate_camera(
        self,
        image_dir: Path,
        checkerboard_size: tuple[int, int],
        square_size_mm: float,
        output_path: Path,
    ) -> dict:
        """
        Calibrate camera using checkerboard pattern images.

        Args:
            image_dir: Directory containing checkerboard images
            checkerboard_size: Inner corner count (columns, rows)
            square_size_mm: Physical size of each square in mm
            output_path: Path to save calibration JSON

        Returns:
            Dictionary containing calibration results
        """
        pass


class RealBackendInterface(BackendInterface):
    """
    Real implementation of the backend interface.

    Connects to the actual measurement extraction and mesh generation modules.
    """

    def __init__(
        self,
        measurements_module_path: Path = None,
        mesh_module_path: Path = None,
        blender_path: Path = None,
    ):
        self.measurements_module_path = measurements_module_path
        self.mesh_module_path = mesh_module_path
        self.blender_path = blender_path

    def extract_measurements(
        self,
        front_image: Path,
        height_cm: float,
        camera_calibration_path: Path,
        marker_details_path: Path,
        gender: str,
        race: str,
    ) -> dict:
        """
        Extract measurements using the measurements_extraction_module.

        Runs the complete_measurements.py script using the submodule's venv Python.
        After extraction, appends gender and race to the measurements.json file.
        """
        project_root = Path(__file__).parent.parent
        module_path = project_root / "measurements_extraction_module"
        script_path = module_path / "complete_measurements.py"
        venv_python = module_path / "venv" / "Scripts" / "python.exe"

        if not venv_python.exists():
            raise RuntimeError(
                f"Virtual environment Python not found at {venv_python}. "
                "Please set up the measurements_extraction_module venv."
            )

        # Create intermediates directory for outputs
        intermediates_dir = project_root / "intermediates"
        intermediates_dir.mkdir(parents=True, exist_ok=True)

        # Output paths
        output_measurements = intermediates_dir / "measurements.json"
        visualization_dir = intermediates_dir

        cmd = [
            str(venv_python),
            str(script_path),
            str(front_image),
            "--marker-details", str(marker_details_path),
            "--camera-calibration", str(camera_calibration_path),
            "--height", str(height_cm),
            "-o", str(output_measurements),
            "--save-visualization", str(visualization_dir),
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(module_path),
        )

        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or "Unknown error"
            raise RuntimeError(f"Measurement extraction failed: {error_msg}")

        if not output_measurements.exists():
            raise RuntimeError("Extraction completed but output file not created")

        with open(output_measurements) as f:
            measurements = json.load(f)

        # Add gender and race to measurements and save back
        updated_measurements = {
            "gender": gender,
            "race": race,
            "body_measurements": measurements.get("body_measurements", {}),
            "hair_measurements": measurements.get("hair_measurements", {}),
        }

        with open(output_measurements, "w") as f:
            json.dump(updated_measurements, f, indent=2)

        # Check for visualization image
        visualization_path = visualization_dir / "aruco_backdrop_detection.jpg"
        if not visualization_path.exists():
            visualization_path = None

        return {
            "gender": gender,
            "race": race,
            "body_measurements": updated_measurements["body_measurements"],
            "hair_measurements": updated_measurements["hair_measurements"],
            "visualization_path": str(visualization_path) if visualization_path else None,
        }

    def generate_avatar(
        self,
        measurements: dict,
        config: dict,
        progress_callback: Callable[[float, str], None] = None,
    ) -> dict:
        """
        Generate avatar using the mesh_generation_module.

        TODO: Implement when mesh generation module is ready.
        """
        raise NotImplementedError("Avatar generation not yet implemented.")

    def open_in_blender(self, file_path: Path) -> None:
        """
        Open file in Blender.

        TODO: Implement using run_blender.py functionality.
        """
        raise NotImplementedError("Blender integration not yet implemented.")

    def calibrate_camera(
        self,
        image_dir: Path,
        checkerboard_size: tuple[int, int],
        square_size_mm: float,
        output_path: Path,
    ) -> dict:
        """
        Calibrate camera using the measurements_extraction_module.

        Runs the calibrate_camera.py script using the submodule's venv Python.
        """
        project_root = Path(__file__).parent.parent
        module_path = project_root / "measurements_extraction_module"
        script_path = module_path / "calibrate_camera.py"
        venv_python = module_path / "venv" / "Scripts" / "python.exe"

        if not venv_python.exists():
            raise RuntimeError(
                f"Virtual environment Python not found at {venv_python}. "
                "Please set up the measurements_extraction_module venv."
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        cols, rows = checkerboard_size
        checkerboard_arg = f"{cols}x{rows}"

        cmd = [
            str(venv_python),
            str(script_path),
            "-i", str(image_dir),
            "-o", str(output_path),
            "--checkerboard-size", checkerboard_arg,
            "--square-size", str(square_size_mm),
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(module_path),
        )

        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or "Unknown error"
            return {
                "success": False,
                "error": f"Calibration script failed: {error_msg}",
            }

        if not output_path.exists():
            return {
                "success": False,
                "error": "Calibration completed but output file not created",
            }

        with open(output_path) as f:
            return json.load(f)


def get_backend() -> BackendInterface:
    """
    Factory function to get the backend interface.

    Returns:
        BackendInterface implementation
    """
    return RealBackendInterface()
