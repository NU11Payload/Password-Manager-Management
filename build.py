import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description='Build Password Manager Analyzer')
    parser.add_argument('--dev-only', action='store_true', help='Build only development version')
    parser.add_argument('--installer-only', action='store_true', help='Build only installer')
    return parser.parse_args()

def clean_build_dirs():
    """Clean up build directories"""
    print("Cleaning up...")
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

def install_build_dependencies():
    """Install dependencies needed for building."""
    print("Installing build dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Install platform-specific dependencies
    if sys.platform == 'win32':
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    elif sys.platform == 'linux':
        # Check if we're running as root for apt commands
        if os.geteuid() == 0:
            subprocess.check_call(["apt-get", "update"])
            subprocess.check_call(["apt-get", "install", "-y", "dpkg-dev", "build-essential"])

def check_installer_requirements():
    """Check platform-specific installer requirements."""
    if sys.platform == 'win32':
        print("Checking NSIS installation...")
        nsis_path = shutil.which('makensis')
        if not nsis_path:
            print("NSIS not found. Please install NSIS from https://nsis.sourceforge.io/Download")
            print("After installation, add NSIS to your system PATH")
            sys.exit(1)
    elif sys.platform == 'linux':
        print("Checking dpkg-deb installation...")
        dpkg_path = shutil.which('dpkg-deb')
        if not dpkg_path:
            print("dpkg-deb not found. Please install build-essential package.")
            sys.exit(1)
    elif sys.platform == 'darwin':
        print("Checking pkgbuild installation...")
        pkgbuild_path = shutil.which('pkgbuild')
        if not pkgbuild_path:
            print("pkgbuild not found. Please install Xcode Command Line Tools.")
            sys.exit(1)

def create_dev_executable():
    """Create development executable using PyInstaller."""
    print("Creating development executable...")
    
    # Build using PyInstaller
    subprocess.check_call([
        "pyinstaller",
        "--name=password_analyzer",
        "--clean",
        "--windowed",
        "--onedir",  # Create a directory with all dependencies
        "--add-data=README.md:.",
        "password_analyzer_gui.py"
    ])
    
    print("\nDevelopment build created in ./dist/password_analyzer directory")

def create_windows_installer():
    """Create Windows NSIS installer."""
    print("Creating Windows installer...")
    with open('installer.nsi', 'w') as f:
        f.write("""
!include "MUI2.nsh"
!include "FileFunc.nsh"

Name "Password Manager Analyzer"
OutFile "dist/PasswordManagerAnalyzer_Setup.exe"
InstallDir "$PROGRAMFILES64\\Password Manager Analyzer"
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
    File "dev_build\\PasswordManagerAnalyzer.exe"
    
    CreateDirectory "$SMPROGRAMS\\Password Manager Analyzer"
    CreateShortCut "$SMPROGRAMS\\Password Manager Analyzer\\Password Manager Analyzer.lnk" "$INSTDIR\\PasswordManagerAnalyzer.exe"
    CreateShortCut "$DESKTOP\\Password Manager Analyzer.lnk" "$INSTDIR\\PasswordManagerAnalyzer.exe"
    
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\PasswordManagerAnalyzer" "DisplayName" "Password Manager Analyzer"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\PasswordManagerAnalyzer" "UninstallString" "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\PasswordManagerAnalyzer.exe"
    Delete "$INSTDIR\\Uninstall.exe"
    
    Delete "$SMPROGRAMS\\Password Manager Analyzer\\Password Manager Analyzer.lnk"
    Delete "$DESKTOP\\Password Manager Analyzer.lnk"
    RMDir "$SMPROGRAMS\\Password Manager Analyzer"
    RMDir "$INSTDIR"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\PasswordManagerAnalyzer"
SectionEnd
""")
    subprocess.check_call(["makensis", "installer.nsi"])

def create_linux_installer():
    """Create Linux .deb package."""
    print("Creating Linux installer...")
    
    # Create package structure
    package_name = "password-manager-analyzer"
    version = "1.0.0"
    arch = "amd64"
    package_dir = f"dist/{package_name}_{version}_{arch}"
    
    # Create directory structure
    os.makedirs(f"{package_dir}/DEBIAN", exist_ok=True)
    os.makedirs(f"{package_dir}/usr/local/bin", exist_ok=True)
    os.makedirs(f"{package_dir}/usr/share/applications", exist_ok=True)
    
    # Create control file
    with open(f"{package_dir}/DEBIAN/control", 'w') as f:
        f.write(f"""Package: {package_name}
Version: {version}
Architecture: {arch}
Maintainer: Your Name <your.email@example.com>
Description: Password Manager Export Analyzer
 A tool to analyze and parse through exported password manager data.
""")
    
    # Copy executable
    shutil.copy2("dev_build/PasswordManagerAnalyzer", f"{package_dir}/usr/local/bin/")
    
    # Create desktop entry
    with open(f"{package_dir}/usr/share/applications/password-manager-analyzer.desktop", 'w') as f:
        f.write("""[Desktop Entry]
Name=Password Manager Analyzer
Exec=/usr/local/bin/PasswordManagerAnalyzer
Type=Application
Categories=Utility;
""")
    
    # Build the package
    subprocess.check_call(["dpkg-deb", "--build", package_dir])

def create_macos_installer():
    """Create macOS .pkg installer."""
    print("Creating macOS installer...")
    
    # Create package structure
    os.makedirs("dist/pkg_root/Applications/Password Manager Analyzer.app/Contents/MacOS", exist_ok=True)
    
    # Copy executable
    shutil.copy2("dev_build/PasswordManagerAnalyzer", "dist/pkg_root/Applications/Password Manager Analyzer.app/Contents/MacOS/")
    
    # Create Info.plist
    with open("dist/pkg_root/Applications/Password Manager Analyzer.app/Contents/Info.plist", 'w') as f:
        f.write("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>PasswordManagerAnalyzer</string>
    <key>CFBundleIdentifier</key>
    <string>com.example.passwordmanageranalyzer</string>
    <key>CFBundleName</key>
    <string>Password Manager Analyzer</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
</dict>
</plist>
""")
    
    # Build the package
    subprocess.check_call([
        "pkgbuild",
        "--root", "dist/pkg_root",
        "--identifier", "com.example.passwordmanageranalyzer",
        "--version", "1.0.0",
        "--install-location", "/",
        "dist/PasswordManagerAnalyzer.pkg"
    ])

def create_installer():
    """Create platform-specific installer."""
    # Ensure dev build exists
    dev_executable = "PasswordManagerAnalyzer.exe" if sys.platform == 'win32' else "PasswordManagerAnalyzer"
    if not os.path.exists(f"dev_build/{dev_executable}"):
        print("Development build not found. Building it first...")
        create_dev_executable()
    
    # Create dist directory
    os.makedirs("dist", exist_ok=True)
    
    # Create platform-specific installer
    if sys.platform == 'win32':
        create_windows_installer()
    elif sys.platform == 'linux':
        create_linux_installer()
    elif sys.platform == 'darwin':
        create_macos_installer()
    else:
        print(f"Installer creation not supported for platform: {sys.platform}")
        sys.exit(1)

def main():
    """Main build script."""
    args = parse_args()
    
    try:
        # Ensure we have icon file
        if not os.path.exists('icon.ico') and sys.platform == 'win32':
            print("Warning: icon.ico not found. Using default icon.")
            shutil.copy(sys.executable, 'icon.ico')

        # Clean up any previous builds
        clean_build_dirs()

        # Install build dependencies
        install_build_dependencies()

        if args.installer_only:
            check_installer_requirements()
            create_installer()
            print(f"\nInstaller created in ./dist directory")
        elif args.dev_only:
            create_dev_executable()
            print("\nDevelopment build created in ./dev_build directory")
        else:
            check_installer_requirements()
            create_dev_executable()
            print("\nDevelopment build created in ./dev_build directory")
            create_installer()
            print(f"\nInstaller created in ./dist directory")

    except subprocess.CalledProcessError as e:
        print(f"Error during build process: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 