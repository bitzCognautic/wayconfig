#!/usr/bin/env python3

import curses
import subprocess
from typing import List, Tuple


TITLE = "Power"


def run(cmd: str) -> None:
    subprocess.run(["bash", "-lc", cmd], check=False)


def safe_output(cmd: list[str]) -> str:
    try:
        return subprocess.run(cmd, check=False, capture_output=True, text=True).stdout.strip()
    except FileNotFoundError:
        return ""


def battery_info() -> List[Tuple[str, str]]:
    items: List[Tuple[str, str]] = []
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
    if not items:
        items.append(("Power", "No battery details available"))
    return items


def draw_box(stdscr: "curses._CursesWindow", y: int, x: int, h: int, w: int, title: str) -> None:
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(y, x, "┌" + "─" * (w - 2) + "┐")
    for row in range(y + 1, y + h - 1):
        stdscr.addstr(row, x, "│")
        stdscr.addstr(row, x + w - 1, "│")
    stdscr.addstr(y + h - 1, x, "└" + "─" * (w - 2) + "┘")
    stdscr.addstr(y, x + 2, f" {title} ", curses.color_pair(1) | curses.A_BOLD)
    stdscr.attroff(curses.color_pair(1))


def app(stdscr: "curses._CursesWindow") -> None:
    curses.curs_set(0)
    stdscr.keypad(True)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_WHITE, -1)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_YELLOW, -1)

    actions = [
        ("Lock", "loginctl lock-session"),
        ("Logout", "hyprctl dispatch exit"),
        ("Suspend", "systemctl suspend"),
        ("Reboot", "systemctl reboot"),
        ("Poweroff", "systemctl poweroff"),
    ]
    selected = 0

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        draw_box(stdscr, 1, 1, h - 2, w - 2, TITLE)
        details = battery_info()

        row = 3
        for key, value in details:
            stdscr.addnstr(row, 4, key, 12, curses.color_pair(4) | curses.A_BOLD)
            stdscr.addnstr(row, 18, value, w - 22, curses.color_pair(2))
            row += 1

        row += 1
        stdscr.addnstr(row, 4, "Actions", 20, curses.color_pair(1) | curses.A_BOLD)
        row += 2
        for idx, (label, _) in enumerate(actions):
            style = curses.color_pair(3) if idx == selected else curses.color_pair(2)
            stdscr.addnstr(row + idx, 6, label, w - 12, style | curses.A_BOLD)

        stdscr.addnstr(h - 2, 4, "[j/k] move  [Enter] select  [Esc/q] close", w - 8, curses.color_pair(2))
        stdscr.refresh()

        key = stdscr.getch()
        if key in (27, ord("q")):
            return
        if key in (curses.KEY_UP, ord("k")):
            selected = max(0, selected - 1)
        elif key in (curses.KEY_DOWN, ord("j")):
            selected = min(len(actions) - 1, selected + 1)
        elif key in (10, 13, curses.KEY_ENTER, ord(" ")):
            run(actions[selected][1])
            return


if __name__ == "__main__":
    curses.wrapper(app)
