"""
Feature views for the Avatar Generator application.

Contains the main feature views:
- CameraCalibrationView: Camera calibration using checkerboard patterns
- AvatarGenerationView: Avatar generation wizard flow
"""

from .camera_calibration import CameraCalibrationView
from .avatar_generation import AvatarGenerationView

__all__ = ["CameraCalibrationView", "AvatarGenerationView"]
