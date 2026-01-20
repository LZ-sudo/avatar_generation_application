"""
Backend interface for the Avatar Generator application.

This module defines the interface between the GUI and the backend modules.
It provides mock implementations for testing the GUI independently.

When the backend modules are ready, replace MockBackendInterface with
a real implementation that calls the actual modules.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Optional
import time


class BackendInterface(ABC):
    """
    Abstract interface for backend operations.

    Defines the contract between GUI and backend modules.
    """

    @abstractmethod
    def extract_measurements(
        self,
        front_image: Path,
        side_image: Path,
    ) -> dict:
        """
        Extract body measurements from front and side images.

        Args:
            front_image: Path to front view image
            side_image: Path to side view image

        Returns:
            Dictionary containing extracted measurements
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


class MockBackendInterface(BackendInterface):
    """
    Mock implementation of the backend interface for GUI testing.

    Returns realistic dummy data to test the GUI flow.
    """

    def extract_measurements(
        self,
        front_image: Path,
        side_image: Path,
    ) -> dict:
        """
        Return mock measurements for testing.

        Simulates the extraction process with a small delay.
        """
        time.sleep(1.0)

        return {
            "height_cm": 175.5,
            "shoulder_width_cm": 45.2,
            "chest_circumference_cm": 98.0,
            "waist_circumference_cm": 82.5,
            "hip_circumference_cm": 96.0,
            "arm_length_cm": 58.0,
            "leg_length_cm": 82.0,
            "head_circumference_cm": 56.5,
        }

    def generate_avatar(
        self,
        measurements: dict,
        config: dict,
        progress_callback: Callable[[float, str], None] = None,
    ) -> dict:
        """
        Simulate avatar generation with progress updates.
        """
        steps = [
            (0.1, "Initializing Blender..."),
            (0.2, "Loading base mesh..."),
            (0.3, "Applying body proportions..."),
            (0.5, "Adjusting measurements..."),
            (0.6, "Generating rig..."),
            (0.7, "Applying hair style..."),
            (0.8, "Finalizing mesh..."),
            (0.9, "Rendering preview..."),
            (1.0, "Exporting files..."),
        ]

        for progress, status in steps:
            if progress_callback:
                progress_callback(progress, status)
            time.sleep(0.5)

        output_dir = Path(config.get("output_directory", "."))
        filename = config.get("output_filename", "avatar")

        result = {
            "fbx_path": output_dir / f"{filename}.fbx",
            "preview_images": [],
        }

        if config.get("export_obj"):
            result["obj_path"] = output_dir / f"{filename}.obj"

        return result

    def open_in_blender(self, file_path: Path) -> None:
        """
        Mock opening in Blender (just prints for testing).
        """
        print(f"[Mock] Would open in Blender: {file_path}")

    def calibrate_camera(
        self,
        image_dir: Path,
        checkerboard_size: tuple[int, int],
        square_size_mm: float,
        output_path: Path,
    ) -> dict:
        """
        Mock camera calibration for testing.
        """
        time.sleep(2.0)

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Mock calibration results
        import json
        results = {
            "success": True,
            "camera_matrix": [
                [1000.0, 0.0, 640.0],
                [0.0, 1000.0, 480.0],
                [0.0, 0.0, 1.0],
            ],
            "distortion_coefficients": [[0.1, -0.2, 0.001, 0.001, 0.05]],
            "reprojection_error": 0.35,
            "num_successful_images": 10,
            "num_failed_images": 2,
            "successful_images": [],
            "failed_images": [],
        }

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        return results


class RealBackendInterface(BackendInterface):
    """
    Real implementation of the backend interface.

    Connects to the actual measurement extraction and mesh generation modules.

    TODO: Implement when backend modules are ready.
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
        side_image: Path,
    ) -> dict:
        """
        Extract measurements using the measurements_extraction_module.

        TODO: Implement actual module integration.
        """
        raise NotImplementedError(
            "Real backend not yet implemented. "
            "Use MockBackendInterface for testing."
        )

    def generate_avatar(
        self,
        measurements: dict,
        config: dict,
        progress_callback: Callable[[float, str], None] = None,
    ) -> dict:
        """
        Generate avatar using the mesh_generation_module.

        TODO: Implement actual module integration.
        """
        raise NotImplementedError(
            "Real backend not yet implemented. "
            "Use MockBackendInterface for testing."
        )

    def open_in_blender(self, file_path: Path) -> None:
        """
        Open file in Blender.

        TODO: Implement using run_blender.py functionality.
        """
        raise NotImplementedError(
            "Real backend not yet implemented. "
            "Use MockBackendInterface for testing."
        )

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
        import subprocess
        import json

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


def get_backend(use_mock: bool = True) -> BackendInterface:
    """
    Factory function to get the appropriate backend interface.

    Args:
        use_mock: If True, returns mock backend for testing.
                  If False, returns real backend (requires modules).

    Returns:
        BackendInterface implementation
    """
    if use_mock:
        return MockBackendInterface()
    else:
        return RealBackendInterface()
