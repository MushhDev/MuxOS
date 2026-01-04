#!/bin/bash
# MuxOS Velocity Theme Installer

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🎨 Installing MuxOS Velocity Theme..."

# Install GTK theme
mkdir -p /usr/share/themes/MuxOS-Velocity
cp -r "$PROJECT_ROOT/desktop/themes/MuxOS-Velocity/"* /usr/share/themes/MuxOS-Velocity/

# Install icons (Papirus)
if ! [ -d /usr/share/icons/Papirus ]; then
    echo "Installing Papirus icon theme..."
    apt-get install -y papirus-icon-theme || {
        wget -qO- https://git.io/papirus-icon-theme-install | sh
    }
fi

# Install fonts
echo "Installing fonts..."
apt-get install -y fonts-inter fonts-jetbrains-mono 2>/dev/null || {
    mkdir -p /usr/share/fonts/truetype/inter /usr/share/fonts/truetype/jetbrains-mono
    # Download fonts if not available via apt
    echo "Please install Inter and JetBrains Mono fonts manually"
}

# Install Openbox theme
mkdir -p /usr/share/themes/MuxOS-Velocity/openbox-3
cp "$PROJECT_ROOT/desktop/themes/MuxOS-Velocity/openbox-3/themerc" /usr/share/themes/MuxOS-Velocity/openbox-3/

# Install compositor config
mkdir -p /etc/xdg/picom
cp "$PROJECT_ROOT/desktop/picom/picom-velocity.conf" /etc/xdg/picom/

# Install panel config
mkdir -p /etc/xdg/tint2
cp "$PROJECT_ROOT/desktop/tint2/tint2rc-velocity" /etc/xdg/tint2/

# Install notification config
mkdir -p /etc/xdg/dunst
cp "$PROJECT_ROOT/desktop/dunst/dunstrc" /etc/xdg/dunst/

# Install rofi theme
mkdir -p /usr/share/rofi/themes
cp "$PROJECT_ROOT/desktop/rofi/muxos-velocity.rasi" /usr/share/rofi/themes/

# Install LightDM config
cp "$PROJECT_ROOT/desktop/lightdm/lightdm-gtk-greeter-velocity.conf" /etc/lightdm/lightdm-gtk-greeter.conf

# Install terminal config
mkdir -p /etc/xdg/xfce4/terminal
cp "$PROJECT_ROOT/desktop/xfce4-terminal/terminalrc" /etc/xdg/xfce4/terminal/

# Generate wallpapers
echo "Generating wallpapers..."
python3 "$PROJECT_ROOT/scripts/generate-wallpapers.py" || {
    echo "Could not generate wallpapers (pycairo may not be installed)"
    mkdir -p /usr/share/backgrounds
}

# Copy logo
mkdir -p /usr/share/muxos/img
cp "$PROJECT_ROOT/img/muximg.png" /usr/share/muxos/img/

# Install theme editor
cp "$PROJECT_ROOT/apps/settings/muxos-theme-editor.py" /usr/bin/muxos-theme-editor
chmod +x /usr/bin/muxos-theme-editor
cp "$PROJECT_ROOT/apps/settings/muxos-theme-editor.desktop" /usr/share/applications/

# Set GTK settings for all users
mkdir -p /etc/gtk-3.0
cp "$PROJECT_ROOT/config/gtk-3.0-settings.ini" /etc/gtk-3.0/settings.ini

# Update font cache
fc-cache -f

echo "✅ MuxOS Velocity Theme installed successfully!"
echo ""
echo "To apply the theme, log out and log back in, or run:"
echo "  openbox --reconfigure"
echo "  pkill picom && picom --config /etc/xdg/picom/picom-velocity.conf &"
echo "  pkill tint2 && tint2 -c /etc/xdg/tint2/tint2rc-velocity &"
