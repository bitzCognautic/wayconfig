#!/usr/bin/env bash

set -euo pipefail

active="$(hyprctl -j activeworkspace 2>/dev/null | jq -r '.id // 1')"

if ! [[ "$active" =~ ^[0-9]+$ ]]; then
  active=1
fi

start=$(( ((active - 1) / 5) * 5 + 1 ))

end=$((start + 4))

printf '(box :class "workspace-strip" :spacing 8'

for workspace in $(seq "$start" "$end"); do
  if (( workspace == active )); then
    label="[$workspace]"
    class="workspace-button active"
  else
    label="$workspace"
    class="workspace-button"
  fi

  printf ' (button :class "%s" :onclick "hyprctl dispatch workspace %s" "%s")' \
    "$class" "$workspace" "$label"
done

printf ')'
