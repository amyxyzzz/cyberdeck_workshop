"""Screen + aquarium scene test — renders the aquarium for 20 seconds.

Run with:
    make test-screen-aquarium

If colors animate but the fish look stuck, check that aquarium.py
synced correctly. If the screen stays black, debug with
test-screen-colors first.
"""
from machine import Pin, SPI
import time

import config
import st7789py as st7789
from aquarium import Aquarium


def main():
    print("[test_aquarium] Setting up display...")
    spi = SPI(
        1, baudrate=config.SCREEN_SPI_BAUD,
        sck=Pin(config.PIN_SCREEN_SCK),
        mosi=Pin(config.PIN_SCREEN_MOSI),
    )
    display = st7789.ST7789(
        spi, 240, 240,
        reset=Pin(config.PIN_SCREEN_RST, Pin.OUT),
        cs=Pin(config.PIN_SCREEN_CS, Pin.OUT),
        dc=Pin(config.PIN_SCREEN_DC, Pin.OUT),
        backlight=None,
        rotation=0,
    )

    print("[test_aquarium] Building aquarium scene...")
    aq = Aquarium(display)
    aq.reset()

    print("[test_aquarium] Running for 20 seconds. Ctrl-C to stop early.")
    end = time.ticks_add(time.ticks_ms(), 20_000)
    try:
        while time.ticks_diff(end, time.ticks_ms()) > 0:
            aq.step()
            time.sleep_ms(config.SCREEN_FRAME_MS)
        print("[test_aquarium] Done.")
    except KeyboardInterrupt:
        print("[test_aquarium] Interrupted.")
    finally:
        display.fill(0)


if __name__ == "__main__":
    main()
