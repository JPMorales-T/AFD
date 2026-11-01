#define NombreAplicacion "Simulador AFD"
#define NombreCompletoAplicacion "Simulador de Autómatas Finitos Deterministas"
#define VersionAplicacion "1.0"
#define EditorAplicacion "Proyecto del curso de Autómatas"
#define EjecutableAplicacion "SimuladorAFD.exe"
#define CarpetaProyecto ".."
#define CarpetaDistribucion CarpetaProyecto + "\dist\SimuladorAFD"

[Setup]
AppId={{550A4B03-B7CF-4B2E-9B05-CCDD086FCEBD}
AppName={#NombreAplicacion}
AppVerName={#NombreCompletoAplicacion} {#VersionAplicacion}
AppVersion={#VersionAplicacion}
AppPublisher={#EditorAplicacion}
DefaultDirName={autopf}\{#NombreAplicacion}
DefaultGroupName={#NombreAplicacion}
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir={#CarpetaProyecto}\salida_instalador
OutputBaseFilename=Instalador_SimuladorAFD
SetupIconFile={#CarpetaProyecto}\recursos\icono.ico
UninstallDisplayIcon={app}\{#EjecutableAplicacion}
UninstallDisplayName={#NombreAplicacion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes

[Languages]
Name: "espanol"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "acceso_escritorio"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "{#CarpetaDistribucion}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#CarpetaProyecto}\ejemplos\*.txt"; DestDir: "{app}\Ejemplos"; Flags: ignoreversion
Source: "{#CarpetaProyecto}\documentacion\Manual_de_usuario.pdf"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#NombreAplicacion}"; Filename: "{app}\{#EjecutableAplicacion}"
Name: "{group}\Manual de usuario"; Filename: "{app}\Manual_de_usuario.pdf"
Name: "{group}\Ejemplos de AFD"; Filename: "{app}\Ejemplos"
Name: "{group}\{cm:UninstallProgram,{#NombreAplicacion}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#NombreAplicacion}"; Filename: "{app}\{#EjecutableAplicacion}"; Tasks: acceso_escritorio

[Run]
Filename: "{app}\{#EjecutableAplicacion}"; Description: "{cm:LaunchProgram,{#NombreAplicacion}}"; Flags: nowait postinstall skipifsilent
