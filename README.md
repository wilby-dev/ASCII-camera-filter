# ascii-cam

Turns your webcam feed into live ASCII art in the terminal.

## Install

```bash
pip install -r requirements.txt
```

Needs OpenCV (for camera capture) and NumPy (for the pixel math). No terminal
libraries required — it renders with plain ANSI escape codes.

## Run it

```bash
python ascii_cam.py                # grayscale, sized to your terminal
python ascii_cam.py --color        # full ANSI truecolor ASCII
python ascii_cam.py --width 120    # wider/narrower render
python ascii_cam.py --invert       # dark-on-light instead of light-on-dark
python ascii_cam.py --camera 1     # pick a different camera
python ascii_cam.py --fps 24       # target frame rate
python ascii_cam.py --mirror off   # disable the default mirror-flip
```

Ctrl+C to quit.

## How it works
1. Grab a frame from the webcam with OpenCV.
2. Downsample it to a small grid (roughly your terminal's width x height,
   with a 0.5 aspect correction since terminal cells are taller than wide).
3. Map each cell's average brightness to a character from a ramp:
   `" .:-=+*#%@"` (space = darkest, `@` = brightest).
4. In `--color` mode, also average each cell's RGB and wrap the character
   in a `\033[38;2;r;g;bm` truecolor escape code instead of plain grey.
5. Reprint the whole grid each frame using a "cursor home" escape code
   instead of clearing the screen, which avoids flicker.

## Files

```
ascii-cam/
├── ascii_cam.py      # capture loop + terminal rendering
├── converter.py       # brightness/color -> ASCII grid conversion
├── requirements.txt
└── README.md
```

## Notes & known limits
- Terminal rendering will always be choppier than a real window — if you
  want smooth 30-60fps ASCII, the natural next step is rendering to a small
  Pygame/Tkinter window with a monospace font instead of printing to stdout.
- Performance is fine at typical terminal widths (80-160 cols) but the pure
  Python pixel loop will chug at very large widths; vectorizing with NumPy
  reshape/mean tricks is the next optimization if you want to push it further.
- If `cv2.VideoCapture(0)` doesn't find your camera, try `--camera 1` or
  check your OS's camera permissions for the terminal app.

## Push to GitHub

```bash
cd ascii-cam
git init
git add .
git commit -m "Initial commit: ASCII webcam filter"
gh repo create ascii-cam --public --source=. --push
```
