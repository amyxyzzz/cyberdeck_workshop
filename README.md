# Desk Pet

A small Pico-powered desk companion with a screen, touch sensor, motion sensor, button, and speaker. Wakes up when you walk past. Shows an animated cat, an ASCII aquarium with day/night cycling, or pages of any text you want to read. Plays lofi music.

Built for a 3.5-hour beginner workshop. No prior coding experience needed.

> Add a photo of your finished device here once you build it.

---

## What it does

- **Cat mode** — a cat sits on screen and reacts to taps with little animations: blink, snuggle, blow kisses. Custom greeting line you can change.
- **Aquarium mode** — ASCII fish swim past, seaweed sways, bubbles rise. The water and fish colors cycle through dawn / day / dusk / night.
- **Reader mode** — turns into a tiny kindle that pages through any `.txt` file you upload.
- **Music** — plays a lofi clip on loop from the speaker. Button toggles it on and off.
- **Motion-aware** — PIR sensor wakes the screen when you walk past; the device goes dark when nothing's been happening for a while.

## What you need

| Item | Notes |
|---|---|
| Raspberry Pi Pico | Pico, Pico W, or Pico 2 all work |
| USB cable | Must be a data cable, not power-only |
| 1.54" 240×240 ST7789 TFT | 7-pin SPI version |
| TTP223B capacitive touch module | The 3-pin breakout |
| HC-SR505 PIR motion sensor | Or HC-SR501, same wiring |
| MAX98357A I2S amplifier | Adafruit #3006 or clone |
| 3W / 4Ω speaker | Small enclosure speaker |
| Tactile button | 4-leg, 6mm |
| 10kΩ resistor | Pull-up for the button |
| Breadboard + ~30 jumper wires | Half-size board is plenty |

Total cost: roughly $25–45 depending on where you source parts.

## Quick start

