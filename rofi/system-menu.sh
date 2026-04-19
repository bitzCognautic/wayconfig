#!/usr/bin/env bash

set -euo pipefail

CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/rofi/menu.rasi"
ICON_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/rofi/icons/external"

choice="$(
  {
    printf 'Wallpaper\0icon\x1f%s/image.svg\n' "$ICON_DIR"
    printf 'Settings\0icon\x1f%s/settings.svg\n' "$ICON_DIR"
    printf 'Hyprland Config\0icon\x1f%s/monitor.svg\n' "$ICON_DIR"
    printf 'Reload Hyprland\0icon\x1f%s/refresh-cw.svg\n' "$ICON_DIR"
    printf 'Restart Bar\0icon\x1f%s/menu.svg\n' "$ICON_DIR"
    printf 'Record Fullscreen\0icon\x1f%s/video.svg\n' "$ICON_DIR"
    printf 'Record Region\0icon\x1f%s/video.svg\n' "$ICON_DIR"
    printf 'Stop Recording\0icon\x1f%s/square.svg\n' "$ICON_DIR"
    printf 'Recordings Folder\0icon\x1f%s/folder.svg\n' "$ICON_DIR"
    printf 'Audio Mixer\0icon\x1f%s/volume-2.svg\n' "$ICON_DIR"
    printf 'Bluetooth\0icon\x1f%s/bluetooth.svg\n' "$ICON_DIR"
    printf 'Wi-Fi\0icon\x1f%s/wifi.svg\n' "$ICON_DIR"
    printf 'Power\0icon\x1f%s/power.svg\n' "$ICON_DIR"
  } | rofi -dmenu -i -p menu -show-icons -config "$CONFIG"
)"

case "${choice:-}" in
  "Wallpaper")
    exec "${XDG_CONFIG_HOME:-$HOME/.config}/rofi/wallpaper-menu.sh"
    ;;
  "Settings")
    exec kitty --title com.omarchy.settings python3 "${XDG_CONFIG_HOME:-$HOME/.config}/tui/settings-screen.py"
    ;;
  "Hyprland Config")
    exec nautilus "${XDG_CONFIG_HOME:-$HOME/.config}/hypr"
    ;;
  "Reload Hyprland")
    exec hyprctl reload
    ;;
  "Restart Bar")
    exec "${XDG_CONFIG_HOME:-$HOME/.config}/launch-bar.sh"
    ;;
  "Record Fullscreen")
    exec "${XDG_CONFIG_HOME:-$HOME/.config}/rofi/start-recording.sh" fullscreen
    ;;
  "Record Region")
    exec "${XDG_CONFIG_HOME:-$HOME/.config}/rofi/start-recording.sh" region
    ;;
  "Stop Recording")
    exec "${XDG_CONFIG_HOME:-$HOME/.config}/rofi/stop-recording.sh"
    ;;
  "Recordings Folder")
    exec nautilus "$HOME/Videos/Recordings"
    ;;
  "Audio Mixer")
    exec pavucontrol
    ;;
  "Bluetooth")
    exec kitty --title com.omarchy.bluepala python3 "${XDG_CONFIG_HOME:-$HOME/.config}/tui/esc-close-wrapper.py" bluepala
    ;;
  "Wi-Fi")
    exec kitty --title com.omarchy.netpala python3 "${XDG_CONFIG_HOME:-$HOME/.config}/tui/esc-close-wrapper.py" netpala
    ;;
  "Power")
    exec kitty --title com.omarchy.powermenu "${XDG_CONFIG_HOME:-$HOME/.config}/tui/launch-power-menu.sh"
    ;;
esac
