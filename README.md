# urmode

A lightweight Windows system tray application for managing Light and Dark themes with automatic switching based on sunrise and sunset times.

![urmode logo](icon.png)

## Features

* Quick theme switching from the system tray
* Automatic theme switching based on sunrise/sunset times
* Minimal resource usage (runs silently in the background)
* Optional startup with Windows
* No external dependencies for end users

## Quick Start

### For End Users

1. Download `urmode.exe` from [Releases](../../releases)
2. Run the executable
3. Right-click the system tray icon to access options
4. Enable "Auto-switch (Sunrise/Sunset)" for automatic theme changes
5. Enable "Run at Startup" to launch with Windows

### For Developers

Clone the repository:

```bash
git clone https://github.com/Mizokuiam/urmode.git
cd urmode
```

Build from source:

```bash
python build.py
```

The executable will be created in the `dist` folder.

## Usage

### Manual Theme Switching

Right-click the system tray icon and select:
* Light Theme
* Dark Theme

### Automatic Theme Switching

Enable "Auto-switch (Sunrise/Sunset)" from the menu to automatically change themes based on your location's sunrise and sunset times.

* Light theme activates at sunrise
* Dark theme activates at sunset
* Location is determined automatically based on your IP address
* Theme checks occur every 5 minutes

### Startup Configuration

Enable "Run at Startup" to have urmode launch automatically when Windows starts.

## System Requirements

* Windows 10 (version 1809 or later) or Windows 11
* Approximately 15-20 MB disk space
* Internet connection (for automatic sunrise/sunset detection)

## Building from Source

### Prerequisites

* Python 3.7 or higher
* pip (Python package installer)

### Dependencies

* pystray
* pillow
* pyinstaller
* requests

### Build Instructions

1. Install dependencies:

```bash
pip install pystray pillow pyinstaller requests
```

2. Build the executable:

```bash
python build.py
```

3. Find the executable in the `dist` folder

## How It Works

urmode integrates with Windows registry to modify theme settings. The application:

1. Creates a system tray icon for easy access
2. Monitors and modifies Windows personalization settings
3. Uses sunrise-sunset.org API to determine local sunrise/sunset times
4. Automatically switches themes based on time of day (when enabled)
5. Stores preferences in Windows registry

## Privacy

* No data collection or telemetry
* Location determined via IP geolocation (only when auto-switch is enabled)
* All settings stored locally in Windows registry
* No network requests except for sunrise/sunset times

## Troubleshooting

### Application doesn't start

* Ensure you're running Windows 10 (1809+) or Windows 11
* Try running as Administrator
* Check `urmode_error.log` in the same folder as the executable

### Theme doesn't change

* Verify Windows version supports theme switching
* Try running as Administrator
* Manually switch once to test registry permissions

### Icon not visible in system tray

* Click the arrow icon near the system clock to show hidden icons
* Pin the icon to keep it visible

### Auto-switch not working

* Check internet connection (required for sunrise/sunset times)
* Verify the setting is enabled in the menu
* Wait up to 5 minutes for the next check cycle

## Contributing

Contributions are welcome. Please open an issue or submit a pull request.

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.