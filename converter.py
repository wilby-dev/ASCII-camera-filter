"""
Converts image frames (numpy arrays from OpenCV) into ASCII text/color grids.
"""

import numpy as np

# Brightness ramp, darkest -> brightest. Feel free to swap for a denser ramp
# like " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
ASCII_RAMP = " .:-=+*#%@"


def frame_to_ascii_grid(frame_gray: np.ndarray, cols: int, rows: int) -> list[str]:
    """
    Downsamples a grayscale frame to (cols x rows) cells and maps each cell's
    average brightness to a character from ASCII_RAMP.

    Returns a list of `rows` strings, each `cols` characters long.
    """
    h, w = frame_gray.shape
    cell_h = h / rows
    cell_w = w / cols

    lines = []
    ramp_len = len(ASCII_RAMP)

    for r in range(rows):
        y0 = int(r * cell_h)
        y1 = int((r + 1) * cell_h) or y0 + 1
        row_chars = []
        for c in range(cols):
            x0 = int(c * cell_w)
            x1 = int((c + 1) * cell_w) or x0 + 1
            cell = frame_gray[y0:y1, x0:x1]
            brightness = cell.mean() if cell.size else 0  # 0-255
            idx = min(int(brightness / 256 * ramp_len), ramp_len - 1)
            row_chars.append(ASCII_RAMP[idx])
        lines.append("".join(row_chars))

    return lines


def frame_to_ascii_grid_color(frame_bgr: np.ndarray, cols: int, rows: int):
    """
    Like frame_to_ascii_grid, but also returns the average (r, g, b) color
    per cell, so the caller can render each character in its original color.

    Returns: (lines: list[str], colors: list[list[(r,g,b)]])
    """
    gray = frame_bgr.mean(axis=2)  # cheap grayscale for brightness
    h, w, _ = frame_bgr.shape
    cell_h = h / rows
    cell_w = w / cols

    lines = []
    colors = []
    ramp_len = len(ASCII_RAMP)

    for r in range(rows):
        y0 = int(r * cell_h)
        y1 = int((r + 1) * cell_h) or y0 + 1
        row_chars = []
        row_colors = []
        for c in range(cols):
            x0 = int(c * cell_w)
            x1 = int((c + 1) * cell_w) or x0 + 1
            cell_bgr = frame_bgr[y0:y1, x0:x1]
            cell_gray = gray[y0:y1, x0:x1]
            brightness = cell_gray.mean() if cell_gray.size else 0
            idx = min(int(brightness / 256 * ramp_len), ramp_len - 1)
            row_chars.append(ASCII_RAMP[idx])

            if cell_bgr.size:
                b, g, r_ = cell_bgr.reshape(-1, 3).mean(axis=0)
            else:
                b, g, r_ = 0, 0, 0
            row_colors.append((int(r_), int(g), int(b)))

        lines.append("".join(row_chars))
        colors.append(row_colors)

    return lines, colors
