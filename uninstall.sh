#!/usr/bin/env bash
set -e

echo "Uninstalling Study Dashboard..."

# Stop any running instances of the app or old conky processes
pkill -f dashboard_app.py 2>/dev/null || true
pkill conky 2>/dev/null || true

# Remove autostart entries
rm -f "$HOME/.config/autostart/study-dashboard.desktop"
rm -f "$HOME/.config/autostart/conky-study.desktop"

# Remove the configuration directory (which contains the virtual environment and scripts)
rm -rf "$HOME/.config/conky-study"

echo "Uninstallation complete!"
