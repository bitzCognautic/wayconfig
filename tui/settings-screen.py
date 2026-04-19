#!/usr/bin/env python3

import curses
import json
import re
import subprocess
from pathlib import Path


CONFIG_HOME = Path.home() / ".config"
WAYBAR_CONFIG = CONFIG_HOME / "waybar" / "config.jsonc"
EWW_YUCK = CONFIG_HOME / "eww" / "eww.yuck"
LAUNCH_BAR = CONFIG_HOME / "launch-bar.sh"


def read_bar_state() -> tuple[str, int]:
    with WAYBAR_CONFIG.open() as f:
        data = json.load(f)
    return data.get("position", "top"), int(data.get("height", 28))


def write_bar_state(position: str, height: int) -> None:
    with WAYBAR_CONFIG.open() as f:
        data = json.load(f)
    data["position"] = position
    data["height"] = height
    with WAYBAR_CONFIG.open("w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    text = EWW_YUCK.read_text()
    anchor = "top left" if position == "top" else "bottom left"
    y_value = f"-{height}px" if position == "top" else "0px"
    text = re.sub(r':y "[^"]+"', f':y "{y_value}"', text, count=1)
    text = re.sub(r':height "[^"]+"', f':height "{height}px"', text, count=1)
    text = re.sub(r':anchor "[^"]+"', f':anchor "{anchor}"', text, count=1)
    EWW_YUCK.write_text(text)


def restart_bar() -> None:
    subprocess.Popen([str(LAUNCH_BAR)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def run_app(stdscr: "curses._CursesWindow") -> None:
    curses.curs_set(0)
    stdscr.keypad(True)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, -1)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_CYAN, -1)

    actions = [
        "Bar Position: Top",
        "Bar Position: Bottom",
        "Bar Height: 28",
        "Bar Height: 34",
        "Apply And Restart Bar",
        "Quit",
    ]
    selected = 0

    while True:
        position, height = read_bar_state()
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        title = "Waybar Settings"
        stdscr.addnstr(1, 2, title, w - 4, curses.color_pair(3) | curses.A_BOLD)
        stdscr.addnstr(3, 2, f"Current position: {position}", w - 4, curses.color_pair(1))
        stdscr.addnstr(4, 2, f"Current height: {height}", w - 4, curses.color_pair(1))

        for idx, label in enumerate(actions):
            row = 6 + idx
            style = curses.color_pair(2) if idx == selected else curses.color_pair(1)
            stdscr.addnstr(row, 4, label, w - 8, style)

        stdscr.addnstr(h - 2, 2, "[j/k] move  [Enter] select  [q/Esc] quit", w - 4, curses.color_pair(1))
        stdscr.refresh()

        key = stdscr.getch()
        if key in (27, ord("q")):
            return
        if key in (curses.KEY_UP, ord("k")):
            selected = max(0, selected - 1)
        elif key in (curses.KEY_DOWN, ord("j")):
            selected = min(len(actions) - 1, selected + 1)
        elif key in (10, 13, curses.KEY_ENTER, ord(" ")):
            choice = actions[selected]
            if choice == "Bar Position: Top":
                write_bar_state("top", height)
            elif choice == "Bar Position: Bottom":
                write_bar_state("bottom", height)
            elif choice == "Bar Height: 28":
                write_bar_state(position, 28)
            elif choice == "Bar Height: 34":
                write_bar_state(position, 34)
            elif choice == "Apply And Restart Bar":
                restart_bar()
            elif choice == "Quit":
                return


if __name__ == "__main__":
    curses.wrapper(run_app)
