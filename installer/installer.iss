; Avatar Generation Application - Inno Setup Installer Script
;
; HOW TO BUILD:
;   1. Convert AvatarGeneratorApplication.bat to AvatarGeneratorApplication.exe
;      using Bat To Exe Converter (free): https://bat-to-exe-converter.en.softonic.com/
;      Place the resulting .exe in this installer/ folder.
;   2. Download and install Inno Setup: https://jrsoftware.org/isdl.php
;   3. Open this file in Inno Setup Compiler and click Build > Compile.
;   4. The compiled AvatarGeneratorSetup.exe will appear in installer/Output/

[Setup]
AppName=Avatar Generation Application
AppVersion=1.0
AppPublisher=SUTD_Group_37
DefaultDirName={localappdata}\AvatarGenerator
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=AvatarGeneratorSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; Require no admin rights - installs to user's local app data
PrivilegesRequired=lowest

[Files]
; The launcher executable is embedded and installed to the chosen directory.
; It must be compiled from AvatarGeneratorApplication.bat before building this installer.
Source: "AvatarGeneratorApplication.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Desktop shortcut
Name: "{autodesktop}\Avatar Generator"; Filename: "{app}\AvatarGeneratorApplication.exe"; WorkingDir: "{app}"
; Start menu shortcut
Name: "{group}\Avatar Generator"; Filename: "{app}\AvatarGeneratorApplication.exe"; WorkingDir: "{app}"

[Code]

function IsBlenderInstalled(): Boolean;
begin
  Result :=
    RegKeyExists(HKLM, 'SOFTWARE\BlenderFoundation\Blender 5.0') or
    RegKeyExists(HKCU, 'SOFTWARE\BlenderFoundation\Blender 5.0') or
    FileExists(ExpandConstant('{pf}\Blender Foundation\Blender 5.0\blender.exe')) or
    FileExists(ExpandConstant('{pf64}\Blender Foundation\Blender 5.0\blender.exe'));
end;

function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;

  // Check that Git is installed and accessible
  if not Exec(ExpandConstant('{cmd}'), '/C git --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode)
     or (ResultCode <> 0) then
  begin
    MsgBox(
      'Git is not installed or not found in PATH.' + #13#10 +
      'Please install Git from https://git-scm.com/download/win and try again.',
      mbError, MB_OK
    );
    Result := False;
    Exit;
  end;

  // Check that Python 3.11-3.13 is installed and accessible
  if not Exec(ExpandConstant('{cmd}'),
       '/C python -c "import sys; exit(0 if (3,11) <= sys.version_info[:2] <= (3,13) else 1)"',
       '', SW_HIDE, ewWaitUntilTerminated, ResultCode)
     or (ResultCode <> 0) then
  begin
    MsgBox(
      'Python 3.11, 3.12, or 3.13 is required but was not found.' + #13#10 +
      'Please install a supported version from https://www.python.org/downloads/ and try again.',
      mbError, MB_OK
    );
    Result := False;
    Exit;
  end;

  // Check that Blender 5.0.1 is installed
  if not IsBlenderInstalled() then
  begin
    MsgBox(
      'Blender 5.0.1 is not installed.' + #13#10 +
      'Please install Blender 5.0.1 from https://www.blender.org/download/ and try again.',
      mbError, MB_OK
    );
    Result := False;
    Exit;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
  InstallDir: String;
begin
  if CurStep <> ssPostInstall then Exit;

  InstallDir := ExpandConstant('{app}');

  // Step 1: Clone the repository with all submodules
  WizardForm.StatusLabel.Caption := 'Cloning repository (this may take several minutes)...';
  if not Exec(
    ExpandConstant('{cmd}'),
    '/C git clone --recurse-submodules https://github.com/LZ-sudo/avatar_generation_application.git "' + InstallDir + '\avatar_generation_application"',
    InstallDir,
    SW_HIDE,
    ewWaitUntilTerminated,
    ResultCode
  ) or (ResultCode <> 0) then
  begin
    MsgBox(
      'Failed to clone the repository.' + #13#10 +
      'Please check your internet connection and try again.',
      mbError, MB_OK
    );
    Exit;
  end;

  // Step 2: Run setup.bat to create virtual environments
  WizardForm.StatusLabel.Caption := 'Setting up virtual environments (this may take several minutes)...';
  if not Exec(
    ExpandConstant('{cmd}'),
    '/C "' + InstallDir + '\avatar_generation_application\setup.bat"',
    InstallDir + '\avatar_generation_application',
    SW_HIDE,
    ewWaitUntilTerminated,
    ResultCode
  ) or (ResultCode <> 0) then
  begin
    MsgBox(
      'Dependency setup failed.' + #13#10 +
      'The application may not run correctly. Please re-run the installer.',
      mbError, MB_OK
    );
  end;
end;
