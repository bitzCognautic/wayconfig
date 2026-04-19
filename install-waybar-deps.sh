#!/usr/bin/env bash

set -euo pipefail

if ! command -v pacman >/dev/null 2>&1; then
  echo "This installer currently supports Arch Linux / pacman only."
  exit 1
fi

packages=(
  bottom
  waybar
  hyprland
  bluez
  bluez-utils
  brightnessctl
  cpupower
  gtk3
  gtk-layer-shell
  jq
  libdbusmenu-gtk3
  network-manager-applet
  networkmanager
  nautilus
  ffmpegthumbnailer
  gdk-pixbuf2
  grim
  libnotify
  pamixer
  pavucontrol
  power-profiles-daemon
  slurp
  rofi
  python
  upower
  wf-recorder
  ttf-jetbrains-mono-nerd
)

echo "Installing Waybar dependencies:"
printf ' - %s\n' "${packages[@]}"

sudo pacman -S --needed "${packages[@]}"

if ! command -v eww >/dev/null 2>&1; then
  if command -v paru >/dev/null 2>&1; then
    paru -S --needed eww
  elif command -v yay >/dev/null 2>&1; then
    yay -S --needed eww
  else
    echo
    echo "eww is not installed."
    echo "Install an AUR helper like paru/yay, then run:"
    echo "  paru -S eww"
    echo "or:"
    echo "  yay -S eww"
  fi
fi

install_aur_or_build() {
  local pkg="$1"
  local repo="$2"

  if command -v "$pkg" >/dev/null 2>&1; then
    return 0
  fi

  if command -v paru >/dev/null 2>&1; then
    paru -S --needed "$pkg"
    return 0
  fi

  if command -v yay >/dev/null 2>&1; then
    yay -S --needed "$pkg"
    return 0
  fi

  if ! command -v go >/dev/null 2>&1; then
    echo
    echo "$pkg is not installed."
    echo "Install an AUR helper like paru/yay, or install Go and re-run this script."
    return 1
  fi

  echo
  echo "Building $pkg from source..."
  tmpdir="$(mktemp -d)"
  git clone "$repo" "$tmpdir/$pkg"
  (
    cd "$tmpdir/$pkg"
    go build
    install -Dm755 "./$pkg" "$HOME/.local/bin/$pkg"
  )
  rm -rf "$tmpdir"
}

install_aur_or_build bluepala https://github.com/joel-sgc/bluepala.git
install_aur_or_build netpala https://github.com/joel-sgc/netpala.git

echo
echo "Enable required services if they are not already running:"
echo "  sudo systemctl enable --now bluetooth.service"
echo "  sudo systemctl enable --now NetworkManager.service"
