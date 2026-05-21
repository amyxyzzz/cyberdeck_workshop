"""Screen smoke test — fills the screen with primary colors, then text.

Run with:
    make test-screen-colors

What you should see, looping forever:
  1. Solid RED for 1s
  2. Solid GREEN for 1s
  3. Solid BLUE for 1s
  4. Solid WHITE for 1s
  5. A page of colored text for 2s

If colors look swapped (e.g. red looks cyan), edit screen driver and
comment out the INVON line. If the screen stays black, check MOSI/SCK
(GP11/GP10) and CS/DC/RST wiring.
"""
from machine import Pin, SPI
import time

import config
import st7789py as st7789
import vga1_8x8 as font


def main():
    print("[test_colors] Setting up SPI + ST7789...")
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

    colors = [
        ("RED",   st7789.color565(255, 0,   0)),
        ("GREEN", st7789.color565(0,   255, 0)),
        ("BLUE",  st7789.color565(0,   0,   255)),
        ("WHITE", st7789.color565(255, 255, 255)),
    ]
    iteration = 0
    try:
        while True:
            iteration += 1
            for name, c in colors:
                print("[test_colors]   fill {}".format(name))
                display.fill(c)
                time.sleep(1)
            print("[test_colors]   text page (iter {})".format(iteration))
            display.fill(st7789.color565(20, 30, 80))
            display.text(font, "HELLO PICO",       10,  10, st7789.WHITE)
            display.text(font, "Screen smoke test", 10,  30, st7789.YELLOW)
            display.text(font, "Colors working?",  10,  60, st7789.CYAN)
            display.text(font, "Text working?",    10,  75, st7789.CYAN)
            display.text(font, "iter {}".format(iteration), 10, 210, st7789.WHITE)
            time.sleep(2)
    except KeyboardInterrupt:
        print("[test_colors] Stopping.")
        display.fill(0)


if __name__ == "__main__":
    main()
