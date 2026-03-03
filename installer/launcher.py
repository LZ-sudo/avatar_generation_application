import subprocess
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    install_dir = Path(sys.executable).resolve().parent
else:
    install_dir = Path(__file__).resolve().parent

project_dir = install_dir / "avatar_generation_application"
pythonw = project_dir / ".venv" / "Scripts" / "pythonw.exe"
subprocess.Popen([str(pythonw), "-m", "gui.main"], cwd=str(project_dir))
