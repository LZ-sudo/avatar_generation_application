# Avatar Generation Application

A desktop GUI application that generates a rigged 3D human avatar from a single photograph. The user provides a front-facing image and their height, and the application extracts body measurements, infers mesh parameters, and produces an export-ready avatar in FBX format.

## Directory Structure

```
avatar_generation_application/
|-- gui/                            # CustomTkinter desktop GUI
|   |-- main.py                     # Application entry point
|   |-- app_state.py                # Centralised wizard state
|   |-- backend_interface.py        # Bridge between GUI and backend modules
|   |-- components/                 # Reusable UI components
|   |-- features/                   # Top-level feature views (calibration, generation)
|   `-- steps/                      # Individual wizard step pages
|
|-- measurements_extraction_module/ # Submodule: body measurement extraction from images
|-- mesh_generation_module/         # Submodule: 3D mesh and rig generation via Blender
|
|-- user_configurations/            # Camera calibration and ArUco marker settings
|-- installer/                      # Windows installer build files (developer use)
|   |-- installer.nsi               # NSIS installer script
|   `-- AvatarGeneratorApplication.bat  # Application launcher (compile to .exe before building)
|-- requirements.txt                # GUI dependencies
|-- setup.bat                       # Windows setup script
`-- setup.sh                        # Linux / macOS setup script
```

## Setup

### Prerequisites

1. **Blender 5.0.1** - Download from [blender.org](https://www.blender.org/download/)
2. **MPFB2 Addon** - Install from Blender Extensions:
   - Open Blender → Edit → Preferences → Extensions
   - Search for "MPFB" and click Install
   - Restart Blender
3. **retarget_bvh Addon** *(Required for BVH animation baking)* - Download from [Diffeomorphic/retarget_bvh](https://bitbucket.org/Diffeomorphic/retarget_bvh/downloads/) (GNU GPL v2+):
   - Download the 2026-01-30 `.zip` release
   - Open Blender → Edit → Preferences → Add-ons → Install from Disk
   - Select the downloaded zip and enable the addon
4. **Python 3.11-3.13** (Support for dependencies)

### Installation

1. Clone the repository with all submodules:

```bash
git clone --recurse-submodules https://github.com/LZ-sudo/avatar_generation_application.git

cd avatar_generation_application
```

2. Run the setup script to create virtual environments and install all dependencies:

**Windows:**
```bat
setup.bat
```

**Linux / macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

The script sets up three separate virtual environments:

| Environment | Location | Purpose |
|---|---|---|
| `.venv` | project root | GUI application |
| `venv` | `measurements_extraction_module/` | Measurement extraction |
| `myenv` | `mesh_generation_module/` | Mesh and rig generation |

## Building the Windows Installer

A self-contained Windows setup executable can be compiled from the files in `installer/`. The installer handles cloning the repository, running `setup.bat`, and creating desktop and Start Menu shortcuts automatically.

**Requirements (developer machine only):**
- [NSIS](https://nsis.sourceforge.io/Download) — Nullsoft Scriptable Install System (zlib/libpng licence, free for commercial use)
- [Bat To Exe Converter](https://bat-to-exe-converter.en.softonic.com/) — to compile the launcher batch file

**Steps:**
1. Compile `installer/AvatarGeneratorApplication.bat` to `AvatarGeneratorApplication.exe` using Bat To Exe Converter and place the `.exe` in the `installer/` folder.
2. Right-click `installer/installer.nsi` and select **Compile NSIS Script** (or run `makensis installer.nsi`).
3. The compiled `AvatarGeneratorSetup.exe` will appear in the `installer/` folder.

End users run `AvatarGeneratorSetup.exe` once. The installer checks for Git, Python, and Blender before proceeding.

## Running the Application

Activate the root virtual environment and launch the GUI:

**Windows:**
```bat
.venv\Scripts\activate
python -m gui.main
```

**Linux / macOS:**
```bash
source .venv/bin/activate
python -m gui.main
```

## Acknowledgements

- [NSIS (Nullsoft Scriptable Install System)](https://nsis.sourceforge.io) — used to build the Windows installer.

### GUI

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern themed tkinter UI framework

### Mesh Generation Module

- [Blender](https://www.blender.org) - 3D creation suite
- [MPFB2](http://www.makehumancommunity.org/) - MakeHuman for Blender
- [MPFB Community Contributed Assets](http://www.makehumancommunity.org/content/user_contributed_assets.html) - Community hair assets
- [retarget_bvh](https://bitbucket.org/Diffeomorphic/retarget_bvh/downloads/) - BVH/FBX animation retargeting addon by Thomas Larsson
- [TabM](https://github.com/yandex-research/tabm) - Tabular regression model
- [PyTorch](https://pytorch.org/) - Machine learning framework

### Motion Capture Data
- [CMU Graphics Lab Motion Capture Database](https://mocap.cs.cmu.edu) - Motion capture animations
- [cmubvh](https://github.com/Shriinivas/cmubvh) - CMU mocap data converted to BVH format for use with retarget_bvh

### Measurements Extraction Module

- [easyViTPose](https://github.com/JunkyByte/easy_ViTPose) - High-accuracy pose estimation
- [ViTPose Paper](https://arxiv.org/abs/2204.12484) - Vision Transformer for Generic Body Pose Estimation
- [Head-Detection-Yolov8](https://github.com/Owen718/Head-Detection-Yolov8) - YOLOv8 head detection model trained on CrowdHuman dataset
- [Mediapipe Pose Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker/python)
- [OpenCV ArUco Marker Detection](https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html)
- [Camera Calibration with OpenCV](https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html)
- [Perspective Transformation (Homography)](https://docs.opencv.org/4.x/d9/dab/tutorial_homography.html)
