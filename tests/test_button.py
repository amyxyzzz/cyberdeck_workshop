"""Button smoke test.

Press the button. The onboard LED should light up while held.
The terminal prints DOWN/UP edges and a once-per-second heartbeat.

Run from your Mac/PC with:
    make test-button
"""
from machine import Pin
import time

import config
from hardware import DebouncedInput, StatusLED


def main():
    button = DebouncedInput(
        config.PIN_BUTTON,
        pull=Pin.PULL_UP,
        active_high=False,        # button to GND with pull-up
        debounce_ms=config.DEBOUNCE_MS,
    )
    led = StatusLED(config.PIN_LED)

    print("[test_button] Press the button. LED should match.")
    print("[test_button] Watch 'raw' — should flip 1 -> 0 while held.")
    print("[test_button] Ctrl-C to stop.")

    last_beat = time.ticks_ms()
    try:
        while True:
            rise, fall = button.update()
            if rise: print("[test_button] DOWN")
            if fall: print("[test_button] UP")

            led.set(button.pressed)

            now = time.ticks_ms()
            if time.ticks_diff(now, last_beat) >= 1000:
                print("[test_button]   heartbeat: raw={} pressed={}".format(
                    int(button.raw), int(button.pressed)))
                last_beat = now

            time.sleep_ms(5)
    except KeyboardInterrupt:
        led.off()
        print("[test_button] Stopped.")


if __name__ == "__main__":
    main()
