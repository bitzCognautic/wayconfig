#!/usr/bin/env bash

set -euo pipefail

mode="${1:-fullscreen}"
out_dir="${HOME}/Videos/Recordings"
mkdir -p "$out_dir"
file="${out_dir}/$(date +%Y-%m-%d_%H-%M-%S)_recording.mp4"

if pgrep -x wf-recorder >/dev/null 2>&1; then
  notify-send -a wayconfig "Screen recording" "wf-recorder is already running"
  exit 0
fi

audio_source=""
default_sink="$(pactl get-default-sink 2>/dev/null || true)"
if [[ -n "$default_sink" ]]; then
  monitor_source="${default_sink}.monitor"
  if pactl list sources short 2>/dev/null | awk '{print $2}' | grep -qx "$monitor_source"; then
    audio_source="$monitor_source"
  fi
fi

cmd=(wf-recorder -f "$file" -a)
if [[ -n "$audio_source" ]]; then
  cmd+=("--audio=$audio_source")
fi

if [[ "$mode" == "region" ]]; then
  geometry="$(slurp 2>/dev/null || true)"
  [[ -n "$geometry" ]] || exit 0
  cmd+=(-g "$geometry")
fi

("${cmd[@]}" >/dev/null 2>&1 & disown)
notify-send -a wayconfig "Screen recording" "Started ${mode} recording to ${file##*/}"
