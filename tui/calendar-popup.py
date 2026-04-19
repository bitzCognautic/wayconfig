#!/usr/bin/env python3

import calendar
import curses
from datetime import date


WEEKDAYS = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


def move_month(year: int, month: int, delta: int) -> tuple[int, int]:
    month += delta
    while month < 1:
        month += 12
        year -= 1
    while month > 12:
        month -= 12
        year += 1
    return year, month


def days_in_month(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]


def clamp_day(year: int, month: int, day: int) -> int:
    return max(1, min(day, days_in_month(year, month)))


def grid_position(year: int, month: int, selected_day: int) -> tuple[int, int]:
    weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(year, month)
    for row, week in enumerate(weeks):
        for col, day in enumerate(week):
            if day == selected_day:
                return row, col
    return 0, 0


def app(stdscr: "curses._CursesWindow") -> None:
    curses.curs_set(0)
    stdscr.keypad(True)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_WHITE, -1)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_YELLOW, -1)

    today = date.today()
    year = today.year
    month = today.month
    selected_day = today.day

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        month_title = date(year, month, 1).strftime("%B %Y")
        stdscr.addnstr(1, 2, month_title, max(1, w - 4), curses.color_pair(1) | curses.A_BOLD)
        stdscr.addnstr(2, 2, "[arrows] day/week  [h/l] month  [j/k] year  [t] today  [q] close", max(1, w - 4), curses.color_pair(2))

        start_x = 3
        start_y = 4
        cell_w = 3
        weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(year, month)

        for idx, header in enumerate(WEEKDAYS):
            if start_x + idx * cell_w < w - 1:
                stdscr.addnstr(start_y, start_x + idx * cell_w, header, max(1, cell_w - 1), curses.color_pair(4) | curses.A_BOLD)

        for row_idx, week in enumerate(weeks):
            for col_idx, day in enumerate(week):
                x = start_x + col_idx * cell_w
                y = start_y + 2 + row_idx
                if day == 0:
                    if y < h - 1 and x < w - 1:
                        stdscr.addnstr(y, x, ".", max(1, cell_w - 1), curses.color_pair(2))
                    continue

                style = curses.color_pair(2)
                if year == today.year and month == today.month and day == today.day:
                    style = curses.color_pair(4) | curses.A_BOLD
                if day == selected_day:
                    style = curses.color_pair(3) | curses.A_BOLD

                if y < h - 1 and x < w - 1:
                    stdscr.addnstr(y, x, f"{day:>2}", max(1, cell_w - 1), style)

        selected_label = f"Selected: {year:04d}-{month:02d}-{selected_day:02d}"
        if h >= 2:
            footer_row = min(h - 2, start_y + 2 + len(weeks) + 1)
            stdscr.addnstr(footer_row, 2, selected_label, max(1, w - 4), curses.color_pair(2))
        stdscr.refresh()

        key = stdscr.getch()
        if key in (27, ord("q")):
            return
        elif key == ord("t"):
            year = today.year
            month = today.month
            selected_day = today.day
        elif key == ord("h"):
            year, month = move_month(year, month, -1)
            selected_day = clamp_day(year, month, selected_day)
        elif key == ord("l"):
            year, month = move_month(year, month, 1)
            selected_day = clamp_day(year, month, selected_day)
        elif key == ord("k"):
            year -= 1
            selected_day = clamp_day(year, month, selected_day)
        elif key == ord("j"):
            year += 1
            selected_day = clamp_day(year, month, selected_day)
        elif key in (curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN):
            row, col = grid_position(year, month, selected_day)
            if key == curses.KEY_LEFT:
                col -= 1
            elif key == curses.KEY_RIGHT:
                col += 1
            elif key == curses.KEY_UP:
                row -= 1
            elif key == curses.KEY_DOWN:
                row += 1

            if col < 0:
                year, month = move_month(year, month, -1)
                selected_day = days_in_month(year, month)
                continue
            if col > 6:
                year, month = move_month(year, month, 1)
                selected_day = 1
                continue

            if row < 0:
                year, month = move_month(year, month, -1)
                selected_day = clamp_day(year, month, selected_day - 7)
                continue
            if row >= len(weeks):
                year, month = move_month(year, month, 1)
                selected_day = clamp_day(year, month, selected_day + 7 - days_in_month(*move_month(year, month, -1)))
                continue

            target = weeks[row][col]
            if target == 0:
                if key == curses.KEY_LEFT:
                    selected_day = max(1, selected_day - 1)
                elif key == curses.KEY_RIGHT:
                    selected_day = min(days_in_month(year, month), selected_day + 1)
                elif key == curses.KEY_UP:
                    selected_day = max(1, selected_day - 7)
                elif key == curses.KEY_DOWN:
                    selected_day = min(days_in_month(year, month), selected_day + 7)
            else:
                selected_day = target


if __name__ == "__main__":
    try:
        curses.wrapper(app)
    except Exception as exc:
        print(f"calendar-popup.py failed: {exc}")
        input("Press Enter to close...")
