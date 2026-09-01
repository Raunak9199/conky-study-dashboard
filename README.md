# Study Dashboard (Linux Desktop App)

A completely interactive, standalone PyQt5 desktop dashboard designed for Linux. It features a translucent, rounded aesthetic to manage a 30-day study schedule with built-in pause tracking and notifications.

*(Note: This application is explicitly built and tested for Linux desktop environments).*

## Key Features
- **Standalone GUI App**: Built with PyQt5. Functions as a normal desktop window (draggable, resizable, closeable).
- **Persistent State**: Safely records schedule pauses across midnight resets and system sleep/wake cycles using atomic lock files.
- **Smart Notifications**: Notifies you precisely when effective study blocks begin.
- **Interactive UI**: A large Pause/Resume button sits directly on the dashboard.

## Installation

1. Clone or download this repository to your local machine.
2. Navigate to the project directory in your terminal:
   ```bash
   cd ~/Downloads/conky-study-dashboard-final
   ```
3. Run the interactive installer:
   ```bash
   ./install.sh
   ```
   *The installer will automatically set up a Python Virtual Environment (`.venv`), install `PyQt5`, and copy the files to `~/.config/conky-study/`. During the installation, you will be prompted to create an autostart desktop entry (type `y` or `n`).*

## Running Locally for Development
If you want to modify the code and test it locally without fully installing it to your system configuration folder, you can run:
```bash
./run.sh
```
*If you haven't installed dependencies yet, `run.sh` will prompt you to automatically build the virtual environment locally before launching the app.*

## Uninstallation
To completely remove the app, its configuration folders, and any autostart desktop entries, simply run:
```bash
./uninstall.sh
```
*(This script will also terminate any legacy Conky instances if you were using an older version of this dashboard).*

## Stop
```bash
pkill -f dashboard_app.py
```