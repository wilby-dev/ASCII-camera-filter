#!/usr/bin/env python3
"""
ascii-cam — live webcam feed rendered as ASCII art in your terminal.

Usage:
    python ascii_cam.py                  # grayscale ASCII, default size
    python ascii_cam.py --color          # ANSI truecolor ASCII
    python ascii_cam.py --width 120      # wider render (height auto-scaled)
    python ascii_cam.py --invert         # dark-on-light instead of light-on-dark
    python ascii_cam.py --camera 1       # use a different camera index
    python ascii_cam.py --mirror off     # disable the default mirror flip

Press Ctrl+C to quit.
"""

import argparse
import os
import shutil
import sys
import time

import cv2

from converter import frame_to_ascii_grid, frame_to_ascii_grid_color, ASCII_RAMP

RESET = "\033[0m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CLEAR_HOME = "\033[H"  # move cursor to top-left (cheaper than clearing + reprint)


def terminal_size(default_cols=80):
    size = shutil.get_terminal_size(fallback=(default_cols, 24))
    return size.columns, size.lines


def compute_grid_size(frame_w, frame_h, target_cols):
    # Terminal character cells are roughly twice as tall as they are wide,
    # so we halve the row count to keep the aspect ratio looking right.
    aspect = frame_h / frame_w
    cols = target_cols
    rows = max(1, int(cols * aspect * 0.5))
    return cols, rows


def render_grayscale(frame, cols, rows, invert):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if invert:
        gray = 255 - gray
    lines = frame_to_ascii_grid(gray, cols, rows)
    return "\n".join(lines)


def render_color(frame, cols, rows, invert):
    if invert:
        frame = 255 - frame
    lines, colors = frame_to_ascii_grid_color(frame, cols, rows)
    out_lines = []
    for line, color_row in zip(lines, colors):
        cells = []
        for ch, (r, g, b) in zip(line, color_row):
            cells.append(f"\033[38;2;{r};{g};{b}m{ch}")
        out_lines.append("".join(cells) + RESET)
    return "\n".join(out_lines)


def main():
    parser = argparse.ArgumentParser(description="Live webcam feed as ASCII art")
    parser.add_argument("--width", type=int, default=None,
                         help="Output width in characters (default: terminal width)")
    parser.add_argument("--color", action="store_true", help="Render in ANSI truecolor")
    parser.add_argument("--invert", action="store_true", help="Invert brightness mapping")
    parser.add_argument("--camera", type=int, default=0, help="Camera index (default 0)")
    parser.add_argument("--fps", type=int, default=15, help="Target frames per second")
    parser.add_argument("--mirror", choices=["on", "off"], default="on",
                         help="Mirror the feed horizontally (default: on)")
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"Could not open camera index {args.camera}.", file=sys.stderr)
        sys.exit(1)

    frame_delay = 1.0 / max(1, args.fps)

    print(HIDE_CURSOR, end="")
    try:
        while True:
            start = time.time()
            ok, frame = cap.read()
            if not ok:
                print("Failed to read frame from camera.", file=sys.stderr)
                break

            if args.mirror == "on":
                frame = cv2.flip(frame, 1)

            term_cols, _ = terminal_size()
            cols = args.width or term_cols
            cols = max(10, cols - 1)  # avoid wrapping at the edge
            frame_h, frame_w = frame.shape[:2]
            grid_cols, grid_rows = compute_grid_size(frame_w, frame_h, cols)

            if args.color:
                output = render_color(frame, grid_cols, grid_rows, args.invert)
            else:
                output = render_grayscale(frame, grid_cols, grid_rows, args.invert)

            sys.stdout.write(CLEAR_HOME + output + "\n")
            sys.stdout.flush()

            elapsed = time.time() - start
            sleep_for = frame_delay - elapsed
            if sleep_for > 0:
                time.sleep(sleep_for)
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        print(SHOW_CURSOR, end="")
        print("\nBye!")


if __name__ == "__main__":
    main()
