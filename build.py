"""
Build script to create standalone Windows executable for urmode
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    packages = ['pystray', 'pillow', 'pyinstaller', 'requests']
    
    for package in packages:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("All packages installed successfully")

def build_executable():
    """Build the executable using PyInstaller"""
    print("\nBuilding executable...")
    
    # Check if icon exists
    icon_param = []
    if os.path.exists('icon.png'):
        icon_param = ['--add-data', 'icon.png;.']
    
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=urmode',
        '--clean',
        'urmode.py'
    ]
    
    if icon_param:
        cmd.extend(icon_param)
    
    try:
        subprocess.check_call(cmd)
        print("\nBuild complete!")
        print("\nYour executable is in the 'dist' folder:")
        print("  dist\\urmode.exe")
        print("\nYou can now:")
        print("  1. Run urmode.exe")
        print("  2. Enable auto-switch based on sunrise/sunset")
        print("  3. Enable startup to run automatically")
        
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed: {e}")
        sys.exit(1)

def main():
    print("Building urmode")
    print("=" * 50)
    
    if not os.path.exists('urmode.py'):
        print("\nError: urmode.py not found!")
        print("Please make sure urmode.py is in the same folder.")
        sys.exit(1)
    
    response = input("\nThis will install dependencies and build urmode.exe. Continue? (y/n): ")
    if response.lower() != 'y':
        print("Build cancelled.")
        sys.exit(0)
    
    install_requirements()
    build_executable()

if __name__ == "__main__":
    main()