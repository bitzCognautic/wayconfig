#!/usr/bin/env bash

set -euo pipefail

CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/rofi/menu.rasi"
WALLPAPER_DIR="${HOME}/Pictures/Wallpapers"

if [[ ! -d "$WALLPAPER_DIR" ]]; then
  exit 0
fi

mapfile -d '' files < <(
  find "$WALLPAPER_DIR" -maxdepth 1 -type f \
    \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' -o -iname '*.bmp' -o -iname '*.gif' -o -iname '*.mp4' -o -iname '*.webm' -o -iname '*.mkv' -o -iname '*.mov' \) \
    -print0 | sort -z
)

if [[ "${#files[@]}" -eq 0 ]]; then
  exit 0
fi

display=()
for file in "${files[@]}"; do
  display+=("$(basename "$file")")
done

choice="$(
  for file in "${files[@]}"; do
    printf '%s\0icon\x1fthumbnail://%s\n' "$(basename "$file")" "$file"
  done | rofi -dmenu -i -p wallpaper -show-icons -config "$CONFIG"
)"

[[ -n "${choice:-}" ]] || exit 0

selected=""
for file in "${files[@]}"; do
  if [[ "$(basename "$file")" == "$choice" ]]; then
    selected="$file"
    break
  fi
done

[[ -n "$selected" ]] || exit 0

if command -v eink-wallpaper >/dev/null 2>&1; then
  exec eink-wallpaper "$selected"
elif [[ -x "$HOME/.local/bin/eink-wallpaper" ]]; then
  exec "$HOME/.local/bin/eink-wallpaper" "$selected"
fi
