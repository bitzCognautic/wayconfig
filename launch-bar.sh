#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

pkill waybar 2>/dev/null || true
eww --config "$ROOT/eww" kill 2>/dev/null || true
pkill -f "$ROOT/eww/scripts/visibility-watch.sh" 2>/dev/null || true

bash -lc '
  sleep 0.3
  eww --config "'"$ROOT"'/eww" daemon >/tmp/eww.log 2>&1 || true

  # On relogin, eww can take a moment before it accepts open requests.
  for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
    if eww --config "'"$ROOT"'/eww" open workspace_bar >/tmp/eww.log 2>&1; then
      exit 0
    fi
    sleep 0.3
  done
' >/tmp/eww-launch.log 2>&1 &

bash -lc '
  sleep 1.2
  "'"$ROOT"'/eww/scripts/visibility-watch.sh"
' >/tmp/eww-visibility.log 2>&1 &

sleep 1.0
waybar -c "$ROOT/waybar/config.jsonc" -s "$ROOT/waybar/style.css" >/tmp/waybar.log 2>&1 &

exit 0
