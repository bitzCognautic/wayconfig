#!/usr/bin/env python3

import curses
import subprocess
import time
from pathlib import Path


TITLE = "Power"
REFRESH_SECONDS = 1.5


def safe_output(cmd: list[str]) -> str:
    try:
        return subprocess.run(cmd, check=False, capture_output=True, text=True).stdout.strip()
    except FileNotFoundError:
        return ""


def run_shell(cmd: str) -> None:
    subprocess.Popen(["bash", "-lc", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def battery_details() -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    devices = safe_output(["upower", "-e"]).splitlines()
    battery = next((line.strip() for line in devices if "battery" in line.lower()), "")
    if battery:
        info = safe_output(["upower", "-i", battery]).splitlines()
        for raw in info:
            line = raw.strip()
            if line.startswith("percentage:"):
                items.append(("Battery", line.split(":", 1)[1].strip()))
            elif line.startswith("state:"):
                items.append(("State", line.split(":", 1)[1].strip()))
            elif line.startswith("time to empty:") or line.startswith("time to full:"):
                items.append(("Time", line.split(":", 1)[1].strip()))
    profile = safe_output(["powerprofilesctl", "get"])
    if profile:
        items.append(("Profile", profile))
    governor_file = Path("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor")
    if governor_file.exists():
        try:
            items.append(("Governor", governor_file.read_text().strip()))
        except OSError:
            pass
    if not items:
        items.append(("Power", "No battery details available"))
    return items


def available_profiles() -> list[str]:
    output = safe_output(["powerprofilesctl", "list"])
    profiles: list[str] = []
    for line in output.splitlines():
        cleaned = line.replace("*", "").strip()
        if cleaned:
            profiles.append(cleaned.split(":", 1)[0].strip())
    return profiles or ["power-saver", "balanced", "performance"]


def current_profile() -> str:
    return safe_output(["powerprofilesctl", "get"]) or "unknown"


def available_governors() -> list[str]:
    governor_file = Path("/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors")
    if governor_file.exists():
        try:
            return [item for item in governor_file.read_text().strip().split() if item]
        except OSError:
            pass
    return ["powersave", "schedutil", "performance"]


def current_governor() -> str:
    governor_file = Path("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor")
    if governor_file.exists():
        try:
            return governor_file.read_text().strip()
        except OSError:
            return "unknown"
    return "unknown"


def draw_box(stdscr: "curses._CursesWindow", y: int, x: int, h: int, w: int, title: str) -> None:
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(y, x, "┌" + "─" * (w - 2) + "┐")
    for row in range(y + 1, y + h - 1):
        stdscr.addstr(row, x, "│")
        stdscr.addstr(row, x + w - 1, "│")
    stdscr.addstr(y + h - 1, x, "└" + "─" * (w - 2) + "┘")
    stdscr.addstr(y, x + 2, f" {title} ", curses.color_pair(1) | curses.A_BOLD)
    stdscr.attroff(curses.color_pair(1))


def apply_action(action: str) -> None:
    power_actions = {
        "Lock": "loginctl lock-session",
        "Logout": "hyprctl dispatch exit",
        "Suspend": "systemctl suspend",
        "Reboot": "systemctl reboot",
        "Poweroff": "systemctl poweroff",
    }
    if action in power_actions:
        run_shell(power_actions[action])
        return
    if action.startswith("Profile: "):
        profile = action.split(": ", 1)[1]
        run_shell(f"powerprofilesctl set {profile}")
        return
    if action.startswith("Governor: "):
        governor = action.split(": ", 1)[1]
        run_shell(f"pkexec cpupower frequency-set -g {governor}")


def build_actions() -> list[str]:
    actions = ["Lock", "Logout", "Suspend", "Reboot", "Poweroff"]
    actions.extend([f"Profile: {profile}" for profile in available_profiles()])
    actions.extend([f"Governor: {governor}" for governor in available_governors()])
    return actions


def app(stdscr: "curses._CursesWindow") -> None:
    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.timeout(120)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, -1)
    curses.init_pair(2, curses.COLOR_WHITE, -1)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_CYAN, -1)

    selected = 0
    last_refresh = 0.0
    details: list[tuple[str, str]] = []
    actions: list[str] = []

    while True:
        now = time.time()
        if now - last_refresh >= REFRESH_SECONDS:
            details = battery_details()
            actions = build_actions()
            selected = min(selected, max(0, len(actions) - 1))
            last_refresh = now

        stdscr.erase()
        h, w = stdscr.getmaxyx()
        draw_box(stdscr, 1, 1, h - 2, w - 2, TITLE)

        row = 3
        for key, value in details:
            stdscr.addnstr(row, 4, key, 12, curses.color_pair(4) | curses.A_BOLD)
            stdscr.addnstr(row, 18, value, w - 22, curses.color_pair(2))
            row += 1

        row += 1
        stdscr.addnstr(row, 4, "Actions", 20, curses.color_pair(1) | curses.A_BOLD)
        row += 2

        current_profile_name = current_profile()
        current_governor_name = current_governor()
        visible_rows = max(1, h - row - 3)
        offset = min(max(0, selected - visible_rows + 1), max(0, len(actions) - visible_rows))

        for idx, label in enumerate(actions[offset: offset + visible_rows]):
            absolute_idx = offset + idx
            style = curses.color_pair(3) if absolute_idx == selected else curses.color_pair(2)
            suffix = ""
            if label == f"Profile: {current_profile_name}" or label == f"Governor: {current_governor_name}":
                suffix = "  *"
            stdscr.addnstr(row + idx, 6, label + suffix, w - 12, style | curses.A_BOLD)

        stdscr.addnstr(h - 2, 4, "[j/k] move  [Enter] select  [Esc/q] close", w - 8, curses.color_pair(2))
        stdscr.refresh()

        key = stdscr.getch()
        if key in (-1,):
            continue
        if key in (27, ord("q")):
            return
        if key in (curses.KEY_UP, ord("k")):
            selected = max(0, selected - 1)
        elif key in (curses.KEY_DOWN, ord("j")):
            selected = min(len(actions) - 1, selected + 1)
        elif key in (10, 13, curses.KEY_ENTER, ord(" ")):
            if actions:
                apply_action(actions[selected])
                if actions[selected].startswith(("Lock", "Logout", "Suspend", "Reboot", "Poweroff")):
                    return
                last_refresh = 0.0


if __name__ == "__main__":
    curses.wrapper(app)
