
!include "MUI2.nsh"
!include "FileFunc.nsh"

Name "Password Manager Analyzer"
OutFile "dist/PasswordManagerAnalyzer_Setup.exe"
InstallDir "$PROGRAMFILES64\Password Manager Analyzer"
RequestExecutionLevel admin

!define MUI_ABORTWARNING
!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    File "dev_build\PasswordManagerAnalyzer.exe"
    
    CreateDirectory "$SMPROGRAMS\Password Manager Analyzer"
    CreateShortCut "$SMPROGRAMS\Password Manager Analyzer\Password Manager Analyzer.lnk" "$INSTDIR\PasswordManagerAnalyzer.exe"
    CreateShortCut "$DESKTOP\Password Manager Analyzer.lnk" "$INSTDIR\PasswordManagerAnalyzer.exe"
    
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PasswordManagerAnalyzer" "DisplayName" "Password Manager Analyzer"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PasswordManagerAnalyzer" "UninstallString" "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\PasswordManagerAnalyzer.exe"
    Delete "$INSTDIR\Uninstall.exe"
    
    Delete "$SMPROGRAMS\Password Manager Analyzer\Password Manager Analyzer.lnk"
    Delete "$DESKTOP\Password Manager Analyzer.lnk"
    RMDir "$SMPROGRAMS\Password Manager Analyzer"
    RMDir "$INSTDIR"
    
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PasswordManagerAnalyzer"
SectionEnd
