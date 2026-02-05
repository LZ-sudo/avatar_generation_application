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

    @abstractmethod
    def compute_mesh_parameters(
        self,
        measurements_path: Path,
    ) -> dict:
        """
        Compute mesh parameters from measurements using ML models.

        Args:
            measurements_path: Path to measurements JSON file (contains gender, race, and measurements)

        Returns:
            Dictionary containing the parameters report with target vs actual comparisons
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

        Runs generate_human.py in Blender with the specified configuration.
        """
        project_root = Path(__file__).parent.parent
        module_path = project_root / "mesh_generation_module"

        # Get mesh_parameters.json path (created by compute_all_parameters.py)
        intermediates_dir = project_root / "intermediates"
        mesh_parameters_path = intermediates_dir / "mesh_parameters.json"

        if not mesh_parameters_path.exists():
            raise RuntimeError(
                f"Mesh parameters file not found at {mesh_parameters_path}. "
                "Please complete the accuracy review step first."
            )

        # Update mesh_parameters.json with output configuration
        with open(mesh_parameters_path) as f:
            mesh_params_data = json.load(f)

        # Add output section to config
        output_filename = config["output_filename"] + ".fbx"
        mesh_params_data["output"] = {
            "directory": config["output_directory"],
            "filename": output_filename
        }

        # Save updated mesh parameters
        with open(mesh_parameters_path, "w") as f:
            json.dump(mesh_params_data, f, indent=2)

        # Get output directory
        output_dir = Path(config["output_directory"])
        output_dir.mkdir(parents=True, exist_ok=True)

        if progress_callback:
            progress_callback(0.1, "Starting Blender...")

        # Build command using run_blender.py wrapper
        run_blender_script = module_path / "run_blender.py"

        cmd = [
            "python",
            str(run_blender_script),
            "--script", "generate_human.py",
            "--",
            "--config", str(mesh_parameters_path),
            "--rig-type", config["rig_type"],
            "--instrumented-arm", config["instrumented_arm"],
            "--output-dir", str(output_dir),
        ]

        # Add optional flags
        if config.get("fk_ik_hybrid"):
            cmd.append("--fk-ik-hybrid")

        if config.get("t_pose"):
            cmd.append("--t-pose")

        # Add hair asset if specified
        if config.get("hair_asset"):
            cmd.extend(["--hair", config["hair_asset"]])

        if progress_callback:
            progress_callback(0.2, "Running Blender script...")

        # Run Blender via run_blender.py
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(module_path),
            timeout=600,  # 10 minute timeout
        )

        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or "Unknown error"
            raise RuntimeError(f"Avatar generation failed: {error_msg}")

        if progress_callback:
            progress_callback(0.9, "Finalizing...")

        # Find output files
        output_filename = config["output_filename"]
        fbx_path = None
        obj_path = None

        if config.get("export_fbx", True):
            fbx_path = output_dir / f"{output_filename}.fbx"
            if not fbx_path.exists():
                raise RuntimeError(f"Expected FBX output not found at {fbx_path}")

        if config.get("export_obj", False):
            obj_path = output_dir / f"{output_filename}.obj"
            if not obj_path.exists():
                obj_path = None  # Optional, don't fail if not found

        # Clean up intermediates directory after successful export
        if progress_callback:
            progress_callback(0.95, "Cleaning up temporary files...")

        try:
            import shutil
            if intermediates_dir.exists():
                shutil.rmtree(intermediates_dir)
        except Exception as e:
            # Don't fail if cleanup fails
            print(f"Warning: Could not clean up intermediates directory: {e}")

        if progress_callback:
            progress_callback(1.0, "Complete!")

        return {
            "fbx_path": str(fbx_path) if fbx_path else None,
            "obj_path": str(obj_path) if obj_path else None,
            "preview_images": [],
        }

    def open_in_blender(self, file_path: Path) -> None:
        """
        Open file in Blender GUI.

        Opens the specified file in Blender. Assumes Blender is in PATH or BLENDER_PATH is set.
        """
        import os
        import shutil

        # Try to find Blender executable
        blender_exe = None

        # Check BLENDER_PATH environment variable
        blender_env = os.environ.get("BLENDER_PATH")
        if blender_env and Path(blender_env).exists():
            blender_exe = blender_env
        else:
            # Try to find in PATH
            blender_exe = shutil.which("blender")

        if not blender_exe:
            raise RuntimeError(
                "Blender executable not found. Please install Blender and ensure it's in PATH, "
                "or set BLENDER_PATH environment variable."
            )

        # Open file in Blender GUI (non-blocking)
        subprocess.Popen([blender_exe, str(file_path)])

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

    def compute_mesh_parameters(
        self,
        measurements_path: Path,
    ) -> dict:
        """
        Compute mesh parameters using the mesh_generation_module.

        Runs compute_all_parameters.py to infer macroparameters and adjust microparameters.
        """
        project_root = Path(__file__).parent.parent
        module_path = project_root / "mesh_generation_module"
        script_path = module_path / "compute_all_parameters.py"

        # Read measurements to get gender and race
        with open(measurements_path) as f:
            measurements_data = json.load(f)

        gender = measurements_data.get("gender", "male")
        race = measurements_data.get("race", "asian")

        # Construct model weights path based on gender and race
        weights_dir = module_path / "macroparameters_inference_weight_files"
        weights_filename = f"macroparameters_inference_models_{gender}_{race}_tabm.pkl"
        weights_path = weights_dir / weights_filename

        if not weights_path.exists():
            raise RuntimeError(
                f"Model weights not found at {weights_path}. "
                f"Expected weights for gender={gender}, race={race}."
            )

        # Output paths
        intermediates_dir = project_root / "intermediates"
        intermediates_dir.mkdir(parents=True, exist_ok=True)
        output_params = intermediates_dir / "mesh_parameters.json"
        output_report = intermediates_dir / "parameters_report.json"

        cmd = [
            "python",
            str(script_path),
            "--input", str(measurements_path),
            "--models", str(weights_path),
            "--output", str(output_params),
            "--report", str(output_report),
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(module_path),
            timeout=600,  # 10 minute timeout
        )

        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or "Unknown error"
            raise RuntimeError(f"Parameter computation failed: {error_msg}")

        if not output_report.exists():
            raise RuntimeError("Computation completed but report file not created")

        with open(output_report) as f:
            report = json.load(f)

        return report


def get_backend() -> BackendInterface:
    """
    Factory function to get the backend interface.

    Returns:
        BackendInterface implementation
    """
    return RealBackendInterface()
