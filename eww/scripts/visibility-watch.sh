#!/usr/bin/env bash

set -euo pipefail

CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/eww"
visible=""

while true; do
  fullscreen="$(hyprctl -j activewindow 2>/dev/null | jq -r '.fullscreen // 0')"
  if [[ "$fullscreen" != "0" ]]; then
    if [[ "$visible" != "no" ]]; then
      eww --config "$CONFIG_DIR" close workspace_bar >/dev/null 2>&1 || true
      visible="no"
    fi
  else
    if [[ "$visible" != "yes" ]]; then
      eww --config "$CONFIG_DIR" open workspace_bar >/dev/null 2>&1 || true
      visible="yes"
    fi
  fi
  sleep 0.2
done