1. **Install Thonny** from [thonny.org](https://thonny.org). It's a single program that bundles Python, an editor, and a serial connection to the Pico. No terminal needed.
2. **Plug in your Pico** with a USB cable.
3. **In Thonny → Tools → Options → Interpreter**, choose "MicroPython (Raspberry Pi Pico)" and pick your port. If MicroPython isn't installed yet, Thonny's "Install or update firmware" link walks you through it.
4. **Wire the hardware** per the pinout table below.
5. **In Thonny → View → Files**, drag everything from this repo's project files onto the Pico panel.
6. **Open `main.py`** and press **F5**. You should see the splash, then the cat.

Full walkthrough: [THONNY_GUIDE.md](THONNY_GUIDE.md).

## Pinout

| Component | GPIO | Physical pin | Notes |
|---|---|---|---|
| Button | GP15 | 20 | with 10kΩ pull-up to 3.3V |
| Touch sensor I/O | GP6 | 9 | |
| Screen CS | GP9 | 12 | |
| Screen SCK (labeled SCL) | GP10 | 14 | |
| Screen MOSI (labeled SDA) | GP11 | 15 | |
| Screen RST | GP12 | 16 | |
| Screen DC | GP13 | 17 | |
| Screen BLK | 3.3V | Pin 36 | always on |
| Speaker BCLK | GP16 | 21 | |
| Speaker LRC | GP17 | 22 | |
| Speaker DIN | GP18 | 24 | |
| PIR OUT | GP22 | 29 | |
| Speaker VIN, PIR VCC | VBUS | Pin 40 | 5V power |
| Touch VCC, Screen VCC | 3V3 | Pin 36 | 3.3V power |
| All GND | GND | any GND pin | common ground |

**Important:** Pin 15 is *not* GP15. Pin 15 is GND. GP15 is physical pin 20. Most common wiring mistake — always verify against the silkscreen labels on the Pico.

## Controls

| Input | What it does |
|---|---|
| Tap touch sensor (under 700 ms) | Mode-specific action: cycles cat animation, turns reader page, does nothing in aquarium |
| Hold touch sensor (700 ms or longer) | Switch mode: aquarium → cat → reader → aquarium |
| Press button | Toggle background music on/off |
| Motion in front of PIR | Wake screen if it's off |
| No motion or touch for 100 seconds | Screen auto-off |

## Customize it

The fun part. Edit these files in Thonny, re-save them to the Pico (File → Save as → MicroPython device), and watch the change.

- **`config.py`** — pin assignments and behavior tunables. Adjust `LONG_PRESS_MS`, `AUTO_OFF_MS`, `PHASE_DURATION_MS`, etc.
- **`cat.py`** — the `LABELS` dictionary at the top is what the cat says for each animation. Change `"hi friend!"` to `"hi <your name>!"`.
- **`aquarium.py`** — `FISH_RIGHT` / `FISH_LEFT` are the ASCII fish; add your own. `PHASES` controls the day/night palette.
- **`content/reader.txt`** — replace with any text you want to read on your pet.
- **`sounds/lofi.wav`** — replace with any 16-bit mono WAV. Convert other files with ffmpeg: `ffmpeg -i input.mp3 -ac 1 -ar 11025 -sample_fmt s16 -filter:a "volume=0.4" sounds/lofi.wav`

## Project structure

```
desk-pet/
  main.py              Entry point. The loop that reads inputs, switches modes, draws scenes.
  config.py            Pin numbers and behavior tunables.
  hardware.py          Debounced inputs (button, touch, PIR) with edge detection.
  splash.py            Boot animation.

  cat.py               Cat scene with idle / blink / snuggle / kiss animations.
  aquarium.py          ASCII aquarium with day/night cycling.
  reader.py            Kindle-style text pager.

  music.py             Streaming WAV playback for background music.
  sound.py             Synthesized tones for chimes and effects.

  lib/                 Third-party libraries (driver and fonts).
    st7789py.py        ST7789 screen driver.
    vga1_8x8.py        8×8 bitmap font.
    vga1_bold_16x16.py 16×16 bitmap font.

  content/
    reader.txt         Text shown in reader mode.

  sounds/
    lofi.wav           Background music.

  thonny_tests/        Self-contained test scripts. Open in Thonny, press F5.
    test_blink.py
    test_button.py
    test_touch.py
    test_button_and_touch.py
    test_screen_colors.py
    test_screen_aquarium.py
    test_speaker.py
    test_pir.py
```

## Documentation

- **[THONNY_GUIDE.md](THONNY_GUIDE.md)** — install Thonny, set up your Pico, daily workflow.
- **[WORKSHOP_SCRIPT.md](WORKSHOP_SCRIPT.md)** — full 3.5-hour workshop walkthrough.
- **[CHEATSHEET.md](CHEATSHEET.md)** — pinout, common errors, reference one-pager.
- **[ARCHITECTURE.md](ARCHITECTURE.md)** — how the code is organized and why.
- **[WORKSHOP.md](WORKSHOP.md)** — facilitator's plan for running the workshop.

## How it works (briefly)

The Pico runs one big loop, about 200 times a second. Each pass it: reads every input, detects what just changed (button presses, touch taps, motion), updates state (which mode is active, whether music is playing), draws the current scene if enough time has passed since the last frame, and streams the next bit of audio to the speaker. Then it sleeps for 5 milliseconds and starts over.

Everything you see and hear is built from this pattern — no hidden magic, just the loop checking and reacting.

## Troubleshooting

- **Screen colors look inverted (red→cyan, green→magenta):** edit `lib/st7789py.py` and comment out the line containing `INVON`.
- **Screen has a thin garbage strip at an edge:** the panel needs an offset. Try `_OFFSET_X = 0` and `_OFFSET_Y = 80` (or 53) in the driver.
- **PIR misfires for the first minute after boot:** normal. PIR sensors need 30–60 seconds to stabilize.
- **Speaker too loud / distorts:** move the GAIN pin to 3.3V instead of GND, or re-encode the WAV with ffmpeg at `volume=0.3`.
- **Music glitches when the screen redraws:** the audio buffer is underrunning. Bump `IBUF_BYTES` in `music.py` to `40000`.
- **Out of flash memory:** `make sync` is copy-only, not mirror. Old files stick around. Right-click → Delete them in the Pico panel of Thonny's file browser.

More detailed fixes are in [CHEATSHEET.md](CHEATSHEET.md).

## Credits

- [**russhughes/st7789py_mpy**](https://github.com/russhughes/st7789py_mpy) — TFT driver and bitmap fonts.
- **MicroPython** — the runtime that makes this whole thing approachable.
- Built for a workshop in 2026 by [your name].

## License

MIT. Use this for anything. If you build something cute with it, tag the workshop so we can see.
