#!/usr/bin/env bash
set -e

sudo apt update
sudo apt install -y conky-all libnotify-bin

mkdir -p "$HOME/.config/conky-study"
cp "$(dirname "$0")/conky_large.conf" "$HOME/.config/conky-study/conky_large.conf"
cp "$(dirname "$0")/conky_small.conf" "$HOME/.config/conky-study/conky_small.conf"
# Initialize with large by default
cp "$HOME/.config/conky-study/conky_large.conf" "$HOME/.config/conky-study/conky.conf"
cp "$(dirname "$0")/study_schedule.py" "$HOME/.config/conky-study/study_schedule.py"
cp "$(dirname "$0")/toggle_pause.py" "$HOME/.config/conky-study/toggle_pause.py"
cp "$(dirname "$0")/toggle_size.sh" "$HOME/.config/conky-study/toggle_size.sh"
cp "$(dirname "$0")/card.png" "$HOME/.config/conky-study/card.png"
chmod +x "$HOME/.config/conky-study/"*.py
chmod +x "$HOME/.config/conky-study/"*.sh

mkdir -p "$HOME/.config/autostart"
cat > "$HOME/.config/autostart/conky-study.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Conky Study Dashboard
Comment=30-day study dashboard
Exec=conky -c $HOME/.config/conky-study/conky.conf
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

pkill conky 2>/dev/null || true
sleep 1
nohup conky -c "$HOME/.config/conky-study/conky.conf" >/tmp/conky-study.log 2>&1 &

echo "Started the final translucent-card dashboard."
