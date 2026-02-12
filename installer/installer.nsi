; Avatar Generation Application - NSIS Installer Script
;
; Installer built using NSIS (Nullsoft Scriptable Install System)
; https://nsis.sourceforge.io -- zlib/libpng licence, free for commercial use
;
; HOW TO BUILD:
;   1. Download and install NSIS: https://nsis.sourceforge.io/Download
;   2. Right-click this file and select "Compile NSIS Script", or run:
;         makensis installer.nsi
;   3. The compiled AvatarGeneratorSetup.exe will appear in this folder.

!include "MUI2.nsh"
!include "LogicLib.nsh"

; ---------------------------------------------------------------------------
; Metadata
; ---------------------------------------------------------------------------
Name "Avatar Generation Application"
OutFile "AvatarGeneratorSetup.exe"
InstallDir "$LOCALAPPDATA\AvatarGenerator"
InstallDirRegKey HKCU "Software\SUTD_Group_37\AvatarGenerator" "InstallDir"
RequestExecutionLevel user

; ---------------------------------------------------------------------------
; Installer pages
; ---------------------------------------------------------------------------
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

; ---------------------------------------------------------------------------
; Prerequisite checks (run before installer pages are shown)
; ---------------------------------------------------------------------------
Function .onInit

  ; Check Git
  nsExec::ExecToStack 'cmd /C git --version'
  Pop $0
  Pop $1
  ${If} $0 != 0
    MessageBox MB_OK|MB_ICONSTOP "Git is not installed or not found in PATH.$\r$\nPlease install Git from https://git-scm.com/download/win and try again."
    Abort
  ${EndIf}

  ; Check Python 3.11-3.13
  nsExec::ExecToStack 'cmd /C python -c "import sys; exit(0 if (3,11) <= sys.version_info[:2] <= (3,13) else 1)"'
  Pop $0
  Pop $1
  ${If} $0 != 0
    MessageBox MB_OK|MB_ICONSTOP "Python 3.11, 3.12, or 3.13 is required but was not found.$\r$\nPlease install a supported version from https://www.python.org/downloads/ and try again."
    Abort
  ${EndIf}

  ; Check Blender 5.0.1 via registry and common install paths
  StrCpy $2 "0"

  ClearErrors
  ReadRegStr $0 HKLM "SOFTWARE\BlenderFoundation\Blender 5.0" ""
  ${IfNot} ${Errors}
    StrCpy $2 "1"
  ${EndIf}

  ClearErrors
  ReadRegStr $0 HKCU "SOFTWARE\BlenderFoundation\Blender 5.0" ""
  ${IfNot} ${Errors}
    StrCpy $2 "1"
  ${EndIf}

  ${If} ${FileExists} "$PROGRAMFILES64\Blender Foundation\Blender 5.0\blender.exe"
    StrCpy $2 "1"
  ${EndIf}
  ${If} ${FileExists} "$PROGRAMFILES\Blender Foundation\Blender 5.0\blender.exe"
    StrCpy $2 "1"
  ${EndIf}

  ${If} $2 == "0"
    MessageBox MB_OK|MB_ICONSTOP "Blender 5.0.1 is not installed.$\r$\nPlease install Blender 5.0.1 from https://www.blender.org/download/ and try again."
    Abort
  ${EndIf}

FunctionEnd

; ---------------------------------------------------------------------------
; Main installation section
; ---------------------------------------------------------------------------
Section "Install"

  SetOutPath "$INSTDIR"

  ; Clone the repository with all submodules
  DetailPrint "Cloning repository (this may take several minutes)..."
  nsExec::ExecToLog 'cmd /C git clone --recurse-submodules https://github.com/LZ-sudo/avatar_generation_application.git "$INSTDIR\avatar_generation_application"'
  Pop $0
  ${If} $0 != 0
    MessageBox MB_OK|MB_ICONSTOP "Failed to clone the repository.$\r$\nPlease check your internet connection and try again."
    Abort
  ${EndIf}

  ; Run setup.bat to create virtual environments
  DetailPrint "Setting up virtual environments (this may take several minutes)..."
  nsExec::ExecToLog 'cmd /C "$INSTDIR\avatar_generation_application\setup.bat"'
  Pop $0
  ${If} $0 != 0
    MessageBox MB_OK|MB_ICONEXCLAMATION "Dependency setup failed.$\r$\nThe application may not run correctly. Please re-run the installer."
  ${EndIf}

  ; Write a Python launcher script to the install directory.
  ; It uses __file__ to locate itself at runtime, so paths are always correct
  ; regardless of how or where the shortcut is invoked.
  FileOpen $4 "$INSTDIR\AvatarGeneratorApplication.py" w
  FileWrite $4 "import subprocess$\r$\n"
  FileWrite $4 "from pathlib import Path$\r$\n"
  FileWrite $4 "$\r$\n"
  FileWrite $4 "install_dir = Path(__file__).resolve().parent$\r$\n"
  FileWrite $4 "project_dir = install_dir / 'avatar_generation_application'$\r$\n"
  FileWrite $4 "pythonw = project_dir / '.venv' / 'Scripts' / 'pythonw.exe'$\r$\n"
  FileWrite $4 "subprocess.Popen([str(pythonw), '-m', 'gui.main'], cwd=str(project_dir))$\r$\n"
  FileClose $4

  ; Create desktop shortcut: runs the launcher script via the venv's pythonw.exe (no console window)
  CreateShortcut "$DESKTOP\Avatar Generator.lnk" "$INSTDIR\avatar_generation_application\.venv\Scripts\pythonw.exe" '"$INSTDIR\AvatarGeneratorApplication.py"'

  ; Create start menu shortcuts
  CreateDirectory "$SMPROGRAMS\Avatar Generator"
  CreateShortcut "$SMPROGRAMS\Avatar Generator\Avatar Generator.lnk" "$INSTDIR\avatar_generation_application\.venv\Scripts\pythonw.exe" '"$INSTDIR\AvatarGeneratorApplication.py"'

  ; Save install directory to registry
  WriteRegStr HKCU "Software\SUTD_Group_37\AvatarGenerator" "InstallDir" "$INSTDIR"

SectionEnd
