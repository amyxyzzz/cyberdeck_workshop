"""Combined button + cap sensor test.

The onboard LED lights when *either* input is active. Terminal shows
edges from each, plus a heartbeat with raw values so you can spot
wiring issues at a glance.

Run with:
    make test-button-cap
"""
from machine import Pin
import time

import config
from hardware import DebouncedInput, StatusLED


def main():
    button = DebouncedInput(
        config.PIN_BUTTON, pull=Pin.PULL_UP,
        active_high=False, debounce_ms=config.DEBOUNCE_MS,
    )
    touch = DebouncedInput(
        config.PIN_TOUCH, pull=None,
        active_high=True, debounce_ms=config.DEBOUNCE_MS,
    )
    led = StatusLED(config.PIN_LED)

    print("[test_btn_cap] Press the button, touch the pad. LED should light.")
    print("[test_btn_cap] Button raw goes 1 -> 0 when pressed.")
    print("[test_btn_cap] Touch raw goes 0 -> 1 when touched.")
    print("[test_btn_cap] Ctrl-C to stop.")

    last_beat = time.ticks_ms()
    try:
        while True:
            btn_rise, btn_fall = button.update()
            tch_rise, tch_fall = touch.update()

            if btn_rise: print("[test_btn_cap] Button DOWN")
            if btn_fall: print("[test_btn_cap] Button UP")
            if tch_rise: print("[test_btn_cap] Touch ON")
            if tch_fall: print("[test_btn_cap] Touch OFF")

            led.set(button.pressed or touch.pressed)

            now = time.ticks_ms()
            if time.ticks_diff(now, last_beat) >= 1000:
                print("[test_btn_cap]   hb  btn raw={} pressed={}  |  touch raw={} pressed={}".format(
                    int(button.raw), int(button.pressed),
                    int(touch.raw),  int(touch.pressed),
                ))
                last_beat = now

            time.sleep_ms(5)
    except KeyboardInterrupt:
        led.off()
        print("[test_btn_cap] Stopped.")


if __name__ == "__main__":
    main()
