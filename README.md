# Pico Hardware Project

A robust MicroPython base for a Raspberry Pi Pico (W) — button + capacitive
touch + onboard LED — set up to run from VS Code and `mpremote` instead of
Thonny.

## Why not Thonny?

Thonny hides the workflow. Once a project gets bigger than one file, you
want code in version control, an editor you actually like, and a single
command to push code to the chip. `mpremote` is the official MicroPython
CLI and gives you exactly that.

## One-time setup (macOS)

```bash
# 1. Tooling
brew install python3 make
python3 -m pip install --user --upgrade mpremote

# 2. Plug the Pico in and confirm it appears
ls /dev/tty.usbmodem*
```

In VS Code, install the **MicroPico** extension by paulober, then create
`.vscode/settings.json` in your project root with:

```json
{
  "python.analysis.extraPaths": ["./src"],
  "python.analysis.typeCheckingMode": "basic",
  "micropico.syncFolder": "src",
  "micropico.openOnStart": true,
  "micropico.autoConnect": true
}
```

If `mpremote` isn't on your PATH after install, add this to `~/.zshrc`:

```bash
export PATH="$HOME/Library/Python/3.*/bin:$PATH"
```

## Daily workflow

```bash
make sync    # copies src/ to the Pico and reboots it
make run     # runs src/main.py once without saving — fastest iteration
make repl    # live MicroPython prompt — Ctrl-X to exit
make reset   # soft reset
make ls      # list files on the Pico
```

If you have multiple Picos plugged in, override the port:
`make sync PORT=/dev/tty.usbmodem1101`

## Project layout

```
src/
  boot.py        # runs once at power-on
  main.py        # entry point
  config.py      # pin assignments + tunables
  hardware.py    # debounced inputs, LED wrapper
Makefile         # mpremote shortcuts
.vscode/         # editor + MicroPico config
```

## What changed vs. the original script

The original loop was correct but had three small problems that
get worse as projects grow:

1. **Bouncy reads** — mechanical switches make and break contact several
   times in a few ms. `DebouncedInput` filters that.
2. **Console spam** — `print("Nothing pressed!")` every 50 ms makes the
   REPL unusable. Logging now fires only on press/release *edges*.
3. **Pin numbers in main logic** — moving them to `config.py` means you
   tweak hardware without touching behavior.

The behavior is otherwise identical: LED on while either input is
active, logs "Button pressed" / "Touch detected" once per actuation.

## Hardware

- GP15 → push button → GND (uses internal pull-up)
- GP6  → TTP223B touch sensor OUT (sensor has its own pull-down)
- "LED" → onboard LED (works on both Pico and Pico W)

## Next steps when you outgrow this

- Add `uasyncio` if you start juggling more than ~3 inputs or need timers.
- Use `Pin.irq()` for true interrupt-driven inputs (lower latency, no polling).
- Split `hardware.py` into a `hardware/` package once it crosses ~200 lines.
