#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

pkill waybar 2>/dev/null || true
eww --config "$ROOT/eww" kill 2>/dev/null || true

waybar -c "$ROOT/waybar/config.jsonc" -s "$ROOT/waybar/style.css" &
sleep 0.3

eww --config "$ROOT/eww" daemon >/dev/null 2>&1 || true

# On relogin, eww can take a moment before it accepts open requests.
for _ in 1 2 3 4 5 6 7 8 9 10; do
  if eww --config "$ROOT/eww" open workspace_bar >/dev/null 2>&1; then
    break
  fi
  sleep 0.2
done

wait
