#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"

link_path() {
  local src="$1"
  local dest="$2"

  mkdir -p "$(dirname "$dest")"

  if [[ -L "$dest" ]]; then
    local current
    current="$(readlink "$dest")"
    if [[ "$current" == "$src" ]]; then
      echo "ok    $dest -> $src"
      return 0
    fi
    rm -f "$dest"
  elif [[ -e "$dest" ]]; then
    echo "skip  $dest exists and is not a symlink"
    return 0
  fi

  ln -s "$src" "$dest"
  echo "link  $dest -> $src"
}

link_dir_contents() {
  local src_dir="$1"
  local dest_dir="$2"

  mkdir -p "$dest_dir"

  local entry
  for entry in "$src_dir"/*; do
    [[ -e "$entry" ]] || continue
    link_path "$entry" "$dest_dir/$(basename "$entry")"
  done
}

dirs=(
  eww
  fastfetch
  fish
  gtk-3.0
  gtk-4.0
  hypr
  rofi
  swaync
  tui
  waybar
)

for dir in "${dirs[@]}"; do
  if [[ -e "$CONFIG_HOME/$dir" && ! -L "$CONFIG_HOME/$dir" ]]; then
    echo "merge $CONFIG_HOME/$dir exists as a real directory"
    link_dir_contents "$ROOT/$dir" "$CONFIG_HOME/$dir"
  else
    link_path "$ROOT/$dir" "$CONFIG_HOME/$dir"
  fi
done

link_path "$ROOT/launch-bar.sh" "$CONFIG_HOME/launch-bar.sh"
link_path "$ROOT/install-waybar-deps.sh" "$CONFIG_HOME/install-waybar-deps.sh"

echo
echo "Done. Reload apps as needed:"
echo "  hyprctl reload"
echo "  $CONFIG_HOME/launch-bar.sh"
