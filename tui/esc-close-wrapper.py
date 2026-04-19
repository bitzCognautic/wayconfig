#!/usr/bin/env python3

import fcntl
import os
import pty
import select
import signal
import subprocess
import sys
import termios
import tty
import struct


def get_winsize(fd: int) -> bytes:
    return fcntl.ioctl(fd, termios.TIOCGWINSZ, b"\x00" * 8)


def set_winsize(fd: int, winsize: bytes) -> None:
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: esc-close-wrapper.py <command> [args...]", file=sys.stderr)
        return 1

    old_attrs = termios.tcgetattr(sys.stdin.fileno())
    master_fd, slave_fd = pty.openpty()

    try:
        winsize = get_winsize(sys.stdin.fileno())
        set_winsize(slave_fd, winsize)
        tty.setraw(sys.stdin.fileno())
        proc = subprocess.Popen(
            sys.argv[1:],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            preexec_fn=os.setsid,
            close_fds=True,
        )
        os.close(slave_fd)

        def handle_winch(_signum: int, _frame: object) -> None:
            try:
                new_size = get_winsize(sys.stdin.fileno())
                set_winsize(master_fd, new_size)
                os.killpg(proc.pid, signal.SIGWINCH)
            except OSError:
                pass

        signal.signal(signal.SIGWINCH, handle_winch)

        while True:
            if proc.poll() is not None:
                break

            read_fds, _, _ = select.select([sys.stdin.fileno(), master_fd], [], [])

            if sys.stdin.fileno() in read_fds:
                data = os.read(sys.stdin.fileno(), 1024)
                if not data:
                    os.killpg(proc.pid, signal.SIGHUP)
                    break
                if data == b"\x1b":
                    os.write(master_fd, b"q")
                else:
                    os.write(master_fd, data)

            if master_fd in read_fds:
                try:
                    output = os.read(master_fd, 4096)
                except OSError:
                    break
                if not output:
                    break
                os.write(sys.stdout.fileno(), output)

        return proc.wait()
    finally:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_attrs)
        try:
            os.close(master_fd)
        except OSError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
