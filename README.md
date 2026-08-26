# Hand Gesture Mouse Control

Control your mouse cursor with a webcam. Move your index finger to move the
cursor; pinch your thumb and index finger together to click and drag.

## Requirements

- Python 3.9–3.11
- A webcam
- Windows, macOS, or Linux

## Setup

```bash
git clone https://github.com/<your-username>/hand-mouse-control.git
cd hand-mouse-control

python -m venv venv
source venv\Scripts\activate

pip install -r requirements.txt

python hand_mouse.py
```

Press `q` in the camera preview window to quit.

## OS-specific permissions

- **macOS**: grant Camera access and Accessibility access (System Settings →
  Privacy & Security) to whichever app runs the script (Terminal, iTerm,
  VS Code, etc.). Without Accessibility access, `pyautogui` cannot move the
  system cursor, the script will run with no visible effect.
- **Windows**: no special permission needed beyond the standard camera
  access prompt.
- **Linux**: depends on your window manager/display server. `pyautogui`'s
  mouse control does not work under native Wayland without additional
  configuration (X11 or XWayland is the reliable path).

## Tuning

All tunable values are constants at the top of `hand_mouse.py`:

| Constant | Effect |
|---|---|
| `CAM_INDEX` | Which camera to use if you have more than one |
| `FRAME_MARGIN` | How far from the camera edge counts as "reaching the screen edge." Larger = less hand travel needed, less precision. |
| `SMOOTHING` | Higher = smoother cursor movement, more input lag |
| `CLICK_DISTANCE_THRESHOLD` | Pixel distance between thumb and index tip that counts as a pinch. Lower = harder to trigger accidentally, but harder to trigger on purpose too |
| `SHOW_CAMERA_WINDOW` | Turn off the preview window once you've tuned things |

## Known limitations

- Tracking accuracy drops in low light or with a cluttered/low-contrast background.
- One hand only, by design (`max_num_hands=1`). Increase it in `hand_mouse.py` if you want two-hand tracking, but you'll need to add logic for which hand controls the cursor.
- No dedicated "right-click" or "scroll" gesture is implemented. Straightforward extensions: track a second gesture (e.g. thumb + middle finger pinch) for right-click, or index+middle finger distance for scroll.
- `pyautogui.FAILSAFE` is disabled so a stray cursor move to a screen corner won't abort the script. Re-enable it in the script if you want that as a manual kill-switch.

## License

MIT — do whatever you want with it.
