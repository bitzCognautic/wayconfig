#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

pkill waybar 2>/dev/null || true
eww --config "$ROOT/eww" kill 2>/dev/null || true

waybar -c "$ROOT/waybar/config.jsonc" -s "$ROOT/waybar/style.css" &
sleep 0.3

eww --config "$ROOT/eww" daemon
eww --config "$ROOT/eww" open workspace_bar

wait
