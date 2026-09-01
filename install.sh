#!/usr/bin/env bash
set -e

sudo apt update
sudo apt install -y python3-venv libnotify-bin

echo "Setting up Python virtual environment..."
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install PyQt5

mkdir -p "$HOME/.config/conky-study"
cp "$(dirname "$0")/study_schedule.py" "$HOME/.config/conky-study/study_schedule.py"
cp "$(dirname "$0")/dashboard_app.py" "$HOME/.config/conky-study/dashboard_app.py"
cp "$(dirname "$0")/card.png" "$HOME/.config/conky-study/card.png"
# Also copy the venv directory so the app can run from the config folder
cp -r "$(dirname "$0")/.venv" "$HOME/.config/conky-study/.venv"
chmod +x "$HOME/.config/conky-study/"*.py

mkdir -p "$HOME/.config/autostart"
read -p "Do you want to create a desktop autostart entry so the dashboard launches on boot? (y/n): " create_desktop
case "$create_desktop" in
  y|Y )
    cat > "$HOME/.config/autostart/study-dashboard.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Study Dashboard
Comment=30-day study dashboard
Exec=$HOME/.config/conky-study/.venv/bin/python $HOME/.config/conky-study/dashboard_app.py
Terminal=false
X-GNOME-Autostart-enabled=true
EOF
    echo "Desktop entry created."
    ;;
  * )
    echo "Skipping desktop entry creation."
    rm -f "$HOME/.config/autostart/study-dashboard.desktop"
    ;;
esac

# Kill conky if it was running previously
pkill conky 2>/dev/null || true
# Kill old instances of the app
pkill -f dashboard_app.py 2>/dev/null || true
sleep 1

# Launch the app using the virtual environment
nohup "$HOME/.config/conky-study/.venv/bin/python" "$HOME/.config/conky-study/dashboard_app.py" >/tmp/study-dashboard.log 2>&1 &

echo "Started the new PyQt5 Study Dashboard App using virtual environment!"


# uninstall desktop ->  sudo apt remove -y conky-all
# rm -f ~/.config/autostart/conky-study.desktop ~/.config/conky-study/conky*.conf ~/.config/conky-study/toggle*.py ~/.config/conky-study/toggle*.sh ~/Downloads/conky-study-dashboard-final/conky*.conf ~/Downloads/conky-study-dashboard-final/toggle*.py ~/Downloads/conky-study-dashboard-final/toggle*.sh