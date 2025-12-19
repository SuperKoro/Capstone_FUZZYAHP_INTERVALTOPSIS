; Inno Setup Script for Supplier Selection Application
; Professional Windows Installer
; Version 1.0.0

#define MyAppName "Supplier Selection"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Organization"
#define MyAppURL "https://yourwebsite.com"
#define MyAppExeName "SupplierSelection.exe"

[Setup]
; Basic Information
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation Directories
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output
OutputDir=installer_output
OutputBaseFilename=SupplierSelection_Setup_v{#MyAppVersion}

; Compression
Compression=lzma2/max
SolidCompression=yes

; Icons
SetupIconFile=assets\icon.ico.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; Wizard Style (modern look)
WizardStyle=modern
WizardImageFile=compiler:WizModernImage-IS.bmp
WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp

; License (optional - uncomment if you have license file)
; LicenseFile=LICENSE.txt

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Version Info
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Setup
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "vietnamese"; MessagesFile: "compiler:Languages\Vietnamese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main application files
Source: "dist\SupplierSelection\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\SupplierSelection\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; README
Source: "dist\SupplierSelection\README.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
; Start Menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop shortcut (optional - based on task)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
; Register .mcdm file association
Root: HKCR; Subkey: ".mcdm"; ValueType: string; ValueName: ""; ValueData: "SupplierSelectionProject"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "SupplierSelectionProject"; ValueType: string; ValueName: ""; ValueData: "{#MyAppName} Project"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SupplierSelectionProject\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKCR; Subkey: "SupplierSelectionProject\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

; Add to Windows App Paths (makes app searchable)
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{#MyAppExeName}"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletekey

[Run]
; Launch app after installation (optional)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up any files created during app usage
Type: filesandordirs; Name: "{app}"

[Code]
// Custom install messages (Vietnamese support)
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Any post-install actions here
  end;
end;
