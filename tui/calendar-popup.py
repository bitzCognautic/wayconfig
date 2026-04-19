#!/usr/bin/env python3

import calendar
import curses
from datetime import date


def month_days(year: int, month: int) -> list[list[int]]:
    cal = calendar.Calendar(firstweekday=0)
    return cal.monthdayscalendar(year, month)


def days_in_month(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]


def move_month(year: int, month: int, delta: int) -> tuple[int, int]:
    month += delta
    while month < 1:
        month += 12
        year -= 1
    while month > 12:
        month -= 12
        year += 1
    return year, month


def clamp_day(year: int, month: int, day: int) -> int:
    return max(1, min(day, days_in_month(year, month)))


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

        title = date(year, month, 1).strftime("%B %Y")
        stdscr.addnstr(1, 2, title, w - 4, curses.color_pair(1) | curses.A_BOLD)
        stdscr.addnstr(2, 2, "[arrows] move  [h/l] month  [j/k] year  [t] today  [q/Esc] close", w - 4, curses.color_pair(2))

        headers = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        start_x = 6
        start_y = 5
        cell_w = 5

        for idx, header in enumerate(headers):
            stdscr.addnstr(start_y, start_x + idx * cell_w, header, cell_w - 1, curses.color_pair(4) | curses.A_BOLD)

        grid = month_days(year, month)
        for row_idx, week in enumerate(grid):
            for col_idx, day in enumerate(week):
                x = start_x + col_idx * cell_w
                y = start_y + 2 + row_idx
                if day == 0:
                    continue

                style = curses.color_pair(2)
                if year == today.year and month == today.month and day == today.day:
                    style = curses.color_pair(4) | curses.A_BOLD
                if day == selected_day:
                    style = curses.color_pair(3) | curses.A_BOLD
                stdscr.addnstr(y, x, f"{day:>2}", cell_w - 1, style)

        footer = f"Selected: {year:04d}-{month:02d}-{selected_day:02d}"
        stdscr.addnstr(h - 2, 2, footer, w - 4, curses.color_pair(2))
        stdscr.refresh()

        key = stdscr.getch()
        if key in (27, ord("q")):
            return
        if key in (curses.KEY_LEFT,):
            selected_day -= 1
            if selected_day < 1:
                year, month = move_month(year, month, -1)
                selected_day = days_in_month(year, month)
        elif key in (curses.KEY_RIGHT,):
            selected_day += 1
            dim = days_in_month(year, month)
            if selected_day > dim:
                year, month = move_month(year, month, 1)
                selected_day = 1
        elif key in (curses.KEY_UP,):
            selected_day -= 7
            if selected_day < 1:
                year, month = move_month(year, month, -1)
                selected_day = clamp_day(year, month, days_in_month(year, month) + selected_day)
        elif key in (curses.KEY_DOWN,):
            selected_day += 7
            dim = days_in_month(year, month)
            if selected_day > dim:
                overflow = selected_day - dim
                year, month = move_month(year, month, 1)
                selected_day = clamp_day(year, month, overflow)
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
        elif key == ord("t"):
            year = today.year
            month = today.month
            selected_day = today.day


if __name__ == "__main__":
    curses.wrapper(app)
