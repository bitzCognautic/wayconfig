#!/usr/bin/env bash

set -euo pipefail

if pkill -INT -x wf-recorder >/dev/null 2>&1; then
  notify-send -a wayconfig "Screen recording" "Stopped recording"
fi
