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
|-- requirements.txt                # GUI dependencies
|-- setup.bat                       # Windows setup script
`-- setup.sh                        # Linux / macOS setup script
```

## Setup

### Prerequisites

- Python 3.11 (For Blender API support)
- Git
- Blender 5.0.1 (required by `mesh_generation_module`)

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
